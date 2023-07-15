from concurrent.futures import ThreadPoolExecutor, as_completed
import paramiko

import config
from utils import get_managed_hosts


def execute_command(host, command, user='root'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='root', key_filename='./env/ssh_key')
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stderr)
    response = stdout.readlines()
    ssh.close()
    return host, response

def prefetch_file_and_execute_function(host, remote_file_path, rfunction, user='root'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='root', key_filename='./env/ssh_key')
    sftp_client = ssh.open_sftp()
    try:
        sftp_client.stat(remote_file_path)
    except FileNotFoundError:
        return host, None
    rfile = sftp_client.open(remote_file_path)
    rfile.prefetch()
    rfile_function_result = rfunction(rfile)
    rfile.close()
    return host, rfile_function_result

def execute_command_on_hosts(command):
    results = {}
    with ThreadPoolExecutor(max_workers=config.max_concurrent_connections) as executor:
        futures = []
        for host, user in get_managed_hosts():
            futures.append(executor.submit(execute_command, host, command, user))
        for future in as_completed(futures):
            # get the downloaded url data
            host, stdout = future.result()
            results[host] = stdout
    return results

def execute_function_on_remote_file(path, rfunction):
    results = {}
    with ThreadPoolExecutor(max_workers=config.max_concurrent_connections) as executor:
        futures = []
        for host, user in get_managed_hosts():
            futures.append(executor.submit(prefetch_file_and_execute_function, host, path, rfunction, user))
        for future in as_completed(futures):
            # get the downloaded url data
            host, stdout = future.result()
            results[host] = stdout
    return results

def get_linux_distro():
    results = execute_command_on_hosts("cat /etc/*-release | awk -F '=' '/^PRETTY_NAME/{print $2}'")
    print(results)


def read_file(rfile):
    for line in rfile:
        pass
        # print(line)
    return "hello there"

get_linux_distro()
print(execute_function_on_remote_file('/etc/passwd', read_file))