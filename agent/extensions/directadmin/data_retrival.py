import os

from utils import run_command

def get_user_list():
    da_users = run_command("find /usr/local/directadmin/data/users -mindepth 1 -maxdepth 1 -type d -printf '%f\n'")
    users = da_users.split(" ")  # Convert command output to a list of usernames
    return users

def get_php_list():
    try:
        php_list = []
        local_path = "/usr/local/directadmin/custombuild/options.conf"
        if os.path.exists(local_path):
            with open(local_path, 'r') as rfile:
                lines = rfile.readlines()
        else:
            return "Unable to find options.conf"
        
        for line in lines:
            for i in range(1, 5):
                if f"php{i}_release=" in line:
                    founded_line = line.strip(f"php{i}_release=").strip("\n")
                    php_list.append(founded_line)
        return php_list
    except Exception as e:
        return "Unable to find options.conf"
    
def get_user_domains(user):
    try:
        domains = []
        user = user.replace("\n", "")
        path = f"/usr/local/directadmin/data/users/{user}/domains.list"
        
        if not os.path.exists(path):
            return "Unable to find domains list"
        
        with open(path, 'r') as rfile:
            for line in rfile:
                domain = line.strip()
                domains.append(domain)
        
        return domains
    except Exception as e:
        return f"Error occurred: {str(e)}"

def get_user_php_version(user, domain):
    try:
        path = f"/usr/local/directadmin/data/users/{user}/domains/{domain}.conf"
        if not os.path.exists(path):
            return "Unable to find domain configuration"
        
        with open(path, 'r') as rfile:
            lines = rfile.readlines()
        
        for line in lines:
            for i in range(1, 5):
                if f"php{i}_select=" in line:
                    output_line = line.strip(f"php{i}_select=").strip()
                    if output_line == str(i):
                        return php_list[i - 1]
        return php_list[0]
    except Exception:
        return "Unable to find domain configuration"
