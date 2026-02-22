import logging
from pathlib import Path
from urllib.parse import unquote

from utils import run_command


def get_user_list():
    da_users = run_command("find /usr/local/directadmin/data/users -mindepth 1 -maxdepth 1 -type d -printf '%f\n'")
    users = da_users.split(" ")  # Convert command output to a list of usernames
    return users


def get_php_list():
    try:
        php_list = []
        local_path = "/usr/local/directadmin/custombuild/options.conf"
        if Path(local_path).exists():
            with open(local_path, "r") as rfile:
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
        logging.error(f"Error reading options.conf: {str(e)}")
        return "Unable to find options.conf"

php_list = get_php_list()


def get_user_domains(user) -> list:
    try:
        domains = []
        user = user.replace("\n", "")
        path = f"/usr/local/directadmin/data/users/{user}/domains.list"

        if not Path(path).exists():
            return ["Unable to find domains list"]

        with open(path) as rfile:
            for line in rfile:
                domain = line.strip()
                domains.append(domain)

        return domains
    except Exception as e:
        logging.error(f"Error retrieving domains for user {user}: {str(e)}")
        return [f"Unable to find domains list for user {user}"]


def get_user_subdomains(user, domain) -> list:
    try:
        subdomains = []
        user = user.replace("\n", "")
        domain = domain.replace("\n", "")
        path = f"/usr/local/directadmin/data/users/{user}/domains/{domain}.subdomains"

        if not Path(path).exists():
            return ["Unable to find subdomains list"]

        with open(path) as rfile:
            for line in rfile:
                subdomain = line.strip()
                if subdomain:
                    subdomains.append(subdomain)

        return subdomains
    except Exception as e:
        logging.error(f"Error retrieving subdomains for user {user}: {str(e)}")
        return [f"Unable to find subdomains list for user {user}"]


def get_user_subdomain_php_version(user, domain):
    try:
        user = user.replace("\n", "")
        domain = domain.replace("\n", "")
        path = Path(
            f"/usr/local/directadmin/data/users/{user}/domains/{domain}.subdomains.docroot.override"
        )

        if not path.exists():
            return "Unable to find subdomain configuration"

        if not isinstance(php_list, list) or not php_list:
            return "Unable to retrieve PHP versions"

        with path.open() as rfile:
            for line in rfile:
                decoded = unquote(line.strip())
                if not decoded:
                    continue

                _, setting = decoded.split("=", 1) if "=" in decoded else ("", decoded)
                if "_select=" in setting:
                    _, value = setting.split("_select=", 1)
                    value = value.strip()
                    if value.isdigit():
                        index = int(value) - 1
                        if 0 <= index < len(php_list):
                            return php_list[index]
                    return value

        return php_list[0]
    except Exception as e:
        logging.error(f"Error retrieving subdomain PHP version for user {user}: {str(e)}")
        return "Unable to find subdomain configuration"


def get_user_domain_php_version(user: str, domain: str) -> str:
    try:
        path = Path(f"/usr/local/directadmin/data/users/{user}/domains/{domain}.conf")
        if not path.exists():
            return "Unable to find domain configuration"

        if not isinstance(php_list, list) or not php_list:
            return "Unable to retrieve PHP versions"

        with path.open() as rfile:
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
