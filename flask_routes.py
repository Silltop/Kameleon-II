from flask import render_template

# from ansible_wrapper import check_service_status
from flask_init import app
from ssh_connection_functions_core import get_disk_devices_status, gather_facts
from utils import get_managed_hosts, get_hosts_only


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/admin-functions")
def admin_functions():

    return render_template("admin_functions.html", host_list=get_hosts_only())


@app.route("/config")
def configuration_page():
    mh = get_managed_hosts()
    return render_template("config.html", managed_hosts=mh)


@app.route("/disks")
def disk_status():
    return render_template("disks-status.html", disk_data=get_disk_devices_status())


@app.route("/")
def index():
    host_details_list = []

    print(type(disk_status))
    return render_template("index.html", host_details_list=gather_facts())
