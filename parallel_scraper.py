import schedule
import time
import threading
from datetime import date
from scraper.fetcher import fetch_majestic_with_offset
from scraper.dns_checker import check_dns
from scraper.blacklist import check_blacklist
from scraper.spamhaus import check_spamhaus
from scraper.reputation import (
    check_talos, check_barracuda, 
    check_virustotal, check_abuseipdb, check_urlvoid
)
from scraper.scorer import score_domain, get_domain_age
from db.database import save_domain, log_scrape, check_domain_exists

def process_domain(domain):
    """Process a single domain"""
    try:
        data = check_dns(domain)
        data.update(check_blacklist(domain))
        
        spamhaus_data = check_spamhaus(domain)
        data.update(spamhaus_data)
        
        data.update(check_talos(domain))
        data.update(check_barracuda(domain))
        
        # Skip VirusTotal to avoid rate limits (or keep it)
        # data.update(check_virustotal(domain))
        data.update({"vt_clean": None, "vt_malicious_count": None})
        
        data.update(check_abuseipdb(domain))
        data.update(check_urlvoid(domain))
        
        domain_age = get_domain_age(domain)
        data["domain_age_years"] = domain_age
        data["score"] = score_domain(data)
        data["last_checked"] = str(date.today())
        
        save_domain(data)
        return True
    except Exception as e:
        print(f"❌ Error on {domain}: {e}")
        return False

def run_scrape_with_offset(offset=0, limit=5000, instance_id=1):
    """Run scraper with offset support"""
    print(f"🚀 Scraper {instance_id} started")
    print(f"📊 Processing domains {offset+1} to {offset+limit}")
    
    # Fetch domains with offset
    domains = fetch_majestic_with_offset(limit, offset)
    
    if not domains:
        print(f"⚠️ No domains found for offset {offset}")
        return
    
    print(f"✅ Fetched {len(domains)} domains")
    
    stored = 0
    failed = 0
    skipped = 0
    
    for i, domain in enumerate(domains):
        # Check if domain already exists
        if check_domain_exists(domain):
            print(f"⏭️ {i+1}/{len(domains)} {domain} already exists (skipped)")
            skipped += 1
            continue
        
        print(f"🔄 {i+1}/{len(domains)} {domain}...", end=" ")
        
        if process_domain(domain):
            print(f"✅ Saved")
            stored += 1
        else:
            print(f"❌ Failed")
            failed += 1
        
        # Rate limit
        time.sleep(0.3)
    
    log_scrape(len(domains), stored, "success" if failed == 0 else "partial")
    print(f"\n📊 Scraper {instance_id} Summary:")
    print(f"   ✅ Stored: {stored}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏭️ Skipped: {skipped}")

def run_batch_with_offset(batch_size=5000, num_batches=4):
    """Run multiple batches with offsets"""
    print(f"🚀 Starting batch processing")
    print(f"📊 Batch size: {batch_size}, Number of batches: {num_batches}")
    
    threads = []
    for i in range(num_batches):
        offset = i * batch_size
        instance_id = i + 1
        
        # Run each batch in its own thread
        thread = threading.Thread(
            target=run_scrape_with_offset,
            args=(offset, batch_size, instance_id)
        )
        threads.append(thread)
        thread.start()
        
        # Add delay between starting threads to avoid rate limits
        time.sleep(5)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("\n🎉 All batches complete!")

if __name__ == "__main__":
    # Example: Run 4 batches of 5000 domains each
    # Terminal 1: python parallel_scraper.py
    run_batch_with_offset(batch_size=5000, num_batches=4)