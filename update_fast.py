from scraper.scorer import get_domain_age
from supabase import create_client
import os
from dotenv import load_dotenv
import time
import threading
import queue

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def get_domain_age_fast(domain, timeout=5):
    """Get domain age with short timeout"""
    result_queue = queue.Queue()
    
    def worker():
        try:
            age = get_domain_age(domain)
            result_queue.put(age)
        except:
            result_queue.put(None)
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        return None  # Timeout
    
    try:
        return result_queue.get_nowait()
    except:
        return None

# Get domains without age
result = supabase.table('domains').select('domain_name').is_('domain_age_years', 'null').execute()
domains = [r['domain_name'] for r in result.data]

print(f"📊 Found {len(domains)} domains without age")
print("-" * 60)

# Skip problematic domains
skip_domains = ['uct.ac.za', 'mindspring.com', 'tinkercad.com', 'ni.com']
domains = [d for d in domains if d not in skip_domains]

print(f"⏭️ Skipping {len(skip_domains)} problematic domains")
print(f"📊 Processing {len(domains)} domains")
print("-" * 60)

updated = 0
failed = 0
timeouts = 0

for i, d in enumerate(domains):
    try:
        print(f"⏳ {i+1}/{len(domains)} {d}...", end=" ")
        
        age = get_domain_age_fast(d, timeout=5)
        
        if age:
            supabase.table('domains').update({'domain_age_years': age}).eq('domain_name', d).execute()
            print(f"✅ {age} years")
            updated += 1
        elif age is None:
            print(f"⏰ Timeout")
            timeouts += 1
        else:
            print(f"⚠️ Not found")
            failed += 1
            
        # Short delay
        time.sleep(0.2)
        
    except Exception as e:
        print(f"❌ Error - {e}")
        failed += 1

print("-" * 60)
print(f"📊 Summary:")
print(f"   ✅ Updated: {updated}")
print(f"   ⏰ Timeouts: {timeouts}")
print(f"   ❌ Failed: {failed}")
print(f"   ⏭️ Skipped: {len(skip_domains)}")