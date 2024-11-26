import logging
import time
from datetime import datetime

from api.app import db, app
from configuration import logger
from connectors.connector import Connection
from connectors.os.remote_data_processor import *
from data_management.db_models import (
    HostFacts,
    HostIps,
    HostDevices,
    HostStatus,
    Host,
    IpsHosts,
    RblHosts,
)
from host_management.rbl_checker import check_rbl


def save_device_data():
    with app.app_context():
        devices = Connection().get_disk_devices()  # get_disk_devices_status()
        for host, device_list in devices.items():
            for device_details in device_list.get("disk_devices"):
                logging.debug(
                    f"#SYNC# Device of {host} found: {device_details.get('device')}"
                )
                host_id = Host.query.filter_by(host_ip=host).first()
                device_entry = (
                    HostDevices.query.filter_by(name=device_details.get("device"))
                    .filter_by(host_id=host_id.id)
                    .first()
                )
                if device_entry is None:
                    device_entry = HostDevices(
                        name=device_details.get("device"),
                        host_id=host_id.id,
                        mountpoint=device_details.get("mountpoint"),
                        size=device_details.get("size"),
                    )
                    db.session.add(device_entry)
        db.session.commit()


def save_ips_data():
    with app.app_context():
        ips = get_all_ips_on_host()
        for host, ip_list in ips.items():
            for ip in ip_list["ips"]:
                logging.debug(f"SYNC | IP found: {ip}")
                if "Error" in ip:
                    ip = host
                ip_entry = HostIps.query.filter_by(ip=ip).first()
                if ip_entry is None:
                    host_id = Host.query.filter_by(host_ip=host).first()
                    ip_entry = HostIps(
                        ip=ip, host_id=host_id.id, is_private=is_private_ip(ip)
                    )
                    db.session.add(ip_entry)
        db.session.commit()


def save_facts(facts):
    with app.app_context():
        for ip, host_details in facts.items():
            host = Host.query.filter_by(host_ip=ip).first()
            host_facts = HostFacts.query.filter_by(host_id=host.id).first()
            if not host_facts:
                continue
            logging.debug(f"host facts {host_facts}")
            host_facts.hostname = host_details.get("hostname")
            host_facts.kernel = host_details.get("kernel")
            host_facts.distro = host_details.get("distro")
            host_facts.user_count = host_details.get("users")
            host_facts.sync_timestamp = datetime.now()
            db.session.add(host_facts)
        db.session.commit()


def sync_all():
    logger.info("Executing sync up with hosts...")
    facts = Connection().host_facts()
    healthcheck_service()
    save_facts(facts)
    save_ips_data()
    save_device_data()
    # asyncio.run(sync_rbl())
    logger.info("Sync up done")
    return 0


async def sync_rbl():
    logging.info("Starting scheduled RBL sync")
    with app.app_context():
        ips = get_all_ips_on_host()
        # print("sync_rbl - ips", ips)
        for host, ip_list in ips.items():
            # print("IP", host)
            results_rbl = check_rbl(host)
            await save_rbls_to_db(host, results_rbl)
    logging.info("RBL sync done")


async def save_rbls_to_db(host, results_rbl):
    for item in results_rbl:
        for key, value in item.items():
            if value == 1:
                IpsHosts.query.filter_by()
                print("RBL", key)
                rblHosts = RblHosts.query.filter_by(orgName=key).first()
                print("rblHosts: ", rblHosts)
                hostIps = HostIps.query.filter_by(ip=host).first()
                print("hostIps: ", hostIps)
                ipsHosts = IpsHosts(host_ip_ip=hostIps.ip, rbl_ip_id=rblHosts.id)
                db.session.add(ipsHosts)
                db.session.commit()


def healthcheck_service():
    def run_healthcheck():
        data = (
            Connection().healthcheck()
        )  # Assumes this returns a dictionary {ip: status}

        with app.app_context():  # Ensure the correct app context
            for ip, output in data.items():
                print(f"Checking IP: {ip}, Status: {output}")

                # Join HostStatus and HostIps based on the IP address
                host_status = (
                    db.session.query(HostStatus)
                    .join(HostIps, HostStatus.host_id == HostIps.host_id)
                    .filter(HostIps.ip == ip)  # Match based on IP
                    .first()
                )

                if host_status:  # If a corresponding HostStatus entry exists
                    # Update state based on output
                    host_status.state = bool(output)
                    db.session.commit()
                else:
                    print(f"No host status found for IP: {ip}")

    # if host_status:
    # Update the state in the HostStatus model
    #    host_status.state = new_state
    #    db.session.commit()
    # else:
    # Handle the case where the HostStatus record does not exist for the specified host_id
    #    pass
    time.sleep(config.check_interval)


# healthcheck_service()
