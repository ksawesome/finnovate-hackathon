"""Vector store module for RAG using ChromaDB."""

from pathlib import Path
from typing import List, Optional
import chromadb
from chromadb.config import Settings

from .db.storage import get_vectors_dir


class VectorStore:
    """ChromaDB vector store for RAG functionality."""
    
    def __init__(self, collection_name: str = "accounting_faqs"):
        """
        Initialize ChromaDB client.
        
        Args:
            collection_name: Name of the collection to use.
        """
        persist_directory = get_vectors_dir()
        self.client = chromadb.Client(
            Settings(persist_directory=str(persist_directory))
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of text documents to embed and store.
            metadatas: Optional list of metadata dicts for each document.
            ids: Optional list of IDs for each document.
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(
        self,
        query_text: str,
        n_results: int = 5
    ) -> dict:
        """
        Query the vector store for similar documents.
        
        Args:
            query_text: Query string to search for.
            n_results: Number of results to return.
            
        Returns:
            Dict with keys: documents, metadatas, distances, ids
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
    
    def delete_collection(self):
        """Delete the collection."""
        self.client.delete_collection(name=self.collection.name)


def initialize_faq_store():
    """Initialize vector store with accounting FAQs."""
    store = VectorStore("accounting_faqs")
    
    # Sample FAQs - replace with actual accounting documentation
    faqs = [
        "Trial balance must always sum to zero. Debits should equal credits.",
        "GL accounts are categorized as: Assets, Liabilities, Equity, Revenue, Expenses.",
        "Supporting documents include invoices, receipts, bank statements, and reconciliations.",
        "Review hierarchy: User uploads → Reviewer checks → Business FC approves.",
        "SAP entities auto-extract trial reports daily. Non-SAP entities upload manually.",
        "Variance threshold for review: 10% change from previous period or $50,000 absolute.",
        "All GL accounts must have backup documentation uploaded within 5 business days.",
        "Monthly close timeline: Trial extraction Day 1, Review Days 2-5, FC approval Day 6-7.",
    ]
    
    metadatas = [{"source": "accounting_policy", "topic": "general"} for _ in faqs]
    
    store.add_documents(faqs, metadatas=metadatas)
    return store


if __name__ == "__main__":
    # Test initialization
    store = initialize_faq_store()
    results = store.query("What is a trial balance?")
    print("Query results:", results)
