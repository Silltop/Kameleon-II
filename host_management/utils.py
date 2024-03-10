import os

import dns.resolver
import ipaddress
from configuration import config


def get_managed_hosts():
    with open(f'{os.getcwd()}/inventory/hosts', 'r') as f:
        file_data = f.readlines()
        to_return = []
        for line in file_data:
            line = line.split(' ')
            host = line[0]
            user = line[1].replace("ansible_user=", '')
            to_return.append((host, user))
        return to_return


def get_hosts_only():
    # todo remove hosts from db when not in file
    with open(f'{os.getcwd()}/inventory/hosts', 'r') as f:
        file_data = f.readlines()
        to_return = []
        for line in file_data:
            line = line.split(' ')
            to_return.append(line[0])
        return to_return


def dns_resolve_ip(domain: str):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [config.dns_ip]
    return resolver.resolve(domain, 'A')[0]


def dns_resolve_ns(domain: str):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [config.dns_ip]
    return resolver.resolve(domain, 'NS')[0]


def ip_address_is_valid(ip_string):
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False


def convert_to_gb(quota):
    try:
        quota_int = int(quota)
        quota_gb = quota_int / 1000
        return f"{quota_gb}GB"
    except ValueError:
        return "Unknown"
