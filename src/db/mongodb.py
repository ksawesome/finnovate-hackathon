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


def get_gl_metadata_collection() -> Collection:
    """Get GL metadata collection for extended GL account information."""
    db = get_mongo_database()
    return db["gl_metadata"]


def get_assignment_details_collection() -> Collection:
    """Get assignment details collection for responsibility matrix metadata."""
    db = get_mongo_database()
    return db["assignment_details"]


def get_review_sessions_collection() -> Collection:
    """Get review sessions collection for tracking review workflows."""
    db = get_mongo_database()
    return db["review_sessions"]


def get_user_feedback_collection() -> Collection:
    """Get user feedback collection for observations and suggestions."""
    db = get_mongo_database()
    return db["user_feedback"]


def get_query_library_collection() -> Collection:
    """Get query library collection for standardized query templates."""
    db = get_mongo_database()
    return db["query_library"]


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
    
    # GL metadata indexes (extended GL account information)
    gl_metadata = db["gl_metadata"]
    gl_metadata.create_index([("gl_code", 1), ("company_code", 1), ("period", 1)], unique=True)
    gl_metadata.create_index("account_category")
    gl_metadata.create_index("criticality")
    
    # Assignment details indexes (responsibility matrix metadata)
    assignment_details = db["assignment_details"]
    assignment_details.create_index([("assignment_id", 1)], unique=True)
    assignment_details.create_index([("gl_code", 1), ("company_code", 1)])
    assignment_details.create_index("assigned_user_email")
    assignment_details.create_index("severity")
    
    # Review sessions indexes (workflow tracking)
    review_sessions = db["review_sessions"]
    review_sessions.create_index([("session_id", 1)], unique=True)
    review_sessions.create_index("period")
    review_sessions.create_index("created_by")
    review_sessions.create_index([("start_date", -1)])
    
    # User feedback indexes (observations and suggestions)
    user_feedback = db["user_feedback"]
    user_feedback.create_index("gl_code")
    user_feedback.create_index("observation_type")
    user_feedback.create_index("status")
    user_feedback.create_index([("created_at", -1)])
    
    # Query library indexes (standardized queries)
    query_library = db["query_library"]
    query_library.create_index([("query_type", 1), ("account_code", 1)])
    query_library.create_index("nature")
    query_library.create_index("is_active")
    query_library.create_index([("usage_count", -1)])  # Most used queries first
    
    print("✅ MongoDB collections and indexes created successfully")
    print(f"   - 8 collections initialized:")
    print(f"     • supporting_docs (file metadata)")
    print(f"     • audit_trail (change tracking)")
    print(f"     • validation_results (data quality)")
    print(f"     • gl_metadata (extended GL info)")
    print(f"     • assignment_details (responsibility tracking)")
    print(f"     • review_sessions (workflow state)")
    print(f"     • user_feedback (observations)")
    print(f"     • query_library (standardized queries)")


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


# ============================================================================
# GL Metadata Operations (Extended GL Account Information)
# ============================================================================

