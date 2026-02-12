import datetime
import hashlib
import hmac
import json
import logging
import threading
import time
from typing import Optional

import jwt
import requests
from configuration import config
from connectors.connector import Connector
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
        self.hmac_key_id = "default"
        self.hmac_secret = "your_hmac_secret_here"

    def create_headers(self) -> dict[str, str]:
        hashed_api_key = hashlib.sha256(self.api_key.encode()).hexdigest()
        headers = {"X-API-KEY": hashed_api_key, "Content-Type": "application/json"}
        return headers

    def _build_hmac_headers(self, method: str, path: str, body: str) -> dict[str, str]:
        timestamp = str(int(time.time()))
        message = f"{method}\n{path}\n{timestamp}\n{body}".encode()
        signature = hmac.new(self.hmac_secret.encode(), message, hashlib.sha256).hexdigest()
        return {
            "X-KEY-ID": self.hmac_key_id,
            "X-TIMESTAMP": timestamp,
            "X-SIGNATURE": signature,
        }

    def _serialize_body(self, data: Optional[dict], json_data: Optional[dict]) -> str:
        if json_data is not None:
            return json.dumps(json_data, separators=(",", ":"), sort_keys=True)
        if data is not None:
            return json.dumps(data, separators=(",", ":"), sort_keys=True)
        return ""

    def call_endpoints(
        self,
        endpoint: str,
        hosts: Optional[tuple] = None,
        method: str = "GET",
        data: Optional[dict] = None,
        json_data: Optional[dict] = None,
        https: bool = False,
    ) -> dict[str, dict]:
        if hosts is None:
            hosts = config.ConfigManager().ip_list

        protocol = "https" if https else "http"
        responses = {}
        threads = []
        lock = threading.Lock()
        
        body = self._serialize_body(data, json_data)

        def call_single_host(host: str) -> None:
            api_url = self.construct_api_url(protocol, host, endpoint)
            headers = self.create_headers_with_token(host, method, endpoint, body)
            response = self.make_request(api_url, method, headers, body)
            if response:
                with lock:
                    responses[host] = response.json()
        
        for host in hosts:
            thread = threading.Thread(target=call_single_host, args=(host,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        return responses

    def construct_api_url(self, protocol: str, host: str, endpoint: str) -> str:
        return f"{protocol}://{host}:{6622}{endpoint}"

    def create_headers_with_token(self, host: str, method: str, path: str, body: str) -> dict[str, str]:
        token = self.token_manager.get_valid_token(host)
        headers = self.create_headers()
        headers.update(self._build_hmac_headers(method, path, body))
        headers["Authorization"] = f"Bearer {token}"
        return headers

    def make_request(self, api_url: str, method: str, headers: dict[str, str], body: str):
        try:
            response = requests.request(
                method=method.upper(),  # Convert method to uppercase
                url=api_url,
                headers=headers,
                data=body if body else None,
                timeout=60,
            )
            if response.status_code == 211:
                return None
            return response
        except requests.exceptions.ConnectionError as e:
            logging.warning(f"Unable to connect to {api_url} {e}")
            return None
        except requests.exceptions.InvalidURL as e:
            logging.warning(f"Invalid URL {api_url} {e}")
            raise ValueError(f"Invalid URL: {api_url}") from e
    def call_hosts(self, endpoint: str, method: str = "GET", hosts: Optional[tuple] = None) -> dict[str, dict]:
        return self.call_endpoints(endpoint, hosts=hosts, method=method)
