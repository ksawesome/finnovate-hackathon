"""Unit tests for data ingestion helpers."""

from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from pandas.api.types import is_float_dtype

from src.data_ingestion import DataProfiler, FileFingerprinter, IngestionOrchestrator, SchemaMapper


@pytest.fixture
def balanced_trial_balance() -> pd.DataFrame:
    """Provide a small, balanced trial balance sample."""
    return pd.DataFrame(
        {
            "account_code": ["11100200", "21100000", "31100000"],
            "account_name": ["Inventory", "Accounts Payable", "Capital"],
            "balance": [5000.0, -5000.0, 0.0],
            "entity": ["ABEX", "ABEX", "ABEX"],
            "company_code": ["5500", "5500", "5500"],
            "period": ["2024-01", "2024-01", "2024-01"],
            "bs_pl": ["BS", "BS", "BS"],
            "status": ["Assets", "Liabilities", "Equity"],
        }
    )


class TestDataProfiler:
    def test_profile_basic_stats(self, balanced_trial_balance: pd.DataFrame) -> None:
        profile = DataProfiler.profile(balanced_trial_balance)

        assert profile["row_count"] == 3
        assert profile["column_count"] == 8
        assert profile["balance_stats"]["sum"] == pytest.approx(0.0, abs=1e-2)

    def test_zero_balance_detection(self) -> None:
        df = pd.DataFrame({"account_code": ["111", "222"], "balance": [0.0, 150.0]})

        profile = DataProfiler.profile(df)

        assert profile["zero_balance_accounts"] == 1
        assert profile["zero_balance_percentage"] == 50.0


class TestSchemaMapper:
    def test_valid_schema(self, balanced_trial_balance: pd.DataFrame) -> None:
        result = SchemaMapper.validate_schema(balanced_trial_balance)

        assert result["is_valid"] is True
        assert result["missing_required"] == []

    def test_missing_required_columns(self) -> None:
        df = pd.DataFrame({"account_code": ["11100200"], "balance": [1000.0]})

        result = SchemaMapper.validate_schema(df)

        assert result["is_valid"] is False
        assert "account_name" in result["missing_required"]

    def test_schema_mapping(self, balanced_trial_balance: pd.DataFrame) -> None:
        mapped = SchemaMapper.map_to_postgres_schema(balanced_trial_balance)

        assert "department" in mapped.columns
        assert "criticality" in mapped.columns
        assert is_float_dtype(mapped["balance"])


class TestFileFingerprinter:
    def test_fingerprint_generation(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.csv"
        test_file.write_text("col\n1")

        fingerprint = FileFingerprinter.generate_fingerprint(str(test_file))

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64

    def test_duplicate_detection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class _FakeCollection:
            def __init__(self, should_match: bool) -> None:
                self.should_match = should_match

            def find_one(self, query: dict[str, str]) -> dict[str, str] | None:
                return {"_id": "existing"} if self.should_match else None

        monkeypatch.setattr(
            "src.db.mongodb.get_audit_trail_collection",
            lambda: _FakeCollection(should_match=True),
        )
        assert FileFingerprinter.check_duplicate("fingerprint") is True

        monkeypatch.setattr(
            "src.db.mongodb.get_audit_trail_collection",
            lambda: _FakeCollection(should_match=False),
        )
        assert FileFingerprinter.check_duplicate("fingerprint") is False


class TestIngestionOrchestrator:
    def test_full_ingestion_flow(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        balanced_trial_balance: pd.DataFrame,
    ) -> None:
        csv_file = tmp_path / "trial_balance.csv"
        balanced_trial_balance.to_csv(csv_file, index=False)

        captured: dict[str, Any] = {}

        def fake_bulk_create_gl_accounts(
            df: pd.DataFrame, entity: str, period: str
        ) -> dict[str, int]:
            captured.setdefault("bulk_calls", []).append((entity, period, len(df)))
            return {"inserted": len(df), "updated": 0, "failed": 0}

        def fake_save_ingestion_metadata(**kwargs: Any) -> None:
            captured["metadata"] = kwargs

        def fake_log_audit_event(**kwargs: Any) -> None:
            captured.setdefault("audit_events", []).append(kwargs)

        def fake_save_processed_parquet(df: pd.DataFrame, name: str) -> Path:
            output_path = tmp_path / f"{name}.parquet"
            captured["parquet"] = (len(df), name)
            return output_path

        monkeypatch.setattr("src.db.postgres.bulk_create_gl_accounts", fake_bulk_create_gl_accounts)
        monkeypatch.setattr("src.db.mongodb.save_ingestion_metadata", fake_save_ingestion_metadata)
        monkeypatch.setattr("src.db.mongodb.log_audit_event", fake_log_audit_event)
        monkeypatch.setattr(
            "src.data_ingestion.save_processed_parquet", fake_save_processed_parquet
        )

        orchestrator = IngestionOrchestrator()
        result = orchestrator.ingest_file(
            file_path=str(csv_file),
            entity="TEST",
            period="2024-01",
            skip_duplicates=False,
            validate_before_insert=False,  # Skip validation for this legacy test
        )

        assert result["status"] == "success"
        assert result["inserted"] == len(balanced_trial_balance)
        assert captured["bulk_calls"][0][:2] == ("TEST", "2024-01")
        assert "fingerprint" in result
        assert captured["metadata"]["entity"] == "TEST"
        assert captured["parquet"][1] == "TEST_2024-01_ingested"
        assert captured["audit_events"][0]["event_type"] == "file_ingested"
