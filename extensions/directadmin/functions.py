from flask import Blueprint
from connectors.api.api_connector import ApiConnector
from web.views import render_template


plugin = Blueprint("da", __name__, url_prefix="/da", static_folder="static", template_folder="templates")


@plugin.route("/users")
def da_users_dashboard():
    return render_template("da_users_dashboard.html", data=ApiConnector().call_hosts("/get-da-all-info"))


@plugin.route("/suspended-users")
def sync_da():
    return render_template("da_suspended_dashboard.html", data=ApiConnector().call_hosts("/get-da-all-info"))


@plugin.route("/apps-versions")
def da_apps_versions():
    data = ApiConnector().call_hosts("/provide-da-apps-versions")
    table_headers = ["Server"] + list(next(iter(data.values())).keys()) if data else []
    return render_template("da_apps_versions.html", table_headers=table_headers, table_data=data)


@plugin.route("/user-websites")
def da_websites():
    data = ApiConnector().call_hosts("/get-da-user-websites")
    table_headers = ["User", "Domain"]
    return render_template("da_user_websites.html", table_headers=table_headers, table_data=data)
