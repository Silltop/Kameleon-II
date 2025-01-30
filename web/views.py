import yaml
from flask import render_template as base_render_template
from flask import url_for, redirect, session, request, jsonify
from sqlalchemy import func
from sqlalchemy.orm import subqueryload
# from ansible_wrapper import check_service_status
from web.app import app, db, cache
from configuration import config
from configuration.config import ConfigManager
from connectors.api.api_connector import ApiConnector
from data_management.db_models import HostFacts, Host, ExtensionRoutes
from data_management.sync_functions import sync_all
from host_management import admin_functions
from host_management.rbl_checker import RblChecker
from host_management.utils import ip_address_is_valid
from .charts import Chart, ChartDataElement, chart_from_column_elements
import web.api  # noqa: F401


def render_template(*args, **kwargs):
    """Dynamic list of navbar items as override to base flask function"""
    extension_routes = db.session.query(ExtensionRoutes).all()
    return base_render_template(*args, **kwargs, extension_routes=extension_routes)


@app.route("/query-rbl/<ip>", methods=["GET"])
def query_rbl_db(ip):
    if ip_address_is_valid(ip):
        result = RblChecker.check_rbl(ip)
        return render_template("rbl_result.html", ip=ip, result=result, success=True)
    return render_template("rbl_result.html", ip=ip, success=False)


@app.route("/admin-functions")
def admin_functions_render():
    results = session.pop("results", [])
    host_list = config.ConfigManager().ip_list
    return render_template("admin_functions.html", host_list=host_list, results=results)


@app.route("/run-function/<functionname>", methods=["POST"])
def run_admin_function(functionname):
    hosts = request.form.get("host", None)
    if hosts is not None:
        hosts = (hosts,)
    adm_function = getattr(admin_functions, functionname)
    session["results"] = adm_function(hosts)
    return redirect(url_for("admin_functions_render"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/config")
def configuration_page():
    file = ConfigManager().file_content
    return render_template("config.html", file_content=yaml.dump(file))


@app.route("/disks")
def disk_status():
    disk_data = ApiConnector().call_hosts("/disk-devices")
    return render_template("disks-status.html", disk_data=disk_data)


@app.route("/sync-all")
def synchronize_data():
    sync_all()
    return (
        jsonify(
            {
                "message": "Data will be synchronized, please wait and refresh page after some time..."
            }
        ),
        200,
    )


@app.route("/")
def index():
    host_details_list = []
    host_details_list = (
        db.session.query(Host, HostFacts)
        .join(HostFacts, Host.id == HostFacts.host_id)
        .options(subqueryload(Host.host_ips))
        .options(subqueryload(Host.host_ips))
        .all()
    )
    print(host_details_list)
    kernel_chart = chart_from_column_elements(HostFacts.kernel, title="Kernels")
    distro_chart = chart_from_column_elements(HostFacts.distro, title="Distributions")
    hosts_all = db.session.query(HostFacts).count()
    hosts_down = (
        db.session.query(func.count())
        .filter(HostFacts.hostname.like("%connection error%"))
        .scalar()
    )
    de1 = ChartDataElement("Hosts up", int(hosts_all - hosts_down))
    de2 = ChartDataElement("Hosts down", int(hosts_down))
    chart = Chart(
        name="hosts_up",
        title="Host Status",
        w="200em",
        h="150em",
        chart_type="pie",
        chart_data=[de1, de2],
    )
    return render_template(
        "index.html",
        host_details_list=host_details_list,
        charts=[chart, kernel_chart, distro_chart],
    )
