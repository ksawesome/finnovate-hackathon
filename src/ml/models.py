"""
ML Models for GL Account Intelligence.

Implements 3 production-ready models:
1. Anomaly Detection (Regression) - Predict anomaly score 0-1
2. Priority Ranking (Regression) - Predict review priority 0-10
3. Attention Prediction (Binary Classification) - Predict needs immediate attention

All models:
- Use MLflow for experiment tracking
- Support hyperparameter tuning
- Provide feature importance analysis
- Include model persistence and loading
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split

from src.ml.feature_engineering import GLFeatureEngineer
from src.ml.target_engineering import create_all_targets


class MLModelTrainer:
    """Train and manage ML models for GL account intelligence."""

    def __init__(self, mlflow_experiment_name: str = "gl_account_intelligence"):
        """
        Initialize ML trainer.

        Args:
            mlflow_experiment_name: Name for MLflow experiment
        """
        self.experiment_name = mlflow_experiment_name
        mlflow.set_experiment(mlflow_experiment_name)

        self.models = {}
        self.feature_engineer = GLFeatureEngineer()
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)

    def prepare_data(
        self,
        period: str = "Mar-24",
        entity: str | None = None,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> dict[str, Any]:
        """
        Prepare training data with features and targets.

        Args:
            period: Period to extract data for
            entity: Optional entity filter
            test_size: Proportion of test set
            random_state: Random seed for reproducibility

        Returns:
            Dict with X_train, X_test, y_train, y_test for each target
        """
        print(f"📊 Preparing data for {entity or 'all entities'} / {period}...")

        # Extract features
        features_df, feature_names = self.feature_engineer.extract_features(
            period=period, entity=entity
        )

        if len(features_df) == 0:
            raise ValueError("No data available for training")

        # Create targets
        data_df = create_all_targets(features_df)

        # Select feature columns (exclude identifiers and targets)
        feature_cols = [
            col
            for col in data_df.columns
            if col not in ["account_id", "account_code"] and not col.startswith("target_")
        ]

        X = data_df[feature_cols].fillna(0)

        # Prepare datasets for each target
        datasets = {}

        # 1. Anomaly Detection (Regression)
        y_anomaly = data_df["target_anomaly_score"]
        X_train_anom, X_test_anom, y_train_anom, y_test_anom = train_test_split(
            X, y_anomaly, test_size=test_size, random_state=random_state
        )
        datasets["anomaly"] = {
            "X_train": X_train_anom,
            "X_test": X_test_anom,
            "y_train": y_train_anom,
            "y_test": y_test_anom,
        }

        # 2. Priority Ranking (Regression)
        y_priority = data_df["target_priority_score"]
        X_train_pri, X_test_pri, y_train_pri, y_test_pri = train_test_split(
            X, y_priority, test_size=test_size, random_state=random_state
        )
        datasets["priority"] = {
            "X_train": X_train_pri,
            "X_test": X_test_pri,
            "y_train": y_train_pri,
            "y_test": y_test_pri,
        }

        # 3. Attention Prediction (Classification)
        y_attention = data_df["target_needs_attention"]
        X_train_att, X_test_att, y_train_att, y_test_att = train_test_split(
            X, y_attention, test_size=test_size, random_state=random_state
        )
        datasets["attention"] = {
            "X_train": X_train_att,
            "X_test": X_test_att,
            "y_train": y_train_att,
            "y_test": y_test_att,
        }

        datasets["feature_names"] = feature_cols
        datasets["n_samples"] = len(X)

        print(f"✅ Data prepared: {len(X)} samples, {len(feature_cols)} features")
        print(f"   - Train/Test split: {len(X_train_anom)}/{len(X_test_anom)}")

        return datasets

    def train_anomaly_detector(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        hyperparameter_tune: bool = False,
    ) -> tuple[Any, dict[str, float]]:
        """
        Train anomaly detection model (Random Forest Regressor).

        Args:
            X_train, y_train: Training data
            X_test, y_test: Test data
            hyperparameter_tune: Whether to run grid search

        Returns:
            Tuple of (trained_model, metrics_dict)
        """
        print("\n🤖 Training Anomaly Detection Model...")

        with mlflow.start_run(run_name="anomaly_detector"):
            # Log parameters
            mlflow.log_param("model_type", "RandomForestRegressor")
            mlflow.log_param("n_samples", len(X_train))
            mlflow.log_param("n_features", X_train.shape[1])

            if hyperparameter_tune:
                print("   🔍 Running hyperparameter tuning...")
                param_grid = {
                    "n_estimators": [50, 100, 200],
                    "max_depth": [10, 20, None],
                    "min_samples_split": [2, 5, 10],
                }

                rf = RandomForestRegressor(random_state=42)
                grid_search = GridSearchCV(
                    rf, param_grid, cv=3, scoring="neg_mean_squared_error", n_jobs=-1
                )
                grid_search.fit(X_train, y_train)

                model = grid_search.best_estimator_
                mlflow.log_params(grid_search.best_params_)
                print(f"   ✅ Best params: {grid_search.best_params_}")
            else:
                # Default hyperparameters
                model = RandomForestRegressor(
                    n_estimators=100, max_depth=20, min_samples_split=5, random_state=42, n_jobs=-1
                )
                mlflow.log_params(
                    {
                        "n_estimators": 100,
                        "max_depth": 20,
                        "min_samples_split": 5,
                    }
                )

                model.fit(X_train, y_train)

            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)

            # Metrics
            metrics = {
                "train_mae": mean_absolute_error(y_train, y_pred_train),
                "train_mse": mean_squared_error(y_train, y_pred_train),
                "train_r2": r2_score(y_train, y_pred_train),
                "test_mae": mean_absolute_error(y_test, y_pred_test),
                "test_mse": mean_squared_error(y_test, y_pred_test),
                "test_r2": r2_score(y_test, y_pred_test),
            }

            # Log metrics
            mlflow.log_metrics(metrics)

            # Feature importance
            feature_importance = pd.DataFrame(
                {"feature": X_train.columns, "importance": model.feature_importances_}
            ).sort_values("importance", ascending=False)

            # Log top 10 features
            for idx, row in feature_importance.head(10).iterrows():
                mlflow.log_metric(f"importance_{row['feature']}", row["importance"])

            # Log model
            mlflow.sklearn.log_model(model, "model")

            print(f"   ✅ Test R²: {metrics['test_r2']:.4f}")
            print(f"   ✅ Test MAE: {metrics['test_mae']:.4f}")

            return model, metrics

    def train_priority_ranker(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        hyperparameter_tune: bool = False,
    ) -> tuple[Any, dict[str, float]]:
        """
        Train priority ranking model (Gradient Boosting Regressor).

        Args:
            X_train, y_train: Training data
            X_test, y_test: Test data
            hyperparameter_tune: Whether to run grid search

        Returns:
            Tuple of (trained_model, metrics_dict)
        """
        print("\n🎯 Training Priority Ranking Model...")

        with mlflow.start_run(run_name="priority_ranker"):
            mlflow.log_param("model_type", "GradientBoostingRegressor")
            mlflow.log_param("n_samples", len(X_train))
            mlflow.log_param("n_features", X_train.shape[1])

            if hyperparameter_tune:
                print("   🔍 Running hyperparameter tuning...")
                param_grid = {
                    "n_estimators": [50, 100, 150],
                    "max_depth": [3, 5, 7],
                    "learning_rate": [0.01, 0.1, 0.2],
                }

                gb = GradientBoostingRegressor(random_state=42)
                grid_search = GridSearchCV(
                    gb, param_grid, cv=3, scoring="neg_mean_squared_error", n_jobs=-1
                )
                grid_search.fit(X_train, y_train)

                model = grid_search.best_estimator_
                mlflow.log_params(grid_search.best_params_)
                print(f"   ✅ Best params: {grid_search.best_params_}")
            else:
                model = GradientBoostingRegressor(
                    n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
                )
                mlflow.log_params(
                    {
                        "n_estimators": 100,
                        "max_depth": 5,
                        "learning_rate": 0.1,
                    }
                )

                model.fit(X_train, y_train)

            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)

            # Metrics
            metrics = {
                "train_mae": mean_absolute_error(y_train, y_pred_train),
                "train_mse": mean_squared_error(y_train, y_pred_train),
                "train_r2": r2_score(y_train, y_pred_train),
                "test_mae": mean_absolute_error(y_test, y_pred_test),
                "test_mse": mean_squared_error(y_test, y_pred_test),
                "test_r2": r2_score(y_test, y_pred_test),
            }

            mlflow.log_metrics(metrics)

            # Feature importance
            feature_importance = pd.DataFrame(
                {"feature": X_train.columns, "importance": model.feature_importances_}
            ).sort_values("importance", ascending=False)

            for idx, row in feature_importance.head(10).iterrows():
                mlflow.log_metric(f"importance_{row['feature']}", row["importance"])

            mlflow.sklearn.log_model(model, "model")

            print(f"   ✅ Test R²: {metrics['test_r2']:.4f}")
            print(f"   ✅ Test MAE: {metrics['test_mae']:.4f}")

            return model, metrics

    def train_attention_classifier(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        hyperparameter_tune: bool = False,
    ) -> tuple[Any, dict[str, float]]:
        """
        Train attention prediction classifier (Random Forest Classifier).

        Args:
            X_train, y_train: Training data
            X_test, y_test: Test data
            hyperparameter_tune: Whether to run grid search

        Returns:
            Tuple of (trained_model, metrics_dict)
        """
        print("\n🚨 Training Attention Prediction Model...")

        with mlflow.start_run(run_name="attention_classifier"):
            mlflow.log_param("model_type", "RandomForestClassifier")
            mlflow.log_param("n_samples", len(X_train))
            mlflow.log_param("n_features", X_train.shape[1])
            mlflow.log_param("class_balance", f"{y_train.sum()}/{len(y_train)}")

            if hyperparameter_tune:
                print("   🔍 Running hyperparameter tuning...")
                param_grid = {
                    "n_estimators": [50, 100, 200],
                    "max_depth": [10, 20, None],
                    "min_samples_split": [2, 5, 10],
                    "class_weight": ["balanced", None],
                }

                rf = RandomForestClassifier(random_state=42)
                grid_search = GridSearchCV(rf, param_grid, cv=3, scoring="roc_auc", n_jobs=-1)
                grid_search.fit(X_train, y_train)

                model = grid_search.best_estimator_
                mlflow.log_params(grid_search.best_params_)
                print(f"   ✅ Best params: {grid_search.best_params_}")
            else:
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=20,
                    min_samples_split=5,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                )
                mlflow.log_params(
                    {
                        "n_estimators": 100,
                        "max_depth": 20,
                        "min_samples_split": 5,
                        "class_weight": "balanced",
                    }
                )

                model.fit(X_train, y_train)

            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)

            # Handle probability prediction for binary classification
            try:
                y_pred_proba_test = model.predict_proba(X_test)[:, 1]
            except IndexError:
                # Only one class present, use probability of that class
                y_pred_proba_test = model.predict_proba(X_test)[:, 0]

            # Metrics
            metrics = {
                "train_accuracy": accuracy_score(y_train, y_pred_train),
                "test_accuracy": accuracy_score(y_test, y_pred_test),
                "test_precision": precision_score(y_test, y_pred_test, zero_division=0),
                "test_recall": recall_score(y_test, y_pred_test, zero_division=0),
                "test_f1": f1_score(y_test, y_pred_test, zero_division=0),
            }

            # ROC-AUC only if both classes present
            if len(np.unique(y_test)) > 1:
                metrics["test_roc_auc"] = roc_auc_score(y_test, y_pred_proba_test)

            mlflow.log_metrics(metrics)

            # Feature importance
            feature_importance = pd.DataFrame(
                {"feature": X_train.columns, "importance": model.feature_importances_}
            ).sort_values("importance", ascending=False)

            for idx, row in feature_importance.head(10).iterrows():
                mlflow.log_metric(f"importance_{row['feature']}", row["importance"])

            mlflow.sklearn.log_model(model, "model")

            print(f"   ✅ Test Accuracy: {metrics['test_accuracy']:.4f}")
            print(f"   ✅ Test F1: {metrics['test_f1']:.4f}")
            if "test_roc_auc" in metrics:
                print(f"   ✅ Test ROC-AUC: {metrics['test_roc_auc']:.4f}")

            return model, metrics

    def train_all_models(
        self, period: str = "Mar-24", entity: str | None = None, hyperparameter_tune: bool = False
    ) -> dict[str, Any]:
        """
        Train all 3 models in sequence.

        Args:
            period: Period to train on
            entity: Optional entity filter
            hyperparameter_tune: Whether to run grid search for all models

        Returns:
            Dict with trained models and metrics
        """
        print("=" * 70)
        print("🚀 Training All ML Models for GL Account Intelligence")
        print("=" * 70)

        # Prepare data
        datasets = self.prepare_data(period=period, entity=entity)

        results = {}

        # Train Anomaly Detector
        anomaly_model, anomaly_metrics = self.train_anomaly_detector(
            datasets["anomaly"]["X_train"],
            datasets["anomaly"]["y_train"],
            datasets["anomaly"]["X_test"],
            datasets["anomaly"]["y_test"],
            hyperparameter_tune=hyperparameter_tune,
        )
        results["anomaly"] = {"model": anomaly_model, "metrics": anomaly_metrics}
        self.models["anomaly"] = anomaly_model

        # Train Priority Ranker
        priority_model, priority_metrics = self.train_priority_ranker(
            datasets["priority"]["X_train"],
            datasets["priority"]["y_train"],
            datasets["priority"]["X_test"],
            datasets["priority"]["y_test"],
            hyperparameter_tune=hyperparameter_tune,
        )
        results["priority"] = {"model": priority_model, "metrics": priority_metrics}
        self.models["priority"] = priority_model

        # Train Attention Classifier
        attention_model, attention_metrics = self.train_attention_classifier(
            datasets["attention"]["X_train"],
            datasets["attention"]["y_train"],
            datasets["attention"]["X_test"],
            datasets["attention"]["y_test"],
            hyperparameter_tune=hyperparameter_tune,
        )
        results["attention"] = {"model": attention_model, "metrics": attention_metrics}
        self.models["attention"] = attention_model

        # Save models locally
        self.save_models()

        print("\n" + "=" * 70)
        print("✅ All Models Trained Successfully!")
        print("=" * 70)
        print("\n📊 Summary:")
        print(f"   Anomaly Detector R²: {anomaly_metrics['test_r2']:.4f}")
        print(f"   Priority Ranker R²: {priority_metrics['test_r2']:.4f}")
        print(f"   Attention Classifier F1: {attention_metrics['test_f1']:.4f}")
        print(f"\n💾 Models saved to: {self.model_dir}/")
        print("📈 MLflow tracking at: mlruns/")

        return results

    def save_models(self):
        """Save all trained models to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for model_name, model in self.models.items():
            filepath = self.model_dir / f"{model_name}_model_{timestamp}.pkl"
            joblib.dump(model, filepath)
            print(f"   💾 Saved {model_name} model to {filepath}")

    def load_model(self, model_name: str, filepath: str | None = None) -> Any:
        """
        Load a trained model from disk.

        Args:
            model_name: Name of model ('anomaly', 'priority', 'attention')
            filepath: Optional custom filepath

        Returns:
            Loaded model
        """
        if filepath:
            model = joblib.load(filepath)
        else:
            # Load latest model for this type
            model_files = list(self.model_dir.glob(f"{model_name}_model_*.pkl"))
            if not model_files:
                raise FileNotFoundError(f"No saved models found for {model_name}")

            latest_file = max(model_files, key=lambda p: p.stat().st_mtime)
            model = joblib.load(latest_file)

        self.models[model_name] = model
        return model

    def predict(
        self, features_df: pd.DataFrame, model_names: list[str] | None = None
    ) -> pd.DataFrame:
        """
        Make predictions with trained models.

        Args:
            features_df: Features DataFrame
            model_names: List of models to use (default: all)

        Returns:
            DataFrame with predictions
        """
        if model_names is None:
            model_names = list(self.models.keys())

        predictions_df = features_df.copy()

        # Select feature columns
        feature_cols = [
            col for col in features_df.columns if col not in ["account_id", "account_code"]
        ]
        X = features_df[feature_cols].fillna(0)

        # Make predictions
        if "anomaly" in model_names and "anomaly" in self.models:
            predictions_df["pred_anomaly_score"] = self.models["anomaly"].predict(X)

        if "priority" in model_names and "priority" in self.models:
            predictions_df["pred_priority_score"] = self.models["priority"].predict(X)

        if "attention" in model_names and "attention" in self.models:
            predictions_df["pred_needs_attention"] = self.models["attention"].predict(X)
            try:
                predictions_df["pred_attention_proba"] = self.models["attention"].predict_proba(X)[
                    :, 1
                ]
            except IndexError:
                predictions_df["pred_attention_proba"] = self.models["attention"].predict_proba(X)[
                    :, 0
                ]

        return predictions_df


if __name__ == "__main__":
    # Test ML training
    print("Testing ML Model Training...")

    trainer = MLModelTrainer(mlflow_experiment_name="test_gl_intelligence")

    # Train all models
    results = trainer.train_all_models(
        period="Mar-24",
        entity="AEML",
        hyperparameter_tune=False,  # Set to True for grid search
    )

    print("\n" + "=" * 70)
    print("🎉 ML Training Complete!")
    print("=" * 70)
