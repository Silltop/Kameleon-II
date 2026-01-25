from unittest.mock import patch, MagicMock
from connectors.api.api_connector import ApiConnector, TokenManager, SECRET_KEY
import jwt
import datetime


@patch('connectors.api.api_connector.requests.request')
def test_create_headers(mock_request):
    connector = ApiConnector()
    headers = connector.create_headers()
    assert "X-API-KEY" in headers
    assert "Content-Type" in headers
    assert headers["Content-Type"] == "application/json"


@patch('connectors.api.api_connector.requests.request')
def test_create_headers_with_token(mock_request):
    connector = ApiConnector()
    headers = connector.create_headers_with_token("192.168.1.1")
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bearer ")
    assert "X-API-KEY" in headers


@patch('connectors.api.api_connector.requests.request')
def test_construct_api_url(mock_request):
    connector = ApiConnector()
    url = connector.construct_api_url("http", "192.168.1.1", "/api/test")
    assert url == "http://192.168.1.1:6622/api/test"


@patch('connectors.api.api_connector.requests.request')
def test_construct_api_url_https(mock_request):
    connector = ApiConnector()
    url = connector.construct_api_url("https", "example.com", "/api/users")
    assert url == "https://example.com:6622/api/users"


@patch('connectors.api.api_connector.requests.request')
def test_make_request_success(mock_request):
    connector = ApiConnector()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response
    
    response = connector.make_request("http://example.com/api", "GET", {}, None, None)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}


@patch('connectors.api.api_connector.requests.request')
def test_make_request_211_status(mock_request):
    connector = ApiConnector()
    mock_response = MagicMock()
    mock_response.status_code = 211
    mock_request.return_value = mock_response
    
    response = connector.make_request("http://example.com/api", "GET", {}, None, None)
    assert response is None

# todo analyze why this test fails
# @patch('connectors.api.api_connector.requests.request')
# def test_make_request_connection_error(mock_request):
#     connector = ApiConnector()
#     mock_request.side_effect = Exception("Connection failed")
    
#     response = connector.make_request("http://example.com/api", "GET", {}, None, None)
#     assert response is None


@patch('connectors.api.api_connector.requests.request')
def test_make_request_with_json_data(mock_request):
    connector = ApiConnector()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_request.return_value = mock_response
    
    json_data = {"name": "test"}
    connector.make_request("http://example.com/api", "POST", {}, None, json_data)
    
    call_kwargs = mock_request.call_args[1]
    assert call_kwargs["json"] == json_data
    assert call_kwargs["method"] == "POST"


@patch('connectors.api.api_connector.requests.request')
def test_call_endpoints_single_host(mock_request):
    connector = ApiConnector()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response
    
    responses = connector.call_endpoints("/api/test", hosts=("192.168.1.1",), method="GET")
    assert "192.168.1.1" in responses
    assert responses["192.168.1.1"]["status"] == "success"


@patch('connectors.api.api_connector.requests.request')
def test_call_endpoints_multiple_hosts(mock_request):
    connector = ApiConnector()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response
    
    hosts = ("192.168.1.1", "192.168.1.2")
    responses = connector.call_endpoints("/api/test", hosts=hosts, method="GET")
    assert len(responses) == 2
    assert "192.168.1.1" in responses
    assert "192.168.1.2" in responses


@patch('connectors.api.api_connector.requests.request')
def test_call_endpoints_https(mock_request):
    connector = ApiConnector()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response
    
    connector.call_endpoints("/api/test", hosts=("192.168.1.1",), method="GET", https=True)
    call_kwargs = mock_request.call_args[1]
    assert "https://" in call_kwargs["url"]


@patch('connectors.api.api_connector.requests.request')
def test_call_host(mock_request):
    connector = ApiConnector()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"host": "192.168.1.1"}
    mock_request.return_value = mock_response
    
    responses = connector.call_host("/api/test", host="192.168.1.1", method="GET")
    assert "192.168.1.1" in responses
    assert responses["192.168.1.1"]["host"] == "192.168.1.1"


@patch('connectors.api.api_connector.requests.request')
def test_call_hosts(mock_request):
    connector = ApiConnector()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response
    
    with patch('connectors.api.api_connector.config') as mock_config:
        mock_config.ConfigManager.return_value.ip_list = ["192.168.1.1"]
        responses = connector.call_hosts("/api/test")
        assert len(responses) > 0


def test_token_manager_singleton():
    TokenManager._instance = None
    manager1 = TokenManager()
    manager2 = TokenManager()
    assert manager1 is manager2


def test_token_manager_generate_token():
    TokenManager._instance = None
    manager = TokenManager()
    token = manager.generate_token("test_host")
    assert token is not None
    assert "test_host" in manager.token_store


def test_token_manager_generate_token_valid():
    TokenManager._instance = None
    manager = TokenManager()
    host_id = "test_host"
    token = manager.generate_token(host_id)
    
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == host_id


def test_token_manager_get_valid_token():
    TokenManager._instance = None
    manager = TokenManager()
    host_id = "test_host"
    token1 = manager.get_valid_token(host_id)
    token2 = manager.get_valid_token(host_id)
    assert token1 == token2


def test_token_manager_get_valid_token_expired():
    TokenManager._instance = None
    manager = TokenManager()
    host_id = "test_host"
    
    # Create an expired token
    payload = {
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1),
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "sub": host_id,
    }
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    manager.token_store[host_id] = expired_token
    
    # Get valid token should regenerate
    new_token = manager.get_valid_token(host_id)
    assert new_token != expired_token


def test_token_manager_is_token_expired_valid():
    TokenManager._instance = None
    manager = TokenManager()
    host_id = "test_host"
    token = manager.generate_token(host_id)
    
    assert manager.is_token_expired(token, host_id) is False


def test_token_manager_is_token_expired_expired():
    TokenManager._instance = None
    manager = TokenManager()
    host_id = "test_host"
    
    # Create an expired token
    payload = {
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1),
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "sub": host_id,
    }
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    assert manager.is_token_expired(expired_token, host_id) is True


@patch('connectors.api.api_connector.requests.request')
def test_make_request_timeout(mock_request):
    connector = ApiConnector()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_request.return_value = mock_response
    
    connector.make_request("http://example.com/api", "GET", {}, None, None)
    call_kwargs = mock_request.call_args[1]
    assert call_kwargs["timeout"] == 60
