"""Test ML model training."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ml.models import MLModelTrainer


def test_ml_training():
    """Test complete ML training pipeline."""
    print("=" * 80)
    print("Testing ML Model Training Pipeline")
    print("=" * 80)

    try:
        # Initialize trainer
        trainer = MLModelTrainer(mlflow_experiment_name="test_gl_intelligence")

        # Train all models
        results = trainer.train_all_models(
            period="Mar-24", entity="AEML", hyperparameter_tune=False  # Faster for testing
        )

        print("\n" + "=" * 80)
        print("✅ ML TRAINING TEST PASSED")
        print("=" * 80)
        print(f"\n📊 Results Summary:")
        print(f"   - Anomaly Detector trained: {'anomaly' in results}")
        print(f"   - Priority Ranker trained: {'priority' in results}")
        print(f"   - Attention Classifier trained: {'attention' in results}")

        if "anomaly" in results:
            print(f"\n   Anomaly Detector Metrics:")
            for key, val in results["anomaly"]["metrics"].items():
                print(f"      {key}: {val:.4f}")

        if "priority" in results:
            print(f"\n   Priority Ranker Metrics:")
            for key, val in results["priority"]["metrics"].items():
                print(f"      {key}: {val:.4f}")

        if "attention" in results:
            print(f"\n   Attention Classifier Metrics:")
            for key, val in results["attention"]["metrics"].items():
                print(f"      {key}: {val:.4f}")

        # Test prediction
        print(f"\n" + "=" * 80)
        print("Testing Prediction Pipeline")
        print("=" * 80)

        from src.ml.feature_engineering import GLFeatureEngineer

        engineer = GLFeatureEngineer()
        features_df, _ = engineer.extract_features(period="Mar-24", entity="AEML")

        predictions = trainer.predict(features_df)

        print(f"\n✅ Predictions generated: {len(predictions)} accounts")
        print(f"\nSample predictions:")
        pred_cols = [
            "account_code",
            "pred_anomaly_score",
            "pred_priority_score",
            "pred_needs_attention",
            "pred_attention_proba",
        ]
        available_cols = [col for col in pred_cols if col in predictions.columns]
        print(predictions[available_cols].head())

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ml_training()
    sys.exit(0 if success else 1)
