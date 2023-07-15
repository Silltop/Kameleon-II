from flask import render_template

# from ansible_wrapper import check_service_status
from flask_init import app
from utils import get_managed_hosts


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/config")
def configuration_page():
    mh = get_managed_hosts()
    return render_template("config.html", managed_hosts=mh)


@app.route("/")
def hello_world():
    app.logger.info('hello there')
    check_service_status('ssh')
    return render_template("index.html")
