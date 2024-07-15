import glob
import os
from dataclasses import dataclass
from typing import List

import ansible_runner
import yaml
from ansible_wrapper import ansible_routes
from pathlib import Path
from ansible_runner import Runner
from ansible_wrapper.ansible_models import *
from api import app, db




@dataclass
class PlaybookDefinition:
    name: str
    host_group: str
    variables: List
    tasks: List


def run_ansible_playbook(playbook_id):
    # Fetch playbook information from the database
    playbook = AnsiblePlaybooks.query.get(playbook_id)
    if not playbook:
        raise ValueError(f"Playbook with ID {playbook_id} not found in the database")

    # Initialize Ansible run record in the database
    ansible_run = AnsibleRuns(
        playbook_id=playbook.playbook_id,
        start_time=datetime.datetime.utcnow(),
        result="Running",
        duration=0
    )
    db.session.add(ansible_run)
    db.session.commit()

    # Run Ansible playbook using ansible_runner
    print(f"{os.getcwd()}/tmp")
    r = ansible_runner.run(private_data_dir=f"{os.getcwd()}/tmp", playbook=playbook.playbook_path)
    print("{}: {}".format(r.status, r.rc))
    # successful: 0
    for each_host_event in r.events:
        print(each_host_event['event'])

    # Update final status based on playbook run result
    try:
        if r.rc == 0:
            ansible_run.result = "success"
        else:
            ansible_run.result = "failed"
    except Exception as e:
        ansible_run.result = f"Error: {str(e)}"
    finally:
        ansible_run.duration = (datetime.datetime.utcnow() - ansible_run.start_time).seconds
        db.session.commit()

    return ansible_run.id

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
        path_yaml = f'{playbook_location}/*.yaml'
        path_yml = f'{playbook_location}/*.yml'
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
                    print(f"ansible template: {ansible_template}")
                    playbook_model = AnsiblePlaybooks.query.filter_by(playbook_name=ansible_template.get("name")).first()
                    if playbook_model:
                        continue
                    new_playbook = AnsiblePlaybooks(playbook_name=ansible_template.get("name"), playbook_path=playbook)
                    db.session.add(new_playbook)
                    print(new_playbook)
            db.session.commit()


# PlaybookManager()
# db.create_all()
