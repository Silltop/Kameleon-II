import paramiko

import config
from utils import get_managed_hosts
from ssh_connection_functions_core import *


def read_file(rfile):
    for line in rfile:
        pass
        # print(line)
    return "hello there"


get_linux_distro()
print(execute_function_on_remote_file('/etc/passwd', read_file))
