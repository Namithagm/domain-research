from scraper.scorer import get_domain_age
from supabase import create_client
import os
from dotenv import load_dotenv
import time
import signal

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def get_domain_age_with_timeout(domain, timeout=10):
    """Get domain age with timeout"""
    import threading
    import queue
    
    result_queue = queue.Queue()
    
    def worker():
        try:
            age = get_domain_age(domain)
            result_queue.put(age)
        except Exception as e:
            result_queue.put(None)
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        print(f"  ⏰ Timeout on {domain}")
        return None
    
    try:
        return result_queue.get_nowait()
    except:
        return None

print("🔄 Domain Age Updater (with Timeout)")
print("=" * 60)

# Get ALL domains without age
result = supabase.table('domains').select('domain_name').is_('domain_age_years', 'null').execute()
domains = [r['domain_name'] for r in result.data]

print(f"📊 Found {len(domains)} domains without age")
print("-" * 60)

if len(domains) == 0:
    print("✅ All domains already have ages!")
    exit()

updated = 0
failed = 0
skipped = 0
timeouts = 0

for i, d in enumerate(domains):
    try:
        print(f"⏳ {i+1}/{len(domains)} {d}...", end=" ")
        
        age = get_domain_age_with_timeout(d, timeout=10)
        
        if age:
            supabase.table('domains').update({'domain_age_years': age}).eq('domain_name', d).execute()
            print(f"✅ {age} years")
            updated += 1
        elif age is None:
            # Check if it was a timeout
            print(f"⏰ Timeout (skipped)")
            timeouts += 1
        else:
            print(f"⚠️ Not found")
            skipped += 1
            
        # Short delay between requests
        time.sleep(0.3)
        
    except Exception as e:
        print(f"❌ Error - {e}")
        failed += 1

print("-" * 60)
print(f"📊 Summary:")
print(f"   ✅ Updated: {updated}")
print(f"   ⏰ Timeouts: {timeouts}")
print(f"   ⚠️ Skipped (no age): {skipped}")
print(f"   ❌ Failed: {failed}")
print(f"   📊 Total processed: {len(domains)}")