"""
RAG Pipeline for Conversational AI.

Retrieval-Augmented Generation system that combines semantic search
with LLM (Gemini) to provide context-aware responses.
"""

import os
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI

from .vector_store_manager import VectorStoreManager


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for GL account queries."""

    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        api_key: str | None = None,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.3,
    ):
        """
        Initialize RAG pipeline.

        Args:
            vector_store_manager: VectorStoreManager instance
            api_key: Google API key (reads from GOOGLE_API_KEY env var if None)
            model: Gemini model to use
            temperature: LLM temperature (0.0-1.0, lower = more factual)
        """
        self.vector_store = vector_store_manager

        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "GOOGLE_API_KEY environment variable not set. "
                    "Please set it with your Gemini API key."
                )

        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model, google_api_key=api_key, temperature=temperature, max_output_tokens=1024
        )

        # System prompt defines the AI assistant's role
        self.system_prompt = """You are an AI assistant for Project Aura, an intelligent GL account review system for Adani Group's finance operations.

Your role:
- Answer questions about GL accounts, financial processes, and system usage
- Provide accurate information based on the context provided
- Cite sources when referencing specific documentation
- Admit when you don't know something rather than guessing
- Be concise but thorough in explanations

Context Guidelines:
- Use the retrieved documents as your primary information source
- If context is insufficient, ask for clarification
- Mention relevant GL account codes when applicable
- Reference specific sections of documentation when helpful

Response Format:
- Start with a direct answer
- Provide supporting details
- List sources at the end if applicable
"""

        self.qa_prompt_template = """Context from documentation:
{context}

Question: {question}

