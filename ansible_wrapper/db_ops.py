from web.db_init import db
from ansible_wrapper.ansible_models import AnsibleRuns, AnsiblePlaybooks


def fetch_playbook_runs():
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
    return runs
