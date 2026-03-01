"""
Tests for token exchange endpoint and database models
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func

from auth.auth_models import TokenBlacklist, UserSession
from web.app import app, db


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


class TestAuthExchangeEndpoint:
    """Test /auth/exchange endpoint"""
    
    def test_exchange_without_session_returns_401(self, client):
        """Test that exchange without session returns 401"""
        response = client.post('/auth/exchange')
        assert response.status_code == 401
        assert "Not authenticated" in response.json["error"]
    
    def test_exchange_with_valid_session(self, client):
        """Test successful token exchange with valid session"""
        with client:
            # Simulate authenticated session
            with client.session_transaction() as sess:
                sess["user_claims"] = {
                    "sub": "user-123",
                    "preferred_username": "testuser",
                    "email": "test@example.com",
                    "name": "Test User"
                }
            
            response = client.post('/auth/exchange')
            assert response.status_code == 200
            
            data = response.json
            assert "token" in data
            assert data["token_type"] == "Bearer"
            assert data["expires_in"] == 24 * 3600  # 24 hours
            assert len(data["token"]) > 0  # Should be a valid JWT
    
    def test_exchange_returns_valid_jwt(self, client):
        """Test that exchanged token is a valid JWT"""
        import jwt
        
        with client:
            with client.session_transaction() as sess:
                sess["user_claims"] = {
                    "sub": "user-123",
                    "preferred_username": "testuser",
                    "email": "test@example.com"
                }
            
            response = client.post('/auth/exchange')
            token = response.json["token"]
            
            # Should be decodable (without verification for now)
            decoded = jwt.decode(token, options={"verify_signature": False})
            assert decoded["preferred_username"] == "testuser"
            assert decoded["sub"] == "user-123"


class TestTokenBlacklistModel:
    """Test TokenBlacklist database model"""
    
    def test_create_blacklist_entry(self, client):
        """Test creating a token blacklist entry"""
        with app.app_context():
            now = datetime.now(timezone.utc)
            entry = TokenBlacklist(
                jti="token-id-123",
                user_id="user-123",
                username="testuser",
                revoked_at=now,
                expires_at=now + timedelta(hours=24),
                reason="logout"
            )
            db.session.add(entry)
            db.session.commit()
            
            # Verify it was saved
            found = TokenBlacklist.query.filter_by(jti="token-id-123").first()
            assert found is not None
            assert found.username == "testuser"
            assert found.reason == "logout"
    
    def test_blacklist_unique_jti(self, client):
        """Test that JTI must be unique"""
        with app.app_context():
            now = datetime.now(timezone.utc)
            
            entry1 = TokenBlacklist(
                jti="duplicate-id",
                user_id="user-123",
                username="testuser",
                revoked_at=now,
                expires_at=now + timedelta(hours=24)
            )
            db.session.add(entry1)
            db.session.commit()
            
            # Try to add duplicate
            entry2 = TokenBlacklist(
                jti="duplicate-id",
                user_id="user-456",
                username="otheruser",
                revoked_at=now,
                expires_at=now + timedelta(hours=24)
            )
            db.session.add(entry2)
            
            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()
    
    def test_blacklist_query_by_user(self, client):
        """Test querying blacklist by user"""
        with app.app_context():
            now = datetime.now(timezone.utc)
            
            # Add multiple entries for same user
            for i in range(3):
                entry = TokenBlacklist(
                    jti=f"token-{i}",
                    user_id="user-123",
                    username="testuser",
                    revoked_at=now,
                    expires_at=now + timedelta(hours=24)
                )
                db.session.add(entry)
            
            db.session.commit()
            
            # Query by user
            entries = TokenBlacklist.query.filter_by(user_id="user-123").all()
            assert len(entries) == 3
            assert all(e.username == "testuser" for e in entries)


class TestUserSessionModel:
    """Test UserSession database model"""
    
    def test_create_session_entry(self, client):
        """Test creating a user session entry"""
        with app.app_context():
            now = datetime.now(timezone.utc)
            session = UserSession(
                user_id="user-123",
                username="testuser",
                jti="session-jti-123",
                created_at=now,
                expires_at=now + timedelta(hours=24),
                ip_address="192.168.1.1",
                user_agent="Mozilla/5.0..."
            )
            db.session.add(session)
            db.session.commit()
            
            # Verify it was saved
            found = UserSession.query.filter_by(jti="session-jti-123").first()
            assert found is not None
            assert found.username == "testuser"
            assert found.ip_address == "192.168.1.1"
            assert found.is_active is True
    
    def test_session_deactivate(self, client):
        """Test deactivating a session"""
        with app.app_context():
            now = datetime.now(timezone.utc)
            session = UserSession(
                user_id="user-123",
                username="testuser",
                jti="session-jti-456",
                created_at=now,
                expires_at=now + timedelta(hours=24)
            )
            db.session.add(session)
            db.session.commit()
            
            # Deactivate
            session.is_active = False
            db.session.commit()
            
            # Verify
            found = UserSession.query.filter_by(jti="session-jti-456").first()
            assert found.is_active is False
    
    def test_query_active_sessions(self, client):
        """Test querying active sessions for a user"""
        with app.app_context():
            now = datetime.now(timezone.utc)
            
            # Add active and inactive sessions
            for i, is_active in enumerate([True, True, False]):
                session = UserSession(
                    user_id="user-123",
                    username="testuser",
                    jti=f"session-{i}",
                    created_at=now,
                    expires_at=now + timedelta(hours=24),
                    is_active=is_active
                )
                db.session.add(session)
            
            db.session.commit()
            
            # Query active sessions
            active = UserSession.query.filter_by(
                user_id="user-123",
                is_active=True
            ).all()
            
            assert len(active) == 2
    
    def test_logout_all_devices(self, client):
        """Test deactivating all sessions for a user"""
        with app.app_context():
            now = datetime.now(timezone.utc)
            
            # Create multiple sessions
            for i in range(3):
                session = UserSession(
                    user_id="user-123",
                    username="testuser",
                    jti=f"session-{i}",
                    created_at=now,
                    expires_at=now + timedelta(hours=24)
                )
                db.session.add(session)
            
            db.session.commit()
            
            # Logout from all devices
            UserSession.query.filter_by(user_id="user-123").update({"is_active": False})
            db.session.commit()
            
            # Verify all are inactive
            sessions = UserSession.query.filter_by(user_id="user-123").all()
            assert all(not s.is_active for s in sessions)


class TestTokenBlacklistIntegration:
    """Integration tests for token blacklisting"""
    
    def test_is_token_blacklisted(self, client):
        """Test checking if a token is blacklisted"""
        with app.app_context():
            now = datetime.now(timezone.utc)
            
            # Add blacklist entry
            entry = TokenBlacklist(
                jti="blacklisted-token",
                user_id="user-123",
                username="testuser",
                revoked_at=now,
                expires_at=now + timedelta(hours=24)
            )
            db.session.add(entry)
            db.session.commit()
            
            # Check if blacklisted
            found = TokenBlacklist.query.filter_by(jti="blacklisted-token").first()
            assert found is not None
            
            # Normal token should not be found
            not_found = TokenBlacklist.query.filter_by(jti="valid-token").first()
            assert not_found is None
    
    def test_cleanup_expired_blacklist_entries(self, client):
        """Test removing expired entries from blacklist"""
        with app.app_context():
            now = datetime.now(timezone.utc)
            
            # Add expired and valid entries
            expired = TokenBlacklist(
                jti="expired-token",
                user_id="user-123",
                username="testuser",
                revoked_at=now - timedelta(hours=25),
                expires_at=now - timedelta(hours=1)  # Expired
            )
            valid = TokenBlacklist(
                jti="valid-token",
                user_id="user-123",
                username="testuser",
                revoked_at=now,
                expires_at=now + timedelta(hours=24)
            )
            db.session.add(expired)
            db.session.add(valid)
            db.session.commit()
            
            # Query for non-expired entries
            valid_entries = TokenBlacklist.query.filter(
                TokenBlacklist.expires_at > now
            ).all()
            
            assert len(valid_entries) == 1
            assert valid_entries[0].jti == "valid-token"
