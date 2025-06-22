from flask import Blueprint

from connectors.api.api_connector import ApiConnector
from web.views import extended_render_template

plugin = Blueprint("da", __name__, url_prefix="/da", static_folder="static", template_folder="templates")


@plugin.route("/users")
def da_users_dashboard():
    return extended_render_template("da_users_dashboard.html", data=ApiConnector().call_hosts("/get-da-all-info"))


@plugin.route("/suspended-users")
def sync_da():
    return extended_render_template(
        "da_suspended_dashboard.html", data=ApiConnector().call_hosts("/get-suspended-users")
    )


@plugin.route("/apps-versions")
def da_apps_versions():
    data = ApiConnector().call_hosts("/provide-da-apps-versions")
    table_headers = ["Server"] + list(next(iter(data.values())).keys()) if data else []
    return extended_render_template("da_apps_versions.html", table_headers=table_headers, table_data=data)


@plugin.route("/user-websites")
def da_websites():
    data = ApiConnector().call_hosts("/get-da-user-websites")
    for ip, host_data in data.items():
        print(host_data)
    table_headers = ["User", "Domain", "PHP Version"]
    # print(data)
    return extended_render_template("da_user_websites.html", table_headers=table_headers, table_data=data)


@plugin.route("/user-emails")
def da_emails():
    data = ApiConnector().call_hosts("/get-da-user-emails")
    for ip, host_data in data.items():
        print(host_data)
    table_headers = ["Email", "Alias", "Last Login", "Size"]
    # print(data)
    return extended_render_template("da_user_emails.html", table_headers=table_headers, table_data=data)
