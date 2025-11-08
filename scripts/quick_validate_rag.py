"""
Quick validation test for RAG system components.
"""

import os
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("🚀 Quick RAG System Validation")
print("=" * 80)

# Test 1: Imports
print("\n1️⃣ Testing imports...")
try:
    from src.agent import create_enhanced_agent
    from src.langchain_tools import get_rag_tools
    from src.rag import DocumentProcessor, RAGPipeline, VectorStoreManager

    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Vector Store
print("\n2️⃣ Testing vector store...")
try:
    manager = VectorStoreManager()
    stats = manager.get_collection_stats()
    total = sum(stats.values())
    print(f"   ✅ Vector store ready: {total} documents")
    for coll, count in stats.items():
        print(f"      - {coll}: {count}")
except Exception as e:
    print(f"   ❌ Vector store error: {e}")

# Test 3: Semantic Search (no LLM)
print("\n3️⃣ Testing semantic search...")
try:
    results = manager.query_collection("gl_knowledge", "What is a trial balance?", n_results=1)
    if results:
        print(f"   ✅ Search working: distance={results[0]['distance']:.4f}")
    else:
        print(f"   ⚠️  No results returned")
except Exception as e:
    print(f"   ❌ Search error: {e}")

# Test 4: RAG Pipeline (with LLM if API key available)
print("\n4️⃣ Testing RAG pipeline...")
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("   ⏭️  Skipped (no GOOGLE_API_KEY)")
else:
    try:
        print("   Initializing RAG pipeline...")
        pipeline = RAGPipeline(manager, api_key=api_key)
        print("   ✅ RAG pipeline initialized")

        # Quick retrieval test only (no LLM call)
        print("   Testing retrieval...")
        results, context = pipeline.retrieve_context("What is a trial balance?", top_k=2)
        print(f"   ✅ Retrieved {len(results)} documents")

    except Exception as e:
        print(f"   ❌ RAG pipeline error: {e}")

# Test 5: Agent Tools
print("\n5️⃣ Testing agent tools...")
try:
    tools = get_rag_tools(rag_pipeline=None)
    print(f"   ✅ {len(tools)} tools available:")
    for tool in tools:
        print(f"      - {tool.name}")
except Exception as e:
    print(f"   ❌ Tools error: {e}")

# Test 6: UI Import
print("\n6️⃣ Testing UI import...")
try:
    from src.dashboards.ai_assistant_page import render_ai_assistant_page

    print("   ✅ AI Assistant UI imported")
except Exception as e:
    print(f"   ❌ UI import error: {e}")

print("\n" + "=" * 80)
print("✅ Quick validation complete!")
print("=" * 80)
print("\n💡 To test full RAG with LLM, ensure GOOGLE_API_KEY is set")
print("💡 To test in Streamlit, run: streamlit run src/app.py")
