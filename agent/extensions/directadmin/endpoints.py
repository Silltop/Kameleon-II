import logging
import os
from datetime import datetime

from flask import Blueprint, jsonify

from utils import run_command

from extensions.directadmin.data_retrival import get_user_domain_php_version, get_user_domains, get_user_list, get_user_subdomains
from extensions.directadmin.data_retrival import get_user_domains

# Import DNS resolver
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../web_scrapping'))
from dns_resolver import get_complete_dns_info
import glob

da = Blueprint("da", __name__)


def calculate_duration_days(date_str):
    input_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    current_date = datetime.now()
    duration_days = (current_date - input_date).days
    return duration_days


@da.route("/get-suspended-users")
def get_suspended_users():
    if not os.path.exists("/usr/local/directadmin"):
        return jsonify({"info": "Directadmin not installed"}), 211
    suspended_users_command = run_command(
        """
    output=$(for path in /usr/local/directadmin/data/users/*/user.conf; do 
        [ -f "$path" ] && 
        user=$(basename $(dirname "$path")) && 
        if grep -q "suspended=yes" "$path"; then 
            suspend_time=$(grep -m1 "suspend_time=" "$path" | cut -d'=' -f2)
            if [ -n "$suspend_time" ]; then
                suspend_date=$(date -d "@$suspend_time" "+%Y-%m-%d %H:%M:%S")
                echo "$user|$suspend_date;"
            else
                echo "$user|N/A;"
            fi
        fi
    done); echo "$output"
    """
    )
    data = {
        entry.split("|")[0]: calculate_duration_days(entry.split("|")[1]) if "N/A" not in entry.split("|")[1] else "N/A"
        for entry in suspended_users_command.split(";")
        if entry.strip() and len(entry.split("|")) == 2
    }
    logging.critical(suspended_users_command)
    return jsonify(data), 200


@da.route("/get-da-user-websites")
def get_da_user_websites():
    user_domains = {}
    users = get_user_list()
    for user in users:
        domains = get_user_domains(user)
        for domain in domains:
            php_version = get_user_domain_php_version(user, domain)
            user_domains[domain] = php_version
    print(user_domains)
    return jsonify(user_domains), 200


@da.route("/provide-da-apps-versions")
def get_da_apps_versions():
    if not os.path.exists("/usr/local/directadmin"):
        return jsonify({"info": "Directadmin not installed"}), 211
    versions = {}
    versions["OS"] = run_command("cat /etc/*-release | awk -F '=' '/^PRETTY_NAME/{print $2}' | tr -d '\"'", "unknown")
    versions["DirectAdmin"] = run_command(
        "da version",
        "unknown",
    )
    versions["Apache"] = run_command(
        "/usr/local/directadmin/custombuild/build versions | grep 'Installed version of Apache' | awk -F: '{print $2}'",
        "unknown",
    )
    versions["FTPD"] = run_command(
        "/usr/local/directadmin/custombuild/build versions | grep 'Installed version of Pure-FTPd' | awk -F: '{print $2}'",
        "unknown",
    )
    versions["Dovecot"] = run_command(
        "/usr/local/directadmin/custombuild/build versions | grep 'Installed version of Dovecot' | awk -F: '{print $2}'",
        "unknown",
    )
    versions["Exim"] = run_command(
        "/usr/local/directadmin/custombuild/build versions | grep 'Installed version of Exim' | awk -F: '{print $2}'",
        "unknown",
    )
    versions["SpamAssassin"] = run_command(
        "/usr/local/directadmin/custombuild/build versions | grep 'Installed version of SpamAssassin' | awk -F: '{print $2}'",
        "unknown",
    )
    versions["RoundCube"] = run_command(
        "/usr/local/directadmin/custombuild/build versions | grep 'Installed version of RoundCube' | awk -F: '{print $2}'",
        "unknown",
    )
    versions["phpMyAdmin"] = run_command(
        "/usr/local/directadmin/custombuild/build versions | grep 'Installed version of phpMyAdmin' | awk -F: '{print $2}'",
        "unknown",
    )
    versions["Database"] = run_command("mysql --version | awk -F, '{print $1}'", "unknown")
    versions["PHP"] = run_command(
        "/usr/local/directadmin/custombuild/build versions | grep 'Installed version of PHP' | awk -F: '{print $2}'",
        "unknown",
    )
    versions["PHP mode"] = run_command(
        "grep php1_mode /usr/local/directadmin/custombuild/options.conf | awk -F= '{print $2}'", "unknown"
    )
    versions["LetsEncrypt"] = run_command(
        "lego --version",
        "Not installed",
    )
    return versions