Answer (be concise and cite sources): """

        print("✅ RAG Pipeline initialized")

    def retrieve_context(
        self,
        query: str,
        collections: list[str] | None = None,
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> tuple[list[dict], str]:
        """
        Retrieve relevant context for a query.

        Args:
            query: User's natural language query
            collections: Collections to search (default: all)
            top_k: Number of documents to retrieve
            filter_metadata: Optional metadata filters

        Returns:
            Tuple of (results_list, formatted_context_string)
        """
        # Default to all collections
        if collections is None:
            collections = ["gl_knowledge", "project_docs", "account_metadata"]

        # Perform hybrid search across collections
        results = self.vector_store.hybrid_search(
            query_text=query,
            collections=collections,
            n_results_per_collection=max(1, top_k // len(collections)),
        )

        # Take top K results
        results = results[:top_k]

        # Format context for LLM prompt
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result["metadata"].get("source", "Unknown")
            doc_type = result["metadata"].get("doc_type", "Unknown")
            content = result["document"]

            # Clean source path for readability
            if isinstance(source, str):
                source_display = source.split("\\")[-1] if "\\" in source else source.split("/")[-1]
            else:
                source_display = str(source)

            context_parts.append(
                f"""[Source {i}: {source_display} ({doc_type})]
{content}
---"""
            )

        context_string = "\n\n".join(context_parts)

        return results, context_string

    def generate_response(self, query: str, context: str) -> dict[str, any]:
        """
        Generate response using LLM with retrieved context.

        Args:
            query: User question
            context: Retrieved context string

        Returns:
            Dict with response and metadata
        """
        # Construct prompt
        prompt = self.qa_prompt_template.format(context=context, question=query)

        # Add system prompt
        full_prompt = f"{self.system_prompt}\n\n{prompt}"

        # Generate response
        try:
            response = self.llm.invoke(full_prompt)
            answer = response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            answer = f"Error generating response: {e!s}"

        return {
            "answer": answer,
            "query": query,
            "context_used": context,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def query(
        self,
        question: str,
        collections: list[str] | None = None,
        filter_metadata: dict | None = None,
        include_sources: bool = True,
        top_k: int = 5,
    ) -> dict:
        """
        End-to-end RAG query.

        Args:
            question: User's natural language question
            collections: Collections to search (default: all)
            filter_metadata: Metadata filters
            include_sources: Include source documents in response
            top_k: Number of context documents to retrieve

        Returns:
            Dict with answer, sources, and metadata
        """
        # Retrieve context
        results, context = self.retrieve_context(
            query=question, collections=collections, top_k=top_k, filter_metadata=filter_metadata
        )

        # Generate response
        response = self.generate_response(question, context)

        # Add sources if requested
        if include_sources and results:
            sources = []
            for result in results:
                source = result["metadata"].get("source", "Unknown")
                # Clean up source path
                if isinstance(source, str):
                    source_display = (
                        source.split("\\")[-1] if "\\" in source else source.split("/")[-1]
                    )
                else:
                    source_display = str(source)

                sources.append(
                    {
                        "source": source_display,
                        "doc_type": result["metadata"].get("doc_type", "Unknown"),
                        "relevance_score": 1
                        - result.get("distance", 0),  # Convert distance to similarity
                        "snippet": (
                            result["document"][:150] + "..."
                            if len(result["document"]) > 150
                            else result["document"]
                        ),
                    }
                )
            response["sources"] = sources
            response["num_sources"] = len(sources)

        return response

    def query_with_entity_context(
        self, question: str, entity: str, period: str | None = None, top_k: int = 5
    ) -> dict:
        """
        Query with entity-specific context filtering.

        Args:
            question: User question
            entity: Entity code (AEML, APSEZ, APEL, etc.)
            period: Optional period filter (Mar-24, etc.)
            top_k: Number of documents to retrieve

        Returns:
            Response dict with entity-filtered results
        """
        # Build metadata filter
        filter_metadata = {"entity": entity}
        if period:
            filter_metadata["period"] = period

        return self.query(
            question=question, filter_metadata=filter_metadata, include_sources=True, top_k=top_k
        )

    def batch_query(self, questions: list[str], collections: list[str] | None = None) -> list[dict]:
        """
        Process multiple queries in batch.

        Args:
            questions: List of questions
            collections: Collections to search

        Returns:
            List of response dicts
        """
        responses = []
        for i, question in enumerate(questions, 1):
            print(f"Processing query {i}/{len(questions)}: {question[:50]}...")
            response = self.query(question=question, collections=collections, include_sources=True)
            responses.append(response)

        return responses

    def get_suggested_questions(self) -> list[str]:
        """
        Get suggested questions based on available knowledge.

        Returns:
            List of suggested question strings
        """
        return [
            "What is a trial balance?",
            "How does variance analysis work?",
            "What are the SLA deadlines for GL account reviews?",
            "How does Project Aura help with financial reviews?",
            "What is a GL hygiene score?",
            "What supporting documents are required for GL accounts?",
            "How are GL accounts categorized by criticality?",
            "What is the review process workflow?",
        ]


if __name__ == "__main__":
    # Test RAG pipeline
    print("=" * 80)
    print("🧪 Testing RAG Pipeline")
    print("=" * 80)

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  GOOGLE_API_KEY not set in environment")
        print("To test RAG pipeline, set your Gemini API key:")
        print("  export GOOGLE_API_KEY='your-key-here'  # Linux/Mac")
        print("  $env:GOOGLE_API_KEY='your-key-here'   # Windows PowerShell")
        print("\nSkipping LLM test, testing retrieval only...\n")

        # Test retrieval without LLM
        from .vector_store_manager import VectorStoreManager

        manager = VectorStoreManager()

        test_query = "What is a trial balance?"
        print(f"Test Query: '{test_query}'")
        print("-" * 80)

        results = manager.hybrid_search(
            query_text=test_query,
            collections=["gl_knowledge", "project_docs"],
            n_results_per_collection=2,
        )

        print(f"\nRetrieved {len(results)} documents:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Source: {result['metadata'].get('source', 'Unknown')}")
            print(f"   Distance: {result['distance']:.4f}")
            print(f"   Content: {result['document'][:200]}...")

        print("\n✅ Retrieval test complete!")
        print("💡 Set GOOGLE_API_KEY to test full RAG pipeline with LLM")

    else:
        # Full RAG test with LLM
        from .vector_store_manager import VectorStoreManager

        print("\n1️⃣ Initializing components...")
        manager = VectorStoreManager()
        pipeline = RAGPipeline(manager, api_key=api_key)

        print("\n2️⃣ Testing RAG query...")
        test_questions = [
            "What is a trial balance?",
            "How does Project Aura work?",
            "What are the SLA deadlines?",
        ]

        for i, question in enumerate(test_questions, 1):
            print(f"\n{'=' * 80}")
            print(f"Query {i}: {question}")
            print("=" * 80)

            response = pipeline.query(question, top_k=3)

            print("\n📝 Answer:")
            print(response["answer"])

            if response.get("sources"):
                print(f"\n📚 Sources ({len(response['sources'])}):")
                for j, source in enumerate(response["sources"][:3], 1):
                    print(
                        f"  {j}. {source['source']} ({source['doc_type']}) - Relevance: {source['relevance_score']:.2f}"
                    )

        print("\n" + "=" * 80)
        print("✅ RAG Pipeline test complete!")
        print("=" * 80)
