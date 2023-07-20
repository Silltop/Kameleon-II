from ssh_connection_functions_core import get_service_status


def check_mailing_services():
    dovecot = get_service_status('dovecot')
    exim = get_service_status('exim')
    spamassasin = get_service_status('spamassasin')
    dicts=[dovecot,exim,spamassasin]
    combined_dict = {}
    for d in dicts:
        for key, value in d.items():
            combined_dict.setdefault(key, {}).update(value)
    status_list = []
    for host, services in combined_dict.items():
        status = 'OK'
        details = ""
        for service, service_status in services.items():
            if 'running' not in service_status:
                status = 'NOK'
                details += f"{service_status}, "
        status_list.append([host, status, details])
    return status_list
