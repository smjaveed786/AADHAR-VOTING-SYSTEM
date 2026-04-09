"""
Authentication API Routes

Endpoints:
- POST /api/auth/login - Admin login with JWT token
- POST /api/auth/logout - Invalidate session (client-side)
- GET /api/auth/verify - Verify JWT token validity
- POST /api/auth/send-otp - Send OTP to voter's phone
- POST /api/auth/verify-otp - Verify OTP code
"""

from datetime import timedelta
from typing import Optional
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from auth import (
    Token, 
    TokenData, 
    authenticate_admin, 
    create_access_token, 
    verify_token
)
from settings import get_settings
from services.otp_service import get_otp_service


router = APIRouter()
security = HTTPBearer(auto_error=False)


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class LoginRequest(BaseModel):
    """Login request body."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response with token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    username: str


class VerifyResponse(BaseModel):
    """Token verification response."""
    valid: bool
    username: Optional[str] = None
    message: str


class SendOTPRequest(BaseModel):
    """Request to send OTP."""
    aadhaar: str


class SendOTPResponse(BaseModel):
    """Response after sending OTP."""
    success: bool
    message: str
    expires_in: Optional[int] = None


class VerifyOTPRequest(BaseModel):
    """Request to verify OTP."""
    aadhaar: str
    otp: str


class VerifyOTPResponse(BaseModel):
    """Response after verifying OTP."""
    success: bool
    message: str


# ============================================
# ROUTES
# ============================================

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Admin login endpoint.
    
    Returns a JWT token that must be included in the Authorization header
    for all protected routes.
    
    Example:
    ```
    POST /api/auth/login
    {
        "username": "admin",
        "password": "admin123"
    }
    
    Response:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
        "token_type": "bearer",
        "expires_in": 3600,
        "username": "admin"
    }
    ```
    
    Usage:
    Include the token in subsequent requests:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI...
    ```
    """
    # Authenticate against environment variables
    if not authenticate_admin(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    settings = get_settings()
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": request.username}
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        username=request.username
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    
    Note: JWT tokens are stateless, so the server cannot invalidate them.
    The client should:
    1. Remove the token from storage
    2. Optionally, the token can be added to a blacklist (not implemented)
    
    This endpoint is provided for API completeness.
    """
    return {
        "message": "Logged out successfully",
        "note": "Please remove the token from client storage"
    }


@router.get("/verify", response_model=VerifyResponse)
async def verify(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Verify if a JWT token is valid.
    
    Include the token in the Authorization header:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI...
    ```
    
    Returns the validity status and username if valid.
    """
    if credentials is None:
        return VerifyResponse(
            valid=False,
            message="No token provided"
        )
    
    token_data = verify_token(credentials.credentials)
    
    if token_data is None:
        return VerifyResponse(
            valid=False,
            message="Invalid or expired token"
        )
    
    return VerifyResponse(
        valid=True,
        username=token_data.username,
        message="Token is valid"
    )


@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(request: SendOTPRequest):
    """
    Send OTP to voter's registered phone number.
    
    This endpoint:
    1. Validates the Aadhaar number
    2. Looks up the voter's phone number from voters.json
    3. Sends a 6-digit OTP via Twilio SMS
    4. Stores the OTP with 5-minute expiry
    
    Example:
    ```
    POST /api/auth/send-otp
    {
        "aadhaar": "123456789012"
    }
    
    Response:
    {
        "success": true,
        "message": "OTP sent successfully",
        "expires_in": 300
    }
    ```
    """
    settings = get_settings()
    voters_file = settings.base_dir.parent / "data" / "voters.json"
    
    # Validate Aadhaar format
    if not request.aadhaar or len(request.aadhaar) != 12 or not request.aadhaar.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Aadhaar number format"
        )
    
    # Load voters data
    if not voters_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter not found. Please register first."
        )
    
    try:
        with open(voters_file, 'r') as f:
            voters = json.load(f)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error loading voter data"
        )
    
    # Find voter by Aadhaar (voters.json is a dict with aadhaar as key)
    voter = voters.get(request.aadhaar)
    
    if not voter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter not found. Please register first."
        )
    
    # Get phone number
    phone_number = voter.get('phone_number')
    if not phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No phone number registered for this voter"
        )
    
    # Ensure phone number is in E.164 format
    if not phone_number.startswith('+'):
        phone_number = '+91' + phone_number  # Assume India if no country code
    
    # Send OTP via Twilio
    otp_service = get_otp_service()
    result = otp_service.send_otp(phone_number, request.aadhaar)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result['message']
        )
    
    return SendOTPResponse(**result)


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(request: VerifyOTPRequest):
    """
    Verify the OTP code sent to voter's phone.
    
    This endpoint:
    1. Validates the OTP format
    2. Checks if OTP matches and hasn't expired
    3. Allows up to 3 verification attempts
    
    Example:
    ```
    POST /api/auth/verify-otp
    {
        "aadhaar": "123456789012",
        "otp": "123456"
    }
    
    Response:
    {
        "success": true,
        "message": "OTP verified successfully"
    }
    ```
    """
    # Validate inputs
    if not request.aadhaar or len(request.aadhaar) != 12 or not request.aadhaar.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Aadhaar number format"
        )
    
    if not request.otp or len(request.otp) != 6 or not request.otp.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP format"
        )
    
    # Verify OTP
    otp_service = get_otp_service()
    result = otp_service.verify_otp(request.aadhaar, request.otp)
    
    return VerifyOTPResponse(**result)
