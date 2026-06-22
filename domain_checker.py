import sys
sys.path.insert(0, r'C:\Users\Namitha\Downloads\domain-research')

from scraper.dns_checker import check_dns
from scraper.blacklist import check_blacklist
from scraper.spamhaus import check_spamhaus
from scraper.reputation import check_talos, check_barracuda, check_virustotal, check_abuseipdb, check_urlvoid
from scraper.scorer import score_domain, get_domain_age
import pandas as pd
import time

def check_single_domain(domain):
    """Check a single domain and return full report"""
    try:
        print(f"🔍 Checking: {domain}")
        
        # Step 1: DNS checks
        data = check_dns(domain)
        
        # Step 2: Blacklist checks
        data.update(check_blacklist(domain))
        
        # Step 3: Spamhaus
        data.update(check_spamhaus(domain))
        
        # Step 4: Talos
        data.update(check_talos(domain))
        
        # Step 5: Barracuda
        data.update(check_barracuda(domain))
        
        # Step 6: VirusTotal (only if API key exists)
        data.update(check_virustotal(domain))
        
        # Step 7: AbuseIPDB
        data.update(check_abuseipdb(domain))
        
        # Step 8: URLVoid
        data.update(check_urlvoid(domain))
        
        # Step 9: Domain Age
        domain_age = get_domain_age(domain)
        data["domain_age_years"] = domain_age
        
        # Step 10: Final Score
        data["score"] = score_domain(data)
        
        return data
    except Exception as e:
        return {"domain_name": domain, "error": str(e)}

def check_bulk_domains(domains):
    """Check multiple domains"""
    results = []
    total = len(domains)
    
    for i, domain in enumerate(domains):
        print(f"⏳ Processing {i+1}/{total}: {domain}")
        result = check_single_domain(domain.strip())
        results.append(result)
        time.sleep(0.3)  # Rate limit
    
    return pd.DataFrame(results)

def export_results_to_csv(results, filename="domain_report.csv"):
    """Export results to CSV"""
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)
    print(f"✅ Exported to {filename}")
    return filename