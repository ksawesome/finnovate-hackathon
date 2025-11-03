"""File storage operations for CSV, Parquet, and supporting documents."""

import os
from pathlib import Path
from typing import Union
import pandas as pd

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SUPPORTING_DOCS_DIR = DATA_DIR / "supporting_docs"
VECTORS_DIR = DATA_DIR / "vectors"

# Ensure directories exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
SUPPORTING_DOCS_DIR.mkdir(parents=True, exist_ok=True)
VECTORS_DIR.mkdir(parents=True, exist_ok=True)


def save_raw_csv(df: pd.DataFrame, filename: str) -> Path:
    """
    Save raw CSV to data/raw/ directory.
    
    Args:
        df: DataFrame to save.
        filename: Name of the CSV file.
        
    Returns:
        Path to saved file.
    """
    filepath = RAW_DIR / filename
    df.to_csv(filepath, index=False)
    return filepath


def load_raw_csv(filename: str) -> pd.DataFrame:
    """
    Load CSV from data/raw/ directory.
    
    Args:
        filename: Name of the CSV file.
        
    Returns:
        Loaded DataFrame.
    """
    filepath = RAW_DIR / filename
    return pd.read_csv(filepath)


def save_processed_parquet(df: pd.DataFrame, filename: str) -> Path:
    """
    Save processed data as Parquet in data/processed/ directory.
    
    Args:
        df: DataFrame to save.
        filename: Name of the Parquet file (without extension).
        
    Returns:
        Path to saved file.
    """
    if not filename.endswith(".parquet"):
        filename = f"{filename}.parquet"
    filepath = PROCESSED_DIR / filename
    df.to_parquet(filepath, index=False, compression="snappy")
    return filepath


def load_processed_parquet(filename: str) -> pd.DataFrame:
    """
    Load Parquet from data/processed/ directory.
    
    Args:
        filename: Name of the Parquet file.
        
    Returns:
        Loaded DataFrame.
    """
    if not filename.endswith(".parquet"):
        filename = f"{filename}.parquet"
    filepath = PROCESSED_DIR / filename
    return pd.read_parquet(filepath)


def save_supporting_document(file_content: bytes, filename: str, gl_code: str) -> Path:
    """
    Save supporting document (PDF, Excel, etc.) to data/supporting_docs/.
    
    Args:
        file_content: Binary content of the file.
        filename: Original filename.
        gl_code: GL account code for organizing files.
        
    Returns:
        Path to saved file.
    """
    gl_dir = SUPPORTING_DOCS_DIR / gl_code
    gl_dir.mkdir(exist_ok=True)
    
    filepath = gl_dir / filename
    with open(filepath, "wb") as f:
        f.write(file_content)
    
    return filepath


def get_supporting_document_path(gl_code: str, filename: str) -> Path:
    """Get path to a supporting document."""
    return SUPPORTING_DOCS_DIR / gl_code / filename


def list_supporting_documents(gl_code: str) -> list[str]:
    """List all supporting documents for a GL account."""
    gl_dir = SUPPORTING_DOCS_DIR / gl_code
    if not gl_dir.exists():
        return []
    return [f.name for f in gl_dir.iterdir() if f.is_file()]


def get_vectors_dir() -> Path:
    """Get the vector store directory for ChromaDB."""
    return VECTORS_DIR


def clear_processed_cache():
    """Clear all processed Parquet files (for testing/reset)."""
    for file in PROCESSED_DIR.glob("*.parquet"):
        file.unlink()
