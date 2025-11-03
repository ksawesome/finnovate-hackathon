"""MongoDB operations for document-based data."""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pymongo.database import Database
from pymongo.collection import Collection

from . import get_mongo_database


def get_supporting_docs_collection() -> Collection:
    """Get supporting documents collection."""
    db = get_mongo_database()
    return db["supporting_docs"]


def get_audit_trail_collection() -> Collection:
    """Get audit trail collection."""
    db = get_mongo_database()
    return db["audit_trail"]


def get_validation_results_collection() -> Collection:
    """Get validation results collection."""
    db = get_mongo_database()
    return db["validation_results"]


def init_mongo_collections():
    """Initialize MongoDB collections with indexes."""
    db = get_mongo_database()
    
    # Supporting docs indexes
    supporting_docs = db["supporting_docs"]
    supporting_docs.create_index("gl_code")
    supporting_docs.create_index([("gl_code", 1), ("period", 1)])
    
    # Audit trail indexes
    audit_trail = db["audit_trail"]
    audit_trail.create_index("gl_code")
    audit_trail.create_index("timestamp")
    audit_trail.create_index([("gl_code", 1), ("timestamp", -1)])
    
    # Validation results indexes
    validation_results = db["validation_results"]
    validation_results.create_index("gl_code")
    validation_results.create_index("validation_suite")


def add_supporting_document(
    gl_code: str,
    period: str,
    file_name: str,
    file_path: str,
    uploaded_by: str,
    entity: str
) -> str:
    """Add a supporting document metadata."""
    collection = get_supporting_docs_collection()
    
    doc = {
        "gl_code": gl_code,
        "period": period,
        "entity": entity,
        "files": [{
            "name": file_name,
            "path": file_path,
            "uploaded_by": uploaded_by,
            "uploaded_at": datetime.utcnow()
        }],
        "comments": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = collection.insert_one(doc)
    return str(result.inserted_id)


def add_file_to_gl(gl_code: str, period: str, file_name: str, file_path: str, uploaded_by: str):
    """Add a file to existing GL document metadata."""
    collection = get_supporting_docs_collection()
    
    collection.update_one(
        {"gl_code": gl_code, "period": period},
        {
            "$push": {
                "files": {
                    "name": file_name,
                    "path": file_path,
                    "uploaded_by": uploaded_by,
                    "uploaded_at": datetime.utcnow()
                }
            },
            "$set": {"updated_at": datetime.utcnow()}
        },
        upsert=True
    )


def add_comment(gl_code: str, period: str, user: str, text: str):
    """Add a comment to a GL account."""
    collection = get_supporting_docs_collection()
    
    collection.update_one(
        {"gl_code": gl_code, "period": period},
        {
            "$push": {
                "comments": {
                    "user": user,
                    "text": text,
                    "timestamp": datetime.utcnow(),
                    "replies": []
                }
            },
            "$set": {"updated_at": datetime.utcnow()}
        }
    )


def log_audit_event(
    gl_code: str,
    action: str,
    actor: Dict[str, str],
    details: Optional[Dict[str, Any]] = None
):
    """Log an audit event."""
    collection = get_audit_trail_collection()
    
    event = {
        "gl_code": gl_code,
        "action": action,
        "actor": actor,
        "details": details or {},
        "timestamp": datetime.utcnow()
    }
    
    collection.insert_one(event)


def get_audit_trail(gl_code: str, limit: int = 100) -> List[Dict]:
    """Get audit trail for a GL account."""
    collection = get_audit_trail_collection()
    
    return list(
        collection.find({"gl_code": gl_code})
        .sort("timestamp", -1)
        .limit(limit)
    )


def save_validation_results(
    gl_code: str,
    period: str,
    validation_suite: str,
    results: Dict[str, Any],
    passed: bool
):
    """Save validation results."""
    collection = get_validation_results_collection()
    
    doc = {
        "gl_code": gl_code,
        "period": period,
        "validation_suite": validation_suite,
        "results": results,
        "passed": passed,
        "validated_at": datetime.utcnow()
    }
    
    collection.insert_one(doc)


def get_validation_results(gl_code: str, period: str) -> List[Dict]:
    """Get validation results for a GL account."""
    collection = get_validation_results_collection()
    
    return list(
        collection.find({"gl_code": gl_code, "period": period})
        .sort("validated_at", -1)
    )
