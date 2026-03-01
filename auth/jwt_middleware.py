"""
Custom JWT middleware for Option B: Backend-controlled token exchange
Backend generates tokens from Keycloak claims, frontend uses custom JWT for API calls.
"""

import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Dict, Optional, Tuple
from uuid import uuid4

import jwt
from flask import jsonify, request
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError

logger = logging.getLogger(__name__)


class CustomJWTManager:
    """
    Manages custom JWT tokens generated from Keycloak claims.
    Backend owns token generation and lifetime management.
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", token_lifetime_hours: int = 24):
        """
        Initialize JWT manager.
        
        Args:
            secret_key: Secret key for signing tokens (Flask app.secret_key)
            algorithm: JWT algorithm (default HS256)
            token_lifetime_hours: Token validity period in hours
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_lifetime_hours = token_lifetime_hours
    
    def generate_token(self, user_claims: Dict) -> str:
        """
        Generate a custom JWT from Keycloak user claims.
        
        Args:
            user_claims: Claims from Keycloak ID token
            
        Returns:
            Signed JWT token
        """
        now = datetime.now(timezone.utc)
        
        payload = {
            "sub": user_claims.get("sub"),  # User ID
            "preferred_username": user_claims.get("preferred_username"),
            "email": user_claims.get("email"),
            "name": user_claims.get("name"),
            "given_name": user_claims.get("given_name"),
            "family_name": user_claims.get("family_name"),
            # Custom fields
            "jti": str(uuid4()),  # JWT ID for token blacklist tracking
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=self.token_lifetime_hours)).timestamp()),
            "type": "api"  # Distinguish from Keycloak tokens
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Generated custom JWT for user: {payload.get('preferred_username')}")
        return token
    
    def validate_token(self, token: str) -> Dict:
        """
        Validate custom JWT and extract claims.
        
        Args:
            token: JWT token
            
        Returns:
            Decoded token claims
            
        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        try:
            claims = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            
            # Verify token type
            if claims.get("type") != "api":
                raise InvalidTokenError("Invalid token type")
            
            logger.debug(f"Token validated for user: {claims.get('preferred_username')}")
            return claims
            
        except ExpiredSignatureError:
            logger.warning("Token has expired")
            raise InvalidTokenError("Token has expired")
        except DecodeError as e:
            logger.warning(f"Token decode failed: {e}")
            raise InvalidTokenError(f"Invalid token: {e}")
        except jwt.InvalidTokenError as e:
            logger.error(f"Token validation failed: {e}")
            raise InvalidTokenError(f"Token validation failed: {e}")


def extract_token_from_header() -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Expected format: Authorization: Bearer <token>
    
    Returns:
        Token string or None if not found
    """
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        return None
    
    return auth_header[7:]  # Remove "Bearer " prefix


def require_api_auth(jwt_manager: CustomJWTManager):
    """
    Decorator to protect API endpoints with custom JWT authentication.
    
    Usage:
        @app.route("/api/protected")
        @require_api_auth(jwt_manager)
        def protected_endpoint():
            user = get_jwt_claims()
            return jsonify({"message": f"Hello {user['preferred_username']}"})
    
    Args:
        jwt_manager: CustomJWTManager instance
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract token from header
            token = extract_token_from_header()
            if not token:
                return jsonify({"error": "Missing Authorization header"}), 401
            
            # Validate token
            try:
                claims = jwt_manager.validate_token(token)
                # Store claims in request context for use in route handler
                request.jwt_claims = claims
                return f(*args, **kwargs)
            except InvalidTokenError as e:
                return jsonify({"error": str(e)}), 401
        
        return decorated_function
    return decorator


def get_jwt_claims() -> Dict:
    """
    Get JWT claims from the current request.
    
    Should be called within a route protected by @require_api_auth decorator.
    
    Returns:
        JWT claims dictionary
        
    Raises:
        RuntimeError: If called outside of protected route
    """
    if not hasattr(request, "jwt_claims"):
        raise RuntimeError("JWT claims not found in request context. "
                          "Ensure route is protected with @require_api_auth decorator.")
    return request.jwt_claims
