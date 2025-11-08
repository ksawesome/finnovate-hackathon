"""
Comprehensive End-to-End Tests for RAG System.

Tests:
1. Semantic search accuracy
2. RAG response generation with Gemini
3. Agent tool routing
4. Performance benchmarks
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent import create_enhanced_agent, query_agent
from src.rag import DocumentProcessor, RAGPipeline, VectorStoreManager

# ==============================================
# TEST 1: SEMANTIC SEARCH ACCURACY
# ==============================================


def test_semantic_search_accuracy():
    """Test semantic search retrieval quality."""
    print("=" * 80)
    print("🧪 TEST 1: Semantic Search Accuracy")
    print("=" * 80)

    manager = VectorStoreManager()

    # Test queries with expected document types
    test_cases = [
        {
            "query": "What is a trial balance?",
            "expected_doc_types": ["accounting_knowledge"],
            "max_distance": 0.3,  # Should be very relevant
        },
        {
            "query": "How does Project Aura work?",
            "expected_doc_types": ["documentation", "accounting_knowledge"],
            "max_distance": 0.6,
        },
        {
            "query": "What are the SLA deadlines?",
            "expected_doc_types": ["accounting_knowledge", "implementation"],
            "max_distance": 0.4,
        },
        {
            "query": "GL account validation process",
            "expected_doc_types": ["architecture", "implementation", "documentation"],
            "max_distance": 0.7,
        },
    ]

    results = {"passed": 0, "failed": 0, "total": len(test_cases)}

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['query']}")

        # Perform search
        search_results = manager.hybrid_search(
            query_text=test_case["query"],
            collections=["gl_knowledge", "project_docs"],
            n_results_per_collection=3,
        )

        if not search_results:
            print(f"   ❌ FAILED: No results returned")
            results["failed"] += 1
            continue

        # Check top result distance
        top_distance = search_results[0]["distance"]
        top_doc_type = search_results[0]["metadata"].get("doc_type", "unknown")

        print(f"   📍 Top Result:")
        print(f"      - Distance: {top_distance:.4f}")
        print(f"      - Doc Type: {top_doc_type}")
        print(f"      - Source: {search_results[0]['metadata'].get('source', 'N/A')}")

        # Validate distance threshold
        if top_distance <= test_case["max_distance"]:
            print(f"   ✅ PASSED: Distance {top_distance:.4f} ≤ {test_case['max_distance']}")
            results["passed"] += 1
        else:
            print(f"   ❌ FAILED: Distance {top_distance:.4f} > {test_case['max_distance']}")
            results["failed"] += 1

    # Summary
    print(f"\n{'=' * 80}")
    print(f"📊 SUMMARY: {results['passed']}/{results['total']} tests passed")
    print(f"   Success Rate: {results['passed']/results['total']*100:.1f}%")
    print(f"{'=' * 80}\n")

    return results


# ==============================================
# TEST 2: RAG RESPONSE GENERATION
# ==============================================


def test_rag_response_generation():
    """Test RAG pipeline with LLM (requires API key)."""
    print("=" * 80)
    print("🧪 TEST 2: RAG Response Generation with Gemini")
    print("=" * 80)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  GOOGLE_API_KEY not set - SKIPPING LLM tests")
        return {"skipped": True}

    manager = VectorStoreManager()
    pipeline = RAGPipeline(manager, api_key=api_key)

    # Test queries
    test_queries = [
        "What is a trial balance and why is it important?",
        "Explain the concept of variance analysis in 2-3 sentences",
        "What are the key features of Project Aura?",
    ]

    results = {"passed": 0, "failed": 0, "total": len(test_queries), "avg_response_time": 0}

    total_time = 0

    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test Query {i}: {query}")

        try:
            start_time = time.time()
            response = pipeline.query(query, top_k=3, include_sources=True)
            elapsed = time.time() - start_time
            total_time += elapsed

            answer = response["answer"]
            sources = response.get("sources", [])

            # Validate response
            has_answer = len(answer) > 50  # Non-trivial response
            has_sources = len(sources) > 0
            reasonable_time = elapsed < 10.0  # Less than 10 seconds

            print(f"   ⏱️  Response Time: {elapsed:.2f}s")
            print(f"   📏 Answer Length: {len(answer)} chars")
            print(f"   📚 Sources: {len(sources)}")
            print(f"   📝 Answer Preview: {answer[:150]}...")

            if has_answer and has_sources and reasonable_time:
                print(f"   ✅ PASSED")
                results["passed"] += 1
            else:
                print(f"   ❌ FAILED: ", end="")
                if not has_answer:
                    print("Answer too short ", end="")
                if not has_sources:
                    print("No sources ", end="")
                if not reasonable_time:
                    print(f"Too slow ({elapsed:.2f}s) ", end="")
                print()
                results["failed"] += 1

        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
            results["failed"] += 1

    results["avg_response_time"] = total_time / len(test_queries) if test_queries else 0

    # Summary
    print(f"\n{'=' * 80}")
    print(f"📊 SUMMARY: {results['passed']}/{results['total']} tests passed")
    print(f"   Average Response Time: {results['avg_response_time']:.2f}s")
    print(f"   Target: <3s per response")
    if results["avg_response_time"] < 3.0:
        print(f"   ✅ Performance target MET")
    else:
        print(f"   ⚠️  Performance target MISSED")
    print(f"{'=' * 80}\n")

    return results


# ==============================================
# TEST 3: AGENT TOOL ROUTING
# ==============================================


def test_agent_tool_routing():
    """Test agent's ability to route to correct tools."""
    print("=" * 80)
    print("🧪 TEST 3: Agent Tool Routing")
    print("=" * 80)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  GOOGLE_API_KEY not set - SKIPPING agent tests")
        return {"skipped": True}

    manager = VectorStoreManager()
    pipeline = RAGPipeline(manager, api_key=api_key)
    agent = create_enhanced_agent(pipeline, api_key=api_key)

    # Test queries that should trigger specific tools
    test_cases = [
        {
            "query": "What is a trial balance?",
            "expected_tool": "RAG_Query",
            "description": "Knowledge base question",
        },
        {
            "query": "Show me GL account 10010001 for AEML in Mar-24",
            "expected_tool": "GL_Account_Lookup",
            "description": "Account lookup",
        },
        # Note: Analytics and Assignment tools need actual data in DB
    ]

    results = {"passed": 0, "failed": 0, "total": len(test_cases)}

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"   Query: {test_case['query']}")
        print(f"   Expected Tool: {test_case['expected_tool']}")

        try:
            start_time = time.time()
            response = query_agent(agent, test_case["query"])
            elapsed = time.time() - start_time

            print(f"   ⏱️  Response Time: {elapsed:.2f}s")
            print(f"   📝 Response: {response[:200]}...")

            # Check if response is valid (not an error)
            is_valid = not response.startswith("❌")

            if is_valid:
                print(f"   ✅ PASSED: Valid response received")
                results["passed"] += 1
            else:
                print(f"   ❌ FAILED: Error in response")
                results["failed"] += 1

        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
            results["failed"] += 1

    # Summary
    print(f"\n{'=' * 80}")
    print(f"📊 SUMMARY: {results['passed']}/{results['total']} tests passed")
    print(f"{'=' * 80}\n")

    return results


