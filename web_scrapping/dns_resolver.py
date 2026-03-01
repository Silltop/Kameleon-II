"""DNS resolver module for retrieving DNS records and information."""
import subprocess
from datetime import datetime
from typing import Dict, List


def get_dns_a_records(domain: str) -> List[Dict[str, str]]:
    """Get DNS A records for a domain.
    
    Args:
        domain: The domain to query
        
    Returns:
        List of dictionaries containing A record information
    """
    try:
        a_records = []
        result = subprocess.run(
            ["dig", domain, "+short", "A"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line and not line.startswith(";"):
                    a_records.append({"type": "A", "value": line.strip()})
        return a_records if a_records else [{"type": "A", "value": "Not found"}]
    except Exception as e:
        print(f"Error getting A records for {domain}: {e}")
        return [{"type": "A", "value": f"Error: {str(e)}"}]


def get_dns_mx_records(domain: str) -> List[Dict[str, str]]:
    """Get DNS MX records for a domain.
    
    Args:
        domain: The domain to query
        
    Returns:
        List of dictionaries containing MX record information
    """
    try:
        mx_records = []
        result = subprocess.run(
            ["dig", domain, "+short", "MX"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line and not line.startswith(";"):
                    mx_records.append({"type": "MX", "value": line.strip()})
        return mx_records if mx_records else [{"type": "MX", "value": "Not found"}]
    except Exception as e:
        print(f"Error getting MX records for {domain}: {e}")
        return [{"type": "MX", "value": f"Error: {str(e)}"}]


def get_dns_cname_records(domain: str) -> List[Dict[str, str]]:
    """Get DNS CNAME records for a domain.
    
    Args:
        domain: The domain to query
        
    Returns:
        List of dictionaries containing CNAME record information
    """
    try:
        cname_records = []
        result = subprocess.run(
            ["dig", domain, "+short", "CNAME"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                for line in output.split("\n"):
                    if line and not line.startswith(";"):
                        cname_records.append({"type": "CNAME", "value": line.strip()})
            else:
                cname_records.append({"type": "CNAME", "value": "Not found"})
        return cname_records
    except Exception as e:
        print(f"Error getting CNAME records for {domain}: {e}")
        return [{"type": "CNAME", "value": f"Error: {str(e)}"}]


def get_target_dns(domain: str) -> Dict:
    """Get target DNS server information for a domain.
    
    Args:
        domain: The domain to query
        
    Returns:
        Dictionary containing nameserver information
    """
    try:
        ns_records = []
        result = subprocess.run(
            ["dig", domain, "+short", "NS"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line and not line.startswith(";"):
                    ns_records.append(line.strip().rstrip("."))
        
        return {
            "domain": domain,
            "nameservers": ns_records if ns_records else ["Not found"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting nameservers for {domain}: {e}")
        return {
            "domain": domain,
            "nameservers": [f"Error: {str(e)}"],
            "timestamp": datetime.now().isoformat()
        }


def get_complete_dns_info(domain: str) -> Dict:
    """Get complete DNS information for a domain.
    
    Args:
        domain: The domain to query
        
    Returns:
        Dictionary containing all DNS information
    """
    return {
        "domain": domain,
        "a_records": get_dns_a_records(domain),
        "mx_records": get_dns_mx_records(domain),
        "cname_records": get_dns_cname_records(domain),
        "nameservers": get_target_dns(domain)["nameservers"],
        "timestamp": datetime.now().isoformat()
    }


def get_dns_info_batch(domains: List[str]) -> List[Dict]:
    """Get DNS information for multiple domains.
    
    Args:
        domains: List of domains to query
        
    Returns:
        List of DNS information dictionaries
    """
    result = []
    for domain in domains:
        info = get_complete_dns_info(domain)
        result.append(info)
    return result


def generate_dns_table_html(dns_info_list: List[Dict]) -> str:
    """Generate an HTML table from DNS information.
    
    Args:
        dns_info_list: List of DNS information dictionaries
        
    Returns:
        HTML string containing formatted table
    """
    html = """
    <table class="table table-bordered" style="width: 100%; border-collapse: collapse;">
        <thead style="background-color: #f0f0f0;">
            <tr>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Domain</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">A Records</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">MX Records</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">CNAME Records</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Nameservers</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Timestamp</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for dns_info in dns_info_list:
        a_records = "<br>".join([r["value"] for r in dns_info["a_records"]])
        mx_records = "<br>".join([r["value"] for r in dns_info["mx_records"]])
        cname_records = "<br>".join([r["value"] for r in dns_info["cname_records"]])
        nameservers = "<br>".join(dns_info["nameservers"])
        
        html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{dns_info["domain"]}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{a_records}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{mx_records}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{cname_records}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{nameservers}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{dns_info["timestamp"]}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    return html


def generate_dns_csv(dns_info_list: List[Dict]) -> str:
    """Generate CSV format from DNS information.
    
    Args:
        dns_info_list: List of DNS information dictionaries
        
    Returns:
        CSV string containing DNS records
    """
    csv_content = "Domain,Record Type,Value,Timestamp\n"
    
    for dns_info in dns_info_list:
        timestamp = dns_info["timestamp"]
        domain = dns_info["domain"]
        
        for record_type in ["a_records", "mx_records", "cname_records"]:
            for record in dns_info[record_type]:
                csv_content += f'{domain},{record["type"]},{record["value"]},{timestamp}\n'
        
        for ns in dns_info["nameservers"]:
            csv_content += f'{domain},NS,{ns},{timestamp}\n'
    
    return csv_content
