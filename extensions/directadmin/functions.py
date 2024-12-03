from connectors.api.api_connector import ApiConnector
from web.app import app
from web.views import render_template


@app.route("/da-users")
def da_users_dashboard():
    return render_template("da_users_dashboard.html", data=ApiConnector().call_hosts("/get-da-all-info"))


@app.route("/da-suspended-users")
def sync_da():
    return render_template("da_suspended_dashboard.html", data=ApiConnector().call_hosts("/get-da-all-info"))


@app.route("/da-apps-versions")
def da_apps_versions():
    return render_template("da_apps_versions.html", data=ApiConnector().call_hosts("/get-da-all-info"))
