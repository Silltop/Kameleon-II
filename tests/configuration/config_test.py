import pytest
from unittest.mock import mock_open, patch, MagicMock
from configuration.config import ConfigManager  # Adjust import based on your project structure

valid_yaml_content = """
hosts:
  host1:
    ip: 192.168.1.1
  host2:
    ip: 192.168.1.2
"""

invalid_yaml_content = """
hosts:
  host1: ip: 192.168.1.1  # Invalid YAML structure
"""


@pytest.fixture
def mock_yaml_file():
    # Mock the open function for reading valid YAML content
    with patch("builtins.open", mock_open(read_data=valid_yaml_content)):
        yield


@pytest.fixture
def mock_invalid_yaml_file():
    # Mock the open function for reading invalid YAML content
    with patch("builtins.open", mock_open(read_data=invalid_yaml_content)):
        yield


def test_singleton_behavior():
    instance1 = ConfigManager()
    instance2 = ConfigManager()
    assert instance1 is instance2  # Ensure only one instance is created


def test_load_content_success(mock_yaml_file):
    with patch("yaml.safe_load", return_value={"hosts": {"host1": {"ip": "192.168.1.1"}}}):
        config = ConfigManager()
        assert config.file_content["hosts"]["host1"]["ip"] == "192.168.1.1"


def test_load_ips(mock_yaml_file):
    with patch("yaml.safe_load",
               return_value={"hosts": {"host1": {"ip": "192.168.1.1"}, "host2": {"ip": "192.168.1.2"}}}):
        config = ConfigManager()
        assert config.load_ips() == ["192.168.1.1", "192.168.1.2"]


def test_load_ips_empty_hosts():
    with patch("yaml.safe_load", return_value={}):  # No "hosts" key in YAML
        config = ConfigManager()
        assert config.load_ips() == []  # Should return an empty list
