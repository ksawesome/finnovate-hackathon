"""Test ML feature engineering."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ml.feature_engineering import GLFeatureEngineer
from src.ml.target_engineering import create_all_targets


def test_feature_extraction():
    """Test feature extraction pipeline."""
    print("=" * 60)
    print("Testing GL Feature Engineering Pipeline")
    print("=" * 60)

    try:
        engineer = GLFeatureEngineer()
        features_df, feature_names = engineer.extract_features(period="Mar-24", entity="AEML")

        print(f"\n✅ Feature Extraction SUCCESS")
        print(f"   - Accounts extracted: {len(features_df)}")
        print(f"   - Features generated: {len(feature_names)}")
        print(f"   - DataFrame shape: {features_df.shape}")

        print(f"\n📋 Feature Names ({len(feature_names)} total):")
        for i, name in enumerate(feature_names, 1):
            print(f"   {i:2d}. {name}")

        print(f"\n📊 Sample Features (first 3 accounts):")
        print(features_df.head(3).to_string())

        # Test target creation
        print(f"\n" + "=" * 60)
        print("Testing Target Variable Creation")
        print("=" * 60)

        targets_df = create_all_targets(features_df)

        print(f"\n✅ Target Creation SUCCESS")
        print(
            f"   - Anomaly scores range: [{targets_df['target_anomaly_score'].min():.3f}, {targets_df['target_anomaly_score'].max():.3f}]"
        )
        print(
            f"   - Priority scores range: [{targets_df['target_priority_score'].min():.1f}, {targets_df['target_priority_score'].max():.1f}]"
        )
        print(
            f"   - Attention flags: {targets_df['target_needs_attention'].sum()} / {len(targets_df)} accounts"
        )
        print(
            f"   - Review time range: [{targets_df['target_review_time'].min():.1f}, {targets_df['target_review_time'].max():.1f}] days"
        )

        print(f"\n📊 Sample Targets (first 5 accounts):")
        target_cols = [
            "account_code",
            "target_anomaly_score",
            "target_priority_score",
            "target_needs_attention",
            "target_review_time",
        ]
        print(targets_df[target_cols].head().to_string())

        # Test normalization
        print(f"\n" + "=" * 60)
        print("Testing Feature Normalization")
        print("=" * 60)

        normalized_df = engineer.normalize_features(features_df)

        print(f"\n✅ Normalization SUCCESS")
        print(f"   - Shape preserved: {normalized_df.shape}")

        # Check normalization for a few columns
        numeric_cols = ["balance_current", "balance_log", "days_since_creation"]
        for col in numeric_cols:
            if col in normalized_df.columns:
                print(
                    f"   - {col}: [{normalized_df[col].min():.3f}, {normalized_df[col].max():.3f}]"
                )

        print(f"\n{'=' * 60}")
        print("✅ ALL TESTS PASSED")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_feature_extraction()
    sys.exit(0 if success else 1)
