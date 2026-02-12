from connectors.api.api_connector import ApiConnector


def check_mailing_services(host: tuple[str]) -> list[tuple[str, str, str]]:
    dovecot = ApiConnector().call_hosts("/service-status/dovecot", hosts=host)
    exim = ApiConnector().call_hosts("/service-status/exim4", hosts=host)
    spamassasin = ApiConnector().call_hosts("/service-status/spamassasin", hosts=host)
    dicts = [dovecot, exim, spamassasin]
    combined_dict = {}
    for d in dicts:
        for key, value in d.items():
            combined_dict.setdefault(key, {}).update(value)
    status_list = []
    for host, services in combined_dict.items():
        status = "OK"
        details = ""
        for _, service_status in services.items():
            if "running" not in service_status:
                status = "NOK"
                details += f"{service_status}, "
        status_list.append([host, status, details])
    return status_list
