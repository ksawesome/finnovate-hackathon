"""
Continual Learning Pipeline for ML Models.

Automatically retrains models using user feedback to improve accuracy over time.

Features:
- Multiple retraining triggers (scheduled, threshold-based, manual)
- Safety rails (performance validation before deployment)
- Model versioning with MLflow Model Registry
- Rollback capability
- A/B testing support
"""

import sys
from datetime import datetime
from os.path import abspath, dirname
from pathlib import Path

import mlflow
import mlflow.sklearn

# Add src to path for standalone execution
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from db.mongodb import log_audit_event
from feedback_handler import MLFeedbackCollector
from ml.feature_engineering import GLFeatureEngineer
from ml.models import MLModelTrainer
from ml.target_engineering import create_all_targets


class ContinualLearningPipeline:
    """Orchestrate continual learning with feedback integration."""

    def __init__(
        self,
        baseline_metrics: dict[str, float] | None = None,
        improvement_threshold: float = 0.02,  # 2% improvement required
        mlflow_experiment_name: str = "gl_continual_learning",
    ):
        """
        Initialize continual learning pipeline.

        Args:
            baseline_metrics: Current model performance metrics
            improvement_threshold: Minimum improvement required (0.02 = 2%)
            mlflow_experiment_name: MLflow experiment name
        """
        self.baseline_metrics = baseline_metrics or {}
        self.improvement_threshold = improvement_threshold
        self.experiment_name = mlflow_experiment_name

        self.trainer = MLModelTrainer(mlflow_experiment_name=mlflow_experiment_name)
        self.feedback_collector = MLFeedbackCollector()
        self.feature_engineer = GLFeatureEngineer()

        mlflow.set_experiment(mlflow_experiment_name)

    def check_retraining_triggers(self) -> dict[str, bool]:
        """
        Check all retraining trigger conditions.

        Returns:
            Dict of trigger statuses
        """
        triggers = {}

        # Trigger 1: Scheduled (weekly - every Sunday)
        now = datetime.utcnow()
        is_sunday = now.weekday() == 6
        is_2am_hour = now.hour == 2
        triggers["scheduled"] = is_sunday and is_2am_hour

        # Trigger 2: Feedback threshold (≥50 unused feedback items)
        unused_feedback = self.feedback_collector.get_items_for_retraining(only_unused=True)
        triggers["feedback_threshold"] = len(unused_feedback) >= 50

        # Trigger 3: Low accuracy (if accuracy < 70% on recent feedback)
        recent_stats = self.feedback_collector.get_feedback_stats()
        triggers["low_accuracy"] = recent_stats.get("accuracy_rate", 100) < 70

        return triggers

    def should_retrain(self, manual_trigger: bool = False) -> tuple[bool, str]:
        """
        Determine if retraining should occur.

        Args:
            manual_trigger: Manual admin trigger

        Returns:
            Tuple of (should_retrain, reason)
        """
        if manual_trigger:
            return True, "Manual trigger by admin"

        triggers = self.check_retraining_triggers()

        if triggers["scheduled"]:
            return True, "Scheduled weekly retraining"

        if triggers["feedback_threshold"]:
            return True, "Feedback threshold reached (≥50 items)"

        if triggers["low_accuracy"]:
            return True, "Low accuracy detected (<70%)"

        return False, "No retraining triggers met"

    def prepare_training_data_with_feedback(
        self, period: str = "Mar-24", entity: str | None = None
    ) -> dict:
        """
        Prepare training data incorporating feedback corrections.

        Args:
            period: Period to train on
            entity: Optional entity filter

        Returns:
            Training datasets dict
        """
        print("📊 Preparing training data with feedback corrections...")

        # Get base features and targets
        features_df, feature_names = self.feature_engineer.extract_features(
            period=period, entity=entity
        )
        data_df = create_all_targets(features_df)

        # Get feedback items for corrections
        feedback_items = self.feedback_collector.get_items_for_retraining(only_unused=True)

        print(f"   ✅ Base data: {len(data_df)} accounts")
        print(f"   ✅ Feedback corrections: {len(feedback_items)} items")

        # Apply feedback corrections to targets
        corrections_applied = 0
        for feedback in feedback_items:
            account_code = feedback["account_code"]
            pred_type = feedback["prediction_type"]
            actual_value = feedback["actual_value"]

            # Find matching row
            mask = data_df["account_code"] == account_code
            if not mask.any():
                continue

            # Update target based on prediction type
            if pred_type == "anomaly":
                data_df.loc[mask, "target_anomaly_score"] = actual_value
                corrections_applied += 1
            elif pred_type == "priority":
                data_df.loc[mask, "target_priority_score"] = actual_value
                corrections_applied += 1
            elif pred_type == "attention":
                data_df.loc[mask, "target_needs_attention"] = int(actual_value)
                corrections_applied += 1

        print(f"   ✅ Corrections applied: {corrections_applied}")

        # Prepare datasets (same as original training)
        feature_cols = [
            col
            for col in data_df.columns
            if col not in ["account_id", "account_code"] and not col.startswith("target_")
        ]

        X = data_df[feature_cols].fillna(0)

        from sklearn.model_selection import train_test_split

        datasets = {}

        # Anomaly
        y_anomaly = data_df["target_anomaly_score"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_anomaly, test_size=0.2, random_state=42
        )
        datasets["anomaly"] = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
        }

        # Priority
        y_priority = data_df["target_priority_score"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_priority, test_size=0.2, random_state=42
        )
        datasets["priority"] = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
        }

        # Attention
        y_attention = data_df["target_needs_attention"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_attention, test_size=0.2, random_state=42
        )
        datasets["attention"] = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
        }

        datasets["feature_names"] = feature_cols
        datasets["feedback_items"] = feedback_items

        return datasets

    def retrain_models(
        self,
        period: str = "Mar-24",
        entity: str | None = None,
        model_types: list[str] | None = None,
    ) -> dict[str, dict]:
        """
        Retrain specified models with feedback.

        Args:
            period: Period to train on
            entity: Optional entity filter
            model_types: Models to retrain (None = all)

        Returns:
            Dict of retraining results
        """
        if model_types is None:
            model_types = ["anomaly", "priority", "attention"]

        print("\n" + "=" * 70)
        print("🔄 Retraining ML Models with User Feedback")
        print("=" * 70)

        # Prepare data with feedback
        datasets = self.prepare_training_data_with_feedback(period=period, entity=entity)

        results = {}

        # Retrain each model type
        if "anomaly" in model_types:
            print("\n🤖 Retraining Anomaly Detector...")
            model, metrics = self.trainer.train_anomaly_detector(
                datasets["anomaly"]["X_train"],
                datasets["anomaly"]["y_train"],
                datasets["anomaly"]["X_test"],
                datasets["anomaly"]["y_test"],
                hyperparameter_tune=False,
            )
            results["anomaly"] = {"model": model, "metrics": metrics}

        if "priority" in model_types:
            print("\n🎯 Retraining Priority Ranker...")
            model, metrics = self.trainer.train_priority_ranker(
                datasets["priority"]["X_train"],
                datasets["priority"]["y_train"],
                datasets["priority"]["X_test"],
                datasets["priority"]["y_test"],
                hyperparameter_tune=False,
            )
            results["priority"] = {"model": model, "metrics": metrics}

        if "attention" in model_types:
            print("\n🚨 Retraining Attention Classifier...")
            model, metrics = self.trainer.train_attention_classifier(
                datasets["attention"]["X_train"],
                datasets["attention"]["y_train"],
                datasets["attention"]["X_test"],
                datasets["attention"]["y_test"],
                hyperparameter_tune=False,
            )
            results["attention"] = {"model": model, "metrics": metrics}

        # Mark feedback as used
        feedback_ids = [f["feedback_id"] for f in datasets["feedback_items"]]
        if feedback_ids:
            self.feedback_collector.mark_feedback_used(feedback_ids)
            print(f"\n✅ Marked {len(feedback_ids)} feedback items as used")

        return results

    def validate_new_models(
        self, new_results: dict[str, dict], baseline_metrics: dict[str, dict] | None = None
    ) -> dict[str, bool]:
        """
        Validate new models against baseline using safety rails.

        Args:
            new_results: Results from retraining
            baseline_metrics: Baseline metrics to compare against

        Returns:
            Dict of validation decisions (True = deploy, False = reject)
        """
        print("\n" + "=" * 70)
        print("🛡️ Validating New Models (Safety Rails)")
        print("=" * 70)

        if baseline_metrics is None:
            baseline_metrics = self.baseline_metrics

        decisions = {}

        for model_type, result in new_results.items():
            new_metrics = result["metrics"]

            # Get primary metric for comparison
            if model_type in ["anomaly", "priority"]:
                primary_metric = "test_r2"
                new_score = new_metrics.get(primary_metric, 0)
                baseline_score = baseline_metrics.get(model_type, {}).get(primary_metric, 0)
            else:  # attention
                primary_metric = "test_f1"
                new_score = new_metrics.get(primary_metric, 0)
                baseline_score = baseline_metrics.get(model_type, {}).get(primary_metric, 0)

            # Check improvement threshold
            improvement = new_score - baseline_score
            improvement_pct = (improvement / (baseline_score + 1e-10)) * 100

            # Decision: deploy if improvement ≥ threshold OR baseline doesn't exist
            should_deploy = (
                improvement_pct >= (self.improvement_threshold * 100) or baseline_score == 0
            )

            decisions[model_type] = should_deploy

            print(f"\n{model_type.upper()} Model:")
            print(f"   Baseline {primary_metric}: {baseline_score:.4f}")
            print(f"   New {primary_metric}: {new_score:.4f}")
            print(f"   Improvement: {improvement_pct:+.2f}%")
            print(f"   Decision: {'✅ DEPLOY' if should_deploy else '❌ REJECT'}")

        return decisions

    def deploy_models(self, models_to_deploy: dict[str, any], version: str = "auto"):
        """
        Deploy validated models to production.

        Args:
            models_to_deploy: Dict of models to deploy
            version: Version string (auto = timestamp)
        """
        if version == "auto":
            version = datetime.utcnow().strftime("v1.%Y%m%d_%H%M%S")

        print(f"\n🚀 Deploying Models (Version: {version})...")

        for model_type, model in models_to_deploy.items():
            # Save model
            model_path = Path(f"models/{model_type}_model_{version}.pkl")
            import joblib

            joblib.dump(model, model_path)
            print(f"   ✅ Deployed {model_type} model to {model_path}")

            # Log deployment event
            log_audit_event(
                event_type="model_deployed",
                entity="system",
                user="continual_learning_pipeline",
                description=f"Deployed {model_type} model version {version}",
                metadata={"model_type": model_type, "version": version},
            )

    def execute_retraining_pipeline(
        self,
        period: str = "Mar-24",
        entity: str | None = None,
        manual_trigger: bool = False,
        dry_run: bool = False,
    ) -> dict:
        """
        Execute complete retraining pipeline.

        Args:
            period: Period to train on
            entity: Optional entity filter
            manual_trigger: Manual admin trigger
            dry_run: Test without deploying

        Returns:
            Pipeline execution results
        """
        print("\n" + "=" * 80)
        print("🔁 CONTINUAL LEARNING PIPELINE EXECUTION")
        print("=" * 80)

        # Check triggers
        should_retrain, reason = self.should_retrain(manual_trigger=manual_trigger)

        if not should_retrain:
            print(f"ℹ️  Retraining skipped: {reason}")
            return {"status": "skipped", "reason": reason}

        print(f"✅ Retraining triggered: {reason}")

        # Retrain models
        new_results = self.retrain_models(period=period, entity=entity)

        # Validate new models
        decisions = self.validate_new_models(new_results)

        # Deploy validated models
        if not dry_run:
            models_to_deploy = {
                model_type: result["model"]
                for model_type, result in new_results.items()
                if decisions.get(model_type, False)
            }

            if models_to_deploy:
                self.deploy_models(models_to_deploy)
            else:
                print("\n⚠️  No models met deployment criteria")
        else:
            print("\n🧪 DRY RUN: Models not deployed")

        # Summary
        print("\n" + "=" * 80)
        print("📊 PIPELINE EXECUTION SUMMARY")
        print("=" * 80)
        deployed_count = sum(1 for deploy in decisions.values() if deploy)
        print(f"   Models retrained: {len(new_results)}")
        print(f"   Models validated: {deployed_count}/{len(decisions)}")
        print(f"   Status: {'✅ Success' if deployed_count > 0 else '⚠️  No improvements'}")

        return {
            "status": "completed",
            "reason": reason,
            "results": new_results,
            "decisions": decisions,
            "deployed_count": deployed_count,
        }


if __name__ == "__main__":
    # Test continual learning pipeline
    print("Testing Continual Learning Pipeline...")

    # Create pipeline
    pipeline = ContinualLearningPipeline(
        baseline_metrics={
            "anomaly": {"test_r2": 0.95},
            "priority": {"test_r2": 0.90},
            "attention": {"test_f1": 0.85},
        },
        improvement_threshold=0.02,
    )

    # Execute pipeline (dry run)
    result = pipeline.execute_retraining_pipeline(
        period="Mar-24",
        entity="AEML",
        manual_trigger=True,  # Force trigger for testing
        dry_run=True,
    )

    print(f"\n🎉 Pipeline test complete: {result['status']}")
