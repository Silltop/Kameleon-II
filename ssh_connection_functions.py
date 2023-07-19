import paramiko

import config
from utils import get_managed_hosts
from ssh_connection_functions_core import *


def check_mailing_services():
    dovecot = get_service_status('dovecot')
    exim = get_service_status('exim')
    spamassasin = get_service_status('spamassasin')

print(check_mailing_services())