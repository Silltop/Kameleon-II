from re import sub
from web.app import db
from datetime import datetime
import json


class HostDAInfo(db.Model):
    host_ip = db.Column(db.String, primary_key=True)
    hostname = db.Column(db.String, nullable=False)


class DAUserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(
        db.Integer, db.ForeignKey("host_da_info.host_ip"), nullable=False
    )
    user_name = db.Column(db.String, nullable=False, default="Unknown")
    email = db.Column(db.String, nullable=False, default="Unknown")
    is_suspended = db.Column(db.Boolean)
    package = db.Column(db.String, nullable=False, default="Unknown")
    quota = db.Column(db.String, nullable=False, default="Unknown")


class Domains(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("da_user_details.id"), nullable=False)
    domain_name = db.Column(db.String, nullable=False, default="Unknown")
    subdomain_count = db.Column(db.Integer, nullable=False, default=0)
    dns_a = db.Column(db.String, nullable=False, default="Unknown")
    dns_mx = db.Column(db.String, nullable=False, default="Unknown")
    dns_ns = db.Column(db.String, nullable=False, default="Unknown")


class DAUserDataSnapshot(db.Model):
    """Historical snapshot of DirectAdmin user data"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    snapshot_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DAUserDataSnapshot {self.snapshot_timestamp}>'


class DAAppsVersionSnapshot(db.Model):
    """Historical snapshot of DirectAdmin apps versions"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    snapshot_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DAAppsVersionSnapshot {self.snapshot_timestamp}>'


class DASuspendedUsersSnapshot(db.Model):
    """Historical snapshot of suspended DirectAdmin users"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    snapshot_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DASuspendedUsersSnapshot {self.snapshot_timestamp}>'


class DAUserEmailsSnapshot(db.Model):
    """Historical snapshot of DirectAdmin user emails"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    snapshot_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DAUserEmailsSnapshot {self.snapshot_timestamp}>'


class DAUserWebsitesSnapshot(db.Model):
    """Historical snapshot of DirectAdmin user websites/domains"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    snapshot_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DAUserWebsitesSnapshot {self.snapshot_timestamp}>'


class DAUserDomainsDNSSnapshot(db.Model):
    """Historical snapshot of DirectAdmin user domains DNS information"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    snapshot_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DAUserDomainsDNSSnapshot {self.snapshot_timestamp}>'

