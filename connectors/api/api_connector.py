import logging
from typing import Dict, List

import requests
from requests import Response

from configuration import config


class ApiConnector:
    def __init__(self, hosts):
        self.hosts = hosts

    @staticmethod
    def call_endpoints(
        endpoint, hosts: tuple = None, method: str = "GET", https=False
    ) -> Dict:
        # todo method handler
        # hosts, users = get_managed_hosts()
        if hosts is None:
            hosts = config.ConfigManager().ip_list
        responses = {}
        for host in hosts:
            api_url = f"http://{host}:{6622}{endpoint}"
            try:
                response = requests.get(api_url)
            except requests.exceptions.ConnectionError as e:
                logging.warning(f"Unable to connect to {api_url} {e}")
                continue
            responses[host] = response.json()
        return responses

    def get_uptime(self) -> Dict[dict]:
        return self.call_endpoints("/uptime", method="GET")

    def healthcheck(self) -> Dict:
        return self.call_endpoints("/healthcheck", method="GET")

    def load_avg(self) -> Dict:
        return self.call_endpoints("/load-avg", method="GET")

    def get_facts(self) -> Dict:
        return self.call_endpoints("/host-facts", method="GET")

    def get_disk_devices(self) -> Dict:
        return self.call_endpoints("/disk-devices", method="GET")