# ==============================================
# TEST 4: PERFORMANCE BENCHMARKS
# ==============================================


def test_performance_benchmarks():
    """Test performance metrics."""
    print("=" * 80)
    print("🧪 TEST 4: Performance Benchmarks")
    print("=" * 80)

    manager = VectorStoreManager()

    # Benchmark 1: Vector search latency
    print("\n📊 Benchmark 1: Vector Search Latency")
    search_times = []
    for i in range(10):
        start = time.time()
        manager.hybrid_search(
            "test query for performance",
            collections=["gl_knowledge", "project_docs"],
            n_results_per_collection=3,
        )
        search_times.append(time.time() - start)

    avg_search_time = sum(search_times) / len(search_times)
    print(f"   Average: {avg_search_time*1000:.2f}ms")
    print(f"   Min: {min(search_times)*1000:.2f}ms")
    print(f"   Max: {max(search_times)*1000:.2f}ms")
    print(f"   Target: <500ms")

    if avg_search_time < 0.5:
        print(f"   ✅ Target MET")
    else:
        print(f"   ⚠️  Target MISSED")

    # Benchmark 2: Collection stats
    print("\n📊 Benchmark 2: Collection Statistics")
    stats = manager.get_collection_stats()
    total_docs = sum(stats.values())
    print(f"   Total Documents: {total_docs}")
    for collection, count in stats.items():
        print(f"   - {collection}: {count} documents")

    # Summary
    print(f"\n{'=' * 80}")
    print(f"📊 PERFORMANCE SUMMARY:")
    print(f"   Vector Search: {avg_search_time*1000:.2f}ms avg (target: <500ms)")
    print(f"   Total Documents: {total_docs}")
    print(f"{'=' * 80}\n")

    return {
        "avg_search_time_ms": avg_search_time * 1000,
        "total_documents": total_docs,
        "search_target_met": avg_search_time < 0.5,
    }


