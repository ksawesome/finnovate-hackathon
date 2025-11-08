"""
LangChain Tools for RAG-enhanced Agent.

Provides 4 structured tools for:
1. RAG_Query - Knowledge base search
2. GL_Account_Lookup - Account details retrieval
3. Analytics - Financial calculations
4. Assignment_Lookup - User assignment checks
"""

from typing import Any

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from .analytics import perform_analytics

# Import database and RAG components
from .db.postgres import get_gl_account_by_code, get_user_assignments

# ============================================================================
# Pydantic Input Schemas
# ============================================================================


class RAGQueryInput(BaseModel):
    """Input schema for RAG knowledge base queries."""

    question: str = Field(
        description="Natural language question about GL accounts, financial processes, or Project Aura system"
    )
    collections: list[str] | None = Field(
        default=None,
        description="Optional list of collections to search: 'gl_knowledge', 'project_docs', 'account_metadata'",
    )


class GLAccountLookupInput(BaseModel):
    """Input schema for GL account details lookup."""

    account_code: str = Field(description="GL account code (e.g., '10010001')")
    entity: str = Field(description="Entity code (e.g., 'AEML', 'APSEZ', 'APEL')")
    period: str | None = Field(
        default=None, description="Optional period (e.g., 'Mar-24') for version-specific lookup"
    )


class AnalyticsInput(BaseModel):
    """Input schema for analytics queries."""

    analysis_type: str = Field(
        description="Type of analysis: 'variance', 'trend', 'completion_rate', 'sla_compliance'"
    )
    entity: str | None = Field(
        default=None, description="Optional entity code for entity-specific analytics"
    )
    period: str | None = Field(default=None, description="Optional period for time-bound analytics")


class AssignmentLookupInput(BaseModel):
    """Input schema for user assignment lookups."""

    account_code: str | None = Field(
        default=None, description="Optional GL account code to check assignments for"
    )
    user_email: str | None = Field(
        default=None, description="Optional user email to check their assignments"
    )


# ============================================================================
# RAG-Enhanced Tools
# ============================================================================


class RAGQueryTool(BaseTool):
    """
    Tool for querying the RAG knowledge base.

    Use this for questions about:
    - GL account concepts and definitions
    - Financial processes (trial balance, variance analysis, etc.)
    - Project Aura system documentation
    - Accounting best practices
    """

    name: str = "RAG_Query"
    description: str = """Query the knowledge base for information about GL accounts, financial processes,
    and Project Aura system. Returns cited answers from documentation.
    Example: 'What is a trial balance?' or 'How does variance analysis work?'"""
    args_schema: type[BaseModel] = RAGQueryInput

    # RAG pipeline reference (injected at runtime)
    rag_pipeline: Any = None

    def _run(self, question: str, collections: list[str] | None = None) -> str:
        """Execute RAG query."""
        if self.rag_pipeline is None:
            return "❌ RAG pipeline not initialized. Please set up the knowledge base first."

        try:
            response = self.rag_pipeline.query(
                question=question, collections=collections, include_sources=True, top_k=3
            )

            # Format response with sources
            answer = response["answer"]
            sources = response.get("sources", [])

            if sources:
                sources_text = "\n\n📚 Sources:\n" + "\n".join(
                    [
                        f"  - {s['source']} ({s['doc_type']}, relevance: {s['relevance_score']:.2f})"
                        for s in sources[:3]
                    ]
                )
                return f"{answer}{sources_text}"

            return answer

        except Exception as e:
            return f"❌ Error querying knowledge base: {e!s}"

    async def _arun(self, question: str, collections: list[str] | None = None) -> str:
        """Async version (not implemented)."""
        return self._run(question, collections)


