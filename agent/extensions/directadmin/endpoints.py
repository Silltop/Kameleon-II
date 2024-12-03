import logging
import os
from flask import Blueprint, jsonify
from datetime import datetime
from utils import run_command

da = Blueprint('da', __name__)


def calculate_duration_days(date_str):
    input_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    current_date = datetime.now()
    duration_days = (current_date - input_date).days
    return duration_days


@da.route("/get-suspended-users")
def get_suspended_users():
    if not os.path.exists("/usr/local/directadmin"):
        return jsonify({"info": "Directadmin not installed"}), 211
    suspended_users_command = run_command('''
    output=$(for path in /usr/local/directadmin/data/users/*/user.conf; do 
        [ -f "$path" ] && 
        user=$(basename $(dirname "$path")) && 
        if grep -q "suspended=yes" "$path"; then 
            suspend_time=$(grep -m1 "suspend_time=" "$path" | cut -d'=' -f2)
            if [ -n "$suspend_time" ]; then
                suspend_date=$(date -d "@$suspend_time" "+%Y-%m-%d %H:%M:%S")
                echo "$user|$suspend_date"
            else
                echo "$user|N/A"
            fi
        fi
    done); echo "$output"
    ''')
    data = {}
    for entry in suspended_users_command:
        entry = entry.split("|")
        user, time = entry[0], entry[1]
        if "N/A" not in time:
            data[user] = calculate_duration_days(time)
        else:
            data[user] = "N/A"
    logging.critical(suspended_users_command)
    return jsonify(data), 200


@da.route("/provide-da-apps-versions")
def get_da_apps_versions():
    if not os.path.exists("/usr/local/directadmin"):
        return jsonify({"info": "Directadmin not installed"}), 211
    command_output = run_command("da build versions")
    version_data = {}

    # Parse the output line by line
    for line in command_output:
        if line.startswith("Latest version of") or line.startswith("Installed version of"):
            parts = line.split(":")
            name = parts[0].replace("Latest version of", "").replace("Installed version of", "").strip()
            version = parts[1].strip()
            version_data[name] = version
    logging.critical(command_output)
    # return jsonify(data), 200


@da.route("/get-da-all-info")
def get_da_all_info():
    try:
        if not os.path.exists("/usr/local/directadmin"):
            return jsonify({"info": "Directadmin not installed"}), 211

        da_users = run_command("find /usr/local/directadmin/data/users -mindepth 1 -maxdepth 1 -type d -printf '%f\n'")
        users = da_users  # .strip().split('\n')  # Convert command output to a list of usernames

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

            # Get user domains
            domains_list_path = f"/usr/local/directadmin/data/users/{user}/domains.list"
            if os.path.isfile(domains_list_path):
                domains = run_command(f"cat {domains_list_path}")  # .strip().split('\n')
                user_info["domains"] = domains

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
