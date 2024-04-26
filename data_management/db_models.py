import datetime
import logging

from api.app import db
from configuration import config


class Host(db.Model):
    # change id to IP?
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_ip = db.Column(db.String, unique=True, nullable=False)
    host_ips = db.relationship('HostIps', backref='host', lazy='selectin')
    host_devices = db.relationship('HostDevices', backref='host', lazy='selectin')


class HostStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'), nullable=False)
    state = db.Column(db.Boolean, default=False)


class HostFacts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'), nullable=False)
    hostname = db.Column(db.String, nullable=False, default="Unknown")
    sync_timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    kernel = db.Column(db.String, nullable=False, default="Unknown")
    distro = db.Column(db.String, nullable=False, default="Unknown")
    user_count = db.Column(db.Integer, nullable=False, default=0)


class HostUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'))
    user = db.Column(db.String)


class HostIps(db.Model):
    ip = db.Column(db.String, nullable=False, unique=True, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'), nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    is_listed = db.Column(db.String, nullable=False, default=False)
    listed_on = db.Column(db.String, nullable=False, default="")


class HostDevices(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'))
    name = db.Column(db.String, nullable=False, default="Unknown")
    mountpoint = db.Column(db.String, nullable=False, default="Unknown")
    size = db.Column(db.String, nullable=False, default="Unknown")


class ExtensionRoutes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, default="Unknown")
    route = db.Column(db.String, nullable=False, default="Unknown")


def init_db_tables_with_data():
    logging.info("Initializing DB entries from source file")
    db.create_all()
    hosts = config.ConfigManager().ip_list
    for ip in hosts:
        exists = Host.query.filter_by(host_ip=ip).first()
        if not exists:
            hst = Host(host_ip=ip)
            db.session.add(hst)
            db.session.commit()
            host_facts = HostFacts(host_id=hst.id)
            db.session.add(host_facts)
    db.session.commit()
    logging.info("DB import done...")
