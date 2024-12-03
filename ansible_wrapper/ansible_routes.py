import base64
import logging
import os
import time

import yaml
from flask import Response, stream_with_context
from flask import render_template, jsonify

from ansible_wrapper.ansible_init import PlaybookManager, run_ansible_playbook
from ansible_wrapper.ansible_models import AnsibleRuns, AnsiblePlaybooks, LogEntry
from web.app import app, db
from configuration import logger


# fix me
# https://stackoverflow.com/questions/41599500/flask-getting-url-prefix-for-blueprint-in-view


def calculate_duration(start_date, end_date):
    if start_date and end_date:
        duration = end_date - start_date
        return duration
    else:
        return None


@app.route("/ansible-wrapper-configuration")
def ansible_configuration():
    config_path = os.path.join(
        os.getcwd(), "ansible_wrapper", "ansible_configuration.yaml"
    )
    with open(config_path) as file:
        config = yaml.safe_load(file)
    PlaybookManager()
    return render_template("ansible_configuration.html", config=config)


@app.route("/ansible-dashboard")
def ansible_dashboard():
    PlaybookManager()
    subquery = (
        db.session.query(
            AnsibleRuns.playbook_id,
            db.func.max(AnsibleRuns.start_time).label("max_start_time"),
        )
        .group_by(AnsibleRuns.playbook_id)
        .subquery()
    )

    runs = (
        db.session.query(AnsiblePlaybooks, AnsibleRuns)
        .outerjoin(subquery, (AnsiblePlaybooks.playbook_id == subquery.c.playbook_id))
        .outerjoin(
            AnsibleRuns,
            (AnsiblePlaybooks.playbook_id == AnsibleRuns.playbook_id)
            & (AnsibleRuns.start_time == subquery.c.max_start_time),
        )
        .all()
    )

    table_data = []

    for playbook, run in runs:
        start_time = run.start_time if run else "Never"
        end_time = run.end_time if run and run.end_time is not None else "Never"
        duration = "N/A"
        if start_time != "Never" and end_time != "Never":
            print(start_time, end_time)
            duration = calculate_duration(start_time, end_time)
        table_data.append(
            {
                "id": playbook.playbook_id,
                "playbook_name": playbook.playbook_name,
                "status": run.result if run else "unknown",
                "started_by": "user"
                if run
                else "N/A",  # Replace with actual user data if available
                "start": run.start_time.strftime("%Y-%m-%d %H:%M:%S")
                if run
                else "Never",
                "duration": duration,
            }
        )
    return render_template("ansible_dashboard.html", table_data=table_data)


@app.route("/recent_run_status/<int:playbook_id>", methods=["GET"])
def recent_run_status(playbook_id):
    recent_run = (
        AnsibleRuns.query.filter_by(playbook_id=playbook_id)
        .order_by(AnsibleRuns.start_time.desc())
        .first()
    )
    if recent_run:
        return jsonify(
            {
                "result": recent_run.result,
            }
        )
    else:
        return jsonify({"error": "No runs found for this playbook"}), 404


@app.route("/recent_run/<int:playbook_id>", methods=["GET"])
def get_recent_run(playbook_id):
    recent_run = (
        AnsibleRuns.query.filter_by(playbook_id=playbook_id)
        .order_by(AnsibleRuns.start_time.desc())
        .first()
    )
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


@app.route("/run_playbook/<int:playbook_id>", methods=["GET"])
def run_playbook(playbook_id):
    try:
        logger.debug(f"Starting runbook with id {playbook_id}")
        ansible_run_id = run_ansible_playbook(playbook_id)
        return jsonify({"status": "started", "run_id": ansible_run_id}), 202
    except Exception as e:
        logger.debug(f"Error {e}")
        return jsonify({"error": str(e)}), 400


@app.route("/logs/<int:playbook_id>", methods=["GET"])
def get_logs(playbook_id):
    # Get the most recent Ansible run
    ansible_run = (
        AnsibleRuns.query.filter_by(playbook_id=playbook_id)
        .order_by(AnsibleRuns.start_time.desc())
        .first()
    )
    if not ansible_run:
        return jsonify([])  # Return empty array if no runs found
    logs = LogEntry.query.filter_by(ansible_run_id=ansible_run.id).all()
    return jsonify([log.message for log in logs])


@app.route("/display_logs/<int:playbook_id>", methods=["GET"])
def display_logs(playbook_id):
    return render_template("log_display.html", playbook_id=playbook_id)


@app.route("/logs-stream/<int:ansible_run_id>")
def stream_logs(ansible_run_id):
    ansible_run = AnsibleRuns.query.get(ansible_run_id)
    time.sleep(2)

    def generate_logs():
        last_sent_id = None  # This will track the ID of the last sent log entry
        with app.app_context():
            time_string = (
                f'Runbook started at <span class="cyan">{ansible_run.start_time}</span>'
            )
            yield f"data: {base64.b64encode(time_string.encode('utf-8')).decode('utf-8')}\n\n"
        while True:
            if last_sent_id:
                log_entries = LogEntry.query.filter(
                    LogEntry.ansible_run_id == ansible_run_id,
                    LogEntry.id > last_sent_id,
                ).all()  # noqa E501
            else:
                log_entries = LogEntry.query.filter_by(
                    ansible_run_id=ansible_run_id
                ).all()
            if log_entries:
                logging.debug(
                    f"Found {len(log_entries)} new log entries. sending stream..."
                )

                for log in log_entries:
                    encoded_message = base64.b64encode(
                        log.message.encode("utf-8")
                    ).decode("utf-8")
                    yield f"data: {encoded_message}\n\n"
                    last_sent_id = log.id

            elif ansible_run.result != "running":
                yield f"event: close\ndata: Playbook completed with result: {ansible_run.result}\n\n"
                logging.debug("Closing stream.")
                break  # Exit the loop to end the stream
            time.sleep(0.5)

    return Response(
        stream_with_context(generate_logs()), content_type="text/event-stream"
    )
