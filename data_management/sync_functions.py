import logging
import time
from datetime import datetime

from configuration import config
from connectors import remote_data_processor
from data_management.db_models import HostFacts, HostIps, HostDevices, HostStatus, Host
from api.app import db, app
from connectors.remote_data_processor import *
from configuration import logger

def merge_list_of_dicts(dict_list: list):
    combined_dict = {}
    for d in dict_list:
        for key, value in d.items():
            combined_dict[key] = combined_dict.get(key, {})
            combined_dict[key].update(value)
    return combined_dict


def gather_facts():
    hostnames = parse_output_to_dict(execute_command('hostname'), 'hostname')
    kernels = parse_output_to_dict(execute_command('uname -r'), 'kernel')
    distro = parse_output_to_dict(
        execute_command("cat /etc/*-release | awk -F '=' '/^PRETTY_NAME/{print $2}' | tr -d '\"' "), 'distro')
    users = parse_output_to_dict(execute_command(
        "awk -F: '$6 ~ /^\/home/ { count++ } END { if (count > 0) print count; else print \"0\" }' /etc/passwd"),
        'users')
    dicts = [hostnames, kernels, distro, users]
    return merge_list_of_dicts(dicts)


def save_device_data():
    with app.app_context():
        devices = get_disk_devices_status()
        for host, device_list in devices.items():
            for device_details in device_list:
                logging.debug(f"SYNC | Device of {host} found: {device_details.get('device')}")
                host_id = Host.query.filter_by(host_ip=host).first()
                device_entry = HostDevices.query.filter_by(name=device_details.get('device')).filter_by(
                    host_id=host_id.id).first()
                if device_entry is None:
                    device_entry = HostDevices(name=device_details.get('device'), host_id=host_id.id,
                                               mountpoint=device_details.get('mountpoint'),
                                               size=device_details.get("size"))
                    db.session.add(device_entry)
        db.session.commit()


def save_ips_data():
    with app.app_context():
        ips = get_all_ips_on_host()
        for host, ip_list in ips.items():
            for ip in ip_list['ips']:
                logging.debug(f"SYNC | IP found: {ip}")
                if 'Error' in ip:
                    ip = host
                ip_entry = HostIps.query.filter_by(ip=ip).first()
                if ip_entry is None:
                    host_id = Host.query.filter_by(host_ip=host).first()
                    ip_entry = HostIps(ip=ip, host_id=host_id.id, is_private=is_private_ip(ip))
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
    facts = gather_facts()
    save_facts(facts)
    save_ips_data()
    save_device_data()
    logger.info("Sync up done")
    return 0


def healthcheck_service():
    # make it a thread
    data = remote_data_processor.execute_command("uptime")
    for ip, output in data.items():
        print(ip)
    host_status = HostStatus.query.filter_by(host_id=host_id_to_update).first()

    #if host_status:
        # Update the state in the HostStatus model
    #    host_status.state = new_state
    #    db.session.commit()
    #else:
        # Handle the case where the HostStatus record does not exist for the specified host_id
    #    pass
    time.sleep(config.check_interval)

#healthcheck_service()