@da.route("/get-da-all-info")
def get_da_all_info():
    try:
        if not os.path.exists("/usr/local/directadmin"):
            return jsonify({"info": "Directadmin not installed"}), 211
        users = get_user_list()
        # Initialize a list to store user-specific data
        user_data = {}
        # Step 2: Loop over each user to gather their data
        for user in users:
            # Skip admin and root users for security reasons
            if user in ["root", "admin"]:
                continue
            # Create a dictionary for the user-specific data
            user_info = {}

            # Get user email
            user_conf_path = f"/usr/local/directadmin/data/users/{user}/user.conf"
            if os.path.isfile(user_conf_path):
                # Run the command and check if there's any result
                email_result = run_command(f"grep -m 1 'email=' {user_conf_path} | sed 's/email=//;s/\\\\n//'")
                if email_result:  # Check if the result is not empty
                    user_info["email"] = email_result  # .strip()
                else:
                    user_info["email"] = None  # Set to None if no email is found

            user_info["domains"] = get_user_domains(user)

            # Get subdomain count per domain and DNS information
            user_info["subdomains"] = {}
            user_info["dns_info"] = {}
            for domain in user_info["domains"]:
                subdomains = get_user_subdomains(user, domain)
                user_info["subdomains"][domain] = len(subdomains)
                
                # Get DNS information for the domain
                try:
                    dns_data = get_complete_dns_info(domain)
                    user_info["dns_info"][domain] = {
                        "a_records": [r["value"] for r in dns_data["a_records"]],
                        "mx_records": [r["value"] for r in dns_data["mx_records"]],
                        "ns_records": dns_data["nameservers"],
                        "cname_records": [r["value"] for r in dns_data["cname_records"]]
                    }
                except Exception as e:
                    logging.error(f"Error getting DNS info for domain {domain}: {str(e)}")
                    user_info["dns_info"][domain] = {
                        "a_records": ["Error"],
                        "mx_records": ["Error"],
                        "ns_records": ["Error"],
                        "cname_records": ["Error"]
                    }

            # Get user quota
            usage_path = f"/usr/local/directadmin/data/users/{user}/user.usage"
            if os.path.isfile(usage_path):
                nemails = run_command(f"grep -oP 'nemails=\\K\\d+' {usage_path}")  # .strip()
                user_info["quota"] = nemails

            # Get user package
            package = run_command(f"grep -m 1 'package=' {user_conf_path} | sed 's/package=//'")  # .strip()
            user_info["package"] = package

            # Add the user-specific data to the list
            user_data[user] = user_info

        # Step 3: Return the collected data as a JSON object, grouped by user
        return jsonify(user_data), 200  # Return HTTP 200 OK

    except Exception as e:
        # If any command fails, return an error message
        return jsonify({"error": "Failed to get data", "details": str(e)}), 500


@da.route("/get-da-user-emails", methods=["GET"])
def get_da_user_emails():
    """
    Returns a dictionary of users and their email accounts with details:
    {user: {email: {alias: [...], last_login: ..., size: ...}}}
    """
    result = {}
    users = get_user_list()
    for user in users:
        user_emails = {}
        for domain in get_user_domains(user):
            passwd_path = f"/etc/virtual/{domain}/passwd"
            if not os.path.isfile(passwd_path):
                continue
            try:
                with open(passwd_path) as f:
                    for line in f:
                        parts = line.strip().split(":")
                        if len(parts) < 9:
                            continue
                        email_name = parts[0]
                        email_addr = f"{email_name}@{domain}"
                        size = parts[8].replace("bytes=", "").strip()
                        # Aliases
                        aliases = []
                        aliases_path = f"/etc/virtual/{domain}/aliases"
                        if os.path.isfile(aliases_path):
                            with open(aliases_path) as af:
                                for aline in af:
                                    if aline.startswith(email_name + ":"):
                                        aliases = [a.strip() for a in aline.split(":", 1)[1].split(",") if a.strip()]
                                        break
                        # Last login
                        last_login = None
                        last_login_file = f"/etc/virtual/{domain}/last_login/{email_name}"
                        if os.path.isfile(last_login_file):
                            with open(last_login_file) as lf:
                                for lline in lf:
                                    if "when=" in lline:
                                        try:
                                            ts = int(lline.split("when=")[-1].split("&", 1)[0])
                                            last_login = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                                        except Exception:
                                            last_login = None
                                        break
                        user_emails[email_addr] = {"alias": aliases, "last_login": last_login, "size": size}
            except Exception:
                continue
        if user_emails:
            result[user] = user_emails
    return jsonify(result), 200
