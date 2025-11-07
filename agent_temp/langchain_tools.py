"""
Relevant Things
---------------
Inputs:
    Functional requests from agent (query, params)
    Calls internal AURA modules: analytics, ml_model, vector_store, data_validation

Outputs:
    Tool results (dict or str) usable by LangChain Agent

Dependencies:
    langchain, pydantic, internal AURA src modules

Side Effects:
    None (pure functions wrapping internal logic)

Usage:
    from src.langchain_tools import get_all_tools
"""

import logging
from typing import Any, Dict, List, Optional

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from src.analytics import calculate_variance, identify_anomalies, get_review_status
from src.ml_model import predict, load_model
from src.vector_store import query_knowledgebase
from src.data_validation import run_validation

logger = logging.getLogger("aura.langchain_tools")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(ch)


# -----------------------------
# Tool Input Schemas
# -----------------------------

class VarianceInput(BaseModel):
    period_a: str = Field(..., description="Current period identifier, e.g. '2025-Q1'")
    period_b: str = Field(..., description="Comparison period, e.g. '2024-Q4'")
    threshold: float = Field(0.1, description="Variance threshold as decimal (e.g. 0.1 = 10%)")


class ValidationInput(BaseModel):
    filepath: str = Field(..., description="Path to uploaded trial balance CSV")


class KnowledgeQueryInput(BaseModel):
    query: str = Field(..., description="Free text query for audit policy or FAQ retrieval")
    top_k: int = Field(3, description="Number of relevant chunks to return")


class PredictInput(BaseModel):
    debit: float
    credit: float
    entity: str = Field(..., description="Entity or business unit")


# -----------------------------
# Tool Wrappers
# -----------------------------

def _variance_tool(input: VarianceInput) -> str:
    try:
        df = calculate_variance(input.period_a, input.period_b)
        anomalies = identify_anomalies(df, threshold=input.threshold)
        return f"Found {len(anomalies)} GL accounts exceeding {input.threshold*100:.0f}% variance."
    except Exception as e:
        logger.exception("Variance tool failed")
        return f"Error: {e}"


def _validation_tool(input: ValidationInput) -> str:
    try:
        result = run_validation(input.filepath)
        return f"Validation {'passed ✅' if result['success'] else 'failed ❌'}"
    except Exception as e:
        logger.exception("Validation tool failed")
        return f"Error: {e}"


def _knowledge_tool(input: KnowledgeQueryInput) -> str:
    try:
        results = query_knowledgebase(input.query, top_k=input.top_k)
        joined = "\n\n".join([r["content"][:300] for r in results])
        return f"Top {len(results)} relevant excerpts:\n\n{joined}"
    except Exception as e:
        logger.exception("Knowledge tool failed")
        return f"Error: {e}"


def _predict_tool(input: PredictInput) -> Dict[str, Any]:
    try:
        df = {
            "Debit": [input.debit],
            "Credit": [input.credit],
            "Entity": [input.entity],
        }
        model = load_model()
        preds = predict(df, feature_cols=["Debit", "Credit", "Entity"], model=model)
        return preds.to_dict(orient="records")[0]
    except Exception as e:
        logger.exception("Prediction tool failed")
        return {"error": str(e)}


# -----------------------------
# Tool Registry
# -----------------------------

def get_all_tools() -> List[StructuredTool]:
    """
    Return a list of all tools for agent initialization.
    """
    return [
        StructuredTool.from_function(
            name="calculate_variance",
            description="Compute period-over-period GL account variance and flag anomalies.",
            func=_variance_tool,
            args_schema=VarianceInput,
        ),
        StructuredTool.from_function(
            name="validate_trial_balance",
            description="Run Great Expectations validation on uploaded trial balance data.",
            func=_validation_tool,
            args_schema=ValidationInput,
        ),
        StructuredTool.from_function(
            name="query_policy_docs",
            description="Retrieve relevant excerpts from embedded audit policy or FAQ documents.",
            func=_knowledge_tool,
            args_schema=KnowledgeQueryInput,
        ),
        StructuredTool.from_function(
            name="predict_gl_category",
            description="Predict GL category using trained ML model.",
            func=_predict_tool,
            args_schema=PredictInput,
        ),
    ]
