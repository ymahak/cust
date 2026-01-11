from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ---------- Internal Imports ----------
from app.routes.chat import router as chat_router
from app.routes.hitl import router as hitl_router
from app.routes.monitoring import router as monitoring_router
from app.routes.auth import router as auth_router
from app.database.mongo import connect_db
from app.monitoring.logger import setup_logger

# ---------- App Initialization ----------
app = FastAPI(
    title="AI Customer Support",
    version="1.0.0",
    description="Multi-agent AI customer support system with HITL"
)

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Logger ----------
logger = setup_logger()

# ---------- Startup ----------
@app.on_event("startup")
async def startup_event():
    await connect_db()
    logger.info("✅ Database connected successfully")

# ---------- Routers ----------
app.include_router(auth_router)                # /api/auth/*
app.include_router(chat_router, prefix="/api") # /api/chat
app.include_router(hitl_router, prefix="/api") # /api/hitl
app.include_router(monitoring_router, prefix="/api") # /api/monitoring

# ---------- Root ----------
@app.get("/")
async def root():
    return {
        "message": "AI Customer Support API",
        "status": "running"
    }

# ---------- Health Check ----------
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-customer-support"
    }

# ---------- Run ----------
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
