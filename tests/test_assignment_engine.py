from types import SimpleNamespace

import pytest

from src.assignment_engine import AssignmentEngine, AssignmentRule


class FakeSession:
    def __init__(self, accounts=None):
        self._accounts = accounts or []
        self.closed = False

    def query(self, model):
        session_accounts = self._accounts

        class Q:
            def __init__(self, accounts, model):
                self._accounts = accounts
                self.model = model

            def filter_by(self, **kwargs):
                return self

            def filter(self, *args, **kwargs):
                return self

            def all(self):
                # Return accounts only when querying GLAccount list in assign_batch
                if getattr(self.model, "__name__", "") == "GLAccount":
                    return self._accounts
                return []

            def count(self):
                return 0

            def get(self, id):
                # For User.get(id) in force override path
                return SimpleNamespace(id=id, name=f"User{id}", role="reviewer")

        return Q(session_accounts, model)

    def commit(self):
        return None

    def close(self):
        self.closed = True


class FakeGL:
    def __init__(self, id, code, entity, period, balance, criticality=None):
        self.id = id
        self.account_code = code
        self.entity = entity
        self.period = period
        self.balance = balance
        self.criticality = criticality


@pytest.fixture(autouse=True)
def _patch_db_and_audit(monkeypatch):
    # Avoid real DB and Mongo calls
    monkeypatch.setattr("src.assignment_engine.get_postgres_session", lambda: FakeSession([]))
    monkeypatch.setattr(
        "src.assignment_engine.create_responsibility_assignment", lambda *a, **k: None
    )
    monkeypatch.setattr("src.assignment_engine.log_audit_event", lambda *a, **k: None)
    yield


def test_critical_high_balance_assignment(monkeypatch):
    eng = AssignmentEngine()
    # Use deterministic assignees
    reviewers = [SimpleNamespace(id=1, name="R1"), SimpleNamespace(id=2, name="R2")]
    approvers = [SimpleNamespace(id=10, name="A1"), SimpleNamespace(id=20, name="A2")]
    monkeypatch.setattr(eng, "_get_available_reviewers", lambda entity: reviewers)
    monkeypatch.setattr(eng, "_get_available_approvers", lambda entity: approvers)
    monkeypatch.setattr(eng, "_least_loaded", lambda users, entity, period: users[0])

    gl = FakeGL(100, "99990000", "ENT01", "2025-03", 150_000_000.0, criticality="Critical")
    res = eng.assign_account(gl)

    assert res.success is True
    assert res.rule_applied == "critical_high_balance"
    assert res.sla_days == 2
    assert res.reviewer_id == 1 and res.approver_id == 10


def test_zero_balance_assignment(monkeypatch):
    eng = AssignmentEngine()
    reviewers = [SimpleNamespace(id=1, name="R1"), SimpleNamespace(id=2, name="R2")]
    monkeypatch.setattr(eng, "_get_available_reviewers", lambda entity: reviewers)
    monkeypatch.setattr(eng, "_least_loaded", lambda users, entity, period: users[1])

    gl = FakeGL(101, "11110000", "ENT01", "2025-03", 0.0, criticality="Normal")
    res = eng.assign_account(gl)
    assert res.rule_applied == "zero_balance"
    assert res.reviewer_id == 2
    assert res.approver_id is None
    assert res.sla_days == 7


def test_force_override_assignment(monkeypatch):
    eng = AssignmentEngine()
    eng.session = FakeSession()

    # Ensure approver path reachable by forcing a 'both' rule (simulate high balance)
    high_balance_rule = AssignmentRule(
        rule_name="forced_high_balance",
        priority=1,
        conditions={"balance_threshold": 1},  # any positive balance triggers
        assignee_type="both",
        sla_days=4,
        description="Forced both assignee rule for test",
    )
    eng.rules = [high_balance_rule]

    gl = FakeGL(102, "22220000", "ENT01", "2025-03", 5_000.0, criticality="Normal")
    res = eng.assign_account(gl, force_reviewer_id=999, force_approver_id=888)

    assert res.reviewer_id == 999
    assert res.approver_id == 888
    assert res.rule_applied == "forced_high_balance"
    assert res.sla_days == 4


def test_assign_batch_basic_summary(monkeypatch):
    # Prepare two accounts, one zero-balance, one normal
    accounts = [
        FakeGL(201, "33330000", "ENT01", "2025-03", 0.0, criticality="Normal"),
        FakeGL(202, "44440000", "ENT01", "2025-03", 50_000.0, criticality="Normal"),
    ]
    eng = AssignmentEngine()
    eng.session = FakeSession(accounts)
    monkeypatch.setattr(
        eng, "_get_available_reviewers", lambda entity: [SimpleNamespace(id=1, name="R1")]
    )
    monkeypatch.setattr(
        eng, "_get_available_approvers", lambda entity: [SimpleNamespace(id=10, name="A1")]
    )
    monkeypatch.setattr(eng, "_least_loaded", lambda users, entity, period: users[0])

    summary = eng.assign_batch("ENT01", "2025-03", skip_existing=False)
    assert summary["entity"] == "ENT01"
    assert summary["period"] == "2025-03"
    assert summary["total_accounts"] == 2
    assert summary["successful_assignments"] == 2
    assert sum(summary["assignments_by_rule"].values()) == 2
