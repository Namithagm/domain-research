import sys
sys.path.insert(0, r'C:\Users\Namitha\Downloads\domain-research')

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import subprocess

load_dotenv()

supabase = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_KEY')
)

print("=" * 60)
print("📊 SCRAPER PERFORMANCE REPORT")
print("=" * 60)
print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# 1. Total Domains
total = supabase.table('domains').select('count', count='exact').execute().count
print(f"\n📊 TOTAL DOMAINS: {total}")

# 2. Fully Processed (has score)
processed = supabase.table('domains').select('count', count='exact').not_.is_('score', 'null').execute().count
print(f"📊 FULLY PROCESSED (has score): {processed}")

# 3. Still Processing
still_processing = total - processed
print(f"📊 STILL PROCESSING: {still_processing}")

# 4. Progress Percentage
if total > 0:
    progress = (processed / total) * 100
    print(f"📊 PROGRESS: {progress:.1f}%")

print("-" * 60)

# 5. High Score Domains
high = supabase.table('domains').select('count', count='exact').gte('score', 70).execute().count
print(f"\n📊 HIGH SCORE (70+): {high}")

# 6. Low Score Domains
low = supabase.table('domains').select('count', count='exact').lt('score', 70).execute().count
print(f"📊 LOW SCORE (<70): {low}")

# 7. Available Now
today = datetime.now().date()
served_today = supabase.table('domains').select('count', count='exact').eq('last_served', str(today)).execute().count
available = high - served_today
print(f"📊 AVAILABLE NOW: {available}")

# 8. Old Domains (7+ years)
old = supabase.table('domains').select('count', count='exact').gte('domain_age_years', 7).execute().count
print(f"📊 OLD DOMAINS (7+ yrs): {old}")

print("-" * 60)

# 9. Domains by DMARC
print("\n📊 DMARC DISTRIBUTION:")
dmarc_types = ['none', 'quarantine', 'missing', 'reject']
for policy in dmarc_types:
    count = supabase.table('domains').select('count', count='exact').eq('dmarc_policy', policy).execute().count
    print(f"  {policy}: {count}")

# 10. Spamhaus Status
print("\n📊 SPAMHAUS STATUS:")
clean = supabase.table('domains').select('count', count='exact').eq('spamhaus_clean', True).execute().count
unknown = supabase.table('domains').select('count', count='exact').is_('spamhaus_clean', 'null').execute().count
flagged = supabase.table('domains').select('count', count='exact').eq('spamhaus_clean', False).execute().count
print(f"  Clean: {clean}")
print(f"  Unknown: {unknown}")
print(f"  Flagged: {flagged}")

# 11. Domain Age Distribution
print("\n📊 DOMAIN AGE DISTRIBUTION:")
age_ranges = [(0, 2), (2, 5), (5, 10), (10, 20), (20, 100)]
for low_val, high_val in age_ranges:
    if high_val == 100:
        count = supabase.table('domains').select('count', count='exact').gte('domain_age_years', low_val).execute().count
        print(f"  {low_val}+ years: {count} domains")
    else:
        count = supabase.table('domains').select('count', count='exact').gte('domain_age_years', low_val).lt('domain_age_years', high_val).execute().count
        print(f"  {low_val}-{high_val} years: {count} domains")

# 12. Latest 10 Domains
print("\n📊 LATEST 10 DOMAINS:")
latest = supabase.table('domains').select('domain_name, score, date_added').order('id', desc=True).limit(10).execute()
for r in latest.data:
    date_str = r['date_added'] if r['date_added'] else 'N/A'
    print(f"  {r['domain_name']}: {r['score']} (Added: {date_str})")

# 13. First and Last Domain
print("\n📊 FIRST AND LAST DOMAIN:")
first = supabase.table('domains').select('id, domain_name, score').order('id').limit(1).execute()
last = supabase.table('domains').select('id, domain_name, score').order('id', desc=True).limit(1).execute()
if first.data:
    print(f"  First: {first.data[0]['domain_name']} (ID: {first.data[0]['id']}, Score: {first.data[0]['score']})")
if last.data:
    print(f"  Last: {last.data[0]['domain_name']} (ID: {last.data[0]['id']}, Score: {last.data[0]['score']})")

# 14. Running Processes
print("\n🔄 RUNNING PROCESSES:")
try:
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], capture_output=True, text=True)
    python_count = result.stdout.count('python.exe')
    print(f"  Python processes: {python_count}")
    if python_count > 1:
        print("  ✅ Scrapers are still running")
    else:
        print("  ⏸️ No scrapers running")
except:
    print("  Could not check processes")

print("\n" + "=" * 60)
print("✅ REPORT COMPLETE")
print("=" * 60)