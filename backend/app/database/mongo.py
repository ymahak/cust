from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from typing import Optional
import os
import bcrypt

# -----------------------------
# Global DB Objects
# -----------------------------
client: AsyncIOMotorClient | None = None
db = None
messages_collection = None
escalations_collection = None
users_collection = None


# -----------------------------
# Connect to MongoDB
# -----------------------------
async def connect_db():
    global client, db, messages_collection, escalations_collection, users_collection

    if client is not None:
        return  # already connected

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

    client = AsyncIOMotorClient(MONGO_URI)
    db = client["customer_support"]

    messages_collection = db["messages"]
    escalations_collection = db["escalations"]
    users_collection = db["users"]

    print("✅ Connected to MongoDB")


# -----------------------------
# User Management
# -----------------------------

async def create_user(username: str, password: str, role: str = "user") -> dict:
    """Create a new user with hashed password"""
    if users_collection is None:
        await connect_db()
    
    # Check if user already exists
    existing = await users_collection.find_one({"username": username})
    if existing:
        raise ValueError("Username already exists")
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = {
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    
    result = await users_collection.insert_one(user)
    user["_id"] = str(result.inserted_id)
    user.pop("password_hash")  # Don't return password hash
    return user


async def verify_user(username: str, password: str) -> Optional[dict]:
    """Verify user credentials"""
    if users_collection is None:
        await connect_db()
    
    user = await users_collection.find_one({"username": username})
    if not user:
        return None
    
    # Verify password
    password_hash = user.get("password_hash", "")
    if not password_hash:
        return None
    
    if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
        return {
            "username": user["username"],
            "role": user.get("role", "user"),
            "_id": str(user["_id"])
        }
    
    return None


async def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username"""
    if users_collection is None:
        await connect_db()
    
    user = await users_collection.find_one({"username": username})
    if user:
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        if "created_at" in user and hasattr(user["created_at"], "isoformat"):
            user["created_at"] = user["created_at"].isoformat()
        if "updated_at" in user and hasattr(user["updated_at"], "isoformat"):
            user["updated_at"] = user["updated_at"].isoformat()
    return user


# -----------------------------
# Save Chat Message
# -----------------------------
async def save_message(
    user_id: str,
    message: str,
    response: str,
    agent_type: str,
    metadata: dict,
):
    if messages_collection is None:
        raise RuntimeError("Database not initialized")

    document = {
        "user_id": user_id,
        "message": message,
        "response": response,
        "agent_type": agent_type,
        "metadata": metadata,
        "timestamp": datetime.now(timezone.utc),
    }

    await messages_collection.insert_one(document)


# -----------------------------
# Get Conversation History
# -----------------------------
async def get_conversation_history(user_id: str, limit: int = 10):
    if messages_collection is None:
        raise RuntimeError("Database not initialized")

    cursor = (
        messages_collection
        .find({"user_id": user_id})
        .sort("timestamp", -1)
        .limit(limit)
    )

    history = []
    async for doc in cursor:
        history.append({
            "message": doc["message"],
            "response": doc["response"],
            "agent_type": doc["agent_type"],
            "timestamp": doc["timestamp"].isoformat(),
        })

    return history


# -----------------------------
# Escalations (HITL)
# -----------------------------
async def create_escalation(user_id: str, reason: str, agent_type: str):
    if escalations_collection is None:
        raise RuntimeError("Database not initialized")

    escalation = {
        "user_id": user_id,
        "reason": reason,
        "agent_type": agent_type,
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
    }

    result = await escalations_collection.insert_one(escalation)
    escalation["_id"] = str(result.inserted_id)
    return escalation


async def get_pending_escalations():
    if escalations_collection is None:
        raise RuntimeError("Database not initialized")

    cursor = escalations_collection.find({"status": "pending"}).sort("created_at", -1)
    escalations = []

    async for esc in cursor:
        esc["_id"] = str(esc["_id"])
        if "created_at" in esc and hasattr(esc["created_at"], "isoformat"):
            esc["created_at"] = esc["created_at"].isoformat()
        escalations.append(esc)

    return escalations


async def get_escalation(escalation_id: str):
    """Get a single escalation by ID"""
    if escalations_collection is None:
        raise RuntimeError("Database not initialized")
    
    from bson import ObjectId
    
    try:
        doc = await escalations_collection.find_one({"_id": ObjectId(escalation_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            if "created_at" in doc and hasattr(doc["created_at"], "isoformat"):
                doc["created_at"] = doc["created_at"].isoformat()
            if "resolved_at" in doc and hasattr(doc["resolved_at"], "isoformat"):
                doc["resolved_at"] = doc["resolved_at"].isoformat()
            if "reviewed_at" in doc and hasattr(doc["reviewed_at"], "isoformat"):
                doc["reviewed_at"] = doc["reviewed_at"].isoformat()
        return doc
    except Exception:
        return None


async def resolve_escalation(escalation_id: str, resolution: str):
    if escalations_collection is None:
        raise RuntimeError("Database not initialized")

    from bson import ObjectId

    await escalations_collection.update_one(
        {"_id": ObjectId(escalation_id)},
        {
            "$set": {
                "status": "resolved",
                "resolution": resolution,
                "resolved_at": datetime.now(timezone.utc),
            }
        },
    )

    return {"status": "resolved"}


async def update_escalation_response(
    escalation_id: str,
    response: str,
    reviewed_by: str,
    notes: Optional[str] = None,
    status: str = "reviewed"
):
    """Update escalation with human response"""
    if escalations_collection is None:
        raise RuntimeError("Database not initialized")
    
    from bson import ObjectId
    
    update_data = {
        "status": status,
        "human_response": response,
        "reviewed_by": reviewed_by,
        "reviewed_at": datetime.now(timezone.utc),
    }
    
    if notes:
        update_data["notes"] = notes
    
    await escalations_collection.update_one(
        {"_id": ObjectId(escalation_id)},
        {"$set": update_data}
    )


async def save_human_feedback(
    escalation_id: str,
    reviewer: str,
    action: str,
    response: str,
    original_response: Optional[str] = None,
    notes: Optional[str] = None
):
    """Save human feedback for agent improvement"""
    if db is None:
        await connect_db()
    
    feedback_collection = db.get_collection("human_feedback")
    
    feedback = {
        "escalation_id": escalation_id,
        "reviewer": reviewer,
        "action": action,  # approved, rejected, edited
        "response": response,
        "original_response": original_response,
        "notes": notes,
        "created_at": datetime.now(timezone.utc),
    }
    
    await feedback_collection.insert_one(feedback)
