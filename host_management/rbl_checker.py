import sys

from web.app import db, app
from data_management.db_models import RblHosts

# Loading dns module.
try:
    import dns.resolver

    resolver = dns.resolver.Resolver()
    resolver.timeout = 0.10
    resolver.lifetime = 0.10
except Exception as exception_details:
    print(f"{exception_details}")
    sys.exit(0)


def check_rbl(ip):
    result = []
    with app.app_context():
        rblHostsList = db.session.query(RblHosts).all()
        for rblHost in rblHostsList:
            if rblHost.use:
                ipRev = ".".join(ip.split(".")[::-1])
                searchQuery = ipRev + "." + rblHost.orgName
                try:
                    resolver.resolve(searchQuery, "A")
                    result.append({rblHost.orgName: 0})
                except:
                    result.append({rblHost.orgName: 1})

        return result
