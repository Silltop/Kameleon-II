import configuration.config
from connectors.api.api_connector import ApiConnector

cfg = configuration.config.ConfigManager().file_content
host_list = cfg.get("hosts")


def separate_hosts():
    method1 = []
    method2 = []
    for host_name, host_definition in host_list.items():
        ip = host_definition.get("ip")
        if host_definition.get("method") == "agent":
            method1.append(ip)
        else:
            method2.append(ip)
    return method1, method2


agent_host_list, ssh_host_list = separate_hosts()


class Connection:
    def __init__(self):
        self.agent_host_list = []
        self.api_connector = ApiConnector(agent_host_list)

    def get_uptime(self):
        return self.api_connector.get_uptime()

    def healthcheck(self):
        return self.api_connector.healthcheck()

    def load_avg(self):
        return self.api_connector.load_avg()

    def host_facts(self):
        return self.api_connector.get_facts()

    def get_disk_devices(self):
        return self.api_connector.get_disk_devices()

    def get_disk_usage_per_user(self):
        pass

    def get_service_status(self):
        pass

    def get_all_ips_on_host(self):
        pass

    def get_da_info(self):
        return self.api_connector.get_da_info()

    def get_da_suspended(self):
        return self.api_connector.get_da_suspended()
