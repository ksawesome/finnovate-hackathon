"""
Initialize RAG System by populating vector stores.

Loads documents, chunks them, and indexes them in ChromaDB collections.
"""

import sys
from os.path import abspath, dirname

# Add src to path for standalone execution
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from src.rag.document_processor import DocumentProcessor
from src.rag.vector_store_manager import VectorStoreManager


def initialize_rag_system(reset: bool = False):
    """
    Initialize RAG system with document ingestion.

    Args:
        reset: If True, delete existing collections and start fresh
    """
    print("\n" + "=" * 80)
    print("🚀 Initializing RAG System")
    print("=" * 80)

    # Step 1: Process documents
    print("\n📚 STEP 1: Processing Documents")
    print("-" * 80)
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    documents_by_type = processor.process_all_documents(docs_dir="docs/")

    # Step 2: Initialize vector store
    print("\n🗄️  STEP 2: Initializing Vector Store")
    print("-" * 80)
    manager = VectorStoreManager(persist_directory="data/vectors/chromadb")

    # Step 3: Create collections and ingest documents
    print("\n📥 STEP 3: Ingesting Documents into Collections")
    print("-" * 80)

    # Collection 1: Project Documentation
    if documents_by_type["project_docs"]:
        print("\n  Collection: project_docs")
        collection = manager.create_or_get_collection("project_docs", reset=reset)
        count = manager.add_documents_to_collection(
            "project_docs", documents_by_type["project_docs"]
        )
        print(f"  ✅ Added {count} documents to project_docs")

    # Collection 2: Accounting Knowledge
    if documents_by_type["gl_knowledge"]:
        print("\n  Collection: gl_knowledge")
        collection = manager.create_or_get_collection("gl_knowledge", reset=reset)
        count = manager.add_documents_to_collection(
            "gl_knowledge", documents_by_type["gl_knowledge"]
        )
        print(f"  ✅ Added {count} documents to gl_knowledge")

    # Collection 3: Account Metadata
    if documents_by_type["account_metadata"]:
        print("\n  Collection: account_metadata")
        collection = manager.create_or_get_collection("account_metadata", reset=reset)
        count = manager.add_documents_to_collection(
            "account_metadata", documents_by_type["account_metadata"]
        )
        print(f"  ✅ Added {count} documents to account_metadata")

    # Step 4: Verify and report
    print("\n📊 STEP 4: Verification")
    print("-" * 80)
    stats = manager.get_collection_stats()

    total_docs = sum(stats.values())
    print(f"\n  Total Collections: {len(stats)}")
    print(f"  Total Documents: {total_docs}")
    print("\n  Collection Breakdown:")
    for name, count in stats.items():
        print(f"    • {name}: {count} documents")

    # Step 5: Test query
    print("\n🔍 STEP 5: Testing Semantic Search")
    print("-" * 80)

    test_queries = [
        "What is a trial balance?",
        "How does Project Aura work?",
        "What are the SLA deadlines?",
    ]

    for query in test_queries:
        print(f"\n  Query: '{query}'")
        results = manager.hybrid_search(
            query_text=query,
            collections=["gl_knowledge", "project_docs"],
            n_results_per_collection=2,
        )

        if results:
            top_result = results[0]
            print(f"    ✅ Top result (distance: {top_result['distance']:.4f}):")
            print(f"       {top_result['document'][:100]}...")
        else:
            print("    ⚠️  No results found")

    # Summary
    print("\n" + "=" * 80)
    print("🎉 RAG System Initialization Complete!")
    print("=" * 80)
    print(f"  Vector Store Location: data/vectors/chromadb/")
    print(f"  Collections: {len(stats)}")
    print(f"  Total Documents: {total_docs}")
    print(f"  Status: ✅ Ready for queries")
    print("=" * 80)

    return manager


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize RAG System")
    parser.add_argument(
        "--reset", action="store_true", help="Reset all collections and start fresh"
    )

    args = parser.parse_args()

    initialize_rag_system(reset=args.reset)
