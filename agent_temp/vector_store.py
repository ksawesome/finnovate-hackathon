"""
Relevant Things
---------------
Inputs:
    doc_dir (str): Path to folder with policy/FAQ documents (txt, md, pdf)
    persist_dir (str): Where Chroma DB will be stored

Outputs:
    vectordb (Chroma): Local persistent vector store
    retriever (langchain retriever)

Dependencies:
    langchain, chromadb, sentence-transformers (Gemma/Gemini), pypdf
    optional: openai embeddings (fallback)

Side Effects:
    Creates data/vectors/ directory and stores embeddings

Usage:
    from src.vector_store import get_retriever, refresh_vector_store
"""

import os
import logging
from typing import Optional

from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings

logger = logging.getLogger("aura.vectorstore")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(ch)

# Default directories
DOC_DIR = os.getenv("DOC_DIR", "docs/policies/")
VECTOR_DIR = os.getenv("VECTOR_DIR", "data/vectors/")

# Embedding model config
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
# Gemini/Gemma alternative model from HuggingFace (if you want to use free embeddings)
ALT_EMBED_MODEL = os.getenv("ALT_EMBED_MODEL", "intfloat/multilingual-e5-base")


def _get_embeddings():
    """
    Use HuggingFace embeddings (Gemma/Gemini type). Fallback to OpenAI if needed.
    """
    try:
        logger.info(f"Using HuggingFace embeddings: {EMBED_MODEL}")
        return HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    except Exception as e:
        logger.warning(f"Falling back to alternate model: {ALT_EMBED_MODEL} ({e})")
        try:
            return HuggingFaceEmbeddings(model_name=ALT_EMBED_MODEL)
        except Exception:
            logger.warning("Falling back to OpenAI embeddings (requires API key)")
            return OpenAIEmbeddings(model="text-embedding-3-small")


def _load_documents(doc_dir: str):
    """
    Loads documents (PDF, TXT, MD) from a directory.
    """
    loaders = []
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir, exist_ok=True)
        logger.warning("Document directory %s created but empty.", doc_dir)

    # Loaders for PDFs and text formats
    pdfs = [f for f in os.listdir(doc_dir) if f.lower().endswith(".pdf")]
    txts = [f for f in os.listdir(doc_dir) if f.lower().endswith((".txt", ".md"))]

    for f in pdfs:
        loaders.append(PyPDFLoader(os.path.join(doc_dir, f)))
    for f in txts:
        loaders.append(TextLoader(os.path.join(doc_dir, f), encoding="utf-8"))

    documents = []
    for loader in loaders:
        try:
            documents.extend(loader.load())
        except Exception as e:
            logger.warning("Failed to load %s: %s", loader, e)

    logger.info("Loaded %d documents from %s", len(documents), doc_dir)
    return documents


def refresh_vector_store(
    doc_dir: Optional[str] = None,
    persist_dir: Optional[str] = None,
    chunk_size: int = 800,
    chunk_overlap: int = 150
):
    """
    Create or rebuild the ChromaDB vector store from documents.
    """
    doc_dir = doc_dir or DOC_DIR
    persist_dir = persist_dir or VECTOR_DIR
    os.makedirs(persist_dir, exist_ok=True)

    docs = _load_documents(doc_dir)
    if not docs:
        logger.warning("No documents to embed in %s", doc_dir)
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)

    embeddings = _get_embeddings()
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
    vectordb.persist()
    logger.info("Chroma vector store persisted at %s", persist_dir)
    return vectordb


def get_vector_store(persist_dir: Optional[str] = None):
    """
    Load an existing Chroma vector store from disk (without rebuilding).
    """
    persist_dir = persist_dir or VECTOR_DIR
    if not os.path.exists(persist_dir):
        raise FileNotFoundError(f"Vector store not found at {persist_dir}. Run refresh_vector_store() first.")
    embeddings = _get_embeddings()
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    logger.info("Loaded vector store from %s", persist_dir)
    return vectordb


def get_retriever(persist_dir: Optional[str] = None, search_k: int = 4):
    """
    Return a retriever object for similarity search.
    """
    vectordb = get_vector_store(persist_dir)
    retriever = vectordb.as_retriever(search_kwargs={"k": search_k})
    return retriever


def query_knowledgebase(query: str, persist_dir: Optional[str] = None, top_k: int = 3):
    """
    Convenience wrapper: query stored embeddings and return top chunks.
    """
    retriever = get_retriever(persist_dir, search_k=top_k)
    docs = retriever.get_relevant_documents(query)
    results = [{"content": d.page_content, "metadata": d.metadata} for d in docs]
    logger.info("Query returned %d chunks.", len(results))
    return results
