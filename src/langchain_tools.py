"""LangChain tools module."""

from langchain.tools import BaseTool


class FinancialAnalysisTool(BaseTool):
    """Tool for financial analysis."""

    name = "financial_analysis"
    description = "Analyze financial data"

    def _run(self, query: str) -> str:
        # Placeholder
        return f"Analysis for {query}"


def get_tools() -> list[BaseTool]:
    """Get list of available tools."""
    return [FinancialAnalysisTool()]
