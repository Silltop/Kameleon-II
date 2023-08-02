from flask import render_template, url_for, redirect, session

from db_models import HostFacts, Host
# from ansible_wrapper import check_service_status
from flask_init import app, db
from ssh_connection_functions_core import get_disk_devices_status, gather_facts
from utils import get_managed_hosts, get_hosts_only
import admin_functions


@app.route("/admin-functions")
def admin_functions_render():
    results = session.pop('results', [])
    return render_template("admin_functions.html", host_list=get_hosts_only(), results=results)
@app.route("/run-function/<functionname>")
def run_admin_function(functionname):
    adm_function = getattr(admin_functions, functionname)
    session['results'] = adm_function()
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


@app.route("/sync")
def sync():
    facts = gather_facts()
    print(facts)
    for ip, host_details in facts.items():
        host = Host.query.filter_by(host_ip=ip).first()
        host_facts = HostFacts.query.filter_by(host_id=host.id).first()
        if host_facts:
            host_facts.hostname = host_details.get("hostname")
            host_facts.kernel = host_details.get("kernel")
            host_facts.distro = host_details.get("distro")
    db.session.commit()
    return redirect(url_for('index'))
@app.route("/")
def index():
    host_details_list = []

    #print(type(disk_status))
    return render_template("index.html", host_details_list=gather_facts())
