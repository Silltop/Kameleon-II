from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
import os
import shutil

from ansible.module_utils.basic import AnsibleModule
import ansible_runner


def run_ansible_command(command):
    result = ansible_runner.run_command(command, quiet=True)
    return result


def execute_remote_command(command):
    # result = ansible_runner.run(inventory=host, host_pattern='all', module='command', module_args=command)
    result = ansible_runner.interface.run(host_pattern='all', module='command', module_args=command, quiet=True,
                                          private_data_dir="./", json_mode=True)
    if result.rc == 0:
        for host in result.events:
            print(f"Command execution successful")
            return result.stdout.read()
    else:
        print(f"Command execution failed")
        return result.stderr.read()


def check_service_status(service_name):
    result = ansible_runner.interface.run(host_pattern='all', module='service',
                                          module_args=f'name={service_name} state=started enabled=true', quiet=True,
                                          private_data_dir="./", json_mode=False)
    # if result.rc == 0:
    #     print(f"Service {service_name} is running")
    # else:
    #     print(f"Service {service_name} is not running ")

    for host in result.events:
        if host['event'] == 'runner_on_ok':
            host_output = host['stdout'][0]
            event_data = host['event_data']
            if host_output:
                print(f"Service status for {event_data['host']}  {event_data['res']}:")
                print(f"host output: {event_data}")
            else:
                print(f"Host variable 'my_variable' is not defined for {event_data['host']}")
        elif host['event'] == 'runner_on_unreachable':
            pass
            # print(host['event'])


''' Debug lines
command = 'ls -l'
output = run_ansible_command(command)
#print(output)
res = execute_remote_command("ls -la")
print(res)
'''
#check_service_status('ssh')
