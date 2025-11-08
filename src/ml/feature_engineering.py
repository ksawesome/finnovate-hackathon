"""
Feature Engineering Pipeline for GL Account Intelligence.

Extracts 30 features from raw GL data for ML models:
- Balance Features (5): Current, absolute, log-scaled, variance, z-score
- Temporal Features (8): Days since creation, review velocity, period attributes
- Metadata Features (6): Name/description length, keywords, documentation status
- Behavioral Features (6): Review history, assignment patterns, interaction metrics
- Categorical Features (5): Category, criticality, department, entity (encoded)

Usage:
    engineer = GLFeatureEngineer(session)
    features_df, feature_names = engineer.extract_features(period='Mar-24')
"""

from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sqlalchemy.orm import Session

from src.db import get_postgres_session
from src.db.postgres import GLAccount, get_gl_accounts_by_period


class GLFeatureEngineer:
    """Extract and engineer features from GL account data for ML models."""

    def __init__(self, session: Session | None = None):
        """
        Initialize feature engineer.

        Args:
            session: SQLAlchemy session (auto-created if None)
        """
        self.session = session or get_postgres_session()
        self.scaler = StandardScaler()
        self.label_encoders = {}

    def extract_features(
        self, period: str | None = None, entity: str | None = None
    ) -> tuple[pd.DataFrame, list[str]]:
        """
        Extract all 30 features from GL accounts.

        Args:
            period: Period to extract features for (None = all periods)
            entity: Entity to filter by (None = all entities)

        Returns:
            Tuple of (features_df, feature_names)
        """
        # Fetch GL accounts
        if period:
            accounts = get_gl_accounts_by_period(period)
        else:
            accounts = self.session.query(GLAccount).all()

        if entity:
            accounts = [a for a in accounts if a.entity == entity]

        if not accounts:
            # Return empty DataFrame with all feature columns
            return pd.DataFrame(columns=self._get_feature_names()), []

        # Convert to DataFrame
        df = pd.DataFrame(
            [
                {
                    "account_id": a.id,
                    "account_code": a.account_code,
                    "account_name": a.account_name,
                    "balance": a.balance,
                    "category": a.status or "Unknown",  # Status field (Assets, Liabilities, etc.)
                    "account_category": a.account_category or "Unknown",
                    "department": a.department or "Unknown",
                    "entity": a.entity,
                    "period": a.period,
                    "criticality": a.criticality or "Medium",
                    "review_status": a.review_status,
                    "created_at": a.created_at,
                    "updated_at": a.updated_at,
                }
                for a in accounts
            ]
        )

        # Extract each feature group
        balance_features = self._extract_balance_features(df)
        temporal_features = self._extract_temporal_features(df)
        metadata_features = self._extract_metadata_features(df)
        behavioral_features = self._extract_behavioral_features(df)
        categorical_features = self._extract_categorical_features(df)

        # Combine all features
        features_df = pd.concat(
            [
                df[["account_id", "account_code"]],  # Keep identifiers
                balance_features,
                temporal_features,
                metadata_features,
                behavioral_features,
                categorical_features,
            ],
            axis=1,
        )

        feature_names = self._get_feature_names()

        return features_df, feature_names

    def _extract_balance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract 5 balance-related features.

        Features:
        1. balance_current: Raw balance
        2. balance_abs: Absolute value
        3. balance_log: Log-scaled (log1p for safety)
        4. balance_variance: Variance from mean
        5. balance_zscore: Z-score normalization
        """
        balance = df["balance"].astype(float).fillna(0)

        return pd.DataFrame(
            {
                "balance_current": balance,
                "balance_abs": balance.abs(),
                "balance_log": np.log1p(balance.abs()),
                "balance_variance": balance - balance.mean(),
                "balance_zscore": (balance - balance.mean()) / (balance.std() + 1e-10),
            }
        )

    def _extract_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract 8 temporal features.

        Features:
        1. days_since_creation: Days from created_at to now
        2. days_since_update: Days from updated_at to now
        3. review_velocity: Days between creation and update (proxy for review speed)
        4. is_recent: Boolean if created in last 7 days
        5. period_month: Month number from period string
        6. period_year: Year from period string
        7. is_quarter_end: Boolean if period is quarter-end month (Mar, Jun, Sep, Dec)
        8. is_year_end: Boolean if period is year-end (Mar for Indian FY)
        """
        now = datetime.utcnow()

        # Handle missing timestamps
        created_at = pd.to_datetime(df["created_at"], errors="coerce").fillna(now)
        updated_at = pd.to_datetime(df["updated_at"], errors="coerce").fillna(now)

        # Parse period (format: "Mar-24" → month=3, year=2024)
        def parse_period(period_str):
            if pd.isna(period_str):
                return 3, 2024
            try:
                month_map = {
                    "Jan": 1,
                    "Feb": 2,
                    "Mar": 3,
                    "Apr": 4,
                    "May": 5,
                    "Jun": 6,
                    "Jul": 7,
                    "Aug": 8,
                    "Sep": 9,
                    "Oct": 10,
                    "Nov": 11,
                    "Dec": 12,
                }
                parts = str(period_str).split("-")
                month = month_map.get(parts[0], 3)
                year = 2000 + int(parts[1]) if len(parts) > 1 else 2024
                return month, year
            except:
                return 3, 2024

        period_data = df["period"].apply(parse_period)
        period_months = period_data.apply(lambda x: x[0])
        period_years = period_data.apply(lambda x: x[1])

        return pd.DataFrame(
            {
                "days_since_creation": (now - created_at).dt.total_seconds() / 86400,
                "days_since_update": (now - updated_at).dt.total_seconds() / 86400,
                "review_velocity": (updated_at - created_at).dt.total_seconds() / 86400,
                "is_recent": ((now - created_at).dt.total_seconds() / 86400 <= 7).astype(int),
                "period_month": period_months,
                "period_year": period_years,
                "is_quarter_end": period_months.isin([3, 6, 9, 12]).astype(int),
                "is_year_end": (period_months == 3).astype(int),  # Indian FY ends in March
            }
        )

    def _extract_metadata_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract 6 metadata features.

        Features:
        1. name_length: Length of account name
        2. code_length: Length of account code
        3. has_expense_keyword: Contains expense-related words
        4. has_revenue_keyword: Contains revenue-related words
        5. has_liability_keyword: Contains liability-related words
        6. description_complexity: Ratio of unique chars to length
        """
        account_name = df["account_name"].fillna("")
        account_code = df["account_code"].fillna("")

        # Keyword checks
        expense_keywords = r"expense|cost|payment|charge|fee"
        revenue_keywords = r"revenue|income|sales|earning|gain"
        liability_keywords = r"liability|payable|debt|loan|owing"

        return pd.DataFrame(
            {
                "name_length": account_name.str.len(),
                "code_length": account_code.str.len(),
                "has_expense_keyword": account_name.str.lower()
                .str.contains(expense_keywords, regex=True)
                .astype(int),
                "has_revenue_keyword": account_name.str.lower()
                .str.contains(revenue_keywords, regex=True)
                .astype(int),
                "has_liability_keyword": account_name.str.lower()
                .str.contains(liability_keywords, regex=True)
                .astype(int),
                "description_complexity": account_name.apply(
                    lambda x: len(set(x)) / (len(x) + 1e-10) if x else 0
                ),
            }
        )

    def _extract_behavioral_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract 6 behavioral features.

        Features:
        1. is_reviewed: Boolean if review_status == 'reviewed'
        2. is_pending: Boolean if review_status == 'pending'
        3. is_flagged: Boolean if review_status == 'flagged'
        4. is_zero_balance: Boolean if balance == 0
        5. is_high_value: Boolean if |balance| > 50M
        6. needs_attention: Combined flag (flagged OR (pending AND high_value))
        """
        balance = df["balance"].fillna(0)
        status = df["review_status"].fillna("pending")

        is_reviewed = (status == "reviewed").astype(int)
        is_pending = (status == "pending").astype(int)
        is_flagged = (status == "flagged").astype(int)
        is_zero_balance = (balance == 0).astype(int)
        is_high_value = (balance.abs() > 50_000_000).astype(int)

        return pd.DataFrame(
            {
                "is_reviewed": is_reviewed,
                "is_pending": is_pending,
                "is_flagged": is_flagged,
                "is_zero_balance": is_zero_balance,
                "is_high_value": is_high_value,
                "needs_attention": (
                    (is_flagged == 1) | ((is_pending == 1) & (is_high_value == 1))
                ).astype(int),
            }
        )

    def _extract_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract 5 categorical features (label-encoded).

        Features:
        1. category_encoded: Account category (Assets, Liabilities, etc.)
        2. criticality_encoded: Criticality level (Critical, High, Medium, Low)
        3. department_encoded: Department name
        4. entity_encoded: Entity code
        5. period_encoded: Period string
        """
        categorical_cols = ["category", "criticality", "department", "entity", "period"]
        encoded_features = {}

        for col in categorical_cols:
            # Fill NaN with 'Unknown'
            values = df[col].fillna("Unknown").astype(str)

            # Create or reuse label encoder
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                self.label_encoders[col].fit(values)

            # Encode
            try:
                encoded = self.label_encoders[col].transform(values)
            except ValueError:
                # Handle unseen categories
                encoded = np.zeros(len(values), dtype=int)

            encoded_features[f"{col}_encoded"] = encoded

        return pd.DataFrame(encoded_features)

    def _get_feature_names(self) -> list[str]:
        """Return list of all 30 feature names."""
        return [
            # Balance features (5)
            "balance_current",
            "balance_abs",
            "balance_log",
            "balance_variance",
            "balance_zscore",
            # Temporal features (8)
            "days_since_creation",
            "days_since_update",
            "review_velocity",
            "is_recent",
            "period_month",
            "period_year",
            "is_quarter_end",
            "is_year_end",
            # Metadata features (6)
            "name_length",
            "code_length",
            "has_expense_keyword",
            "has_revenue_keyword",
            "has_liability_keyword",
            "description_complexity",
            # Behavioral features (6)
            "is_reviewed",
            "is_pending",
            "is_flagged",
            "is_zero_balance",
            "is_high_value",
            "needs_attention",
            # Categorical features (5)
            "category_encoded",
            "criticality_encoded",
            "department_encoded",
            "entity_encoded",
            "period_encoded",
        ]

    def normalize_features(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize numeric features to [0, 1] range.

        Args:
            features_df: Features DataFrame from extract_features()

        Returns:
            Normalized features DataFrame
        """
        # Select numeric columns only (exclude identifiers and encoded categoricals)
        numeric_cols = [
            "balance_current",
            "balance_abs",
            "balance_log",
            "balance_variance",
            "balance_zscore",
            "days_since_creation",
            "days_since_update",
            "review_velocity",
            "name_length",
            "code_length",
            "description_complexity",
        ]

        normalized_df = features_df.copy()

        for col in numeric_cols:
            if col in normalized_df.columns:
                values = normalized_df[col].fillna(0)
                min_val = values.min()
                max_val = values.max()
                if max_val > min_val:
                    normalized_df[col] = (values - min_val) / (max_val - min_val)
                else:
                    normalized_df[col] = 0

        return normalized_df


# Convenience function
def extract_gl_features(
    period: str = "Mar-24", entity: str | None = None
) -> tuple[pd.DataFrame, list[str]]:
    """
    Quick feature extraction function.

    Args:
        period: Period to extract features for
        entity: Optional entity filter

    Returns:
        Tuple of (features_df, feature_names)
    """
    engineer = GLFeatureEngineer()
    return engineer.extract_features(period=period, entity=entity)


if __name__ == "__main__":
    # Test feature extraction
    print("Testing GL Feature Engineering...")

    engineer = GLFeatureEngineer()
    features_df, feature_names = engineer.extract_features(period="Mar-24", entity="AEML")

    print(f"\n✅ Extracted {len(features_df)} GL accounts")
    print(f"✅ Generated {len(feature_names)} features: {feature_names[:10]}...")
    print(f"\n📊 Feature DataFrame shape: {features_df.shape}")
    print("\n🔍 Sample features:")
    print(features_df.head())

    # Test normalization
    normalized_df = engineer.normalize_features(features_df)
    print(f"\n✅ Normalized features shape: {normalized_df.shape}")