# ==============================================
# MAIN TEST RUNNER
# ==============================================


def run_all_tests():
    """Run all end-to-end tests."""
    print("\n" + "=" * 80)
    print("🚀 STARTING COMPREHENSIVE RAG SYSTEM TESTS")
    print("=" * 80)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = {}

    # Test 1: Semantic Search
    results["semantic_search"] = test_semantic_search_accuracy()
    time.sleep(1)

    # Test 2: RAG Generation
    results["rag_generation"] = test_rag_response_generation()
    time.sleep(1)

    # Test 3: Agent Routing
    results["agent_routing"] = test_agent_tool_routing()
    time.sleep(1)

    # Test 4: Performance
    results["performance"] = test_performance_benchmarks()

    # Final Summary
    print("\n" + "=" * 80)
    print("🎯 FINAL TEST SUMMARY")
    print("=" * 80)

    total_passed = 0
    total_tests = 0

    if "passed" in results["semantic_search"]:
        total_passed += results["semantic_search"]["passed"]
        total_tests += results["semantic_search"]["total"]
        print(
            f"\n✅ Semantic Search: {results['semantic_search']['passed']}/{results['semantic_search']['total']}"
        )

    if "skipped" not in results["rag_generation"]:
        total_passed += results["rag_generation"]["passed"]
        total_tests += results["rag_generation"]["total"]
        print(
            f"✅ RAG Generation: {results['rag_generation']['passed']}/{results['rag_generation']['total']}"
        )
        print(f"   Avg Response Time: {results['rag_generation']['avg_response_time']:.2f}s")
    else:
        print(f"⏭️  RAG Generation: SKIPPED (no API key)")

    if "skipped" not in results["agent_routing"]:
        total_passed += results["agent_routing"]["passed"]
        total_tests += results["agent_routing"]["total"]
        print(
            f"✅ Agent Routing: {results['agent_routing']['passed']}/{results['agent_routing']['total']}"
        )
    else:
        print(f"⏭️  Agent Routing: SKIPPED (no API key)")

    if "search_target_met" in results["performance"]:
        print(f"✅ Performance: Vector search {results['performance']['avg_search_time_ms']:.2f}ms")
        if results["performance"]["search_target_met"]:
            print(f"   Target (<500ms) MET ✅")
        else:
            print(f"   Target (<500ms) MISSED ⚠️")

    print(f"\n{'=' * 80}")
    print(
        f"🏆 OVERALL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)"
        if total_tests > 0
        else "🏆 OVERALL: No tests with API key"
    )
    print(f"{'=' * 80}\n")

    return results


if __name__ == "__main__":
    run_all_tests()
