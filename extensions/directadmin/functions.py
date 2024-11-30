from connectors.connector import Connection
from api.app import app, db
from api.routes import render_template
from connectors.os import remote_data_processor
from connectors.os.os_connector import execute_command_v2
from extensions.directadmin.database_model import HostDAInfo, DAUserDetails


@app.route("/da-users")
def da_users_dashboard():
    data=Connection().get_da_info()
    print(data)
    return render_template("da_users_dashboard.html", data=data)


@app.route("/da-suspended-users")
def sync_da():
    data = Connection().get_da_suspended()
    return render_template("da_suspended_dashboard.html", data=data)