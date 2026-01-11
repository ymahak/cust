import os
import bcrypt
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# ---------- MongoDB Connection ----------
MONGO_URI = os.getenv("MONGO_URI")

client: AsyncIOMotorClient | None = None
db = None

users_collection = None
escalations_collection = None
messages_collection = None


async def connect_db():
    """Initialize MongoDB connection once on startup"""
    global client, db, users_collection, escalations_collection, messages_collection

    if client is None:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client["ai_customer_support"]

        users_collection = db["users"]
        escalations_collection = db["escalations"]
        messages_collection = db["messages"]


# ---------- USER AUTH ----------
async def create_user(username: str, password: str, role: str):
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user = {
        "username": username,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.utcnow()
    }

    await users_collection.insert_one(user)
    return user  # ✅ IMPORTANT


async def verify_user(username: str, password: str):
    user = await users_collection.find_one({"username": username})
    if not user:
        return None

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"].encode("utf-8")
    ):
        return None

    return user


async def get_user_by_username(username: str):
    return await users_collection.find_one({"username": username})


# ---------- CHAT MESSAGES ----------
async def save_message(message: str, response: str, intent: str, escalated: bool, timestamp: datetime):
    doc = {
        "message": message,
        "response": response,
        "intent": intent,
        "escalated": escalated,
        "timestamp": timestamp
    }
    await messages_collection.insert_one(doc)


# ---------- HITL / ESCALATION ----------
async def create_escalation(user_message: str, ai_response: str, intent: str, reason: str):
    escalation = {
        "user_message": user_message,
        "ai_response": ai_response,
        "intent": intent,
        "reason": reason,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "resolved_at": None,
        "human_response": None,
        "notes": None
    }
    await escalations_collection.insert_one(escalation)


async def get_pending_escalations():
    cursor = escalations_collection.find({"status": "pending"})
    return await cursor.to_list(length=100)


async def resolve_escalation(escalation_id, human_response: str, notes: str | None = None):
    from bson import ObjectId

    await escalations_collection.update_one(
        {"_id": ObjectId(escalation_id)},
        {
            "$set": {
                "status": "resolved",
                "human_response": human_response,
                "notes": notes,
                "resolved_at": datetime.utcnow()
            }
        }
    )
