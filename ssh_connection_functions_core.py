"""
Notes:
    1. I tried paramiko but seems like there is a problem with private key when trying to connect at once to multiple hosts.
    When I tried to connect to only one connection was fine, but otherwise package was returning Unauthorized.
    2. Parallel-ssh also seem to have a weird issue with pkeys, this lib is only able to authenticate using ed25519 key, weird.
    3. Of course, I tested, locally keys using ssh -i command.
"""
import paramiko
from pint import UnitRegistry

import config
from utils import get_managed_hosts, get_hosts_only
from pssh.clients import ParallelSSHClient


def execute_command(command):
    # hosts, users = get_managed_hosts()
    hosts = get_hosts_only()
    client = ParallelSSHClient(hosts, user='root', pkey='/home/patryk/PycharmProjects/Kameleon-II/env/id_ed')
    output = client.run_command(command)
    response_dict = {}
    for host_out in output:
        new_output = []
        for line in host_out.stdout:
            new_output.append(line.strip("\n"))
        response_dict[host_out.host] = new_output
    # print(response_dict)
    return response_dict


def get_linux_distro():
    results = execute_command("cat /etc/*-release | awk -F '=' '/^PRETTY_NAME/{print $2}'")
    return results


def get_disk_devices_status():
    results = execute_command("df -h | awk 'NR>1 {print $1, $2, $3, $5}'")
    results_to_return = {}
    for host, values in results.items():
        new_list = []
        for list_entry in values:
            device, size, used, percentage = list_entry.split(" ")
            new_list.append({'device': device, 'size': size, 'used': used, 'percentage': percentage.strip("%\n")})
        results_to_return[host] = new_list
    return results_to_return


def get_disk_usage_per_user():
    results = execute_command("du -sh /home/* | sort -hr | awk '{print $2, $1}'")
    return results


def get_hostnames():
    results = execute_command("hostname")
    hostnames = {}
    for host, res in results.items():
        hostnames[host] = res[0].strip("\n")
    return hostnames


def read_remote_file(remote_file_path):
    pass

