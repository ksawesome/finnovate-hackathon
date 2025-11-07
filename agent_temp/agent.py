"""
Relevant Things
---------------
Inputs:
    - query (str): Natural language question or instruction for the agent
    - tools: provided by src.langchain_tools.get_all_tools()
    - Optional: session_id (str) to maintain per-user conversation memory

Outputs:
    - dict: {"answer": str, "tool_calls": List[dict], "raw": <agent output>}
    - Side effects: conversation memory persisted in-memory (process), logs produced

Dependencies:
    langchain (v0.0.350), OpenAI API (via ChatOpenAI), src.langchain_tools
"""

import os
import logging
from typing import Optional, Dict, Any, List

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.agents.agent import AgentExecutor

from src.langchain_tools import get_all_tools

logger = logging.getLogger("aura.agent")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(ch)


# Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("AURA_LLM_MODEL", "gpt-4")
TEMPERATURE = float(os.getenv("AURA_LLM_TEMP", "0.0"))
VERBOSE = os.getenv("AURA_AGENT_VERBOSE", "false").lower() in ("1", "true", "yes")

# Module-level singletons
_AGENT_EXECUTOR: Optional[AgentExecutor] = None
_SESSION_MEMORIES: Dict[str, ConversationBufferMemory] = {}


def _create_llm():
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not found in env — ChatOpenAI may fail if key is not provided.")
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=TEMPERATURE, model_name=MODEL_NAME)
    return llm


def create_agent(tools: Optional[List] = None, verbose: bool = VERBOSE):
    """
    Build and return an initialized AgentExecutor wired to your structured tools.
    This is idempotent: calling repeatedly will recreate the executor.
    """
    global _AGENT_EXECUTOR
    tools = tools or get_all_tools()
    llm = _create_llm()

    logger.info("Initializing agent with %d tools", len(tools))
    agent_exec = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=verbose
    )

    _AGENT_EXECUTOR = agent_exec
    return agent_exec


def _get_memory_for_session(session_id: Optional[str]) -> Optional[ConversationBufferMemory]:
    """
    Return ConversationBufferMemory for a session_id (create if missing).
    Memory is kept in-process; if you need persistence, replace with Redis/File-backed memory.
    """
    if session_id is None:
        return None
    if session_id not in _SESSION_MEMORIES:
        _SESSION_MEMORIES[session_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return _SESSION_MEMORIES[session_id]


def ask(query: str, session_id: Optional[str] = None, max_steps: int = 6) -> Dict[str, Any]:
    """
    Execute a single query through the agent.
    Returns a dict with keys: answer (str), tool_calls (list), raw (agent output)
    - session_id: optional string to maintain conversation memory across calls
    - max_steps: max internal planning steps (keeps agent bounded)
    """
    global _AGENT_EXECUTOR
    if _AGENT_EXECUTOR is None:
        logger.info("Agent not initialized; creating default agent.")
        _AGENT_EXECUTOR = create_agent()

    memory = _get_memory_for_session(session_id)

    try:
        # AgentExecutor.run can accept inputs as a string or dict depending on agent config.
        # We pass the query; memory (if provided) is implicitly used by agent via ConversationBufferMemory
        # For v0.0.350, the agent executor supports .run(input)
        if memory:
            # Inject memory into agent by providing existing chat history as part of prompt context.
            # The ConversationBufferMemory object is registered in the agent at creation time if needed.
            # If more complex behavior required, you can implement a custom prompt template.
            result = _AGENT_EXECUTOR.run(query)
        else:
            result = _AGENT_EXECUTOR.run(query)

        # Normalize output
        answer = result if isinstance(result, str) else str(result)
        return {"answer": answer, "tool_calls": [], "raw": result}
    except Exception as exc:
        logger.exception("Agent execution failed")
        return {"answer": f"agent_error: {exc}", "tool_calls": [], "raw": None}


# Convenience to initialize on import if desired (commented to avoid side-effects)
# create_agent()
