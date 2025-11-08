"""
Enhanced LangChain Agent with RAG Integration.

Provides multi-step reasoning over:
- Knowledge base (RAG)
- GL account data (PostgreSQL)
- Financial analytics
- User assignments
"""

import os
from typing import Any

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

from .langchain_tools import get_rag_tools

# Agent system prompt
AGENT_SYSTEM_PROMPT = """You are an intelligent assistant for Project Aura, a GL account review system for Adani Group.

Your role:
- Help users with GL account queries and financial analysis
- Use tools to retrieve accurate information
- Provide clear, actionable responses
- Cite sources when referencing documentation

Available Tools:
- RAG_Query: Search knowledge base for documentation and concepts
- GL_Account_Lookup: Get detailed GL account information
- Analytics: Run financial analysis (variance, trends, completion rates, SLA)
- Assignment_Lookup: Check user assignments

Guidelines:
1. Use tools to gather information before responding
2. Break complex queries into multiple tool calls
3. Always cite sources when using RAG_Query
4. Format financial data clearly with currency symbols
5. Escalate to human if unsure

Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""


def create_agent(tools: list[BaseTool], api_key: str | None = None) -> AgentExecutor:
    """
    Create a LangChain REACT agent with tools.

    Args:
        tools: List of tools for the agent to use
        api_key: Google API key (reads from GOOGLE_API_KEY env var if None)

    Returns:
        AgentExecutor: Configured agent executor
    """
    # Get API key
    if api_key is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable not set. "
                "Please set it with your Gemini API key."
            )

    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.3,  # Balance between creativity and consistency
        max_output_tokens=1024,
    )

    # Create prompt template
    prompt = PromptTemplate.from_template(AGENT_SYSTEM_PROMPT)

    # Create REACT agent
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    # Create agent executor
    executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,  # Enable logging for debugging
        handle_parsing_errors=True,  # Gracefully handle malformed outputs
        max_iterations=5,  # Prevent infinite loops
    )

    return executor


def create_enhanced_agent(rag_pipeline: Any = None, api_key: str | None = None) -> AgentExecutor:
    """
    Create an enhanced agent with RAG and all tools.

    Args:
        rag_pipeline: RAGPipeline instance (optional, for RAG_Query tool)
        api_key: Google API key (reads from GOOGLE_API_KEY env var if None)

    Returns:
        AgentExecutor: Configured agent executor with all tools
    """
    # Get RAG-enhanced tools
    tools = get_rag_tools(rag_pipeline)

    # Create agent with tools
    agent = create_agent(tools, api_key)

    return agent


def query_agent(agent: AgentExecutor, query: str) -> str:
    """
    Query the agent with a natural language question.

    Args:
        agent: Agent executor
        query: User's natural language query

    Returns:
        str: Agent's response
    """
    try:
        result = agent.invoke({"input": query})
        return result.get("output", "No response generated")
    except Exception as e:
        return f"❌ Error querying agent: {e!s}"
