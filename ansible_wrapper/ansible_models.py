import datetime

from api.app import db


class AnsiblePlaybooks(db.Model):
    playbook_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playbook_name = db.Column(db.String, nullable=False)
    playbook_path = db.Column(db.String, nullable=False)


class AnsibleRuns(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playbook_id = db.Column(
        db.Integer, db.ForeignKey("ansible_playbooks.playbook_id"), nullable=False
    )
    start_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    result = db.Column(db.String, nullable=False, default="Unknown")
    end_time = db.Column(db.DateTime, nullable=True)
    # duration = db.Column(db.Integer, nullable=False)


class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playbook_id = db.Column(
        db.Integer, db.ForeignKey("ansible_playbooks.playbook_id"), nullable=False
    )
    ansible_run_id = db.Column(
        db.Integer, db.ForeignKey("ansible_runs.id"), nullable=False
    )
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<LogEntry {self.message}>"
