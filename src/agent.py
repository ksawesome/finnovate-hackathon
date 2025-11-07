"""LangChain agent module."""

from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI


def create_agent(tools: list[Tool]) -> AgentExecutor:
    """
    Create a LangChain agent with tools.

    Args:
        tools: List of tools.

    Returns:
        AgentExecutor: Configured agent.
    """
    llm = ChatOpenAI(temperature=0)
    agent = ...  # Placeholder for agent creation
    executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools)
    return executor


def query_agent(agent: AgentExecutor, query: str) -> str:
    """
    Query the agent.

    Args:
        agent: Agent executor.
        query: User query.

    Returns:
        str: Response.
    """
    return agent.run(query)