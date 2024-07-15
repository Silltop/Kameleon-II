from flask import render_template, jsonify, redirect, url_for

from ansible_wrapper.ansible_init import PlaybookManager, run_ansible_playbook
from ansible_wrapper.ansible_models import AnsibleRuns, AnsiblePlaybooks
from api.app import app, db, cache
from configuration.config import ConfigManager


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
        table_data.append({
            'id': playbook.playbook_id,
            'playbook_name': playbook.playbook_name,
            'status': run.result if run else "unknown",
            'started_by': 'user' if run else "N/A",  # Replace with actual user data if available
            'start': run.start_time.strftime("%Y-%m-%d %H:%M:%S") if run else "Never",
            'duration': run.duration if run else "N/A"
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
    print(playbook_id)
    run_ansible_playbook(playbook_id)
    return redirect(url_for('ansible_dashboard'))