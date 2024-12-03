import configuration.config
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


class Connector:
    def __init__(self):
        self.agent_host_list = []

    def call(self, call_hosts):
        raise NotImplementedError
