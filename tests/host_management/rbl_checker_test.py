import unittest
from unittest.mock import patch, MagicMock
from host_management.rbl_checker import RblChecker

@patch('host_management.rbl_checker.dns.resolver.Resolver.resolve')
def test_check_single_rbl_success(mock_resolve):
    checker = RblChecker()
    mock_resolve.return_value = True
    rblHost = MagicMock()
    rblHost.orgName = "test.rbl"
    result = checker._check_single_rbl("1.2.3.4", rblHost)
    assert result == {"test.rbl": 0}

@patch('host_management.rbl_checker.dns.resolver.Resolver.resolve')
def test_check_single_rbl_failure(mock_resolve):
    checker = RblChecker()
    mock_resolve.side_effect = Exception("DNS query failed")
    rblHost = MagicMock()
    rblHost.orgName = "test.rbl"
    result = checker._check_single_rbl("1.2.3.4", rblHost)
    assert result == {"test.rbl": 1}

@patch('host_management.rbl_checker.db.session.query')
@patch('host_management.rbl_checker.app.app_context')
def test_check_rbl(mock_app_context, mock_query):
    checker = RblChecker()
    mock_app_context.return_value.__enter__.return_value = True
    rblHost1 = MagicMock()
    rblHost1.orgName = "test1.rbl"
    rblHost1.use = True
    rblHost2 = MagicMock()
    rblHost2.orgName = "test2.rbl"
    rblHost2.use = False
    mock_query.return_value.all.return_value = [rblHost1, rblHost2]
    
    with patch.object(checker, '_check_single_rbl', return_value={"test1.rbl": 0}) as mock_check_single_rbl:
        result = checker.check_rbl("1.2.3.4")
        assert result == [{"test1.rbl": 0}]
        mock_check_single_rbl.assert_called_once_with("1.2.3.4", rblHost1)