import subprocess
from flask import jsonify, abort
from api import app


def execute_command(command):
    try:
        result = subprocess.check_output(
            command, shell=True, executable="/bin/bash", stderr=subprocess.STDOUT
        )

    except subprocess.CalledProcessError as cpe:
        result = cpe.output

    finally:
        return result.decode("utf-8")


@app.route("/host-facts", methods=["GET"])
def gather_facts():
    hostname = execute_command("hostname").strip("\n")
    kernel = execute_command("uname -r").strip("\n")
    distro = execute_command(
        "cat /etc/*-release 2>/dev/null | grep -v '/etc/upstream-release/' | awk -F '=' "
        "'/^PRETTY_NAME/{print $2}' | tr -d '\"' "
    ).strip("\n")
    users = execute_command(
        'awk -F: \'$6 ~ /^\/home/ { count++ } END { if (count > 0) print count; else print "0" '
        "}' /etc/passwd"
    ).strip("\n")
    to_return = {
        "hostname": hostname,
        "kernel": kernel,
        "distro": distro,
        "users": users,
    }
    return jsonify(to_return)


@app.route("/get-all-ips-on-host", methods=["GET"])
def get_all_ips_on_host():
    result = execute_command(
        "ip -br addr | grep -v 'lo'  | awk '{print $3}' | cut -d'/' -f1"
    )
    return jsonify(
        list(filter(None, result.split("\n")))
    )  # filter will remove empty list entries


@app.route("/uptime", methods=["GET"])
def uptime():
    result = execute_command("uptime").strip("\n")
    return jsonify({"uptime": result})


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return jsonify("up", 200)


@app.route("/load-avg", methods=["GET"])
def load_avg():
    result = execute_command("cat /proc/loadavg | awk '{print $1, $2, $3}'").strip("\n")
    return jsonify({"load-avg": result})


@app.route("/disk-devices", methods=["GET"])
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


@app.route("/", methods=["GET"])
def index():
    result = {"Welcome": "This is api response"}
    return jsonify(result)


@app.route("/error", methods=["GET"])
def error_page():
    return abort(400)
