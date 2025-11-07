"""
Auto-assignment engine for GL account review assignments.
Phase 1 Part 2: Implements risk-based routing with SLA prioritization and audit logging.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .db.mongodb import log_audit_event

# Third-party / DB
from .db.postgres import (
    GLAccount,
    ResponsibilityMatrix,
    User,
    create_responsibility_assignment,
    get_postgres_session,
)

# Optional logger (Phase 0 convention)
try:
    from .utils.logging_config import StructuredLogger  # type: ignore
    logger = StructuredLogger(__name__)
except Exception:  # pragma: no cover - fallback
    class _Dummy:
        def log_event(self, *args, **kwargs):
            pass
    logger = _Dummy()


@dataclass
class AssignmentRule:
    """Rule for assigning GL accounts."""
    rule_name: str
    priority: int  # lower = higher priority
    conditions: Dict[str, Any]
    assignee_type: str  # "reviewer", "approver", "both"
    sla_days: int
    description: str


@dataclass
class AssignmentResult:
    """Result of assignment operation."""
    gl_account_id: int
    account_code: str
    entity: str
    period: str
    reviewer_id: Optional[int]
    reviewer_name: Optional[str]
    approver_id: Optional[int]
    approver_name: Optional[str]
    assignment_date: datetime
    due_date: datetime
    sla_days: int
    criticality: str
    rule_applied: str
    success: bool
    error: Optional[str] = None

    def to_dict(self) -> dict:
        result = asdict(self)
        result["assignment_date"] = self.assignment_date.isoformat()
        result["due_date"] = self.due_date.isoformat()
        return result


class AssignmentEngine:
    """Engine for automatic GL account assignment."""

    # Updated thresholds per decisions: 100M / 25M
    DEFAULT_RULES = [
        AssignmentRule(
            rule_name="critical_high_balance",
            priority=1,
            conditions={"criticality": "Critical", "balance_threshold": 100_000_000},
            assignee_type="both",
            sla_days=2,
            description="Critical accounts > ₹100M require senior reviewer + approver",
        ),
        AssignmentRule(
            rule_name="critical_accounts",
            priority=2,
            conditions={"criticality": "Critical"},
            assignee_type="both",
            sla_days=3,
            description="All critical accounts require dual review",
        ),
        AssignmentRule(
            rule_name="high_balance",
            priority=3,
            conditions={"balance_threshold": 25_000_000},
            assignee_type="both",
            sla_days=5,
            description="High-value accounts > ₹25M require dual review",
        ),
        AssignmentRule(
            rule_name="zero_balance",
            priority=4,
            conditions={"balance": 0.0},
            assignee_type="reviewer",
            sla_days=7,
            description="Zero-balance accounts can be reviewed by a reviewer only",
        ),
        AssignmentRule(
            rule_name="standard_review",
            priority=5,
            conditions={},
            assignee_type="reviewer",
            sla_days=10,
            description="Standard review for all other accounts",
        ),
    ]

    def __init__(self, rules: Optional[List[AssignmentRule]] = None):
        self.rules = sorted(rules or self.DEFAULT_RULES, key=lambda r: r.priority)
        self.session = get_postgres_session()

    def _match_rule(self, gl_account: GLAccount, rule: AssignmentRule) -> bool:
        cond = rule.conditions
        # Criticality
        if "criticality" in cond and (gl_account.criticality or "") != cond["criticality"]:
            return False
        # Balance threshold
        if "balance_threshold" in cond and abs(float(gl_account.balance or 0)) < cond["balance_threshold"]:
            return False
        # Exact balance
        if "balance" in cond and float(gl_account.balance or 0) != float(cond["balance"]):
            return False
        return True

    def _get_available_reviewers(self, entity: str) -> List[User]:
        return (
            self.session.query(User)
            .filter(User.role.in_(["reviewer", "senior_reviewer"]))
            .all()
        )

    def _get_available_approvers(self, entity: str) -> List[User]:
        return self.session.query(User).filter(User.role == "approver").all()

    def _least_loaded(self, users: List[User], entity: str, period: str) -> Optional[User]:
        if not users:
            return None
        counts: Dict[int, int] = {}
        for u in users:
            q = self.session.query(ResponsibilityMatrix).filter_by(entity=entity, period=period)
            # Count both reviewer and approver assignments for fairness
            counts[u.id] = q.filter(
                (ResponsibilityMatrix.reviewer_id == u.id) | (ResponsibilityMatrix.approver_id == u.id)
            ).count()
        min_user_id = min(counts, key=counts.get)
        return next(u for u in users if u.id == min_user_id)

    def assign_account(
        self,
        gl_account: GLAccount,
        force_reviewer_id: Optional[int] = None,
        force_approver_id: Optional[int] = None,
    ) -> AssignmentResult:
        try:
            # Determine rule
            matched = None
            for rule in self.rules:
                if self._match_rule(gl_account, rule):
                    matched = rule
                    break
            matched = matched or self.rules[-1]

            # Resolve assignees
            reviewer = None
            approver = None
            if matched.assignee_type in ("reviewer", "both"):
                reviewer = self.session.query(User).get(force_reviewer_id) if force_reviewer_id else self._least_loaded(
                    self._get_available_reviewers(gl_account.entity), gl_account.entity, gl_account.period
                )
            if matched.assignee_type in ("approver", "both"):
                approver = self.session.query(User).get(force_approver_id) if force_approver_id else self._least_loaded(
                    self._get_available_approvers(gl_account.entity), gl_account.entity, gl_account.period
                )

            assignment_date = datetime.utcnow()
            due_date = assignment_date + timedelta(days=matched.sla_days)

            data = {
                "gl_account_id": gl_account.id,
                "account_code": gl_account.account_code,
                "entity": gl_account.entity,
                "period": gl_account.period,
                "reviewer_id": reviewer.id if reviewer else None,
                "approver_id": approver.id if approver else None,
                "assignment_date": assignment_date,
                "due_date": due_date,
                "status": "pending",
                "criticality": gl_account.criticality or "Normal",
            }
            create_responsibility_assignment(self.session, data)
            self.session.commit()

            # Audit log
            log_audit_event(
                event_type="assignment_created",
                entity=gl_account.entity,
                period=gl_account.period,
                gl_code=gl_account.account_code,
                actor="AssignmentEngine",
                details={
                    "rule": matched.rule_name,
                    "reviewer": getattr(reviewer, "name", None),
                    "approver": getattr(approver, "name", None),
                    "sla_days": matched.sla_days,
                },
            )
            logger.log_event(
                "assignment_created",
                gl_account_id=gl_account.id,
                account_code=gl_account.account_code,
                rule=matched.rule_name,
                reviewer=getattr(reviewer, "name", None),
                approver=getattr(approver, "name", None),
            )

            return AssignmentResult(
                gl_account_id=gl_account.id,
                account_code=gl_account.account_code,
                entity=gl_account.entity,
                period=gl_account.period,
                reviewer_id=getattr(reviewer, "id", None),
                reviewer_name=getattr(reviewer, "name", None),
                approver_id=getattr(approver, "id", None),
                approver_name=getattr(approver, "name", None),
                assignment_date=assignment_date,
                due_date=due_date,
                sla_days=matched.sla_days,
                criticality=gl_account.criticality or "Normal",
                rule_applied=matched.rule_name,
                success=True,
            )
        except Exception as e:  # pragma: no cover - defensive
            logger.log_event("assignment_failed", error=str(e), gl_account_id=getattr(gl_account, "id", None))
            return AssignmentResult(
                gl_account_id=getattr(gl_account, "id", 0),
                account_code=getattr(gl_account, "account_code", "UNKNOWN"),
                entity=getattr(gl_account, "entity", "UNKNOWN"),
                period=getattr(gl_account, "period", "UNKNOWN"),
                reviewer_id=None,
                reviewer_name=None,
                approver_id=None,
                approver_name=None,
                assignment_date=datetime.utcnow(),
                due_date=datetime.utcnow(),
                sla_days=0,
                criticality=getattr(gl_account, "criticality", "Unknown"),
                rule_applied="none",
                success=False,
                error=str(e),
            )

    def assign_batch(self, entity: str, period: str, skip_existing: bool = True) -> Dict[str, Any]:
        # Fetch candidate accounts
        query = self.session.query(GLAccount).filter_by(entity=entity, period=period)
        if skip_existing:
            assigned_ids = (
                self.session.query(ResponsibilityMatrix.gl_account_id)
                .filter_by(entity=entity, period=period)
                .all()
            )
            assigned_ids = [i[0] for i in assigned_ids]
            if assigned_ids:
                query = query.filter(GLAccount.id.notin_(assigned_ids))
        accounts = query.all()

        results: List[AssignmentResult] = []
        for acc in accounts:
            results.append(self.assign_account(acc))

        by_rule: Dict[str, int] = {}
        for r in results:
            by_rule[r.rule_applied] = by_rule.get(r.rule_applied, 0) + (1 if r.success else 0)

        summary = {
            "entity": entity,
            "period": period,
            "total_accounts": len(results),
            "successful_assignments": sum(1 for r in results if r.success),
            "failed_assignments": sum(1 for r in results if not r.success),
            "assignments_by_rule": by_rule,
            "results": [r.to_dict() for r in results],
        }

        logger.log_event(
            "batch_assignment_completed",
            entity=entity,
            period=period,
            total=summary["total_accounts"],
            successful=summary["successful_assignments"],
            failed=summary["failed_assignments"],
        )
        return summary

    def __del__(self) -> None:  # pragma: no cover - best-effort cleanup
        try:
            if hasattr(self, "session"):
                self.session.close()
        except Exception:
            pass


def assign_accounts_for_period(entity: str, period: str, **kwargs) -> Dict[str, Any]:
    engine = AssignmentEngine()
    return engine.assign_batch(entity, period, **kwargs)
