"""
Vector Store Manager for RAG System.

Manages ChromaDB vector store for semantic search and retrieval.
"""

from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain.schema import Document


class VectorStoreManager:
    """Manage ChromaDB vector store for RAG system."""

    def __init__(self, persist_directory: str = "data/vectors/chromadb"):
        """
        Initialize vector store manager.

        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # Initialize embedding function - use Google Gemini for embeddings
        # This avoids onnxruntime dependency issues on Windows
        import os

        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            self.embedding_fn = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                api_key=google_api_key, model_name="models/embedding-001"
            )
        else:
            # Fallback to default if no API key (will use basic text embeddings)
            print("⚠️ Warning: GOOGLE_API_KEY not found, using default embedding function")
            # Use a simple embedding function that doesn't require onnxruntime
            self.embedding_fn = None  # Will use ChromaDB's default

        self.collections = {}
        print(f"✅ VectorStoreManager initialized (storage: {self.persist_directory})")

    def create_or_get_collection(
        self, collection_name: str, reset: bool = False
    ) -> chromadb.Collection:
        """
        Create or retrieve a ChromaDB collection.

        Args:
            collection_name: Name of collection
            reset: If True, delete existing and create fresh

        Returns:
            ChromaDB Collection object
        """
        if reset:
            try:
                self.client.delete_collection(collection_name)
                print(f"  🗑️  Deleted existing collection: {collection_name}")
            except:
                pass

        # Get or create collection with cosine similarity
        collection_kwargs = {
            "name": collection_name,
            "metadata": {"hnsw:space": "cosine"},  # Cosine similarity for semantic search
        }

        # Only add embedding function if one is configured
        if self.embedding_fn is not None:
            collection_kwargs["embedding_function"] = self.embedding_fn

        collection = self.client.get_or_create_collection(**collection_kwargs)

        self.collections[collection_name] = collection
        print(f"  ✅ Collection ready: {collection_name}")
        return collection

    def add_documents_to_collection(
        self, collection_name: str, documents: list[Document], batch_size: int = 100
    ) -> int:
        """
        Add documents to vector store collection.

        Args:
            collection_name: Target collection
            documents: List of LangChain Document objects
            batch_size: Number of documents per batch

        Returns:
            Number of documents added
        """
        collection = self.create_or_get_collection(collection_name)

        # Process in batches to avoid memory issues
        total_added = 0
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]

            # Prepare data for ChromaDB
            ids = [f"{collection_name}_{i+j}" for j in range(len(batch))]
            texts = [doc.page_content for doc in batch]
            metadatas = [doc.metadata for doc in batch]

            # Add to collection (ChromaDB handles embedding internally)
            collection.add(ids=ids, documents=texts, metadatas=metadatas)

            total_added += len(batch)
            print(f"    Added batch {i//batch_size + 1}: {len(batch)} documents")

        return total_added

    def query_collection(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[dict]:
        """
        Query vector store for similar documents.

        Args:
            collection_name: Collection to query
            query_text: Natural language query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {'doc_type': 'accounting_knowledge'})

        Returns:
            List of result dictionaries with documents and scores
        """
        if collection_name not in self.collections:
            collection = self.create_or_get_collection(collection_name)
        else:
            collection = self.collections[collection_name]

        # Check if collection is empty
        if collection.count() == 0:
            print(f"  ⚠️  Collection {collection_name} is empty")
            return []

        # Query with optional filtering
        results = collection.query(
            query_texts=[query_text],
            n_results=min(n_results, collection.count()),
            where=filter_metadata if filter_metadata else None,
        )

        # Format results
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append(
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                }
            )

        return formatted_results

    def hybrid_search(
        self, query_text: str, collections: list[str], n_results_per_collection: int = 3
    ) -> list[dict]:
        """
        Search across multiple collections and merge results.

        Args:
            query_text: Natural language query
            collections: List of collection names to search
            n_results_per_collection: Results per collection

        Returns:
            Merged and deduplicated results sorted by relevance
        """
        all_results = []

        for coll_name in collections:
            try:
                results = self.query_collection(coll_name, query_text, n_results_per_collection)
                all_results.extend(results)
            except Exception as e:
                print(f"  ⚠️  Error querying {coll_name}: {e}")

        # Sort by distance (lower is better)
        all_results.sort(key=lambda x: x.get("distance", float("inf")))

        # Deduplicate by content fingerprint
        seen_content = set()
        unique_results = []
        for result in all_results:
            # Use first 100 chars as fingerprint
            content_fingerprint = result["document"][:100]
            if content_fingerprint not in seen_content:
                unique_results.append(result)
                seen_content.add(content_fingerprint)

        return unique_results[: n_results_per_collection * len(collections)]

    def get_collection_stats(self) -> dict[str, int]:
        """
        Get document counts for all collections.

        Returns:
            Dict mapping collection names to document counts
        """
        stats = {}
        for collection in self.client.list_collections():
            stats[collection.name] = collection.count()
        return stats

    def reset_all_collections(self):
        """Delete all collections and start fresh."""
        for collection in self.client.list_collections():
            self.client.delete_collection(collection.name)
            print(f"  🗑️  Deleted: {collection.name}")

        self.collections = {}
        print("✅ All collections reset")

    def delete_collection(self, collection_name: str):
        """Delete a specific collection."""
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            print(f"  🗑️  Deleted collection: {collection_name}")
        except Exception as e:
            print(f"  ⚠️  Error deleting {collection_name}: {e}")


if __name__ == "__main__":
    # Test vector store manager
    print("=" * 80)
    print("🧪 Testing Vector Store Manager")
    print("=" * 80)

    # Initialize
    manager = VectorStoreManager()

    # Create test collection
    print("\n1️⃣ Creating test collection...")
    collection = manager.create_or_get_collection("test_collection", reset=True)

    # Add test documents
    print("\n2️⃣ Adding test documents...")
    test_docs = [
        Document(
            page_content="Project Aura is an AI-powered GL account review system.",
            metadata={"source": "test", "doc_type": "test"},
        ),
        Document(
            page_content="ChromaDB provides semantic search with vector embeddings.",
            metadata={"source": "test", "doc_type": "test"},
        ),
        Document(
            page_content="The system supports 1,000+ entities for Adani Group.",
            metadata={"source": "test", "doc_type": "test"},
        ),
    ]

    manager.add_documents_to_collection("test_collection", test_docs)

    # Query collection
    print("\n3️⃣ Querying collection...")
    results = manager.query_collection("test_collection", "What is Project Aura?", n_results=2)

    for i, result in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"    Document: {result['document'][:80]}...")
        print(f"    Distance: {result['distance']:.4f}")

    # Get stats
    print("\n4️⃣ Collection statistics...")
    stats = manager.get_collection_stats()
    for name, count in stats.items():
        print(f"    {name}: {count} documents")

    # Cleanup
    print("\n5️⃣ Cleaning up...")
    manager.delete_collection("test_collection")

    print("\n✅ Vector store manager test complete!")
