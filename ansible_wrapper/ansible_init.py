import datetime
import glob
import logging
import os
import threading
from dataclasses import dataclass
from typing import List
import ansible_runner
import yaml
from ansible_wrapper.ansible_models import AnsibleRuns, AnsiblePlaybooks, LogEntry
from web.db_init import db
from web.app import app


@dataclass
class PlaybookDefinition:
    name: str
    host_group: str
    variables: List
    tasks: List


def run_playbook(playbook_id, ansible_run_id, playbook_path):
    logger = logging.getLogger("Worker")
    logger.critical("Worker spawned.")
    with app.app_context():
        try:
            ansible_run = fetch_ansible_run(ansible_run_id)
            if not ansible_run:
                raise ValueError(f"Ansible run with ID {ansible_run_id} not found")

            ansible_run.result = "running"
            db.session.commit()

            r = execute_playbook(playbook_path, playbook_id, ansible_run_id)
            logger.info(f"{r.status}: {r.rc}")

            for each_host_event in r.events:
                logger.info(each_host_event["event"])

            update_ansible_run_result(ansible_run, r.rc)
        except Exception as e:
            logger.error(f"Error running playbook: {e}")
            ansible_run.result = f"Error: {str(e)}"
        finally:
            finalize_ansible_run(ansible_run)


def fetch_ansible_run(ansible_run_id):
    return AnsibleRuns.query.get(ansible_run_id)


def execute_playbook(playbook_path, playbook_id, ansible_run_id):
    def callback(event_data):
        stdout_str = event_data.get("stdout")
        if stdout_str:
            with app.app_context():
                log_entry = LogEntry(
                    playbook_id=playbook_id,
                    ansible_run_id=ansible_run_id,
                    message=stdout_str,
                )
                db.session.add(log_entry)
                db.session.commit()

    return ansible_runner.run(
        private_data_dir=f"{os.getcwd()}/tmp",
        playbook=playbook_path,
        event_handler=callback,
    )


def update_ansible_run_result(ansible_run, return_code):
    if return_code == 0:
        ansible_run.result = "success"
    else:
        ansible_run.result = "failed"
    db.session.commit()


def finalize_ansible_run(ansible_run):
    with app.app_context():
        ansible_run.end_time = datetime.datetime.now(datetime.timezone.utc)
        db.session.commit()


def run_ansible_playbook(playbook_id):
    # Fetch playbook information from the database
    logger = logging.getLogger("Ansible")
    logger.setLevel(logging.DEBUG)
    logger.propagate = True
    playbook = AnsiblePlaybooks.query.get(playbook_id)
    if not playbook:
        raise ValueError(f"Playbook with ID {playbook_id} not found in the database")
    with app.app_context():
        ansible_run = AnsibleRuns(
            playbook_id=playbook.playbook_id,
            start_time=datetime.datetime.utcnow(),
            result="Running",
            end_time=None,
        )
        db.session.add(ansible_run)
        db.session.commit()
        runid = ansible_run.id
        logging.info(f"Starting playbook thread for run {ansible_run.id}...")
        thread = threading.Thread(target=run_playbook, args=(playbook_id, runid, playbook.playbook_path))
        thread.daemon = True
        thread.start()
        return runid


class PlaybookManager:
    def __init__(self, playbook_location=""):
        print(__file__)
        print(os.getcwd())
        if playbook_location == "":
            self.playbook_location = os.path.join(os.getcwd(), "ansible_wrapper", "playbooks")
        else:
            self.playbook_location = playbook_location
        self.playbook_definitions: List[PlaybookDefinition] = []
        self.synchronize_to_db()

    @staticmethod
    def get_playbook_list(playbook_location) -> List:
        path_yaml = f"{playbook_location}/*.yaml"
        path_yml = f"{playbook_location}/*.yml"
        files = glob.glob(path_yaml) + glob.glob(path_yml)
        return files

    # def load_playbook_definition(self):
    #     playbook_list = self.get_playbook_list(self.playbook_location)
    #     print(playbook_list)

    def synchronize_to_db(self):
        with app.app_context():
            db.create_all()
            for playbook in self.get_playbook_list(self.playbook_location):
                with open(playbook) as file:
                    ansible_template = yaml.safe_load(file)[0]
                    playbook_model = AnsiblePlaybooks.query.filter_by(
                        playbook_name=ansible_template.get("name")
                    ).first()
                    if playbook_model:
                        continue
                    new_playbook = AnsiblePlaybooks(
                        playbook_name=ansible_template.get("name"),
                        playbook_path=playbook,
                    )
                    db.session.add(new_playbook)
            db.session.commit()
