import threading
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
        self.inventory = {}
        self.load_inventory()

    def load_inventory(self):
        print("HI")
        with open('inventory/inventory.yaml') as stream:
            try:
                self.inventory = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.exception(exc)
