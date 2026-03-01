"""
Tests for Option B: Backend-controlled JWT token exchange
Tests custom JWT generation, validation, and token blacklist
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest

from auth.jwt_middleware import CustomJWTManager, extract_token_from_header, require_api_auth, get_jwt_claims
from auth.auth_models import TokenBlacklist, UserSession
from web.app import app


class TestCustomJWTManager:
    """Test custom JWT token management"""
    
    @pytest.fixture
    def jwt_manager(self):
        return CustomJWTManager(secret_key="test-secret", token_lifetime_hours=24)
    
    @pytest.fixture
    def sample_claims(self):
        return {
            "sub": "user-123",
            "preferred_username": "testuser",
            "email": "test@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User"
        }
    
    def test_generate_token(self, jwt_manager, sample_claims):
        """Test custom JWT token generation"""
        token = jwt_manager.generate_token(sample_claims)
        
        assert isinstance(token, str)
        assert token.count(".") == 2  # JWT structure: header.payload.signature
        
        # Decode and verify payload
        decoded = jwt.decode(token, jwt_manager.secret_key, algorithms=["HS256"])
        assert decoded["sub"] == "user-123"
        assert decoded["preferred_username"] == "testuser"
        assert decoded["type"] == "api"
        assert "jti" in decoded
    
    def test_token_contains_all_user_claims(self, jwt_manager, sample_claims):
        """Test that generated token includes all user information"""
        token = jwt_manager.generate_token(sample_claims)
        decoded = jwt.decode(token, jwt_manager.secret_key, algorithms=["HS256"])
        
        assert decoded["email"] == "test@example.com"
        assert decoded["name"] == "Test User"
        assert decoded["given_name"] == "Test"
        assert decoded["family_name"] == "User"
    
    def test_token_expiration(self, jwt_manager, sample_claims):
        """Test that token has correct expiration"""
        token = jwt_manager.generate_token(sample_claims)
        decoded = jwt.decode(token, jwt_manager.secret_key, algorithms=["HS256"])
        
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        iat_time = datetime.fromtimestamp(decoded["iat"], tz=timezone.utc)
        
        # Token should be valid for approximately 24 hours
        delta = exp_time - iat_time
        assert 23 <= delta.total_seconds() / 3600 <= 25  # Allow 1 hour tolerance
    
    def test_validate_token_success(self, jwt_manager, sample_claims):
        """Test successful token validation"""
        token = jwt_manager.generate_token(sample_claims)
        decoded = jwt_manager.validate_token(token)
        
        assert decoded["sub"] == "user-123"
        assert decoded["preferred_username"] == "testuser"
    
    def test_validate_token_invalid(self, jwt_manager):
        """Test validation of invalid token"""
        from jwt import InvalidTokenError
        
        with pytest.raises(InvalidTokenError):
            jwt_manager.validate_token("invalid.token.here")
    
    def test_validate_token_expired(self, jwt_manager, sample_claims):
        """Test validation of expired token"""
        from jwt import InvalidTokenError
        
        # Manually create an expired token
        now = datetime.now(timezone.utc)
        payload = {
            "sub": sample_claims["sub"],
            "preferred_username": sample_claims["preferred_username"],
            "exp": int((now - timedelta(hours=1)).timestamp()),
            "iat": int(now.timestamp()),
            "type": "api"
        }
        expired_token = jwt.encode(payload, jwt_manager.secret_key, algorithm="HS256")
        
        with pytest.raises(InvalidTokenError, match="expired"):
            jwt_manager.validate_token(expired_token)
    
    def test_validate_token_wrong_type(self, jwt_manager):
        """Test validation of token with wrong type"""
        from jwt import InvalidTokenError
        
        payload = {
            "sub": "user-123",
            "type": "session",  # Wrong type
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp())
        }
        token = jwt.encode(payload, jwt_manager.secret_key, algorithm="HS256")
        
        with pytest.raises(InvalidTokenError, match="Invalid token type"):
            jwt_manager.validate_token(token)
    
    def test_different_instances_can_validate_same_token(self):
        """Test that different JWT manager instances can validate tokens if using same secret"""
        claims = {"sub": "user-123", "preferred_username": "testuser", "email": "test@example.com"}
        
        manager1 = CustomJWTManager(secret_key="shared-secret", token_lifetime_hours=24)
        manager2 = CustomJWTManager(secret_key="shared-secret", token_lifetime_hours=24)
        
        token = manager1.generate_token(claims)
        decoded = manager2.validate_token(token)
        
        assert decoded["sub"] == "user-123"


class TestTokenExtraction:
    """Test token extraction from headers"""
    
    def test_extract_valid_token(self):
        """Test extraction of valid Authorization header"""
        with app.test_request_context(headers={"Authorization": "Bearer test-token-123"}):
            token = extract_token_from_header()
            assert token == "test-token-123"
    
    def test_extract_missing_header(self):
        """Test extraction when header is missing"""
        with app.test_request_context():
            token = extract_token_from_header()
            assert token is None
    
    def test_extract_invalid_header_format(self):
        """Test extraction with invalid header format"""
        with app.test_request_context(headers={"Authorization": "InvalidFormat token"}):
            token = extract_token_from_header()
            assert token is None
    
    def test_extract_with_case_sensitive(self):
        """Test that Bearer is case sensitive"""
        with app.test_request_context(headers={"Authorization": "bearer test-token"}):
            token = extract_token_from_header()
            assert token is None  # Should not match lowercase 'bearer'


class TestAPIAuthDecorator:
    """Test API authentication decorator"""
    
    @pytest.fixture
    def jwt_manager(self):
        return CustomJWTManager(secret_key="test-secret")
    
    @pytest.fixture
    def valid_token(self, jwt_manager):
        claims = {
            "sub": "user-123",
            "preferred_username": "testuser",
            "email": "test@example.com"
        }
        return jwt_manager.generate_token(claims)
    
    def test_missing_token_returns_401(self, jwt_manager):
        """Test that missing token returns 401"""
        @require_api_auth(jwt_manager)
        def protected_route():
            return {"message": "success"}
        
        with app.test_request_context():
            response = protected_route()
            assert response[1] == 401
            assert "Missing Authorization header" in response[0]["error"]
    
    def test_invalid_token_returns_401(self, jwt_manager):
        """Test that invalid token returns 401"""
        @require_api_auth(jwt_manager)
        def protected_route():
            return {"message": "success"}
        
        with app.test_request_context(headers={"Authorization": "Bearer invalid-token"}):
            response = protected_route()
            assert response[1] == 401
    
    def test_valid_token_allows_access(self, jwt_manager, valid_token):
        """Test that valid token allows access"""
        @require_api_auth(jwt_manager)
        def protected_route():
            claims = get_jwt_claims()
            return {"message": f"Hello {claims['preferred_username']}"}
        
        with app.test_request_context(headers={"Authorization": f"Bearer {valid_token}"}):
            result = protected_route()
            assert result[0]["message"] == "Hello testuser"
    
    def test_claims_available_in_route(self, jwt_manager, valid_token):
        """Test that JWT claims are available in the route handler"""
        @require_api_auth(jwt_manager)
        def protected_route():
            claims = get_jwt_claims()
            return {
                "user_id": claims["sub"],
                "username": claims["preferred_username"],
                "email": claims["email"]
            }
        
        with app.test_request_context(headers={"Authorization": f"Bearer {valid_token}"}):
            result = protected_route()
            assert result["user_id"] == "user-123"
            assert result["username"] == "testuser"
            assert result["email"] == "test@example.com"


class TestGetJWSClaims:
    """Test get_jwt_claims function"""
    
    def test_get_claims_outside_protected_route_raises_error(self):
        """Test that accessing claims outside protected route raises error"""
        with app.test_request_context():
            with pytest.raises(RuntimeError, match="JWT claims not found"):
                get_jwt_claims()
    
    def test_get_claims_with_manual_assignment(self):
        """Test accessing claims when manually assigned"""
        with app.test_request_context():
            from flask import request
            request.jwt_claims = {"sub": "user-123", "name": "Test"}
            
            claims = get_jwt_claims()
            assert claims["sub"] == "user-123"


@pytest.fixture(scope="session", autouse=True)
def setup_test_app():
    """Setup Flask app for testing"""
    app.config["TESTING"] = True


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    return app.test_client()
