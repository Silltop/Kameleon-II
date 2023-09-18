from datetime import datetime

from flask import url_for, redirect, session, request
from flask import render_template as base_render_template

from db_models import HostFacts, Host, ExtensionRoutes
# from ansible_wrapper import check_service_status
from flask_init import app, db
from ssh_connection_functions_core import get_disk_devices_status, get_all_ips_on_host
from utils import get_managed_hosts, get_hosts_only
import admin_functions

def render_template(*args, **kwargs):
    # automatic add of navbar items as override to base flask function
    extension_routes = db.session.query(ExtensionRoutes).all()
    return base_render_template(*args, **kwargs, extension_routes=extension_routes)

@app.route("/admin-functions")
def admin_functions_render():
    results = session.pop('results', [])
    return render_template("admin_functions.html", host_list=get_hosts_only(), results=results)
@app.route("/run-function/<functionname>", methods=['POST'])
def run_admin_function(functionname):
    hosts = request.form.get('host', None)
    if hosts is not None:
        hosts = (hosts,)
    adm_function = getattr(admin_functions, functionname)
    session['results'] = adm_function(hosts)
    return redirect(url_for('admin_functions_render'))

@app.route("/login")
def login():
    return render_template("login.html")

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
    host_details_list = db.session.query(Host).join(HostFacts, Host.id == HostFacts.host_id).add_entity(HostFacts).all()
    #print(get_all_ips_on_host())
    return render_template("index.html", host_details_list=host_details_list)
