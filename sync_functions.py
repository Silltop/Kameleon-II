from datetime import datetime

import schedule

from db_models import HostFacts
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


def save_facts(facts):
    for ip, host_details in facts.items():
        host = Host.query.filter_by(host_ip=ip).all()

        host_facts = HostFacts.query.filter_by(host_id=host.id).first()
        if host_facts:
            host_facts.hostname = host_details.get("hostname")
            host_facts.kernel = host_details.get("kernel")
            host_facts.distro = host_details.get("distro")
            host_facts.sync_timestamp = datetime.utcnow()
    with app.app_context():
        db.session.commit()


def sync_all():
    facts = gather_facts()
    save_facts(facts)
    return 0



