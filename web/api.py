from flask import Blueprint, jsonify

from auth.jwt_middleware import require_api_auth
from connectors.api.api_connector import ApiConnector
from data_management.sync_functions import sync_all
from web.app import app, cached_endpoint, jwt_manager

api = Blueprint("api", __name__)  # fix me


# All API routes require JWT authentication (Option B)
@app.route("/api/load-avg", methods=["GET"])
@require_api_auth(jwt_manager)
@cached_endpoint(timeout=60)  # Cache for 60 seconds
def api_get_load_avg():
    return ApiConnector().call_hosts("/load-avg")


@app.route("/api/uptime", methods=["GET"])
@require_api_auth(jwt_manager)
@cached_endpoint(timeout=60)  # Cache for 60 seconds
def api_uptime():
    return ApiConnector().call_hosts("/uptime")


@app.route("/api/sync-all", methods=["POST"])
@require_api_auth(jwt_manager)
def api_sync_all():
    """Synchronize all host data"""
    try:
        sync_all()
        return jsonify({"message": "Data synchronization started"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
