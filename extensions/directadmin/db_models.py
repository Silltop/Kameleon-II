from web.app import db


class HostDAInfo(db.Model):
    host_ip = db.Column(db.String, primary_key=True)
    hostname = db.Column(db.String, nullable=False)


class DAUserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(
        db.Integer, db.ForeignKey("host_da_info.host_ip"), nullable=False
    )
    user_name = db.Column(db.String, nullable=False, default="Unknown")
    email = db.Column(db.String, nullable=False, default="Unknown")
    is_suspended = db.Column(db.Boolean)
    package = db.Column(db.String, nullable=False, default="Unknown")
    quota = db.Column(db.String, nullable=False, default="Unknown")


class Domains(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("da_user_details.id"), nullable=False)
    domain_name = db.Column(db.String, nullable=False, default="Unknown")
    dns_a = db.Column(db.String, nullable=False, default="Unknown")
    dns_mx = db.Column(db.String, nullable=False, default="Unknown")
    dns_ns = db.Column(db.String, nullable=False, default="Unknown")
