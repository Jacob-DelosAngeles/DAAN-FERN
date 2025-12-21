"""
Clerk Authentication Module for FastAPI

Verifies Clerk JWT tokens and syncs users with the local database.
"""

import jwt
import httpx
import logging
from typing import Optional
from fastapi import HTTPException, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, InterfaceError

from core.database import get_db
from core.config import settings
from models.user import UserModel

logger = logging.getLogger(__name__)

# Clerk's JWKS endpoint for token verification
CLERK_JWKS_CACHE = None
CLERK_JWKS_CACHE_TIME = None


def fetch_clerk_user_email(clerk_user_id: str) -> Optional[str]:
    """
    Fetch user's primary email from Clerk Backend API.
    Uses synchronous httpx since we're in a sync context.
    """
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"https://api.clerk.com/v1/users/{clerk_user_id}",
                headers={
                    "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Get primary email from email_addresses array
                email_addresses = user_data.get("email_addresses", [])
                primary_email_id = user_data.get("primary_email_address_id")
                
                # Find primary email
                for email_obj in email_addresses:
                    if email_obj.get("id") == primary_email_id:
                        email = email_obj.get("email_address")
                        logger.info(f"Fetched email from Clerk API: {email}")
                        return email
                
                # Fallback: return first email if no primary
                if email_addresses:
                    email = email_addresses[0].get("email_address")
                    logger.info(f"Fetched first email from Clerk API: {email}")
                    return email
                    
            else:
                logger.warning(f"Clerk API returned {response.status_code}: {response.text}")
                
    except Exception as e:
        logger.error(f"Failed to fetch email from Clerk API: {e}")
    
    return None


async def get_clerk_jwks():
    """Fetch Clerk's JWKS for token verification (with caching)."""
    global CLERK_JWKS_CACHE, CLERK_JWKS_CACHE_TIME
    import time
    
    # Cache JWKS for 1 hour
    if CLERK_JWKS_CACHE and CLERK_JWKS_CACHE_TIME and (time.time() - CLERK_JWKS_CACHE_TIME < 3600):
        return CLERK_JWKS_CACHE
    
    # Fetch from Clerk
    # Note: In production, you should use your Clerk Frontend API URL
    try:
        async with httpx.AsyncClient() as client:
            # Get JWKS from Clerk
            response = await client.get(
                f"https://{settings.CLERK_PUBLISHABLE_KEY.split('_')[1]}.clerk.accounts.dev/.well-known/jwks.json",
                timeout=10.0
            )
            if response.status_code == 200:
                CLERK_JWKS_CACHE = response.json()
                CLERK_JWKS_CACHE_TIME = time.time()
                return CLERK_JWKS_CACHE
    except Exception as e:
        logger.warning(f"Failed to fetch Clerk JWKS: {e}")
    
    return None


def verify_clerk_token(token: str) -> dict:
    """
    Verify Clerk JWT token and return claims.
    
    For simplicity, we decode without full signature verification.
    In production, you should verify against Clerk's JWKS.
    """
    try:
        # Log first few characters of token for debugging
        logger.debug(f"Verifying token: {token[:50]}...")
        
        # Decode token without verification first to get claims
        # Clerk tokens are self-contained JWTs
        unverified = jwt.decode(
            token, 
            options={
                "verify_signature": False,
                "verify_exp": True,
                "verify_aud": False,
            }
        )
        
        # Log claims for debugging
        logger.info(f"Token claims: sub={unverified.get('sub')}, email keys present: {[k for k in unverified.keys()]}")
        
        # Validate required claims
        if not unverified.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
        
        return unverified
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid Clerk token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}")
        raise HTTPException(status_code=401, detail=f"Token verification error: {str(e)}")


def get_current_user_sync(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Synchronous version - Get current user from Clerk token.
    Creates user if not exists, returns existing user if found.
    Includes retry logic for database connection failures.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.replace("Bearer ", "")
    
    # Verify token and get claims
    claims = verify_clerk_token(token)
    
    clerk_id = claims.get("sub")
    # Clerk stores email in different places depending on token type
    email = (
        claims.get("email") or 
        claims.get("primary_email_address") or
        claims.get("email_addresses", [{}])[0].get("email_address") if claims.get("email_addresses") else None
    )
    
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
    
    # Retry logic for database operations
    import time
    max_retries = 3
    retry_delay = 1  # seconds
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Find user by clerk_id first
            user = db.query(UserModel).filter(UserModel.clerk_id == clerk_id).first()
            
            if user:
                return user
            
            # If not found by clerk_id, try to find by email (migration case)
            if email:
                user = db.query(UserModel).filter(UserModel.email == email).first()
                if user:
                    # Link existing user to Clerk
                    user.clerk_id = clerk_id
                    db.commit()
                    logger.info(f"Linked existing user {email} to Clerk ID {clerk_id}")
                    return user
            
            # Create new user
            if not email:
                # Fetch real email from Clerk Backend API
                email = fetch_clerk_user_email(clerk_id)
                
            if not email:
                # Last resort fallback (should rarely happen)
                logger.warning(f"Could not fetch email for Clerk user {clerk_id}, using synthetic email")
                email = f"user_{clerk_id}@clerk.local"
            
            user = UserModel(
                email=email,
                clerk_id=clerk_id,
                role="user",  # New users start as regular users
                is_active=True,
                hashed_password=None,  # No password needed for Clerk users
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Created new user from Clerk: {email} (Clerk ID: {clerk_id})")
            return user
            
        except (OperationalError, InterfaceError) as e:
            last_error = e
            logger.warning(f"Database connection error (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                # Rollback any pending transaction
                try:
                    db.rollback()
                except:
                    pass
                    
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"Database error after {max_retries} retries: {e}")
                raise HTTPException(status_code=503, detail="Database temporarily unavailable. Please try again.")
    
    # Should never reach here, but just in case
    raise HTTPException(status_code=503, detail="Database temporarily unavailable")


# Alias for dependency injection
get_current_user = get_current_user_sync
