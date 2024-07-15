import datetime
from flask_sqlalchemy import SQLAlchemy
from api.app import db
from sqlalchemy import Table, Column, Integer, String


class AnsiblePlaybooks(db.Model):
    playbook_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playbook_name = db.Column(db.String, nullable=False)
    playbook_path = db.Column(db.String, nullable=False)


class AnsibleRuns(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playbook_id = db.Column(db.Integer, db.ForeignKey('ansible_playbooks.playbook_id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    result = db.Column(db.String, nullable=False, default="Unknown")
    duration = db.Column(db.Integer, nullable=False)
