from flask_sqlalchemy import SQLAlchemy
from api.app import app, db


class HostDAInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hostname = db.Column(db.String, nullable=False)


class DAUserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('HostDAInfo.id'), nullable=False)
    user_name = db.Column(db.String, nullable=False, default="Unknown")
    email = db.Column(db.String, nullable=False, default="Unknown")
    is_suspended = db.Column(db.Boolean)
    package = db.Column(db.String, nullable=False, default="Unknown")
    quota = db.Column(db.String, nullable=False, default="Unknown")


class Domains(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('DAUserDetails.user_id'), nullable=False)
    domain_name = db.Column(db.String, nullable=False, default="Unknown")
    dns_a = db.Column(db.String, nullable=False, default="Unknown")
    dns_mx = db.Column(db.String, nullable=False, default="Unknown")
    dns_ns = db.Column(db.String, nullable=False, default="Unknown")
