"""
Test Enhanced Agent with RAG Tools.

This script tests the enhanced LangChain agent with 4 structured tools:
1. RAG_Query - Knowledge base search
2. GL_Account_Lookup - Account details
3. Analytics - Financial calculations
4. Assignment_Lookup - User assignments
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent import create_enhanced_agent, query_agent
from src.rag import RAGPipeline, VectorStoreManager


def test_agent_without_rag():
    """Test agent with tools (no RAG pipeline)."""
    print("=" * 80)
    print("🧪 Testing Enhanced Agent - Without RAG")
    print("=" * 80)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  GOOGLE_API_KEY not set in environment")
        print("To test agent, set your Gemini API key:")
        print("  $env:GOOGLE_API_KEY='your-key-here'   # Windows PowerShell")
        print("  export GOOGLE_API_KEY='your-key-here'  # Linux/Mac")
        print("\nSkipping agent test...")
        return

    print("\n1️⃣ Creating enhanced agent (tools only, no RAG)...")
    agent = create_enhanced_agent(rag_pipeline=None, api_key=api_key)

    print("\n2️⃣ Testing tool-based queries...")

    # Test queries that use different tools
    test_queries = [
        "What GL accounts are assigned to user test@adani.com?",
        "Show me details for GL account 10010001 in entity AEML for period Mar-24",
        "Run a variance analysis for entity AEML in period Mar-24",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Query {i}: {query}")
        print("=" * 80)

        try:
            response = query_agent(agent, query)
            print(f"\n📝 Response:")
            print(response)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

    print("\n" + "=" * 80)
    print("✅ Agent test (without RAG) complete!")
    print("=" * 80)


def test_agent_with_rag():
    """Test full agent with RAG pipeline."""
    print("\n" + "=" * 80)
    print("🧪 Testing Enhanced Agent - With RAG")
    print("=" * 80)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  GOOGLE_API_KEY not set in environment")
        print("Skipping RAG-enabled agent test...")
        return

    print("\n1️⃣ Initializing RAG pipeline...")
    manager = VectorStoreManager()
    rag_pipeline = RAGPipeline(manager, api_key=api_key)

    print("\n2️⃣ Creating enhanced agent with RAG tools...")
    agent = create_enhanced_agent(rag_pipeline=rag_pipeline, api_key=api_key)

    print("\n3️⃣ Testing RAG-enhanced queries...")

    # Test queries that combine RAG with other tools
    test_queries = [
        "What is a trial balance?",
        "Explain variance analysis and then run variance analysis for AEML in Mar-24",
        "What are the SLA deadlines? Then check SLA compliance for all entities",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Query {i}: {query}")
        print("=" * 80)

        try:
            response = query_agent(agent, query)
            print(f"\n📝 Response:")
            print(response)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

    print("\n" + "=" * 80)
    print("✅ Full agent test (with RAG) complete!")
    print("=" * 80)


if __name__ == "__main__":
    # Test agent without RAG first
    print("🚀 Starting Enhanced Agent Tests\n")

    test_agent_without_rag()
    test_agent_with_rag()

    print("\n" + "=" * 80)
    print("💡 All agent tests complete!")
    print("=" * 80)
    print("\nNote: Agent uses REACT pattern with 5 max iterations")
    print("Tools available: RAG_Query, GL_Account_Lookup, Analytics, Assignment_Lookup")
