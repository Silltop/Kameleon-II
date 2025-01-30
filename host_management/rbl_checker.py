import json
import os
from web.app import db, app

import dns.resolver


class RblChecker:
    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 0.10
        self.resolver.lifetime = 0.10

    @staticmethod
    def get_rbls_from_json():
        with open(f"{os.getcwd()}/inventory/rbl.json", "r") as f:
            file_data = json.load(f)
            return file_data    

    def check_rbl(self, ip):
        result = []
        from data_management.db_models import RblHosts
        with app.app_context():
            rblHostsList = db.session.query(RblHosts).all()
            for rblHost in rblHostsList:
                if rblHost.use:
                    result.append(self._check_single_rbl(ip, rblHost))
        return result

    def _check_single_rbl(self, ip, rblHost):
        ipRev = ".".join(ip.split(".")[::-1])
        searchQuery = ipRev + "." + rblHost.orgName
        try:
            self.resolver.resolve(searchQuery, "A")
            return {rblHost.orgName: 0}
        except:
            return {rblHost.orgName: 1}
