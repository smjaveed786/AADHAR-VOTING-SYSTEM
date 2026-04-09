"""
JWT Authentication Utilities for Voting System

This module provides:
- JWT token creation and verification
- Password hashing (for future use)
- Admin authentication against environment variables

GUIDE TO JWT-BASED AUTHENTICATION:
==================================

1. WHAT IS JWT?
   - JSON Web Token (JWT) is a compact, self-contained way to transmit
     information between parties as a JSON object.
   - It's digitally signed, so it can be verified and trusted.

2. HOW IT WORKS:
   a) Admin logs in with username/password
   b) Server verifies credentials against environment variables
   c) If valid, server creates a JWT token with:
      - Subject (sub): The admin username
      - Expiration (exp): When the token expires
   d) Token is signed with JWT_SECRET_KEY
   e) Client stores token and sends it with each request
   f) Server verifies token on protected routes

3. TOKEN STRUCTURE:
   header.payload.signature
   - Header: Algorithm used (HS256)
   - Payload: Data (username, expiration)
   - Signature: HMAC-SHA256(header + payload, secret_key)

4. SECURITY BEST PRACTICES:
   - Use long, random secret keys in production
   - Set reasonable expiration times
   - Use HTTPS in production
   - Store tokens securely on client (httpOnly cookies or secure storage)
   - Never expose secret key
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from settings import get_settings


# Password hashing context (for future database storage)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data extracted from JWT token."""
    username: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    Used when passwords are stored hashed in database.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storage.
    Example: get_password_hash("admin123") -> "$2b$12$..."
    """
    return pwd_context.hash(password)


def authenticate_admin(username: str, password: str) -> bool:
    """
    Authenticate admin against environment variables.
    
    In this implementation, admin credentials are stored in environment
    variables for simplicity. In a production system with multiple admins,
    you would store hashed passwords in a database.
    
    Args:
        username: Admin username from login form
        password: Admin password from login form
        
    Returns:
        True if credentials match, False otherwise
    """
    settings = get_settings()
    
    # DEBUG: Print credentials for troubleshooting
    print(f"DEBUG AUTH: Received username='{username}', password='{password}'")
    print(f"DEBUG AUTH: Expected username='{settings.admin_username}', password='{settings.admin_password}'")
    
    # Compare with environment variables
    if username != settings.admin_username:
        print("DEBUG AUTH: Username mismatch")
        return False
    if password != settings.admin_password:
        print("DEBUG AUTH: Password mismatch")
        return False
    
    return True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary with claims to encode (e.g., {"sub": "admin"})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
        
    Example:
        token = create_access_token({"sub": "admin"})
        # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    settings = get_settings()
    
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    
    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        TokenData with username if valid, None if invalid
        
    Example:
        data = verify_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        if data:
            print(f"Welcome, {data.username}")
    """
    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


# ============================================
# EXAMPLE USAGE
# ============================================
"""
# 1. Admin Login
username = "admin"
password = "admin123"

if authenticate_admin(username, password):
    token = create_access_token({"sub": username})
    print(f"Login successful! Token: {token}")
else:
    print("Invalid credentials")

# 2. Verify Token on Protected Route
token_data = verify_token(token)
if token_data:
    print(f"Authenticated as: {token_data.username}")
else:
    print("Invalid or expired token")

# 3. Hash a password (for future database storage)
hashed = get_password_hash("my_secure_password")
print(f"Hashed: {hashed}")

# 4. Verify hashed password
is_valid = verify_password("my_secure_password", hashed)
print(f"Password valid: {is_valid}")
"""
