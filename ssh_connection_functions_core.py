"""
Notes:
    1. I tried paramiko but seems like there is a problem with private key when trying to connect at once to multiple hosts.
    When I tried to connect to only one connection was fine, but otherwise package was returning Unauthorized.
    2. Parallel-ssh also seem to have a weird issue with pkeys, this lib is only able to authenticate using ed25519 key, weird.
    3. Of course, I tested, locally keys using ssh -i command.
"""
import ipaddress
from utils import get_managed_hosts, get_hosts_only
from pssh.clients import ParallelSSHClient


def execute_command(command):
    # hosts, users = get_managed_hosts()
    hosts = get_hosts_only()

    client = ParallelSSHClient(hosts, user='root', pkey='/home/patryk/PycharmProjects/Kameleon-II/env/id_ed', timeout=2, retry_delay=1, num_retries=3)
    output = client.run_command(command, stop_on_errors=False)
    response_dict = {}
    for host_out in output:
        print(host_out)
        new_output = []
        if host_out.exception is not None:
            print(host_out.exception)
            response_dict[host_out.host] = [str(host_out.exception)]
            continue
        for line in host_out.stdout:
            new_output.append(line.strip("\n"))
        for line in host_out.stderr:
            new_output.append(line.strip("\n"))
        response_dict[host_out.host] = new_output
    # print(response_dict)
    return response_dict


def get_linux_distro():
    results = execute_command("cat /etc/*-release | awk -F '=' '/^PRETTY_NAME/{print $2}'")
    distro = {host: {'distro': res[0].strip("\n")} for host, res in results.items()}
    return distro


def get_linux_kernel_version():
    results = execute_command("uname -r")
    versions = {host: {'kernel': res[0].strip("\n")} for host, res in results.items()}
    return versions


def get_disk_devices_status():
    results = execute_command("df -h | awk 'NR>1 {print $1, $2, $3, $5}'")
    results_to_return = {}
    for host, values in results.items():
        results_to_return[host] = [{'device': device, 'size': size, 'used': used, 'percentage': percentage.strip("%\n")}
                                   for list_entry in values
                                   for device, size, used, percentage in [list_entry.split(" ")]]
    return results_to_return


def get_disk_devices_names():
    results = execute_command("df -h | awk 'NR>1 {print $1, $6}'")
    return {host: {'devices': values} for host, values in results.items()}


def get_disk_usage_per_user():
    results = execute_command("du -sh /home/* | sort -hr | awk '{print $2, $1}'")
    return results


def get_hostnames():
    results = execute_command("hostname")
    hostnames = {host: {'hostname': res[0].strip("\n")} for host, res in results.items()}
    return hostnames


def get_service_status(service_name):
    result = execute_command(f"service {service_name} status")
    result = {host: {service_name: res[0].strip("\n")} for host, res in result.items()}
    return result



def restart_service(service_name):
    result = execute_command(f"service {service_name} status")
    return result


def get_user_count():
    results = execute_command("grep -c bash /etc/passwd")
    hostnames = {host: {'users': res[0].strip("\n")} for host, res in results.items()}
    return hostnames


def is_private_ip(ip):
    try:
        ip_obj = ipaddress.IPv4Address(ip)
        return ip_obj.is_private
    except ipaddress.AddressValueError:
        return False


def get_all_ips_on_host():
    result = execute_command("ip -br addr | awk '{print $3}' | cut -d'/' -f1")
    return {host: {'ips': values} for host, values in result.items()}


def read_remote_file(remote_file_path):
    pass


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

