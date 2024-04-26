"""
Notes:
    1. I tried paramiko but seems like there is a problem with private key when trying to connect at once to multiple hosts.
    When I tried to connect to only one connection was fine, but otherwise package was returning Unauthorized.
    2. Parallel-ssh also seem to have a weird issue with pkeys, this lib is only able to authenticate using ed25519 key, weird.
    3. Of course, I tested, locally keys using ssh -i command.
"""
import ipaddress
from secrets import token_hex
# from host_management.utils import get_hosts_only
from pssh.clients import ParallelSSHClient
from pssh.exceptions import ConnectionErrorException

from configuration import config


def execute_command(command, hosts: tuple = None):
    # hosts, users = get_managed_hosts()
    if hosts is None:
        hosts = config.ConfigManager().ip_list
    client = ParallelSSHClient(hosts, user='root', pkey='./env/id_ed', timeout=1, retry_delay=1, num_retries=1)
    output = client.run_command(command, stop_on_errors=False)
    response_dict = {}
    for host_out in output:
        new_output = []
        if isinstance(host_out.exception, ConnectionErrorException):
            response_dict[host_out.host] = ["Connection Error"]
            continue
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


def parse_output_to_dict(result_to_parse, assignment_key):
    parsed_output = {host: {assignment_key: res[0].strip("\n")} for host, res in result_to_parse.items()}
    return parsed_output


def parse_device_results(values):
    parsed_results = []
    for list_entry in values:
        if len(list_entry.split(" ")) != 5:
            parsed_results.append(
                {'device': 'unknown', 'size': 0, 'used': 0, 'percentage': 0, 'mountpoint': 'unknown'})
            break
        device, size, used, percentage, mountpoint = list_entry.split(" ")
        parsed_result = {
            'device': device,
            'size': size,
            'used': used,
            'percentage': percentage,
            'mountpoint': mountpoint.strip("%\n"),
        }
        parsed_results.append(parsed_result)
    return parsed_results


def get_disk_devices_status(hosts: tuple = None):
    results = execute_command("df | awk 'NR>1 {print $1, $2, $3, $5, $6}'")
    results_to_return = {}
    for host, values in results.items():
        results_to_return[host] = parse_device_results(values)
    return results_to_return


def get_disk_devices_names(hosts: tuple = None):
    results = execute_command("df -h | awk 'NR>1 {print $1, $6}'")
    return {host: {'devices': values} for host, values in results.items()}


def get_disk_usage_per_user(hosts: tuple = None):
    results = execute_command("du -sh /home/* | sort -hr | awk '{print $2, $1}'", hosts)
    return results


def get_service_status(service_name, hosts: tuple = None):
    result = execute_command(f"service {service_name} status", hosts)
    result = parse_output_to_dict(result, service_name)
    return result


def restart_service(service_name, hosts: tuple = None):
    return execute_command(f"service {service_name} status", hosts)


def is_private_ip(ip):
    try:
        ip_obj = ipaddress.IPv4Address(ip)
        return ip_obj.is_private
    except ipaddress.AddressValueError:
        return False


def get_all_ips_on_host(hosts: tuple = None):
    result = execute_command("ip -br addr | grep -v 'lo'  | awk '{print $3}' | cut -d'/' -f1", hosts)
    return {host: {'ips': values} for host, values in result.items()}



def read_remote_file(remote_file_path):
    pass