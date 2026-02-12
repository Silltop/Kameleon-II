import logging
import os
from functools import wraps

import yaml
from authlib.integrations.base_client.errors import MismatchingStateError
from flask import abort, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy import func
from sqlalchemy.orm import subqueryload

import web.api  # noqa: F401
from configuration import config
from configuration.config import ConfigManager
from connectors.api.api_connector import ApiConnector
from data_management.db_models import ExtensionRoutes, Host, HostFacts
from data_management.sync_functions import sync_all
from host_management import admin_functions
from host_management.rbl_checker import RblChecker
from host_management.utils import ip_address_is_valid

# from ansible_wrapper import check_service_status
from web.app import app, db, keycloak

from .charts import Chart, ChartDataElement, chart_from_column_elements


def extended_render_template(*args, **kwargs):
    """Dynamic list of navbar items as override to base flask function"""
    extension_routes = db.session.query(ExtensionRoutes).all()
    user = session.get("user_claims", None)
    extension_routes_json = [route.to_dict() for route in extension_routes]
    return render_template(*args, **kwargs, user=user, extension_routes=extension_routes_json)


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "user_claims" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return decorated_function


@app.route("/logout")
def logout():
    print(url_for("index", _external=True))
    id_token = session.pop("id_token", None)
    logout_url = (
        f"http://localhost:8080/realms/kameleon/protocol/openid-connect/logout"
        f"?id_token_hint={id_token}"
        f"&post_logout_redirect_uri={url_for('index', _external=True)}"
    )
    session.clear()
    return redirect(logout_url)


@app.before_request
def before_request():
    if request.endpoint not in ["login", "auth", "static"] and "user_claims" not in session:
        return redirect(url_for("login"))


@app.route("/query-rbl/<ip>", methods=["GET"])
@login_required
def query_rbl_db(ip):
    if ip_address_is_valid(ip):
        result = RblChecker().check_rbl(ip)
        return extended_render_template("rbl_result.html", ip=ip, result=result, success=True)
    return extended_render_template("rbl_result.html", ip=ip, success=False)


@app.route("/admin-functions")
@login_required
def admin_functions_render():
    results = session.pop("results", [])
    host_list = config.ConfigManager().ip_list
    admin_functions_config = [
        {
            "id": "check_mailing_services",
            "title": "Check Mailing Services",
            "description": (
                "This functionality will run Service check on desired host and return result. "
                "Checked Services: Exim, Dovecot, Spamassasin"
            ),
            "endpoint": "/run-function/check_mailing_services",
        }
    ]
    return extended_render_template(
        "admin_functions.html",
        host_list=host_list,
        results=results,
        admin_functions_config=admin_functions_config,
    )


@app.route("/run-function/<functionname>", methods=["POST"])
@login_required
def run_admin_function(functionname):
    payload = request.get_json(silent=True) or {}
    hosts = payload.get("host", None) or request.form.get("host", None)
    logging.info("Hosts received for admin function: %s", hosts)
    if hosts is None:
        abort(400, description="Host(s) must be provided")
    if hosts == "all":
        hosts = None
    else:
        hosts = tuple(hosts.split(","))
    adm_function = getattr(admin_functions, functionname)
    results = adm_function(hosts)
    wants_json = (
        request.is_json
        or "application/json" in request.headers.get("Accept", "")
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )
    if wants_json:
        return jsonify({"results": results})
    session["results"] = results
    return redirect(url_for("admin_functions_render"))


@app.route("/login")
def login():
    redirect_uri = url_for("auth", _external=True)
    nonce = os.urandom(16).hex()  # Generate a unique nonce
    session["nonce"] = nonce  # Store it in the session for later validation
    return keycloak.authorize_redirect(redirect_uri, nonce=nonce)  # type: ignore


@app.route("/auth")
def auth():
    try:
        token = keycloak.authorize_access_token()  # type: ignore
        # Ensure nonce validation
        id_token = token.get("id_token")
        claims = keycloak.parse_id_token(token, nonce=session.pop("nonce", None))  # type: ignore
        # Store claims in session
        session["user_claims"] = claims
        session["id_token"] = id_token
        print(claims)
        return redirect(url_for("index"))
    except MismatchingStateError:
        session.clear()
        return redirect(url_for("login"))


@app.route("/configuration")
@login_required
def configuration_page():
    file = ConfigManager().file_content
    return extended_render_template("config.html", file_content=yaml.dump(file))


@app.route("/disks")
@login_required
def disk_status():
    disk_data = ApiConnector().call_hosts("/disk-devices")
    return extended_render_template("disks-status.html", disk_data=disk_data)


@app.route("/sync-all")
@login_required
def synchronize_data():
    sync_all()
    return (
        jsonify({"message": "Data will be synchronized, please wait and refresh page after some time..."}),
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
    host_details_json = [
    {
        "host": host.to_dict(),
        "facts": facts.to_dict() if facts else None,
    }
    for host, facts in host_details_list
    ]
    upgradeable_packages = ApiConnector().call_hosts("/packages-status")
    kernel_chart = chart_from_column_elements(HostFacts.kernel, title="Kernels")
    distro_chart = chart_from_column_elements(HostFacts.distro, title="Distributions")
    packages_chart = Chart(
        name="upgradeable_packages",
        title="Upgradeable Packages",
        w="300em",
        h="150em",
        chart_type="bar",
        chart_data=[
            ChartDataElement(label=host, value=data.get("upgradable", 0))
            for host, data in upgradeable_packages.items()
        ],
    )
    hosts_all = db.session.query(HostFacts).count()
    hosts_down = db.session.query(func.count()).filter(HostFacts.hostname.like("%connection error%")).scalar()
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
    return extended_render_template(
        "index.html",
        host_details_json=host_details_json,
        charts=[chart.to_dict(), kernel_chart.to_dict(), distro_chart.to_dict(), packages_chart.to_dict()],
    )
