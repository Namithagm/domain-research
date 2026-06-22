import requests
import os
from dotenv import load_dotenv

load_dotenv()

VT_API_KEY = os.environ.get("VT_API_KEY")
ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_KEY")

def check_talos(domain):
    """Check Talos Intelligence reputation - returns neutral since it's blocked"""
    return {"talos_score": "unknown", "talos_category": "unknown", "talos_clean": None}

def check_barracuda(domain):
    """Check Barracuda Central reputation with timeout"""
    try:
        url = f"https://www.barracudacentral.org/lookups/lookup-reputation?type=5&ip={domain}"
        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        if r.status_code == 200:
            if "Good" in r.text:
                return {"barracuda_clean": True, "barracuda_status": "good"}
            elif "Poor" in r.text:
                return {"barracuda_clean": False, "barracuda_status": "poor"}
            else:
                return {"barracuda_clean": None, "barracuda_status": "unknown"}
        return {"barracuda_clean": None, "barracuda_status": "unknown"}
    except requests.Timeout:
        return {"barracuda_clean": None, "barracuda_status": "timeout"}
    except:
        return {"barracuda_clean": None, "barracuda_status": "error"}

def check_virustotal(domain):
    """Check VirusTotal reputation with timeout"""
    if not VT_API_KEY:
        return {"vt_clean": None, "vt_malicious_count": None, "vt_suspicious_count": None, "vt_total_scans": None}
    
    try:
        url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        headers = {"x-apikey": VT_API_KEY}
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            stats = data["data"]["attributes"].get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            total = sum(stats.values()) if stats else 0
            
            return {
                "vt_clean": (malicious == 0 and suspicious == 0),
                "vt_malicious_count": malicious,
                "vt_suspicious_count": suspicious,
                "vt_total_scans": total
            }
        return {"vt_clean": None, "vt_malicious_count": None, "vt_suspicious_count": None, "vt_total_scans": None}
    except requests.Timeout:
        return {"vt_clean": None, "vt_malicious_count": None, "vt_suspicious_count": None, "vt_total_scans": None}
    except Exception as e:
        return {"vt_clean": None, "vt_malicious_count": None, "vt_suspicious_count": None, "vt_total_scans": None}

def check_abuseipdb(domain):
    """Check AbuseIPDB reputation with timeout"""
    if not ABUSEIPDB_KEY:
        return {"abuse_score": None, "abuse_clean": None, "abuse_reports": None}
    
    try:
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
        params = {"ipAddress": domain}
        r = requests.get(url, headers=headers, params=params, timeout=15)
        
        if r.status_code == 200:
            data = r.json()["data"]
            score = data.get("abuseConfidenceScore", 0)
            return {
                "abuse_score": score,
                "abuse_clean": score < 10,
                "abuse_reports": data.get("totalReports", 0)
            }
        return {"abuse_score": None, "abuse_clean": None, "abuse_reports": None}
    except requests.Timeout:
        return {"abuse_score": None, "abuse_clean": None, "abuse_reports": None}
    except:
        return {"abuse_score": None, "abuse_clean": None, "abuse_reports": None}

def check_urlvoid(domain):
    """Check URLVoid reputation - often blocked"""
    try:
        url = f"https://www.urlvoid.com/scan/{domain}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            if "0 detections" in r.text.lower() or "no detections" in r.text.lower():
                return {"urlvoid_clean": True}
            return {"urlvoid_clean": False}
        return {"urlvoid_clean": None}
    except requests.Timeout:
        return {"urlvoid_clean": None}
    except:
        return {"urlvoid_clean": None}