from flask import render_template

# from ansible_wrapper import check_service_status
from flask_init import app
from ssh_connection_functions_core import get_disk_devices_status
from utils import get_managed_hosts


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/config")
def configuration_page():
    mh = get_managed_hosts()
    return render_template("config.html", managed_hosts=mh)


@app.route("/")
def index():
    # app.logger.info('hello there')
    disk_status = get_disk_devices_status()
    print(type(disk_status))
    return render_template("index.html", disk_data=disk_status)
