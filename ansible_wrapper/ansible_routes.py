from flask import render_template, jsonify, redirect, url_for

from ansible_wrapper.ansible_init import PlaybookManager, run_ansible_playbook
from ansible_wrapper.ansible_models import AnsibleRuns, AnsiblePlaybooks, LogEntry
from api.app import app, db, cache
from configuration import logger
from configuration.config import ConfigManager

def calculate_duration(start_date, end_date):
    if start_date and end_date:
        duration = end_date - start_date
        return duration
    else:
        return None

@app.route('/ansible-wrapper-configuration')
def ansible_configuration():
    PlaybookManager()
    return render_template('ansible_config_dashboard.html')

@app.route('/ansible-dashboard')
def ansible_dashboard():
    PlaybookManager()
    subquery = db.session.query(
        AnsibleRuns.playbook_id,
        db.func.max(AnsibleRuns.start_time).label('max_start_time')
    ).group_by(AnsibleRuns.playbook_id).subquery()

    runs = db.session.query(AnsiblePlaybooks, AnsibleRuns).outerjoin(
        subquery,
        (AnsiblePlaybooks.playbook_id == subquery.c.playbook_id)
    ).outerjoin(
        AnsibleRuns,
        (AnsiblePlaybooks.playbook_id == AnsibleRuns.playbook_id) &
        (AnsibleRuns.start_time == subquery.c.max_start_time)
    ).all()

    table_data = []

    for playbook, run in runs:
        start_time = run.start_time if run else "Never"
        end_time = run.end_time if run and run.end_time is not None else "Never"
        duration = "N/A"
        if start_time != "Never" and end_time != "Never":
            print(start_time, end_time)
            duration = calculate_duration(start_time, end_time)
        table_data.append({
            'id': playbook.playbook_id,
            'playbook_name': playbook.playbook_name,
            'status': run.result if run else "unknown",
            'started_by': 'user' if run else "N/A",  # Replace with actual user data if available
            'start': run.start_time.strftime("%Y-%m-%d %H:%M:%S") if run else "Never",
            'duration': duration
        })
    print(table_data)
    return render_template('ansible_dashboard.html', table_data=table_data)


@app.route('/recent_run/<int:playbook_id>', methods=['GET'])
def get_recent_run(playbook_id):
    recent_run = AnsibleRuns.query.filter_by(playbook_id=playbook_id).order_by(AnsibleRuns.start_time.desc()).first()
    if recent_run:
        return jsonify({
            'id': recent_run.id,
            'playbook_id': recent_run.playbook_id,
            'start_time': recent_run.start_time,
            'result': recent_run.result,
            'duration': recent_run.duration
        })
    else:
        return jsonify({'error': 'No runs found for this playbook'}), 404

@app.route('/run_playbook/<int:playbook_id>', methods=['GET'])
def run_playbook(playbook_id):
    logger.debug(f"Starting runbook with id {playbook_id}")
    run_ansible_playbook(playbook_id)
    return jsonify({'message': 'Runbook will start shortly...'}), 200

@app.route('/logs/<int:playbook_id>', methods=['GET'])
def get_logs(playbook_id):
    # Get the most recent Ansible run
    ansible_run = AnsibleRuns.query.filter_by(playbook_id=playbook_id).order_by(AnsibleRuns.start_time.desc()).first()
    if not ansible_run:
        return jsonify([])  # Return empty array if no runs found

    # Get logs for the most recent run
    logs = LogEntry.query.filter_by(ansible_run_id=ansible_run.id).all()
    return jsonify([log.message for log in logs])

@app.route('/display_logs/<int:playbook_id>', methods=['GET'])
def display_logs(playbook_id):
    return render_template('log_display.html', playbook_id=playbook_id)