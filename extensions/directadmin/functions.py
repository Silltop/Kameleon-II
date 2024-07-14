from api.routes import render_template
from connectors.os import remote_data_processor
from api.app import app, db
from connectors.os.os_connector import execute_command_v2
from extensions.directadmin.database_model import HostDAInfo, DAUserDetails


@app.route("/da-users")
def da_users_dashboard():
    return render_template("da_users_dashboard.html")


@app.route("/da-sync")
def sync_da():
    with app.app_context():
        dar = DAReport()

        hostnames = dar.get_hostname_if_da_present()
        da_users = dar.get_da_users()
        da_user_email = dar.get_user_email()
        da_users_domains = dar.get_user_domains()
        da_suspended_users = dar.suspended_user()
        da_user_quota = dar.get_user_quota()
        da_user_packages = dar.get_user_package()
        print(f"HOSTNAME: {hostnames}")
        print(f"USERS: {da_users}")
        print(f"EMAILS: {da_user_email}")
        print(f"DOMAINS: {da_users_domains}")
        print(f"SUS: {da_suspended_users}")
        print(f"QUOTA: {da_user_quota}")
        print(f"PACKAGES: {da_user_packages}")
        valid_da_hosts = []
        for ip, hostname in dar.get_hostname_if_da_present().items():
            if hostname == "":
                continue
            print(ip)
            valid_da_hosts.append(hostname)
            host_id = HostDAInfo.query.filter_by(host_ip=ip).first()
            if host_id is None:
                hdi = HostDAInfo(host_ip=ip, hostname=hostname)
                db.session.add(hdi)
            current_users = da_users.get(ip)
            print(f"current users {current_users}")
            emails = da_user_email.get(ip).split('\n')
            for entry in emails:
                user, email = entry.split(':')
            print(f"e : {user}, {email}")
            dad = DAUserDetails(host_id=ip, user_name=da_users.get(ip),
                                email=da_user_email.get(ip), is_suspended=da_suspended_users.get(ip),
                                package=da_user_packages.get(ip), quota=da_user_quota.get(ip)
                                )
            # db.session.add(dad)

    # device_entry = HostDevices.query.filter_by(name=device_details.get('device')).filter_by(
    #     host_id=host_id.id).first()
    # if device_entry is None:
    # host_facts = HostFacts.query.filter_by(host_id=host.id).first()
        db.session.commit()
    return "ok"


class DAReport:
    def __init__(self):
        self.users = []

    @staticmethod
    def get_hostname_if_da_present():
        command = '[ -x /usr/local/directadmin/directadmin ] && hostname || echo ""'
        hom = execute_command_v2(command, default_on_error="")
        return hom.get_output_per_host(merge_output=True)

    @staticmethod
    def get_da_users():
        command = "find /usr/local/directadmin/data/users -mindepth 1 -maxdepth 1 -type d -printf '%f\n'"
        hom = execute_command_v2(command, default_on_error="")
        return hom.get_output_per_host()

    @staticmethod
    def get_user_email():
        command = '''for user in /usr/local/directadmin/data/users/*; do user=${user##*/}; [ "$user" != "root" ] && [ \
                  "$user" != "admin" ] && path="/usr/local/directadmin/data/users/$user/user.conf"; [ -f "$path" ] \
                  && email=$(cat "$path" | grep "email=" | sed "s/email=//;s/\\\\n//") && echo "$user: $email"; done'''
        hom = execute_command_v2(command, default_on_error="")
        return hom.get_output_per_host(merge_output=True)

    @staticmethod
    def get_user_domains():
        command = '''output=$(for path in /usr/local/directadmin/data/users/*/domains.list; do [ -f "$path" ] && \
                  user=$(echo "$path" | awk -F/ '{print $(NF-1)}') && domains=$(cat "$path") && echo "$user: \
                  $domains"; done); echo "$output"'''
        return remote_data_processor.execute_command(command)

    @staticmethod
    def suspended_user():
        command = '''output=$(for path in /usr/local/directadmin/data/users/*/user.conf; do [ -f "$path" ] && user=$( \
                  echo "$path" | awk -F/ '{print $(NF-1)}') && grep -q "suspended=yes" "$path" && echo "$user: True" \
                  || echo "$user: False"; done); echo "$output"'''
        return remote_data_processor.execute_command(command)

    @staticmethod
    def get_user_quota():
        command = '''output=$(for path in /usr/local/directadmin/data/users/*/user.usage; do [ -f "$path" ] && user=$( \
                  echo "$path" | awk -F/ '{print $(NF-1)}') && nemails=$(grep -oP "nemails=\\K\\d+\\w*" "$path") && \
                  echo "$user: $nemails"; done); echo "$output"'''
        return remote_data_processor.execute_command(command)

    @staticmethod
    def get_user_package():
        command = 'output=$(for user in /usr/local/directadmin/data/users/*; do user=${user##*/}; ' \
                  'path="/usr/local/directadmin/data/users/$user/user.conf"; [ -f "$path" ] && package=$(grep ' \
                  '"package=" "$path" | sed "s/package=//") && echo "$user: $package"; done); echo "$output"'
        return remote_data_processor.execute_command(command)
