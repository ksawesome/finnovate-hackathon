#!/usr/bin/env python
"""
E2E Integration Test: Validation + Assignment Workflow
Tests complete pipeline with real PostgreSQL + MongoDB persistence.
"""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.assignment_engine import AssignmentEngine
from src.data_ingestion import IngestionOrchestrator
from src.db import get_mongo_database, get_postgres_session
from src.db.mongodb import get_audit_trail_collection
from src.db.postgres import GLAccount, ResponsibilityMatrix, User


def cleanup_test_data(entity: str, period: str):
    """Remove test data from databases."""
    print(f"\n🧹 Cleaning up test data for {entity}/{period}...")

    # PostgreSQL cleanup
    session = get_postgres_session()
    try:
        # ResponsibilityMatrix uses gl_code, not entity/period directly
        gl_codes = [
            gl.account_code
            for gl in session.query(GLAccount).filter_by(entity=entity, period=period).all()
        ]
        if gl_codes:
            session.query(ResponsibilityMatrix).filter(
                ResponsibilityMatrix.gl_code.in_(gl_codes)
            ).delete(synchronize_session=False)
        session.query(GLAccount).filter_by(entity=entity, period=period).delete()
        session.commit()
        print("  ✓ PostgreSQL cleaned")
    except Exception as e:
        print(f"  ⚠ PostgreSQL cleanup warning: {e}")
        session.rollback()
    finally:
        session.close()

    # MongoDB cleanup
    db = get_mongo_database()
    try:
        db["ingestion_metadata"].delete_many({"entity": entity, "period": period})
        db["validation_results"].delete_many({"period": period})
        db["audit_trail"].delete_many({"entity": entity, "period": period})
        print("  ✓ MongoDB cleaned")
    except Exception as e:
        print(f"  ⚠ MongoDB cleanup warning: {e}")


def verify_postgres_data(entity: str, period: str) -> dict:
    """Verify PostgreSQL ingestion and assignments."""
    session = get_postgres_session()
    try:
        gl_count = session.query(GLAccount).filter_by(entity=entity, period=period).count()

        # Get GL codes for this entity/period
        gl_codes = [
            gl.account_code
            for gl in session.query(GLAccount).filter_by(entity=entity, period=period).all()
        ]
        assignments = 0
        sample_assignment = None
        if gl_codes:
            assignments = (
                session.query(ResponsibilityMatrix)
                .filter(ResponsibilityMatrix.gl_code.in_(gl_codes))
                .count()
            )
            sample_assignment = (
                session.query(ResponsibilityMatrix)
                .filter(ResponsibilityMatrix.gl_code.in_(gl_codes))
                .first()
            )

        # Get sample records
        sample_gl = session.query(GLAccount).filter_by(entity=entity, period=period).first()

        return {
            "gl_accounts": gl_count,
            "assignments": assignments,
            "sample_gl_code": sample_gl.account_code if sample_gl else None,
            "sample_reviewer_id": sample_assignment.reviewer_id if sample_assignment else None,
        }
    finally:
        session.close()


def verify_mongo_data(entity: str, period: str) -> dict:
    """Verify MongoDB validation and audit trail."""
    db = get_mongo_database()

    validation_docs = list(db["validation_results"].find({"period": period}).limit(5))
    audit_docs = list(db["audit_trail"].find({"entity": entity, "period": period}).limit(10))
    ingestion_docs = list(db["ingestion_metadata"].find({"entity": entity, "period": period}))

    return {
        "validation_results": len(validation_docs),
        "audit_events": len(audit_docs),
        "ingestion_metadata": len(ingestion_docs),
        "sample_validation": validation_docs[0] if validation_docs else None,
    }


