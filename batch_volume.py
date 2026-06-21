from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

print("📊 BATCH VOLUME REPORT")
print("=" * 50)

# Total domains
total = supabase.table('domains').select('count', count='exact').execute().count
print(f"Total Domains: {total}")

# High score domains
high = supabase.table('domains').select('count', count='exact').gte('score', 70).execute().count
print(f"High Score (70+): {high}")

# Available domains
available = supabase.table('domains').select('count', count='exact').gte('score', 70).eq('is_blacklisted', False).execute().count
print(f"Available Now: {available}")

# Old domains
old = supabase.table('domains').select('count', count='exact').gte('domain_age_years', 7).execute().count
print(f"Old Domains (7+ yrs): {old}")

# Domains without age
no_age = supabase.table('domains').select('count', count='exact').is_('domain_age_years', 'null').execute().count
print(f"Domains without age: {no_age}")

print("\n📊 Score Distribution:")
# Score ranges
ranges = [(0, 49), (50, 69), (70, 79), (80, 89), (90, 100)]
for low, high in ranges:
    count = supabase.table('domains').select('count', count='exact').gte('score', low).lt('score', high + 1).execute().count
    print(f"  {low}-{high}: {count} domains")

print("\n📊 DMARC Distribution:")
dmarc_types = ['none', 'quarantine', 'missing', 'reject']
for policy in dmarc_types:
    count = supabase.table('domains').select('count', count='exact').eq('dmarc_policy', policy).execute().count
    print(f"  {policy}: {count} domains")

print("\n📊 Spamhaus Status:")
clean = supabase.table('domains').select('count', count='exact').eq('spamhaus_clean', True).execute().count
unknown = supabase.table('domains').select('count', count='exact').is_('spamhaus_clean', 'null').execute().count
flagged = supabase.table('domains').select('count', count='exact').eq('spamhaus_clean', False).execute().count
print(f"  Clean: {clean}")
print(f"  Unknown: {unknown}")
print(f"  Flagged: {flagged}")

print("\n📊 Domain Age Distribution:")
age_ranges = [(0, 2), (2, 5), (5, 10), (10, 20), (20, 100)]
for low, high in age_ranges:
    if high == 100:
        count = supabase.table('domains').select('count', count='exact').gte('domain_age_years', low).execute().count
        print(f"  {low}+ years: {count} domains")
    else:
        count = supabase.table('domains').select('count', count='exact').gte('domain_age_years', low).lt('domain_age_years', high).execute().count
        print(f"  {low}-{high} years: {count} domains")

print("\n" + "=" * 50)
print(f"📅 Report generated: {date.today()}")