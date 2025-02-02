import os
import time
import yaml
from flask import Blueprint, Response, request, stream_with_context
from flask import render_template, jsonify
from ansible_wrapper.ansible_init import PlaybookManager, run_ansible_playbook
from ansible_wrapper.ansible_models import AnsibleRuns, LogEntry
from ansible_wrapper.db_ops import fetch_playbook_runs
from configuration import logger
from ansible_wrapper.stream import generate_logs


ansible = Blueprint("ansible", __name__, url_prefix="/ansible", static_folder="static", template_folder="templates")


def calculate_duration(start_date, end_date):
    if start_date and end_date:
        duration = end_date - start_date
        return duration
    else:
        return None


@ansible.route("/wrapper-configuration", methods=["GET"])
def ansible_configuration():
    config_path = os.path.join(os.getcwd(), "ansible_wrapper", "ansible_configuration.yaml")
    with open(config_path) as file:
        config = yaml.safe_load(file)
    PlaybookManager()
    return render_template("ansible_configuration.html", config=config)


@ansible.route("/update_configuration", methods=["POST"])
def update_ansible_configuration():
    config_path = os.path.join(os.getcwd(), "ansible_wrapper", "ansible_configuration.yaml")
    with open(config_path, "w") as file:
        yaml.dump(request.json, file)
    return jsonify({"message": "Configuration updated"})


@ansible.route("/dashboard")
def ansible_dashboard():
    PlaybookManager()
    runs = fetch_playbook_runs()

    table_data = []

    for playbook, run in runs:
        start_time = run.start_time if run else "Never"
        end_time = run.end_time if run and run.end_time is not None else "Never"
        duration = "N/A"
        if start_time != "Never" and end_time != "Never":
            duration = calculate_duration(start_time, end_time)
        table_data.append(
            {
                "id": playbook.playbook_id,
                "playbook_name": playbook.playbook_name,
                "status": run.result if run else "unknown",
                "started_by": "user" if run else "N/A",  # Replace with actual user data if available
                "start": run.start_time.strftime("%Y-%m-%d %H:%M:%S") if run else "Never",
                "duration": duration,
            }
        )
    return render_template("ansible_dashboard.html", table_data=table_data)


@ansible.route("/recent_run_status/<int:playbook_id>", methods=["GET"])
def recent_run_status(playbook_id):
    recent_run = AnsibleRuns.query.filter_by(playbook_id=playbook_id).order_by(AnsibleRuns.start_time.desc()).first()
    if recent_run:
        return jsonify(
            {
                "result": recent_run.result,
            }
        )
    else:
        return jsonify({"error": "No runs found for this playbook"}), 404


@ansible.route("/recent_run/<int:playbook_id>", methods=["GET"])
def get_recent_run(playbook_id):
    recent_run = AnsibleRuns.query.filter_by(playbook_id=playbook_id).order_by(AnsibleRuns.start_time.desc()).first()
    if recent_run:
        return jsonify(
            {
                "id": recent_run.id,
                "playbook_id": recent_run.playbook_id,
                "start_time": recent_run.start_time,
                "result": recent_run.result,
                "duration": recent_run.duration,
            }
        )
    else:
        return jsonify({"error": "No runs found for this playbook"}), 404


@ansible.route("/run_playbook/<int:playbook_id>", methods=["GET"])
def run_playbook(playbook_id):
    try:
        logger.debug(f"Starting runbook with id {playbook_id}")
        ansible_run_id = run_ansible_playbook(playbook_id)
        return jsonify({"status": "started", "run_id": ansible_run_id}), 202
    except Exception as e:
        logger.debug(f"Error {e}")
        return jsonify({"error": str(e)}), 400


@ansible.route("/logs/<int:playbook_id>", methods=["GET"])
def get_logs(playbook_id):
    ansible_run = AnsibleRuns.query.filter_by(playbook_id=playbook_id).order_by(AnsibleRuns.start_time.desc()).first()
    if not ansible_run:
        return jsonify([])  # Return empty array if no runs found
    logs = LogEntry.query.filter_by(ansible_run_id=ansible_run.id).all()
    return jsonify([log.message for log in logs])


@ansible.route("/display_logs/<int:playbook_id>", methods=["GET"])
def display_logs(playbook_id):
    return render_template("log_display.html", playbook_id=playbook_id)


@ansible.route("/logs-stream/<int:ansible_run_id>")
def stream_logs(ansible_run_id):
    ansible_run = AnsibleRuns.query.get(ansible_run_id)
    time.sleep(2)
    return Response(stream_with_context(generate_logs(ansible_run, ansible_run_id)), content_type="text/event-stream")
