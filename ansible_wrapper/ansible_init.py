import glob
import os
from dataclasses import dataclass
from typing import List

from ansible_wrapper import ansible_routes
from pathlib import Path


@dataclass
class PlaybookDefinition:
    name: str
    host_group: str
    variables: List
    tasks: List


class PlaybookManager:
    def __init__(self, playbook_location="playbooks"):
        print(__file__)
        print(os.getcwd())
        if not Path(playbook_location).is_absolute():
            self.playbook_location = os.path.abspath(playbook_location)
        else:
            self.playbook_location = playbook_location
        self.playbook_definitions: List[PlaybookDefinition] = []
        self.load_playbook_definition()

    @staticmethod
    def get_playbook_list(playbook_location) -> List:
        print(playbook_location)
        path_yaml = f'{playbook_location}/*.yaml'
        path_yml = f'{playbook_location}/*.yml'
        files = glob.glob(path_yaml) + glob.glob(path_yml)
        return files

    def load_playbook_definition(self):
        playbook_list = self.get_playbook_list(self.playbook_location)
        print(playbook_list)


PlaybookManager()
# db.create_all()
