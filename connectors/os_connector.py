"""
1. OS CONNECTION VARIETY (BASE SSH - PARAMIKO)
2. OS DISCOVERY INCLUDING PACKAGE MANAGER 0 os_functionalities
3. command execution?
"""
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
from pssh.clients import ParallelSSHClient
from pssh.exceptions import ConnectionError
from host_management.utils import get_hosts_only


@dataclass
class HostOutput:
    ip: str
    stdout: Optional[List] = None  # list of the lines
    stderr: Optional[List] = None
    exception: bool = False
    exception_details: str = ""
    stdstr: str = ""

    def merge_output_data_to_string(self) -> str:
        """Return data in one string, merge stdout, stderr and exception"""
        return_str = ""
        if self.stdout is not None:
            return_str += '\n'.join(self.stdout)
        if self.stderr is not None:
            return_str += '\n'.join(self.stderr)
        return_str += str(self.exception_details)
        return return_str

    def merge_output_data(self) -> List:
        merged_list = []
        if self.stdout is not None:
            merged_list.extend(self.stdout)
        if self.stderr is not None:
            merged_list.extend(self.stderr)
        if self.exception_details is not None:
            merged_list.extend([self.exception_details])
        return merged_list

    def get_ip_with_output(self, merge_output: bool = False) -> Dict[str, str]:
        if merge_output:
            return {self.ip: self.merge_output_data_to_string()}
        else:
            return {self.ip: self.merge_output_data()}


class HostOutputManager:
    def __init__(self):
        self.host_output_list = []

    def add_host_output(self, host_output: HostOutput):
        self.host_output_list.append(host_output)

    def get_output_per_host(self, merge_output: bool = False):
        return {k: v for entry in self.host_output_list for k, v in entry.get_ip_with_output(merge_output).items()}


def execute_command_v2(command, hosts: tuple = None, default_on_error=None) -> HostOutputManager:
    # hosts, users = get_managed_hosts()
    if hosts is None:
        hosts = get_hosts_only()
    client = ParallelSSHClient(hosts, user='root', pkey='./env/id_ed', timeout=1, retry_delay=1, num_retries=1)
    command_output = client.run_command(command, stop_on_errors=False)
    hom = HostOutputManager()
    for entry in command_output:
        host_output = HostOutput(ip=entry.host)
        if entry.exception is not None:
            host_output.exception = True
            if default_on_error is not None:
                host_output.exception_details = default_on_error
            elif type(entry.exception) == ConnectionError:
                host_output.exception_details = "Connection error"
            else:
                host_output.exception_details = entry.exception
        if entry.stdout:
            host_output.stdout = entry.stdout
        if entry.stderr:
            if default_on_error is not None:
                host_output.stderr = default_on_error
            else:
                host_output.stderr = entry.stderr
        hom.add_host_output(host_output)
    return hom
