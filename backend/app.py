"""
FastAPI Main Application for Voting System

This is the main entry point for the backend API server.
Run with: uvicorn app:app --reload --port 5000
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from settings import get_settings
from auth import Token, TokenData, authenticate_admin, create_access_token, verify_token

# Import route blueprints
from api.routes.auth import router as auth_router
from api.routes.admin import router as admin_router
from api.routes.verification import router as verification_router
from api.routes.voting import router as voting_router
from api.routes.results import router as results_router


# Security scheme for JWT Bearer tokens
security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Used to initialize ML models, database connections, etc.
    """
    # Startup
    print("🚀 Starting Voting System API...")
    settings = get_settings()
    print(f"   CORS Origins: {settings.cors_origins_list}")
    print(f"   Admin Username: {settings.admin_username}")
    print("✅ API Ready!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Voting System API...")


# Create FastAPI app
app = FastAPI(
    title="Voting System API",
    description="""
    Secure Voting System API with:
    - Admin authentication (JWT)
    - Voter registration with face embeddings
    - Dual verification (liveness + face recognition)
    - Constituency-based voting
    - Anonymous blockchain voting
    - Real-time results dashboard
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# DEPENDENCY: Get Current Admin User
# ============================================
async def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenData:
    """
    Dependency to verify JWT token and get current admin user.
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(admin: TokenData = Depends(get_current_admin)):
            return {"message": f"Hello, {admin.username}"}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if credentials is None:
        raise credentials_exception
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    return token_data


# ============================================
# INCLUDE ROUTERS
# ============================================
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(verification_router, prefix="/api/verify", tags=["Verification"])
app.include_router(voting_router, prefix="/api/vote", tags=["Voting"])
app.include_router(results_router, prefix="/api/results", tags=["Results"])


# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "ok",
        "message": "Voting System API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# ============================================
# RUN WITH UVICORN
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5001,
        reload=True
    )
