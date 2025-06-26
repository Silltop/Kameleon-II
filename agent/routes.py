import re
from typing import Union
import hashlib
import html
import subprocess

from flask import Blueprint, abort, jsonify, request

API_KEY = "your_api_key_here"  # Replace with your actual API key

api_bp = Blueprint("api", __name__)


# todo make HMAC
def validate_api_key():
    api_key = request.headers.get("X-API-KEY")
    hashed_api_key = hashlib.sha256(API_KEY.encode()).hexdigest() if API_KEY else None
    if hashed_api_key != api_key:
        abort(401, description="Invalid API key")


def validate_certificate():
    if not request.is_secure:
        abort(403, description="SSL certificate required")
    cert = request.headers.get("X-SSL-CERT")
    if not cert:
        abort(403, description="Client certificate required")


@api_bp.before_request
def before_request():
    validate_api_key()
    # validate_certificate()


def execute_command(command: Union[str, list]):
    result = b"Error"
    try:
        if isinstance(command, list):
            result = subprocess.check_output(command, shell=False, executable="/bin/bash", stderr=subprocess.STDOUT)
        else:
            result = subprocess.check_output(
                command, shell=True, executable="/bin/bash", stderr=subprocess.STDOUT
            )  # noqa: S602
    except subprocess.CalledProcessError as cpe:
        result = cpe.output
    finally:
        return result.decode("utf-8")


@api_bp.route("/host-facts", methods=["GET"])
def gather_facts():
    hostname = execute_command("hostname").strip("\n")
    kernel = execute_command("uname -r").strip("\n")
    distro = execute_command(
        "cat /etc/*-release 2>/dev/null | grep -v '/etc/upstream-release/' | awk -F '=' "
        "'/^PRETTY_NAME/{print $2}' | tr -d '\"' "
    ).strip("\n")
    users = execute_command(
        'awk -F: \'$6 ~ /^\/home/ { count++ } END { if (count > 0) print count; else print "0" '
        "}' /etc/passwd"  # noqa: W605
    ).strip("\n")
    to_return = {
        "hostname": hostname,
        "kernel": kernel,
        "distro": distro,
        "users": users,
    }
    return jsonify(to_return)


@api_bp.route("/get-all-ips-on-host", methods=["GET"])
def get_all_ips_on_host():
    result = execute_command("ip -br addr | grep -v 'lo'  | awk '{print $3}' | cut -d'/' -f1")
    return jsonify(list(filter(None, result.split("\n"))))  # filter will remove empty list entries


@api_bp.route("/uptime", methods=["GET"])
def uptime():
    result = execute_command("uptime").strip("\n")
    return jsonify({"uptime": result})


@api_bp.route("/healthcheck", methods=["GET"])
def healthcheck():
    return jsonify("up", 200)


@api_bp.route("/load-avg", methods=["GET"])
def load_avg():
    result = execute_command("cat /proc/loadavg | awk '{print $1, $2, $3}'").strip("\n")
    return jsonify({"load-avg": result})


@api_bp.route("/disk-devices", methods=["GET"])
def disk_devices():
    result = execute_command("df | awk 'NR>1 {print $1, $2, $3, $5, $6}'").split("\n")
    extracted_result = []
    for entry in result:
        if len(entry) < 1:  # filter out empty lines
            continue
        device, size, used, percentage, mountpoint = entry.split(" ")
        extracted_result.append(
            {
                "device": device,
                "size": size,
                "used": used,
                "percentage": percentage,
                "mountpoint": mountpoint.strip("%\n"),
            }
        )
    return jsonify({"disk_devices": extracted_result})


@api_bp.route("/", methods=["GET"])
def index():
    result = {"Welcome": "This is web response"}
    return jsonify(result)


@api_bp.route("/error", methods=["GET"])
def error_page():
    return abort(400)


@api_bp.route("/service-status/<service_name>", methods=["GET"])
def get_service_status(service_name: str):
    result = execute_command(["systemctl", "status", service_name])
    return jsonify({"uptime": result})


@api_bp.route("/get-all-ips-on-host", methods=["GET"])
def execute_command_route():
    result = execute_command("ip -br addr | grep -v 'lo'  | awk '{print $3}' | cut -d'/' -f1")
    return jsonify({"result": result})
