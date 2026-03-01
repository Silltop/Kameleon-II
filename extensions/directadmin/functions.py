from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from connectors.api.api_connector import ApiConnector
from web.views import extended_render_template
from extensions.directadmin.db_models import (
    DAUserDataSnapshot,
    DAAppsVersionSnapshot,
    DASuspendedUsersSnapshot,
    DAUserEmailsSnapshot,
    DAUserWebsitesSnapshot,
)
from web.app import db

plugin = Blueprint("da", __name__, url_prefix="/da", static_folder="static", template_folder="templates")


@plugin.route("/users")
def da_users_dashboard():
    # Load latest snapshot, or fetch fresh data if none exist
    latest_snapshot = DAUserDataSnapshot.query.order_by(DAUserDataSnapshot.snapshot_timestamp.desc()).first()
    if latest_snapshot:
        data = latest_snapshot.data
    else:
        data = ApiConnector().call_hosts("/get-da-all-info")
        snapshot = DAUserDataSnapshot(data=data)
        db.session.add(snapshot)
        db.session.commit()
    return extended_render_template("da_users_dashboard.html", data=data)


@plugin.route("/api/user-snapshots")
def get_user_snapshots():
    """Get list of available data snapshots with timestamps"""
    snapshots = DAUserDataSnapshot.query.order_by(DAUserDataSnapshot.snapshot_timestamp.desc()).all()
    return jsonify([
        {
            "id": s.id,
            "timestamp": s.snapshot_timestamp.isoformat(),
            "created_at": s.created_at.isoformat(),
            "display": s.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for s in snapshots
    ])


@plugin.route("/api/user-snapshot/<int:snapshot_id>")
def get_user_snapshot(snapshot_id):
    """Get specific snapshot data by ID"""
    snapshot = DAUserDataSnapshot.query.get(snapshot_id)
    if not snapshot:
        return jsonify({"error": "Snapshot not found"}), 404
    return jsonify({"data": snapshot.data, "timestamp": snapshot.snapshot_timestamp.isoformat()})


@plugin.route("/api/refresh-snapshot")
def refresh_snapshot():
    """Force create a new snapshot of current data"""
    try:
        data = ApiConnector().call_hosts("/get-da-all-info")
        snapshot = DAUserDataSnapshot(data=data)
        db.session.add(snapshot)
        db.session.commit()
        return jsonify({
            "status": "success",
            "snapshot": {
                "id": snapshot.id,
                "timestamp": snapshot.snapshot_timestamp.isoformat(),
                "display": snapshot.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plugin.route("/apps-versions")
def da_apps_versions():
    # Load latest snapshot, or fetch fresh data if none exist
    latest_snapshot = DAAppsVersionSnapshot.query.order_by(DAAppsVersionSnapshot.snapshot_timestamp.desc()).first()
    if latest_snapshot:
        data = latest_snapshot.data
    else:
        data = ApiConnector().call_hosts("/provide-da-apps-versions")
        snapshot = DAAppsVersionSnapshot(data=data)
        db.session.add(snapshot)
        db.session.commit()
    table_headers = ["Server"] + list(next(iter(data.values())).keys()) if data else []
    return extended_render_template("da_apps_versions.html", table_headers=table_headers, table_data=data)


@plugin.route("/api/apps-versions-snapshots")
def get_apps_versions_snapshots():
    snapshots = DAAppsVersionSnapshot.query.order_by(DAAppsVersionSnapshot.snapshot_timestamp.desc()).all()
    return jsonify([
        {
            "id": s.id,
            "timestamp": s.snapshot_timestamp.isoformat(),
            "display": s.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for s in snapshots
    ])


@plugin.route("/api/apps-versions-snapshot/<int:snapshot_id>")
def get_apps_versions_snapshot(snapshot_id):
    snapshot = DAAppsVersionSnapshot.query.get(snapshot_id)
    if not snapshot:
        return jsonify({"error": "Snapshot not found"}), 404
    return jsonify({"data": snapshot.data, "timestamp": snapshot.snapshot_timestamp.isoformat()})


@plugin.route("/api/refresh-apps-versions-snapshot")
def refresh_apps_versions_snapshot():
    try:
        data = ApiConnector().call_hosts("/provide-da-apps-versions")
        snapshot = DAAppsVersionSnapshot(data=data)
        db.session.add(snapshot)
        db.session.commit()
        return jsonify({
            "status": "success",
            "snapshot": {
                "id": snapshot.id,
                "timestamp": snapshot.snapshot_timestamp.isoformat(),
                "display": snapshot.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plugin.route("/suspended-users")
def sync_da():
    # Load latest snapshot, or fetch fresh data if none exist
    latest_snapshot = DASuspendedUsersSnapshot.query.order_by(DASuspendedUsersSnapshot.snapshot_timestamp.desc()).first()
    if latest_snapshot:
        data = latest_snapshot.data
    else:
        data = ApiConnector().call_hosts("/get-suspended-users")
        snapshot = DASuspendedUsersSnapshot(data=data)
        db.session.add(snapshot)
        db.session.commit()
    return extended_render_template("da_suspended_dashboard.html", data=data)


@plugin.route("/api/suspended-users-snapshots")
def get_suspended_users_snapshots():
    snapshots = DASuspendedUsersSnapshot.query.order_by(DASuspendedUsersSnapshot.snapshot_timestamp.desc()).all()
    return jsonify([
        {
            "id": s.id,
            "timestamp": s.snapshot_timestamp.isoformat(),
            "display": s.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for s in snapshots
    ])


@plugin.route("/api/suspended-users-snapshot/<int:snapshot_id>")
def get_suspended_users_snapshot(snapshot_id):
    snapshot = DASuspendedUsersSnapshot.query.get(snapshot_id)
    if not snapshot:
        return jsonify({"error": "Snapshot not found"}), 404
    return jsonify({"data": snapshot.data, "timestamp": snapshot.snapshot_timestamp.isoformat()})


@plugin.route("/api/refresh-suspended-users-snapshot")
def refresh_suspended_users_snapshot():
    try:
        data = ApiConnector().call_hosts("/get-suspended-users")
        snapshot = DASuspendedUsersSnapshot(data=data)
        db.session.add(snapshot)
        db.session.commit()
        return jsonify({
            "status": "success",
            "snapshot": {
                "id": snapshot.id,
                "timestamp": snapshot.snapshot_timestamp.isoformat(),
                "display": snapshot.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plugin.route("/user-emails")
def da_emails():
    # Load latest snapshot, or fetch fresh data if none exist
    latest_snapshot = DAUserEmailsSnapshot.query.order_by(DAUserEmailsSnapshot.snapshot_timestamp.desc()).first()
    if latest_snapshot:
        data = latest_snapshot.data
    else:
        data = ApiConnector().call_hosts("/get-da-user-emails")
        snapshot = DAUserEmailsSnapshot(data=data)
        db.session.add(snapshot)
        db.session.commit()
    table_headers = ["Email", "Alias", "Last Login", "Size"]
    return extended_render_template("da_user_emails.html", table_headers=table_headers, table_data=data)


@plugin.route("/api/user-emails-snapshots")
def get_user_emails_snapshots():
    snapshots = DAUserEmailsSnapshot.query.order_by(DAUserEmailsSnapshot.snapshot_timestamp.desc()).all()
    return jsonify([
        {
            "id": s.id,
            "timestamp": s.snapshot_timestamp.isoformat(),
            "display": s.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for s in snapshots
    ])


@plugin.route("/api/user-emails-snapshot/<int:snapshot_id>")
def get_user_emails_snapshot(snapshot_id):
    snapshot = DAUserEmailsSnapshot.query.get(snapshot_id)
    if not snapshot:
        return jsonify({"error": "Snapshot not found"}), 404
    return jsonify({"data": snapshot.data, "timestamp": snapshot.snapshot_timestamp.isoformat()})


@plugin.route("/api/refresh-user-emails-snapshot")
def refresh_user_emails_snapshot():
    try:
        data = ApiConnector().call_hosts("/get-da-user-emails")
        snapshot = DAUserEmailsSnapshot(data=data)
        db.session.add(snapshot)
        db.session.commit()
        return jsonify({
            "status": "success",
            "snapshot": {
                "id": snapshot.id,
                "timestamp": snapshot.snapshot_timestamp.isoformat(),
                "display": snapshot.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@plugin.route("/user-websites")
def da_websites():
    # Load latest snapshot, or fetch fresh data if none exist
    latest_snapshot = DAUserWebsitesSnapshot.query.order_by(DAUserWebsitesSnapshot.snapshot_timestamp.desc()).first()
    if latest_snapshot:
        data = latest_snapshot.data
    else:
        data = ApiConnector().call_hosts("/get-da-all-info")
        snapshot = DAUserWebsitesSnapshot(data=data)
        db.session.add(snapshot)
        db.session.commit()
    table_headers = ["User", "Domain", "PHP Version", "Subdomains", "A Records", "MX Records", "NS Records"]
    return extended_render_template("da_user_websites.html", table_headers=table_headers, table_data=data)


@plugin.route("/api/user-websites-snapshots")
def get_user_websites_snapshots():
    snapshots = DAUserWebsitesSnapshot.query.order_by(DAUserWebsitesSnapshot.snapshot_timestamp.desc()).all()
    return jsonify([
        {
            "id": s.id,
            "timestamp": s.snapshot_timestamp.isoformat(),
            "display": s.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for s in snapshots
    ])


@plugin.route("/api/user-websites-snapshot/<int:snapshot_id>")
def get_user_websites_snapshot(snapshot_id):
    snapshot = DAUserWebsitesSnapshot.query.get(snapshot_id)
    if not snapshot:
        return jsonify({"error": "Snapshot not found"}), 404
    return jsonify({"data": snapshot.data, "timestamp": snapshot.snapshot_timestamp.isoformat()})


@plugin.route("/api/refresh-user-websites-snapshot")
def refresh_user_websites_snapshot():
    try:
        data = ApiConnector().call_hosts("/get-da-all-info")
        snapshot = DAUserWebsitesSnapshot(data=data)
        db.session.add(snapshot)
        db.session.commit()
        return jsonify({
            "status": "success",
            "snapshot": {
                "id": snapshot.id,
                "timestamp": snapshot.snapshot_timestamp.isoformat(),
                "display": snapshot.snapshot_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