class GLAccountLookupTool(BaseTool):
    """
    Tool for retrieving GL account details.

    Returns account information including:
    - Account code and description
    - Entity and period
    - Current balance and variance
    - Review status and assignments
    """

    name: str = "GL_Account_Lookup"
    description: str = """Retrieve detailed information about a specific GL account for an entity and period.
    Returns account balance, variance, review status, and other metadata.
    Example: account_code='10010001', entity='AEML', period='Mar-24'"""
    args_schema: type[BaseModel] = GLAccountLookupInput

    def _run(self, account_code: str, entity: str, period: str | None = None) -> str:
        """Execute GL account lookup."""
        try:
            # Get account from database
            account = get_gl_account_by_code(
                account_code=account_code,
                company_code=entity,
                period=period or "Mar-24",  # Default period if not specified
            )

            if account is None:
                return f"❌ GL account {account_code} not found for entity {entity}"

            # Format account details
            result = f"""✅ GL Account Details:

**Account**: {account.account_code} - {account.account_description}
**Entity**: {account.entity}
**Period**: {account.period}

**Financial Data**:
- Current Balance: {account.current_balance:,.2f} {account.currency}
- Prior Period Balance: {account.prior_period_balance:,.2f} {account.currency}
- Variance Amount: {account.variance_amount:,.2f} {account.currency}
- Variance %: {account.variance_percentage:.2f}%

**Review Status**:
- Status: {account.review_status or 'Not Started'}
- Last Reviewed: {account.last_reviewed_at or 'Never'}
- Reviewed By: {account.reviewed_by or 'N/A'}

**Classification**:
- Criticality: {account.criticality_level or 'Medium'}
- Hygiene Score: {account.hygiene_score:.2f}/100

**Supporting Documents**:
- Documents Required: {account.supporting_docs_required}
- Documents Submitted: {account.supporting_docs_submitted}
"""
            return result

        except Exception as e:
            return f"❌ Error retrieving account: {e!s}"

    async def _arun(self, account_code: str, entity: str, period: str | None = None) -> str:
        """Async version (not implemented)."""
        return self._run(account_code, entity, period)


class AnalyticsTool(BaseTool):
    """
    Tool for running financial analytics.

    Supported analysis types:
    - variance: Analyze account variances
    - trend: Analyze historical trends
    - completion_rate: Review completion statistics
    - sla_compliance: SLA compliance tracking
    """

    name: str = "Analytics"
    description: str = """Run financial analytics on GL accounts.
    Supports variance analysis, trend analysis, completion rates, and SLA compliance.
    Example: analysis_type='variance', entity='AEML', period='Mar-24'"""
    args_schema: type[BaseModel] = AnalyticsInput

    def _run(self, analysis_type: str, entity: str | None = None, period: str | None = None) -> str:
        """Execute analytics query."""
        try:
            # Run analytics
            results = perform_analytics(analysis_type=analysis_type, entity=entity, period=period)

            if not results:
                return f"❌ No data found for {analysis_type} analysis"

            # Format results based on analysis type
            if analysis_type == "variance":
                return self._format_variance_results(results, entity, period)
            elif analysis_type == "trend":
                return self._format_trend_results(results, entity)
            elif analysis_type == "completion_rate":
                return self._format_completion_results(results, entity, period)
            elif analysis_type == "sla_compliance":
                return self._format_sla_results(results, entity, period)
            else:
                return f"✅ {analysis_type.title()} Analysis:\n{results!s}"

        except Exception as e:
            return f"❌ Error running analytics: {e!s}"

    def _format_variance_results(
        self, results: dict[str, Any], entity: str | None, period: str | None
    ) -> str:
        """Format variance analysis results."""
        entity_str = f" for {entity}" if entity else ""
        period_str = f" in {period}" if period else ""

        return f"""✅ Variance Analysis{entity_str}{period_str}:

**Summary**:
- Total Accounts: {results.get('total_accounts', 0)}
- High Variance Accounts: {results.get('high_variance_count', 0)}
- Avg Variance %: {results.get('avg_variance_pct', 0):.2f}%
- Max Variance: {results.get('max_variance', 0):,.2f}

**Top Variances**:
{self._format_top_items(results.get('top_variances', []))}
"""

    def _format_trend_results(self, results: dict[str, Any], entity: str | None) -> str:
        """Format trend analysis results."""
        entity_str = f" for {entity}" if entity else ""

        return f"""✅ Trend Analysis{entity_str}:

**Metrics**:
- Periods Analyzed: {results.get('period_count', 0)}
- Trend Direction: {results.get('trend_direction', 'N/A')}
- Growth Rate: {results.get('growth_rate', 0):.2f}%

**Period Summary**:
{self._format_period_data(results.get('period_data', []))}
"""

    def _format_completion_results(
        self, results: dict[str, Any], entity: str | None, period: str | None
    ) -> str:
        """Format completion rate results."""
        entity_str = f" for {entity}" if entity else ""
        period_str = f" in {period}" if period else ""

        return f"""✅ Review Completion{entity_str}{period_str}:

**Status**:
- Completed: {results.get('completed', 0)}
- Pending: {results.get('pending', 0)}
- Total: {results.get('total', 0)}
- Completion Rate: {results.get('completion_pct', 0):.1f}%
- Avg Days to Review: {results.get('avg_days_to_review', 0):.1f}
"""

    def _format_sla_results(
        self, results: dict[str, Any], entity: str | None, period: str | None
    ) -> str:
        """Format SLA compliance results."""
        entity_str = f" for {entity}" if entity else ""
        period_str = f" in {period}" if period else ""

        return f"""✅ SLA Compliance{entity_str}{period_str}:

**Performance**:
- Met SLA: {results.get('met_sla', 0)}
- Breached SLA: {results.get('breached_sla', 0)}
- Compliance Rate: {results.get('compliance_pct', 0):.1f}%
- Avg Response Time: {results.get('avg_response_days', 0):.1f} days
"""

    def _format_top_items(self, items: list) -> str:
        """Format list of top items."""
        if not items:
            return "  No data"
        return "\n".join([f"  {i+1}. {item}" for i, item in enumerate(items[:5])])

    def _format_period_data(self, periods: list) -> str:
        """Format period data."""
        if not periods:
            return "  No data"
        return "\n".join([f"  {period['name']}: {period['value']}" for period in periods[:5]])

    async def _arun(
        self, analysis_type: str, entity: str | None = None, period: str | None = None
    ) -> str:
        """Async version (not implemented)."""
        return self._run(analysis_type, entity, period)