def save_gl_metadata(
    gl_code: str,
    company_code: str,
    period: str,
    metadata: Dict[str, Any]
) -> str:
    """Save extended metadata for a GL account."""
    collection = get_gl_metadata_collection()
    
    doc = {
        "gl_code": gl_code,
        "company_code": company_code,
        "period": period,
        "description_long": metadata.get("description_long", ""),
        "account_category": metadata.get("account_category"),
        "sub_category": metadata.get("sub_category"),
        "criticality": metadata.get("criticality"),
        "review_notes": metadata.get("review_notes", []),
        "historical_issues": metadata.get("historical_issues", []),
        "reconciliation_details": metadata.get("reconciliation_details", {}),
        "supporting_schedule_refs": metadata.get("supporting_schedule_refs", []),
        "tags": metadata.get("tags", []),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = collection.update_one(
        {"gl_code": gl_code, "company_code": company_code, "period": period},
        {"$set": doc},
        upsert=True
    )
    return str(result.upserted_id) if result.upserted_id else "updated"


def get_gl_metadata(gl_code: str, company_code: str, period: str) -> Optional[Dict]:
    """Get metadata for a specific GL account."""
    collection = get_gl_metadata_collection()
    return collection.find_one({"gl_code": gl_code, "company_code": company_code, "period": period})


def add_review_note_to_gl(gl_code: str, company_code: str, period: str, note: str, added_by: str):
    """Add a review note to GL metadata."""
    collection = get_gl_metadata_collection()
    
    collection.update_one(
        {"gl_code": gl_code, "company_code": company_code, "period": period},
        {
            "$push": {
                "review_notes": {
                    "note": note,
                    "added_by": added_by,
                    "timestamp": datetime.utcnow()
                }
            },
            "$set": {"updated_at": datetime.utcnow()}
        }
    )


# ============================================================================
# Assignment Details Operations (Responsibility Matrix Metadata)
# ============================================================================

def save_assignment_details(
    assignment_id: str,
    gl_code: str,
    company_code: str,
    details: Dict[str, Any]
) -> str:
    """Save detailed assignment metadata."""
    collection = get_assignment_details_collection()
    
    doc = {
        "assignment_id": assignment_id,
        "gl_code": gl_code,
        "company_code": company_code,
        "person_name": details.get("person_name"),
        "assigned_user_email": details.get("assigned_user_email"),
        "severity": details.get("severity"),
        "query_type": details.get("query_type"),
        "working_needed": details.get("working_needed", ""),
        "preparer_comment": details.get("preparer_comment", ""),
        "reviewer_comment": details.get("reviewer_comment", ""),
        "communication_log": details.get("communication_log", []),
        "status_history": details.get("status_history", []),
        "attachments": details.get("attachments", []),
        "escalations": details.get("escalations", []),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = collection.update_one(
        {"assignment_id": assignment_id},
        {"$set": doc},
        upsert=True
    )
    return str(result.upserted_id) if result.upserted_id else "updated"


def get_assignment_details(assignment_id: str) -> Optional[Dict]:
    """Get detailed assignment information."""
    collection = get_assignment_details_collection()
    return collection.find_one({"assignment_id": assignment_id})


def add_communication_to_assignment(assignment_id: str, message: str, from_user: str, to_user: str):
    """Add communication entry to assignment log."""
    collection = get_assignment_details_collection()
    
    collection.update_one(
        {"assignment_id": assignment_id},
        {
            "$push": {
                "communication_log": {
                    "message": message,
                    "from_user": from_user,
                    "to_user": to_user,
                    "timestamp": datetime.utcnow()
                }
            },
            "$set": {"updated_at": datetime.utcnow()}
        }
    )


# ============================================================================
# Review Sessions Operations (Workflow Tracking)
# ============================================================================

def create_review_session(
    session_id: str,
    period: str,
    created_by: str,
    session_data: Dict[str, Any]
) -> str:
    """Create a new review session."""
    collection = get_review_sessions_collection()
    
    doc = {
        "session_id": session_id,
        "period": period,
        "created_by": created_by,
        "start_date": session_data.get("start_date", datetime.utcnow()),
        "target_completion_date": session_data.get("target_completion_date"),
        "status": session_data.get("status", "not_started"),
        "accounts_in_scope": session_data.get("accounts_in_scope", []),
        "checkpoints": session_data.get("checkpoints", []),
        "milestones": session_data.get("milestones", []),
        "overall_progress": session_data.get("overall_progress", 0),
        "blockers": session_data.get("blockers", []),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = collection.insert_one(doc)
    return str(result.inserted_id)


def get_review_session(session_id: str) -> Optional[Dict]:
    """Get review session by ID."""
    collection = get_review_sessions_collection()
    return collection.find_one({"session_id": session_id})


def update_review_session_progress(session_id: str, progress: int, checkpoint: str):
    """Update review session progress."""
    collection = get_review_sessions_collection()
    
    collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "overall_progress": progress,
                "updated_at": datetime.utcnow()
            },
            "$push": {
                "checkpoints": {
                    "name": checkpoint,
                    "completed_at": datetime.utcnow()
                }
            }
        }
    )


def get_active_review_sessions(period: Optional[str] = None) -> List[Dict]:
    """Get all active review sessions."""
    collection = get_review_sessions_collection()
    
    query = {"status": {"$in": ["not_started", "in_progress"]}}
    if period:
        query["period"] = period
    
    return list(collection.find(query).sort("start_date", -1))


# ============================================================================
# User Feedback Operations (Observations and Suggestions)
# ============================================================================

