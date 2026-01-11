from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

try:
    from .auth.jwt import verify_token, create_token
    from .routes.chat import router as chat_router
    from .routes.hitl import router as hitl_router
    from .routes.monitoring import router as monitoring_router
    from .database.mongo import connect_db, create_user, verify_user
    from .monitoring.logger import setup_logger
except ImportError:
    from auth.jwt import verify_token, create_token
    from routes.chat import router as chat_router
    from routes.hitl import router as hitl_router
    from routes.monitoring import router as monitoring_router
    from database.mongo import connect_db, create_user, verify_user
    from monitoring.logger import setup_logger

app = FastAPI(title="AI Customer Support", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logger
logger = setup_logger()

# Include routers
app.include_router(chat_router, prefix="/api")
app.include_router(hitl_router, prefix="/api")
app.include_router(monitoring_router, prefix="/api")

security = HTTPBearer()

# User models
class User(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.get("/")
async def root():
    return {"message": "AI Customer Support API", "status": "running"}

@app.post("/api/auth/signup", response_model=dict)
async def signup(signup_data: SignupRequest):
    """Signup endpoint - Create new user account"""
    await connect_db()
    
    # Validate role
    if signup_data.role and signup_data.role not in ["user", "agent", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'user', 'agent', or 'admin'"
        )
    
    # Validate username
    if len(signup_data.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters"
        )
    
    # Validate password
    if len(signup_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    try:
        user = await create_user(
            username=signup_data.username,
            password=signup_data.password,
            role=signup_data.role or "user"
        )
        logger.info(f"New user signed up: {signup_data.username}")
        return {
            "message": "User created successfully",
            "username": user["username"],
            "role": user["role"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user: User):
    """Login endpoint"""
    await connect_db()
    
    user_data = await verify_user(user.username, user.password)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token = create_token({"username": user_data["username"], "role": user_data["role"]})
    logger.info(f"User {user_data['username']} logged in successfully")
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/auth/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user info"""
    payload = verify_token(credentials.credentials)
    return {"username": payload["username"], "role": payload["role"]}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-customer-support"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
