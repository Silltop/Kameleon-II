import logging
from typing import Dict
import requests
from configuration import config
from connectors.connector import Connector
import jwt
import datetime

SECRET_KEY = 'your_secret_key'


class TokenManager:
    def __init__(self, secret_keys):
        self.secret_keys = secret_keys  # Dictionary mapping host IDs to their secret keys
        self.token_store = {}  # To store generated tokens temporarily

    def generate_token(self, host_id):
        if host_id not in self.secret_keys:
            raise ValueError("Invalid host ID")

        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # Token valid for 1 hour
            'iat': datetime.datetime.utcnow(),
            'sub': host_id  # Host identifier
        }
        token = jwt.encode(payload, self.secret_keys[host_id], algorithm='HS256')
        self.token_store[host_id] = token  # Store the token
        return token

    def get_valid_token(self, host_id):
        # If no token exists or it has expired, generate a new one
        token = self.token_store.get(host_id)
        if not token or self.is_token_expired(token, host_id):
            return self.generate_token(host_id)
        return token

    def is_token_expired(self, token, host_id):
        try:
            jwt.decode(token, self.secret_keys[host_id], algorithms=["HS256"])
            return False  # Token is still valid
        except jwt.ExpiredSignatureError:
            return True  # Token has expired
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")  # Other token issues


class ApiConnector(Connector):
    def __init__(self):
        super().__init__()

    @staticmethod
    def call_endpoints(
            endpoint, hosts: tuple = None, method: str = "GET", data: dict = None, json_data: dict = None, https: bool = False
    ) -> Dict:
        if hosts is None:
            hosts = config.ConfigManager().ip_list

        protocol = "https" if https else "http"
        responses = {}
        for host in hosts:
            api_url = f"{protocol}://{host}:{6622}{endpoint}"
            try:
                response = requests.request(
                    method=method.upper(),  # Convert method to uppercase
                    url=api_url,
                    data=data,
                    json=json_data
                )
            except requests.exceptions.ConnectionError as e:
                logging.warning(f"Unable to connect to {api_url} {e}")
                continue
            if response.status_code == 211:
                continue
            responses[host] = response.json()
        return responses

    def call_hosts(self, endpoint):
        return self.call_endpoints(endpoint, method="GET")