def run_e2e_test(cleanup: bool = True):
    """Run complete E2E workflow."""
    # Use actual values from sample CSV
    entity = "ABEX"
    period = "2022-06"
    csv_path = "data/sample/trial_balance_cleaned.csv"

    print("=" * 70)
    print("🚀 E2E Integration Test: Validation + Assignment Workflow")
    print("=" * 70)

    # Cleanup before test
    if cleanup:
        cleanup_test_data(entity, period)

    # Step 1: Ingest with validation
    print(f"\n📥 Step 1: Ingest {csv_path}")
    orch = IngestionOrchestrator()
    result = orch.ingest_file(
        csv_path,
        entity=entity,
        period=period,
        validate_before_insert=True,
        fail_on_validation_error=False,  # Allow continuation despite validation failures
        skip_duplicates=False,
    )

    print(f"  Status: {result['status']}")
    print(f"  Inserted: {result.get('inserted', 0)}")
    print(f"  Validation Passed: {result.get('validation_passed', 'N/A')}")
    print(f"  Validation Checks: {result.get('validation_total_checks', 0)}")
    print(f"  Failed Checks: {result.get('validation_failed_checks', 0)}")
    print(f"  Critical Failures: {result.get('validation_critical_failures', 0)}")

    assert result["status"] in [
        "success",
        "validation_failed",
    ], f"Unexpected status: {result['status']}"
    assert result.get("inserted", 0) > 0, "No records inserted"

    # Debug: Check immediately after ingestion
    from src.db import get_postgres_session
    from src.db.postgres import GLAccount

    debug_session = get_postgres_session()
    try:
        count = debug_session.query(GLAccount).filter_by(entity=entity, period=period).count()
        print(f"  DEBUG: Immediate count after ingestion: {count}")
    finally:
        debug_session.close()

    # Step 2: Verify PostgreSQL data
    print("\n🔍 Step 2: Verify PostgreSQL data")
    pg_data = verify_postgres_data(entity, period)
    print(f"  GL Accounts: {pg_data['gl_accounts']}")
    print(f"  Sample GL Code: {pg_data['sample_gl_code']}")

    assert pg_data["gl_accounts"] > 0, "No GL accounts in PostgreSQL"

    # Step 3: Verify MongoDB validation results
    print("\n🔍 Step 3: Verify MongoDB validation results")
    mongo_data = verify_mongo_data(entity, period)
    print(f"  Validation Results: {mongo_data['validation_results']}")
    print(f"  Audit Events: {mongo_data['audit_events']}")
    print(f"  Ingestion Metadata: {mongo_data['ingestion_metadata']}")

    assert mongo_data["validation_results"] > 0, "No validation results in MongoDB"
    assert mongo_data["ingestion_metadata"] > 0, "No ingestion metadata in MongoDB"

    # Step 4: Run assignment engine
    print("\n🎯 Step 4: Run assignment engine")

    # First, ensure we have test users
    session = get_postgres_session()
    try:
        reviewer_count = (
            session.query(User).filter(User.role.in_(["reviewer", "senior_reviewer"])).count()
        )
        approver_count = session.query(User).filter_by(role="approver").count()

        if reviewer_count == 0 or approver_count == 0:
            print(
                f"  ⚠ Warning: Insufficient users (reviewers: {reviewer_count}, approvers: {approver_count})"
            )
            print("  Skipping assignment step - run scripts/seed_sample_data.py to add users")
            assignment_summary = {
                "total_accounts": 0,
                "successful_assignments": 0,
                "note": "Skipped due to no users",
            }
        else:
            print(f"  Users available: {reviewer_count} reviewers, {approver_count} approvers")
            engine = AssignmentEngine()
            assignment_summary = engine.assign_batch(entity, period, skip_existing=False)

            print(f"  Total Accounts: {assignment_summary['total_accounts']}")
            print(f"  Successful: {assignment_summary['successful_assignments']}")
            print(f"  Failed: {assignment_summary['failed_assignments']}")
            print(f"  By Rule: {assignment_summary['assignments_by_rule']}")

            assert assignment_summary["successful_assignments"] > 0, "No successful assignments"
    finally:
        session.close()

    # Step 5: Verify assignments in PostgreSQL
    if assignment_summary.get("successful_assignments", 0) > 0:
        print("\n🔍 Step 5: Verify assignments in PostgreSQL")
        pg_data_after = verify_postgres_data(entity, period)
        print(f"  Assignments: {pg_data_after['assignments']}")
        print(f"  Sample Reviewer ID: {pg_data_after['sample_reviewer_id']}")

        assert pg_data_after["assignments"] > 0, "No assignments created in PostgreSQL"
    else:
        print("\n⏭  Step 5: Skipped (no assignments created)")

    # Step 6: Verify audit trail
    print("\n🔍 Step 6: Verify audit trail completeness")
    audit_collection = get_audit_trail_collection()
    audit_count = audit_collection.count_documents({"entity": entity, "period": period})
    print(f"  Total Audit Events: {audit_count}")

    # Sample recent events
    recent = list(
        audit_collection.find({"entity": entity, "period": period}).sort("timestamp", -1).limit(3)
    )
    for i, event in enumerate(recent, 1):
        print(
            f"  Event {i}: {event.get('event_type', 'unknown')} at {event.get('timestamp', 'N/A')}"
        )

    assert audit_count > 0, "No audit events logged"

    # Final summary
    print("\n" + "=" * 70)
    print("✅ E2E Test Summary")
    print("=" * 70)
    print(f"  Records Ingested: {result.get('inserted', 0)}")
    print(f"  Validation Checks: {result.get('validation_total_checks', 0)}")
    print(f"  Assignments Created: {assignment_summary.get('successful_assignments', 0)}")
    print(f"  Audit Events: {audit_count}")
    print(f"  Duration: {result.get('duration_seconds', 0):.2f}s")

    # Cleanup after test
    if cleanup:
        cleanup_test_data(entity, period)
        print("\n✓ Test data cleaned up")

    print("\n🎉 E2E Test Passed!")
    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run E2E validation and assignment test")
    parser.add_argument("--no-cleanup", action="store_true", help="Skip cleanup (keep test data)")
    args = parser.parse_args()

    try:
        run_e2e_test(cleanup=not args.no_cleanup)
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
