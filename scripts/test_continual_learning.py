"""
Test script for continual learning pipeline.
"""

import sys
from os.path import abspath, dirname

# Add src to path
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from src.ml.continual_learning import ContinualLearningPipeline


def test_continual_learning():
    """Test the continual learning pipeline."""
    print("=" * 80)
    print("🧪 Testing Continual Learning Pipeline")
    print("=" * 80)

    # Create pipeline with baseline metrics
    pipeline = ContinualLearningPipeline(
        baseline_metrics={
            "anomaly": {"test_r2": 0.95},
            "priority": {"test_r2": 0.90},
            "attention": {"test_f1": 0.85},
        },
        improvement_threshold=0.02,  # 2% improvement required
    )

    print("\n✅ Pipeline initialized")
    print(f"   Baseline metrics: {pipeline.baseline_metrics}")
    print(f"   Improvement threshold: {pipeline.improvement_threshold * 100}%")

    # Check retraining triggers
    print("\n" + "=" * 80)
    print("🔍 Checking Retraining Triggers")
    print("=" * 80)

    triggers = pipeline.check_retraining_triggers()
    for trigger_name, status in triggers.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {trigger_name}: {status}")

    # Test manual trigger
    should_retrain, reason = pipeline.should_retrain(manual_trigger=True)
    print(f"\n   Manual trigger test: {should_retrain}")
    print(f"   Reason: {reason}")

    # Execute pipeline (dry run)
    print("\n" + "=" * 80)
    print("🔄 Executing Pipeline (DRY RUN)")
    print("=" * 80)

    result = pipeline.execute_retraining_pipeline(
        period="Mar-24",
        entity="AEML",
        manual_trigger=True,  # Force execution
        dry_run=True,  # Don't deploy
    )

    # Print results
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)
    print(f"   Status: {result['status']}")
    print(f"   Reason: {result['reason']}")

    if "results" in result:
        print(f"   Models retrained: {len(result['results'])}")
        for model_type, model_result in result["results"].items():
            print(f"\n   {model_type.upper()}:")
            for metric, value in model_result["metrics"].items():
                print(f"      {metric}: {value:.4f}")

    if "decisions" in result:
        print(f"\n   Deployment decisions:")
        for model_type, decision in result["decisions"].items():
            status = "✅ DEPLOY" if decision else "❌ REJECT"
            print(f"      {model_type}: {status}")

    print("\n🎉 Test completed successfully!")
    return result


if __name__ == "__main__":
    test_continual_learning()
