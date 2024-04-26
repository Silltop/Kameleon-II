import threading
from typing import List

import yaml
from configuration import logger

dns_ip = '8.8.8.8'
check_interval = 60
max_concurrent_connections = 10


class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.file_content = {}
        self.load_content()
        self.ip_list = self.load_ips()

    def load_content(self) -> None:
        with open('configuration.yaml') as stream:
            try:
                self.file_content = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.exception(
                    f"Unable to load configuration file make sure that .yaml file is valid. more info: {repr(exc)}")

    def validate(self):
        # todo add validation
        raise NotImplementedError

    def load_ips(self) -> List:
        host_list = self.file_content.get("hosts")
        ip_list = []
        for host_name, host_definition in host_list.items():
            ip_list.append(host_definition.get("ip"))
        return ip_list
