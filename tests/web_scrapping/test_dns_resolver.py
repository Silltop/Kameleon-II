"""Tests for DNS resolver module."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from web_scrapping.dns_resolver import (
    get_dns_a_records,
    get_dns_mx_records,
    get_dns_cname_records,
    get_target_dns,
    get_complete_dns_info,
    get_dns_info_batch,
    generate_dns_table_html,
    generate_dns_csv
)


class TestDNSARecords(unittest.TestCase):
    """Test cases for get_dns_a_records function."""
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_dns_a_records_success(self, mock_run):
        """Test successful A record retrieval."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="192.168.1.1\n192.168.1.2\n"
        )
        
        result = get_dns_a_records("example.com")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["type"], "A")
        self.assertEqual(result[0]["value"], "192.168.1.1")
        self.assertEqual(result[1]["value"], "192.168.1.2")
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_dns_a_records_empty(self, mock_run):
        """Test A record retrieval with no results."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        result = get_dns_a_records("example.com")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["value"], "Not found")
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_dns_a_records_error(self, mock_run):
        """Test A record retrieval with error."""
        mock_run.side_effect = Exception("Connection error")
        
        result = get_dns_a_records("example.com")
        
        self.assertEqual(len(result), 1)
        self.assertIn("Error:", result[0]["value"])


class TestDNSMXRecords(unittest.TestCase):
    """Test cases for get_dns_mx_records function."""
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_dns_mx_records_success(self, mock_run):
        """Test successful MX record retrieval."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="10 mail.example.com.\n20 mail2.example.com.\n"
        )
        
        result = get_dns_mx_records("example.com")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["type"], "MX")
        self.assertIn("mail.example.com", result[0]["value"])
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_dns_mx_records_empty(self, mock_run):
        """Test MX record retrieval with no results."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        result = get_dns_mx_records("example.com")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["value"], "Not found")
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_dns_mx_records_error(self, mock_run):
        """Test MX record retrieval with error."""
        mock_run.side_effect = Exception("Timeout")
        
        result = get_dns_mx_records("example.com")
        
        self.assertEqual(len(result), 1)
        self.assertIn("Error:", result[0]["value"])


class TestDNSCNAMERecords(unittest.TestCase):
    """Test cases for get_dns_cname_records function."""
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_dns_cname_records_success(self, mock_run):
        """Test successful CNAME record retrieval."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="alias.example.com.\n"
        )
        
        result = get_dns_cname_records("www.example.com")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "CNAME")
        self.assertIn("alias.example.com", result[0]["value"])
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_dns_cname_records_not_found(self, mock_run):
        """Test CNAME record when none exists."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        result = get_dns_cname_records("example.com")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["value"], "Not found")
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_dns_cname_records_error(self, mock_run):
        """Test CNAME record retrieval with error."""
        mock_run.side_effect = Exception("DNS failure")
        
        result = get_dns_cname_records("example.com")
        
        self.assertEqual(len(result), 1)
        self.assertIn("Error:", result[0]["value"])


class TestTargetDNS(unittest.TestCase):
    """Test cases for get_target_dns function."""
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_target_dns_success(self, mock_run):
        """Test successful nameserver retrieval."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="ns1.example.com.\nns2.example.com.\n"
        )
        
        result = get_target_dns("example.com")
        
        self.assertEqual(result["domain"], "example.com")
        self.assertEqual(len(result["nameservers"]), 2)
        self.assertIn("ns1.example.com", result["nameservers"])
        self.assertIn("timestamp", result)
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_target_dns_not_found(self, mock_run):
        """Test nameserver retrieval when none found."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        result = get_target_dns("invalid.domain")
        
        self.assertEqual(result["domain"], "invalid.domain")
        self.assertEqual(result["nameservers"], ["Not found"])
    
    @patch('web_scrapping.dns_resolver.subprocess.run')
    def test_get_target_dns_error(self, mock_run):
        """Test nameserver retrieval with error."""
        mock_run.side_effect = Exception("Network error")
        
        result = get_target_dns("example.com")
        
        self.assertEqual(result["domain"], "example.com")
        self.assertIn("Error:", result["nameservers"][0])


class TestCompleteDNSInfo(unittest.TestCase):
    """Test cases for get_complete_dns_info function."""
    
    @patch('web_scrapping.dns_resolver.get_dns_a_records')
    @patch('web_scrapping.dns_resolver.get_dns_mx_records')
    @patch('web_scrapping.dns_resolver.get_dns_cname_records')
    @patch('web_scrapping.dns_resolver.get_target_dns')
    def test_get_complete_dns_info(self, mock_ns, mock_cname, mock_mx, mock_a):
        """Test complete DNS information retrieval."""
        mock_a.return_value = [{"type": "A", "value": "192.168.1.1"}]
        mock_mx.return_value = [{"type": "MX", "value": "10 mail.example.com."}]
        mock_cname.return_value = [{"type": "CNAME", "value": "Not found"}]
        mock_ns.return_value = {
            "domain": "example.com",
            "nameservers": ["ns1.example.com", "ns2.example.com"],
            "timestamp": "2026-03-01T10:00:00"
        }
        
        result = get_complete_dns_info("example.com")
        
        self.assertEqual(result["domain"], "example.com")
        self.assertEqual(len(result["a_records"]), 1)
        self.assertEqual(len(result["mx_records"]), 1)
        self.assertEqual(len(result["nameservers"]), 2)
        self.assertIn("timestamp", result)


class TestDNSBatch(unittest.TestCase):
    """Test cases for get_dns_info_batch function."""
    
    @patch('web_scrapping.dns_resolver.get_complete_dns_info')
    def test_get_dns_info_batch(self, mock_complete):
        """Test batch DNS information retrieval."""
        mock_complete.return_value = {
            "domain": "example.com",
            "a_records": [{"type": "A", "value": "192.168.1.1"}],
            "mx_records": [],
            "cname_records": [],
            "nameservers": ["ns1.example.com"],
            "timestamp": "2026-03-01T10:00:00"
        }
        
        domains = ["example.com", "test.com"]
        result = get_dns_info_batch(domains)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(mock_complete.call_count, 2)
        self.assertEqual(result[0]["domain"], "example.com")


class TestDNSTableHTML(unittest.TestCase):
    """Test cases for generate_dns_table_html function."""
    
    def test_generate_dns_table_html(self):
        """Test HTML table generation."""
        dns_info = [
            {
                "domain": "example.com",
                "a_records": [{"type": "A", "value": "192.168.1.1"}],
                "mx_records": [{"type": "MX", "value": "10 mail.example.com."}],
                "cname_records": [{"type": "CNAME", "value": "Not found"}],
                "nameservers": ["ns1.example.com"],
                "timestamp": "2026-03-01T10:00:00"
            }
        ]
        
        html = generate_dns_table_html(dns_info)
        
        self.assertIn("<table", html)
        self.assertIn("example.com", html)
        self.assertIn("192.168.1.1", html)
        self.assertIn("10 mail.example.com.", html)
        self.assertIn("ns1.example.com", html)
        self.assertIn("</table>", html)
    
    def test_generate_dns_table_html_multiple_records(self):
        """Test HTML table generation with multiple records."""
        dns_info = [
            {
                "domain": "example.com",
                "a_records": [
                    {"type": "A", "value": "192.168.1.1"},
                    {"type": "A", "value": "192.168.1.2"}
                ],
                "mx_records": [
                    {"type": "MX", "value": "10 mail1.example.com."},
                    {"type": "MX", "value": "20 mail2.example.com."}
                ],
                "cname_records": [],
                "nameservers": ["ns1.example.com", "ns2.example.com"],
                "timestamp": "2026-03-01T10:00:00"
            }
        ]
        
        html = generate_dns_table_html(dns_info)
        
        self.assertIn("192.168.1.1<br>192.168.1.2", html)
        self.assertIn("10 mail1.example.com.<br>20 mail2.example.com.", html)
        self.assertIn("ns1.example.com<br>ns2.example.com", html)


class TestDNSCSV(unittest.TestCase):
    """Test cases for generate_dns_csv function."""
    
    def test_generate_dns_csv(self):
        """Test CSV generation."""
        dns_info = [
            {
                "domain": "example.com",
                "a_records": [{"type": "A", "value": "192.168.1.1"}],
                "mx_records": [{"type": "MX", "value": "10 mail.example.com."}],
                "cname_records": [{"type": "CNAME", "value": "Not found"}],
                "nameservers": ["ns1.example.com"],
                "timestamp": "2026-03-01T10:00:00"
            }
        ]
        
        csv = generate_dns_csv(dns_info)
        
        self.assertIn("Domain,Record Type,Value,Timestamp", csv)
        self.assertIn("example.com,A,192.168.1.1", csv)
        self.assertIn("example.com,MX,10 mail.example.com.", csv)
        self.assertIn("example.com,NS,ns1.example.com", csv)
    
    def test_generate_dns_csv_multiple_records(self):
        """Test CSV generation with multiple records."""
        dns_info = [
            {
                "domain": "example.com",
                "a_records": [
                    {"type": "A", "value": "192.168.1.1"},
                    {"type": "A", "value": "192.168.1.2"}
                ],
                "mx_records": [
                    {"type": "MX", "value": "10 mail.example.com."}
                ],
                "cname_records": [],
                "nameservers": ["ns1.example.com"],
                "timestamp": "2026-03-01T10:00:00"
            }
        ]
        
        csv = generate_dns_csv(dns_info)
        lines = csv.strip().split("\n")
        
        # Headers + 3 A records + 1 MX + 1 NS = 6 lines total
        self.assertEqual(len(lines), 6)
        self.assertIn("example.com,A,192.168.1.1", csv)
        self.assertIn("example.com,A,192.168.1.2", csv)


if __name__ == "__main__":
    unittest.main()
