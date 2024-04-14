from functools import wraps

from flask import url_for, redirect, session, request, jsonify
from flask import render_template as base_render_template
from sqlalchemy import func
from sqlalchemy.orm import subqueryload

from connectors import remote_data_processor
from connectors.api_connector import call_endpoints
from .charts import Chart, ChartDataElement, chart_from_column_elements
from data_management.db_models import HostFacts, Host, ExtensionRoutes
# from ansible_wrapper import check_service_status
from api.app import app, db, cache
from host_management.rbl_checker import check_rbl
from connectors.remote_data_processor import get_disk_devices_status
from data_management.sync_functions import sync_all
from host_management.utils import get_managed_hosts, get_hosts_only, ip_address_is_valid
from host_management import admin_functions


def cached_endpoint(timeout=300):  # Default cache timeout is 300 seconds (5 minutes)
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = request.full_path
            cached_data = cache.get(cache_key)
            if cached_data is None:
                data = f(*args, **kwargs)
                cache.set(cache_key, data, timeout=timeout)
            else:
                data = cached_data
            return jsonify(data)

        return decorated_function

    return decorator


def render_template(*args, **kwargs):
    """Dynamic list of navbar items as override to base flask function"""
    extension_routes = db.session.query(ExtensionRoutes).all()
    return base_render_template(*args, **kwargs, extension_routes=extension_routes)


@app.route("/active-crontabs", methods=['GET'])
def get_crontabs():
    res = remote_data_processor.execute_command("crontab -l")
    return render_template('crontab.html', result=res)


@app.route("/query-rbl/<ip>", methods=['GET'])
def query_rbl_db(ip):
    if ip_address_is_valid(ip):
        result = check_rbl(ip)
        return render_template("rbl_result.html", ip=ip, result=result, success=True)
    return render_template("rbl_result.html", ip=ip, success=False)


@app.route('/load-avg', methods=['GET'])
@cached_endpoint(timeout=60)  # Cache for 60 seconds
def get_load_avg():
    #  raise NotImplementedError
    return call_endpoints("/load-avg", method='GET')
    #  return remote_data_processor.execute_command("cat /proc/loadavg | awk '{print $1, $2, $3}'")


@app.route('/uptime', methods=['GET'])
@cached_endpoint(timeout=60)  # Cache for 60 seconds
def uptime():
    return call_endpoints("/uptime", method='GET')
    #  return remote_data_processor.execute_command("uptime")


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
    disk_data = get_disk_devices_status()
    print(disk_data)
    return render_template("disks-status.html", disk_data=disk_data)


@app.route("/sync-all")
def synchronize_data():
    sync_all()
    return redirect(url_for('index'))


@app.route("/")
def index():
    host_details_list = []
    host_details_list = db.session.query(Host, HostFacts) \
        .join(HostFacts, Host.id == HostFacts.host_id) \
        .options(subqueryload(Host.host_ips)) \
        .options(subqueryload(Host.host_ips)) \
        .all()
    print(host_details_list)
    kernel_chart = chart_from_column_elements(HostFacts.kernel, title='Kernels')
    distro_chart = chart_from_column_elements(HostFacts.distro, title='Distributions')
    hosts_all = db.session.query(HostFacts).count()
    hosts_down = db.session.query(func.count()).filter(HostFacts.hostname.like('%connection error%')).scalar()
    de1 = ChartDataElement('Hosts up', int(hosts_all - hosts_down))
    de2 = ChartDataElement('Hosts down', int(hosts_down))
    chart = Chart(name="hosts_up", title="Host Status", w="200em", h="150em", chart_type="pie", chart_data=[de1, de2])
    return render_template("index.html", host_details_list=host_details_list,
                           charts=[chart, kernel_chart, distro_chart])
