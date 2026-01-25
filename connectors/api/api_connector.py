import logging
from typing import Dict, Optional
import requests
from configuration import config
from connectors.connector import Connector
import jwt
import datetime
import hashlib
import threading
from werkzeug.exceptions import Unauthorized

SECRET_KEY = "your_secret_key"


class TokenManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):  # Ensure __init__ is only called once
            self.secret_keys = None  # secret_keys  # Dictionary mapping host IDs to their secret keys
            self.token_store = {}  # To store generated tokens temporarily
            self.initialized = True

    def generate_token(self, host_id):
        # if host_id not in self.secret_keys:
        #     raise ValueError("Invalid host ID")

        payload = {
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),  # Token valid for 1 hour
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "sub": host_id,  # Host identifier
        }
        # todo unique token for each host
        # token = jwt.encode(payload, self.secret_keys[host_id], algorithm="HS256")
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
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
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return False  # Token is still valid
        except jwt.ExpiredSignatureError:
            return True  # Token has expired
        except jwt.InvalidTokenError:
            raise Unauthorized from jwt.InvalidTokenError


class ApiConnector(Connector):
    def __init__(self):
        super().__init__()
        self.token_manager = TokenManager()
        self.api_key = "your_api_key_here"

    def create_headers(self) -> dict[str, str]:
        hashed_api_key = hashlib.sha256(self.api_key.encode()).hexdigest()
        headers = {"X-API-KEY": hashed_api_key, "Content-Type": "application/json"}
        return headers

    def call_endpoints(
        self,
        endpoint,
        hosts: Optional[tuple] = None,
        method: str = "GET",
        data: Optional[dict] = None,
        json_data: Optional[dict] = None,
        https: bool = False,
    ) -> dict:
        if hosts is None:
            hosts = config.ConfigManager().ip_list

        protocol = "https" if https else "http"
        responses = {}
        for host in hosts:
            api_url = self.construct_api_url(protocol, host, endpoint)
            headers = self.create_headers_with_token(host)
            response = self.make_request(api_url, method, headers, data, json_data)
            if response:
                responses[host] = response.json()
        return responses

    def construct_api_url(self, protocol, host, endpoint):
        return f"{protocol}://{host}:{6622}{endpoint}"

    def create_headers_with_token(self, host):
        token = self.token_manager.get_valid_token(host)
        headers = self.create_headers()
        headers["Authorization"] = f"Bearer {token}"
        return headers

    def make_request(self, api_url, method, headers, data, json_data):
        try:
            response = requests.request(
                method=method.upper(),  # Convert method to uppercase
                url=api_url,
                headers=headers,
                data=data,
                json=json_data,
                timeout=60,
            )
            if response.status_code == 211:
                return None
            return response
        except requests.exceptions.ConnectionError as e:
            logging.warning(f"Unable to connect to {api_url} {e}")
            return None

    def call_hosts(self, endpoint, method="GET"):
        return self.call_endpoints(endpoint, method=method)

    def call_host(self, endpoint, host, method="GET"):
        return self.call_endpoints(endpoint, hosts=(host,), method=method)
