import base64
import logging
import time
from web.app import app
from ansible_wrapper.ansible_models import LogEntry, AnsibleRuns, AnsibleRuns


def generate_logs(ansible_run: AnsibleRuns, ansible_run_id: int):
    last_sent_id = None  # This will track the ID of the last sent log entry
    with app.app_context():
        time_string = f'Runbook started at <span class="cyan">{ansible_run.start_time}</span>'
        yield f"data: {base64.b64encode(time_string.encode('utf-8')).decode('utf-8')}\n\n"
    while True:
        if last_sent_id:
            log_entries = LogEntry.query.filter(
                LogEntry.ansible_run_id == ansible_run_id,
                LogEntry.id > last_sent_id,
            ).all()  # noqa E501
        else:
            log_entries = LogEntry.query.filter_by(ansible_run_id=ansible_run_id).all()
        if log_entries:
            logging.debug(f"Found {len(log_entries)} new log entries. sending stream...")

            for log in log_entries:
                encoded_message = base64.b64encode(log.message.encode("utf-8")).decode("utf-8")
                yield f"data: {encoded_message}\n\n"
                last_sent_id = log.id

        elif ansible_run.result != "running":
            yield f"event: close\ndata: Playbook completed with result: {ansible_run.result}\n\n"
            logging.debug("Closing stream.")
            break  # Exit the loop to end the stream
        time.sleep(0.5)