class AssignmentLookupTool(BaseTool):
    """
    Tool for checking GL account assignments.

    Returns:
    - User's assigned accounts
    - Account assignment details
    - Review responsibilities
    """

    name: str = "Assignment_Lookup"
    description: str = """Check GL account assignments for users or accounts.
    Returns list of assigned accounts or users responsible for an account.
    Example: user_email='john@adani.com' or account_code='10010001'"""
    args_schema: type[BaseModel] = AssignmentLookupInput

    def _run(self, account_code: str | None = None, user_email: str | None = None) -> str:
        """Execute assignment lookup."""
        try:
            if user_email:
                # Get user's assignments
                assignments = get_user_assignments(user_email)

                if not assignments:
                    return f"❌ No assignments found for user {user_email}"

                return f"""✅ Assignments for {user_email}:

**Total Accounts**: {len(assignments)}

**Accounts**:
{self._format_assignments(assignments)}
"""

            elif account_code:
                # Get account assignments
                # This would need a new DB function - placeholder for now
                return f"""✅ Assignment for Account {account_code}:

**Assigned To**: [User lookup not implemented]
**Role**: Reviewer
**Status**: Active
"""

            else:
                return "❌ Please provide either account_code or user_email"

        except Exception as e:
            return f"❌ Error checking assignments: {e!s}"

    def _format_assignments(self, assignments: list) -> str:
        """Format assignment list."""
        if not assignments:
            return "  No assignments"

        formatted = []
        for i, assignment in enumerate(assignments[:10], 1):
            formatted.append(
                f"  {i}. {assignment.get('account_code', 'N/A')} - "
                f"{assignment.get('entity', 'N/A')} - "
                f"{assignment.get('status', 'Pending')}"
            )

        if len(assignments) > 10:
            formatted.append(f"  ... and {len(assignments) - 10} more")

        return "\n".join(formatted)

    async def _arun(self, account_code: str | None = None, user_email: str | None = None) -> str:
        """Async version (not implemented)."""
        return self._run(account_code, user_email)


# ============================================================================
# Tool Factory Function
# ============================================================================


def get_rag_tools(rag_pipeline: Any = None) -> list[BaseTool]:
    """
    Get list of RAG-enhanced tools.

    Args:
        rag_pipeline: RAGPipeline instance (optional)

    Returns:
        List of BaseTool instances
    """
    # Create tools
    rag_query_tool = RAGQueryTool()
    if rag_pipeline:
        rag_query_tool.rag_pipeline = rag_pipeline

    gl_lookup_tool = GLAccountLookupTool()
    analytics_tool = AnalyticsTool()
    assignment_tool = AssignmentLookupTool()

    return [rag_query_tool, gl_lookup_tool, analytics_tool, assignment_tool]
