import datetime
from flask_sqlalchemy import SQLAlchemy
from api.app import app, db


class AnsiblePlaybooks(db.Model):
    playbook_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playbook_name = db.Column(db.String, nullable=False)
    last_execution_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_execution_result = db.Column(db.String, nullable=False, default="Unknown")
    last_execution_duration = db.Column(db.Integer, nullable=False, default="Unknown")


class AnsibleRuns(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playbook_id = db.Column(db.Integer, db.ForeignKey('host_da_info.host_ip'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    result = db.Column(db.String, nullable=False, default="Unknown")
    duration = db.Column(db.Integer, nullable=False)
