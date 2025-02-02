from flask import Blueprint
from web.app import app, cached_endpoint
from connectors.api.api_connector import ApiConnector

api = Blueprint("api", __name__)  # fix me


@app.route("/load-avg", methods=["GET"])
@cached_endpoint(timeout=60)  # Cache for 60 seconds
def get_load_avg():
    return ApiConnector().call_hosts("/load-avg")


@app.route("/uptime", methods=["GET"])
@cached_endpoint(timeout=60)  # Cache for 60 seconds
def uptime():
    return ApiConnector().call_hosts("/uptime")