def save_user_feedback(
    gl_code: Optional[str],
    observation_type: str,
    feedback_text: str,
    submitted_by: str,
    additional_data: Optional[Dict[str, Any]] = None
) -> str:
    """Save user feedback or observation."""
    collection = get_user_feedback_collection()
    
    doc = {
        "gl_code": gl_code,
        "observation_type": observation_type,  # query, reclassification, observation, suggestion
        "feedback_text": feedback_text,
        "submitted_by": submitted_by,
        "status": "open",
        "priority": additional_data.get("priority", "medium") if additional_data else "medium",
        "category": additional_data.get("category") if additional_data else None,
        "resolution": None,
        "resolved_by": None,
        "resolved_at": None,
        "upvotes": 0,
        "tags": additional_data.get("tags", []) if additional_data else [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = collection.insert_one(doc)
    return str(result.inserted_id)


def get_feedback_by_gl(gl_code: str) -> List[Dict]:
    """Get all feedback for a specific GL account."""
    collection = get_user_feedback_collection()
    return list(collection.find({"gl_code": gl_code}).sort("created_at", -1))


def get_open_feedback(observation_type: Optional[str] = None) -> List[Dict]:
    """Get all open feedback items."""
    collection = get_user_feedback_collection()
    
    query = {"status": "open"}
    if observation_type:
        query["observation_type"] = observation_type
    
    return list(collection.find(query).sort("created_at", -1))


def resolve_feedback(feedback_id: str, resolution: str, resolved_by: str):
    """Mark feedback as resolved."""
    from bson import ObjectId
    collection = get_user_feedback_collection()
    
    collection.update_one(
        {"_id": ObjectId(feedback_id)},
        {
            "$set": {
                "status": "resolved",
                "resolution": resolution,
                "resolved_by": resolved_by,
                "resolved_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )


# ============================================================================
# Query Library Operations (Standardized Query Templates)
# ============================================================================

def save_query_template(
    query_type: str,
    account_code: str,
    template_data: Dict[str, Any]
) -> str:
    """Save a standardized query template."""
    collection = get_query_library_collection()
    
    doc = {
        "query_type": query_type,
        "account_code": account_code,
        "account_name": template_data.get("account_name"),
        "nature": template_data.get("nature"),
        "query_text": template_data.get("query_text", ""),
        "standard_response": template_data.get("standard_response", ""),
        "required_fields": template_data.get("required_fields", []),
        "validation_rules": template_data.get("validation_rules", []),
        "related_accounts": template_data.get("related_accounts", []),
        "department": template_data.get("department"),
        "is_active": template_data.get("is_active", True),
        "usage_count": 0,
        "last_used": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = collection.update_one(
        {"query_type": query_type, "account_code": account_code},
        {"$set": doc},
        upsert=True
    )
    return str(result.upserted_id) if result.upserted_id else "updated"


def get_query_template(query_type: str, account_code: str) -> Optional[Dict]:
    """Get query template for specific account and query type."""
    collection = get_query_library_collection()
    
    # Increment usage counter
    collection.update_one(
        {"query_type": query_type, "account_code": account_code},
        {
            "$inc": {"usage_count": 1},
            "$set": {"last_used": datetime.utcnow()}
        }
    )
    
    return collection.find_one({"query_type": query_type, "account_code": account_code})


def get_templates_by_nature(nature: str) -> List[Dict]:
    """Get all templates for a specific nature classification."""
    collection = get_query_library_collection()
    return list(collection.find({"nature": nature, "is_active": True}))


def get_most_used_templates(limit: int = 20) -> List[Dict]:
    """Get most frequently used query templates."""
    collection = get_query_library_collection()
    return list(
        collection.find({"is_active": True})
        .sort("usage_count", -1)
        .limit(limit)
    )


# ============================================================================
# Data Ingestion Support Functions
# ============================================================================

def save_gl_metadata(
    entity: str,
    period: str,
    profile: Dict[str, Any],
    fingerprint: str,
    ingestion_result: Dict[str, Any]
) -> str:
    """
    Save GL metadata to MongoDB
    
    Args:
        entity: Entity code
        period: Period
        profile: Data profile dictionary
        fingerprint: File fingerprint
        ingestion_result: Ingestion result
        
    Returns:
        Inserted document ID
    """
    db = get_mongo_database()
    collection = db.gl_metadata
    
    document = {
        "entity": entity,
        "period": period,
        "file_fingerprint": fingerprint,
        "data_profile": profile,
        "ingestion_result": ingestion_result,
        "created_at": datetime.utcnow(),
    }
    
    result = collection.insert_one(document)
    
    return str(result.inserted_id)


def log_audit_event(
    event_type: str,
    entity: str = None,
    period: str = None,
    **metadata
) -> str:
    """
    Log audit event to MongoDB
    
    Args:
        event_type: Event taxonomy type
        entity: Entity code
        period: Period
        **metadata: Additional metadata
        
    Returns:
        Inserted document ID
    """
    db = get_mongo_database()
    collection = db.audit_trail
    
    document = {
        "event_type": event_type,
        "entity": entity,
        "period": period,
        "timestamp": datetime.utcnow(),
        "metadata": metadata
    }
    
    result = collection.insert_one(document)
    
    return str(result.inserted_id)
