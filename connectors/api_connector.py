from typing import List, Dict
from host_management.utils import get_hosts_only
import requests


def call_endpoints(endpoint, hosts: tuple = None, method: str = 'GET', https=False) -> Dict:
    # todo method handler
    # hosts, users = get_managed_hosts()
    if hosts is None:
        hosts = get_hosts_only()
    responses = {}
    for host in hosts:
        api_url = f"http://{host}:{6622}{endpoint}"
        try:
            response = requests.get(api_url)
        except requests.exceptions.ConnectionError as e:
            print(f"ERROR CONNECTING TO {api_url} {e}")
            continue
        responses[host] = response.json()
    return responses
