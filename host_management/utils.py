import ipaddress
import dns.resolver
from configuration import config


def dns_resolve_ip(domain: str):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [config.dns_ip]
    return resolver.resolve(domain, "A")[0]


def dns_resolve_ns(domain: str):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [config.dns_ip]
    return resolver.resolve(domain, "NS")[0]


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
