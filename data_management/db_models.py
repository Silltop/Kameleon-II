import datetime
import logging

from api.app import db
from host_management.utils import get_hosts_only, get_rbls_from_json


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

class IpsHosts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_ip_ip = db.Column(db.String, db.ForeignKey('host_ips.ip'), nullable=False)
    rbl_ip_id = db.Column(db.Integer, db.ForeignKey('rbl_hosts.id'), nullable=False)

class RblHosts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orgName = db.Column(db.String, nullable=False, default="")
    url = db.Column(db.String, nullable=False, default="")
    use = db.Column(db.Boolean, nullable=False, default="")


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
    hosts = get_hosts_only()
    for ip in hosts:
        exists = Host.query.filter_by(host_ip=ip).first()
        if not exists:
            hst = Host(host_ip=ip)
            db.session.add(hst)
            db.session.commit()
            host_facts = HostFacts(host_id=hst.id)
            db.session.add(host_facts)

    rbls = get_rbls_from_json()
    for entry in rbls:
        rblHosts = RblHosts(orgName=entry["NAME"], url=entry["URL"], use=True)
        db.session.add(rblHosts)
        db.session.commit()

    db.session.commit()
    logging.info("DB import done...")
