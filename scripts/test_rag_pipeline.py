"""
Test RAG Pipeline functionality.

This script tests the RAG Pipeline without requiring an API key
(retrieval-only mode).
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag import RAGPipeline, VectorStoreManager


def test_retrieval_only():
    """Test RAG pipeline retrieval without LLM."""
    print("=" * 80)
    print("🧪 Testing RAG Pipeline - Retrieval Only")
    print("=" * 80)

    print("\n1️⃣ Initializing vector store manager...")
    manager = VectorStoreManager()

    print("\n2️⃣ Testing semantic search...")
    test_queries = [
        "What is a trial balance?",
        "How does Project Aura work?",
        "What are the SLA deadlines?",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Query {i}: {query}")
        print("=" * 80)

        results = manager.hybrid_search(
            query_text=query,
            collections=["gl_knowledge", "project_docs"],
            n_results_per_collection=2,
        )

        print(f"\nRetrieved {len(results)} documents:")
        for j, result in enumerate(results[:3], 1):
            source = result["metadata"].get("source", "Unknown")
            # Clean up source path
            if isinstance(source, str):
                source_display = source.split("\\")[-1] if "\\" in source else source.split("/")[-1]
            else:
                source_display = str(source)

            print(f"\n  {j}. Source: {source_display}")
            print(f"     Doc Type: {result['metadata'].get('doc_type', 'Unknown')}")
            print(f"     Distance: {result['distance']:.4f}")
            print(f"     Snippet: {result['document'][:150]}...")

    print("\n" + "=" * 80)
    print("✅ Retrieval test complete!")
    print("=" * 80)


def test_rag_with_llm():
    """Test full RAG pipeline with LLM (requires API key)."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  GOOGLE_API_KEY not set in environment")
        print("To test full RAG pipeline with LLM, set your Gemini API key:")
        print("  $env:GOOGLE_API_KEY='your-key-here'   # Windows PowerShell")
        print("  export GOOGLE_API_KEY='your-key-here'  # Linux/Mac")
        print("\nSkipping LLM test...")
        return

    print("\n" + "=" * 80)
    print("🧪 Testing RAG Pipeline - Full Pipeline with LLM")
    print("=" * 80)

    print("\n1️⃣ Initializing RAG pipeline with Gemini...")
    manager = VectorStoreManager()
    pipeline = RAGPipeline(manager, api_key=api_key)

    print("\n2️⃣ Testing RAG queries...")
    test_questions = [
        "What is a trial balance?",
        "How does Project Aura help with GL account reviews?",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 80}")
        print(f"Query {i}: {question}")
        print("=" * 80)

        response = pipeline.query(question, top_k=3)

        print(f"\n📝 Answer:")
        print(response["answer"])

        if response.get("sources"):
            print(f"\n📚 Sources ({len(response['sources'])}):")
            for j, source in enumerate(response["sources"][:3], 1):
                print(
                    f"  {j}. {source['source']} ({source['doc_type']}) - Relevance: {source['relevance_score']:.2f}"
                )

    print("\n" + "=" * 80)
    print("✅ Full RAG Pipeline test complete!")
    print("=" * 80)


if __name__ == "__main__":
    # Test retrieval first (no API key needed)
    test_retrieval_only()

    # Test full RAG if API key is available
    test_rag_with_llm()

    print("\n💡 All tests complete!")
