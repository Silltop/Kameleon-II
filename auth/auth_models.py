"""
Database models for authentication and token management.
Tracks blacklisted tokens for immediate revocation.
"""

import datetime
from sqlalchemy.orm import Mapped

from web.app import db


class TokenBlacklist(db.Model):
    """
    Tracks revoked/blacklisted tokens to enable immediate invalidation.
    Useful for logout, token rotation, or permission changes.
    """
    
    __tablename__ = "token_blacklist"
    
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti: Mapped[str] = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id: Mapped[str] = db.Column(db.String(255), nullable=False, index=True)
    username: Mapped[str] = db.Column(db.String(255), nullable=False)
    revoked_at: Mapped[datetime.datetime] = db.Column(
        db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    expires_at: Mapped[datetime.datetime] = db.Column(db.DateTime, nullable=False)
    reason: Mapped[str] = db.Column(db.String(255), nullable=True)
    
    def __repr__(self) -> str:
        return f"<TokenBlacklist {self.username}:{self.jti[:8]}...>"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "jti": self.jti,
            "user_id": self.user_id,
            "username": self.username,
            "revoked_at": self.revoked_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "reason": self.reason
        }


class UserSession(db.Model):
    """
    Tracks active user sessions for audit and security.
    Useful for device tracking, logout-all-devices, and security events.
    """
    
    __tablename__ = "user_session"
    
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = db.Column(db.String(255), nullable=False, index=True)
    username: Mapped[str] = db.Column(db.String(255), nullable=False)
    jti: Mapped[str] = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = db.Column(
        db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False
    )
    expires_at: Mapped[datetime.datetime] = db.Column(db.DateTime, nullable=False)
    ip_address: Mapped[str] = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    user_agent: Mapped[str] = db.Column(db.String(255), nullable=True)
    is_active: Mapped[bool] = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self) -> str:
        return f"<UserSession {self.username}:{self.jti[:8]}...>"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "jti": self.jti,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "ip_address": self.ip_address,
            "is_active": self.is_active
        }
