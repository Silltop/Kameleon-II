import datetime

from flask_init import db
from utils import get_hosts_only


class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_ip = db.Column(db.String, unique=True, nullable=False)


class HostFacts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'), nullable=False)
    hostname = db.Column(db.String, nullable=False, default="Unknown")
    sync_timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    kernel = db.Column(db.String, nullable=False, default="Unknown")
    distro = db.Column(db.String, nullable=False, default="Unknown")


class HostUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'))
    user = db.Column(db.String)


class HostDevices(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'))
    name = db.Column(db.String, nullable=False, default="Unknown")
    mountpoint = db.Column(db.String, nullable=False, default="Unknown")


def init_db_tables_with_data():
    db.create_all()
    hosts = get_hosts_only()
    for ip in hosts:
        exists = Host.query.filter_by(host_ip=ip).first()
        if not exists:
            hst = Host(host_ip=ip)
            db.session.add(hst)
            db.session.commit()
            print(hst.id)
            host_facts = HostFacts(host_id=hst.id)
            db.session.add(host_facts)
    db.session.commit()
