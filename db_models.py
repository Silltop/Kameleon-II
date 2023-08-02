from flask_init import db


class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    host_ip = db.Column(db.String, unique=True, nullable=False)


class HostFacts(db.Model):
    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'))
    hostname = db.Column(db.String, unique=True, nullable=False)
    sync_timestamp = db.Column(db.DateTime)
    kernel = db.Column(db.String, nullable=False)
    distro = db.Column(db.String, nullable=False)


class HostUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
