import schedule
import time
import threading
from datetime import date
from scraper.fetcher import get_all_domains
from scraper.dns_checker import check_dns
from scraper.blacklist import check_blacklist
from scraper.spamhaus import check_spamhaus
from scraper.reputation import (
    check_talos, check_barracuda, 
    check_virustotal, check_abuseipdb, check_urlvoid
)
from scraper.scorer import score_domain, get_domain_age
from db.database import save_domain, log_scrape

def run_scrape():
    """Main scraping function - runs daily at 6AM"""
    print(f"🚀 Scrape started: {date.today()}")
    domains = get_all_domains(limit=5000)
    stored = 0
    failed = 0
    
    for i, domain in enumerate(domains):
        try:
            print(f"Checking {i+1}/{len(domains)}: {domain}")
            
            # Step 1: DNS checks
            data = check_dns(domain)
            
            # Step 2: Blacklist checks
            data.update(check_blacklist(domain))
            
            # Step 3: Spamhaus
            spamhaus_data = check_spamhaus(domain)
            print(f"  Spamhaus for {domain}: {spamhaus_data}")
            data.update(spamhaus_data)
            
            # Step 4: Talos
            data.update(check_talos(domain))
            
            # Step 5: Barracuda
            data.update(check_barracuda(domain))
            
            # Step 6: VirusTotal
            data.update(check_virustotal(domain))
            
            # Step 7: AbuseIPDB
            data.update(check_abuseipdb(domain))
            
            # Step 8: URLVoid
            data.update(check_urlvoid(domain))
            
            # Step 9: Domain Age
            domain_age = get_domain_age(domain)
            data["domain_age_years"] = domain_age
            if domain_age:
                print(f"  Domain Age: {domain_age} years")
            else:
                print(f"  Domain Age: Unknown")
            
            # Step 10: Final Score
            data["score"] = score_domain(data)
            data["last_checked"] = str(date.today())
            
            # Step 11: Save
            print(f"  Saving: {domain} | Spamhaus: {data.get('spamhaus_clean')} | Age: {domain_age} yrs | Score: {data['score']}")
            save_domain(data)
            stored += 1
            
            # Rate limit
            time.sleep(0.3)
            
        except Exception as e:
            print(f"❌ Error on {domain}: {e}")
            failed += 1
    
    log_scrape(len(domains), stored, "success" if failed == 0 else "partial")
    print(f"✅ Scrape done: {stored} stored, {failed} failed")

def start_scheduler():
    """Start the scheduler that runs daily at 6AM"""
    print("⏰ Scheduler started - will run daily at 6AM")
    schedule.every().day.at("06:00").do(run_scrape)
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(60)

def launch_background_scheduler():
    """Launch scheduler in a background thread"""
    thread = threading.Thread(target=start_scheduler, daemon=True)
    thread.start()
    print("🔁 Scheduler thread launched in background")