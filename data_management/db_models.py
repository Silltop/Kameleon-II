import datetime
import logging

from sqlalchemy.orm import Mapped

from configuration import config
from host_management.rbl_checker import RblChecker
from web.app import db


class Host(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_ip: Mapped[str] = db.Column(db.String, unique=True, nullable=False)
    host_ips = db.relationship("HostIps", backref="host", lazy="selectin")
    host_devices = db.relationship("HostDevices", backref="host", lazy="selectin")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "host_ip": self.host_ip,
            "host_ips": [ip.to_dict() for ip in self.host_ips],
            "host_devices": [device.to_dict() for device in self.host_devices]
        }


class HostStatus(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("host.id"), nullable=False)
    state: Mapped[bool] = db.Column(db.Boolean, default=False)


class HostFacts(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("host.id"), nullable=False)
    hostname: Mapped[str] = db.Column(db.String, nullable=False, default="Unknown")
    sync_timestamp: Mapped[datetime.datetime] = db.Column(
        db.DateTime, default=datetime.datetime.now(datetime.timezone.utc)
    )
    kernel: Mapped[str] = db.Column(db.String, nullable=False, default="Unknown")
    distro: Mapped[str] = db.Column(db.String, nullable=False, default="Unknown")
    user_count: Mapped[int] = db.Column(db.Integer, nullable=False, default=0)
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "host_id": self.host_id,
            "hostname": self.hostname,
            "sync_timestamp": self.sync_timestamp.isoformat(),
            "kernel": self.kernel,
            "distro": self.distro,
            "user_count": self.user_count
        }

class HostUsers(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("host.id"))
    user: Mapped[str] = db.Column(db.String)


class HostIps(db.Model):
    ip: Mapped[str] = db.Column(db.String, nullable=False, unique=True, primary_key=True)
    host_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("host.id"), nullable=False)
    is_private: Mapped[bool] = db.Column(db.Boolean, default=False)
    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "host_id": self.host_id,
            "is_private": self.is_private
        }


class IpsHosts(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_ip_ip: Mapped[str] = db.Column(db.String, db.ForeignKey("host_ips.ip"), nullable=False)
    rbl_ip_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("rbl_hosts.id"), nullable=False)


class RblHosts(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orgName: Mapped[str] = db.Column(db.String, nullable=False, default="")
    url: Mapped[str] = db.Column(db.String, nullable=False, default="")
    use: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=True)


class HostDevices(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("host.id"))
    name: Mapped[str] = db.Column(db.String, nullable=False, default="Unknown")
    mountpoint: Mapped[str] = db.Column(db.String, nullable=False, default="Unknown")
    size: Mapped[str] = db.Column(db.String, nullable=False, default="Unknown")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "host_id": self.host_id,
            "name": self.name,
            "mountpoint": self.mountpoint,
            "size": self.size,
        }


class ExtensionRoutes(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    extension_name: Mapped[str] = db.Column(db.String, nullable=False, default="Unknown")
    route_name: Mapped[str] = db.Column(db.String, nullable=False, default="Unknown")
    route_endpoint: Mapped[str] = db.Column(db.String, nullable=False, default="Unknown")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "extension_name": self.extension_name,
            "route_name": self.route_name,
            "route_endpoint": self.route_endpoint,
        }


def init_db_tables_with_data() -> None:
    logging.info("Initializing DB entries from source file")
    db.create_all()
    hosts = config.ConfigManager().ip_list
    for ip in hosts:
        exists = Host.query.filter_by(host_ip=ip).first()
        if not exists:
            hst = Host(host_ip=ip)  # type: ignore
            db.session.add(hst)
            db.session.commit()
            host_facts = HostFacts(host_id=hst.id)  # type: ignore
            db.session.add(host_facts)

    rbls = RblChecker.get_rbls_from_json()
    for entry in rbls:
        rblHosts = RblHosts(orgName=entry["NAME"], url=entry["URL"], use=True)  # type: ignore
        db.session.add(rblHosts)
        db.session.commit()

    db.session.commit()
    logging.info("DB import done...")
