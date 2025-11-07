import pandas as pd

from src.data_validation import ValidationOrchestrator, create_expectation_suite


def make_clean_df():
    # Provide only required columns in correct order to satisfy critical expectation
    return pd.DataFrame(
        [
            {
                "account_code": "11112222",
                "account_name": "Cash in bank",
                "balance": 0.0,
                "entity": "ABEX",
                "period": "2025-03",
            },
            {
                "account_code": "33334444",
                "account_name": "Short term loan",
                "balance": 0.0,
                "entity": "ABEX",
                "period": "2025-03",
            },
        ]
    )


def make_dirty_df():
    # invalid account_code and period, duplicate composite key, null name
    return pd.DataFrame(
        [
            {
                "account_code": "BAD",
                "account_name": "",
                "balance": 10.0,
                "entity": "UNKNOWN",
                "period": "2025/03",
                "bs_pl": "X",
                "status": "Foo",
            },
            {
                "account_code": "11112222",
                "account_name": None,
                "balance": 10.0,
                "entity": "ABEX",
                "period": "2025-03",
                "bs_pl": "BS",
                "status": "Assets",
            },
            {
                "account_code": "11112222",
                "account_name": "Dup Row",
                "balance": -10.0,
                "entity": "ABEX",
                "period": "2025-03",
                "bs_pl": "BS",
                "status": "Assets",
            },
        ]
    )


def test_expectation_suite_builds():
    df = make_clean_df()
    suite = create_expectation_suite(df, "unit_suite")
    assert suite.expectation_suite_name == "unit_suite"


def test_validation_clean_passes_or_has_no_critical_failures(monkeypatch):
    # Ensure ABEX is in approved entities in case DB lookup fails

    monkeypatch.setattr(
        "src.data_validation._get_approved_entities", lambda: ["ABEX", "AGEL", "APL"], raising=False
    )

    orch = ValidationOrchestrator(suite_name="unit_suite_clean")
    df = make_clean_df()
    result = orch.validate_dataframe(df, entity="ABEX", period="2025-03", fail_on_critical=False)
    assert result.total_checks > 0
    assert result.critical_failures == 0


def test_validation_dirty_has_failures(monkeypatch):
    monkeypatch.setattr(
        "src.data_validation._get_approved_entities", lambda: ["ABEX", "AGEL", "APL"], raising=False
    )
    orch = ValidationOrchestrator(suite_name="unit_suite_dirty")
    df = make_dirty_df()
    result = orch.validate_dataframe(df, entity="ABEX", period="2025-03", fail_on_critical=False)
    assert result.failed_checks > 0
    assert result.critical_failures >= 1
    # Expect duplicate composite key failure
    failed_types = {fe["expectation_type"] for fe in result.failed_expectations}
    assert "expect_compound_columns_to_be_unique" in failed_types


def test_severity_counts_high_medium_low(monkeypatch):
    # Force approved entities list
    monkeypatch.setattr(
        "src.data_validation._get_approved_entities", lambda: ["ABEX", "AGEL", "APL"], raising=False
    )

    # 3 rows to trigger distinct severities without any critical failures
    df = pd.DataFrame(
        [
            {  # medium: account_name too short (<3)
                "account_code": "11112222",
                "account_name": "OK",
                "balance": 0.0,
                "entity": "ABEX",
                "period": "2025-03",
            },
            {  # low: too many zeros (zero-balance mostly threshold)
                "account_code": "33334444",
                "account_name": "Valid Name",
                "balance": 0.0,
                "entity": "ABEX",
                "period": "2025-03",
            },
            {  # high: null balance violates not-null
                "account_code": "55556666",
                "account_name": "Another",
                "balance": float("nan"),
                "entity": "ABEX",
                "period": "2025-03",
            },
        ]
    )

    orch = ValidationOrchestrator(suite_name="unit_suite_severity")
    result = orch.validate_dataframe(df, entity="ABEX", period="2025-03", fail_on_critical=False)
    assert result.critical_failures == 0
    assert result.high_failures >= 1
    assert result.medium_failures >= 1
    assert result.low_failures >= 1


def test_validation_persists_to_mongo(monkeypatch):
    calls = []

    def fake_save(gl_code, period, validation_suite, results, passed):
        calls.append(
            {
                "gl_code": gl_code,
                "period": period,
                "validation_suite": validation_suite,
                "passed": passed,
                "results_keys": list(results.keys()) if isinstance(results, dict) else [],
            }
        )

    monkeypatch.setattr("src.data_validation.save_validation_results", fake_save)
    monkeypatch.setattr("src.data_validation.log_audit_event", lambda *a, **k: None)
    monkeypatch.setattr(
        "src.data_validation._get_approved_entities", lambda: ["ABEX", "AGEL", "APL"], raising=False
    )

    df = make_clean_df()
    orch = ValidationOrchestrator(suite_name="unit_suite_persist")
    res = orch.validate_dataframe(df, entity="ABEX", period="2025-03", fail_on_critical=False)

    assert calls, "save_validation_results was not called"
    last = calls[-1]
    assert last["validation_suite"] == "unit_suite_persist"
    assert last["gl_code"] == "ABEX_2025-03"
    assert "total_checks" in last["results_keys"]
