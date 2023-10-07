import logging
from datetime import datetime
import schedule
from db_models import HostFacts, HostIps
from flask_init import db, app
from ssh_connection_functions_core import *


def gather_facts():
    hostnames = get_hostnames()
    kernels = get_linux_kernel_version()
    devices = get_disk_devices_names()
    distro = get_linux_distro()
    users = get_user_count()
    dicts = [hostnames, kernels, devices, distro, users]
    combined_dict = {}
    for d in dicts:
        for key, value in d.items():
            if key in combined_dict:
                # If the key already exists in the combined dictionary, merge the nested dictionaries
                combined_dict[key].update(value)
            else:
                # If the key does not exist, add it to the combined dictionary
                combined_dict[key] = value
    return combined_dict


def save_ips_data():
    with app.app_context():
        ips = get_all_ips_on_host()
        for host, ip_list in ips.items():
            for ip in ip_list['ips']:
                print(type(ip))
                logging.debug(f"SYNC | IP found: {ip}")
                if 'Error' in ip:
                    ip = host
                ip_entry = HostIps.query.filter_by(ip=ip).first()
                if ip_entry is None:
                    host_id = Host.query.filter_by(host_ip=host).first()
                    ip_entry = HostIps(ip=ip, host_id=host_id.id)
                    db.session.add(ip_entry)
        db.session.commit()


def save_facts(facts):
    with app.app_context():
        for ip, host_details in facts.items():
            host = Host.query.filter_by(host_ip=ip).first()
            host_facts = HostFacts.query.filter_by(host_id=host.id).first()
            if host_facts:
                logging.debug(f"host facts {host_facts}")
                host_facts.hostname = host_details.get("hostname")
                host_facts.kernel = host_details.get("kernel")
                host_facts.distro = host_details.get("distro")
                host_facts.sync_timestamp = datetime.utcnow()
                db.session.add(host_facts)
        db.session.commit()



def sync_all():
    logging.info("Executing sync up with hosts...")
    facts = gather_facts()
    save_facts(facts)
    save_ips_data()

    logging.info("Sync up done")
    return 0
