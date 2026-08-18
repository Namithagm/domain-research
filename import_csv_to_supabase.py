#!/usr/bin/env python3
"""
Bulk import domains from CSV to Supabase
Run this ONCE to restore your 45K domains from available_domains.csv
"""

import os
import csv
from datetime import date
from supabase import create_client
from dotenv import load_dotenv
import time

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 70)
print("📥 BULK IMPORT: CSV → Supabase")
print("=" * 70)

# Read CSV file
csv_file = "available_domains.csv"
if not os.path.exists(csv_file):
    print(f"❌ File not found: {csv_file}")
    exit(1)

domains_to_import = []
try:
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            domain_name = row.get('Domain', '').strip()
            if not domain_name:
                continue
            
            # Parse values
            try:
                score = int(row.get('Score', 0)) if row.get('Score') else 0
            except:
                score = 0
            
            dmarc_policy = row.get('DMARC', '').strip() or None
            
            try:
                domain_age = float(row.get('Age', 0)) if row.get('Age') else None
            except:
                domain_age = None
            
            spamhaus_clean_str = row.get('Spamhaus', '').strip().lower()
            if spamhaus_clean_str == 'true':
                spamhaus_clean = True
            elif spamhaus_clean_str == 'false':
                spamhaus_clean = False
            else:
                spamhaus_clean = None
            
            domains_to_import.append({
                'domain_name': domain_name,
                'score': score,
                'dmarc_policy': dmarc_policy,
                'domain_age_years': domain_age,
                'spamhaus_clean': spamhaus_clean,
                'talos_score': row.get('Talos', '').strip() or None,
                'vt_clean': row.get('VT Clean', '').strip().lower() == 'true' if row.get('VT Clean', '').strip() else None,
                'abuse_score': int(row.get('Abuse Score', 0)) if row.get('Abuse Score') else None,
                'last_checked': str(date.today()),
                'has_mx': True,  # Assumed from CSV
                'has_spf': True,  # Assumed from CSV
                'is_blacklisted': False,  # Assumed from CSV
                'times_served': 0,
                'spamhaus_class': 'clean' if spamhaus_clean else 'unknown',
            })
    
    print(f"✅ Parsed {len(domains_to_import)} domains from CSV")
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
    exit(1)

if not domains_to_import:
    print("❌ No domains found in CSV")
    exit(1)

# Check how many already exist
print(f"\n⏳ Checking existing domains in Supabase...")
try:
    existing = supabase.table("domains").select("count", count="exact").execute().count
    print(f"   Current domains in DB: {existing}")
except:
    print("   Could not check existing count")

# Upload in batches of 100
batch_size = 100
total_imported = 0
failed = 0

print(f"\n📤 Uploading {len(domains_to_import)} domains in batches of {batch_size}...")

for i in range(0, len(domains_to_import), batch_size):
    batch = domains_to_import[i:i+batch_size]
    batch_num = (i // batch_size) + 1
    total_batches = (len(domains_to_import) + batch_size - 1) // batch_size
    
    try:
        result = supabase.table("domains").upsert(batch, on_conflict="domain_name").execute()
        imported_count = len(batch)
        total_imported += imported_count
        
        print(f"   [{batch_num}/{total_batches}] ✅ Uploaded {imported_count} domains (Total: {total_imported})")
        time.sleep(0.5)  # Rate limit
        
    except Exception as e:
        print(f"   [{batch_num}/{total_batches}] ❌ Error: {e}")
        failed += batch_size

print("\n" + "=" * 70)
print("✅ IMPORT COMPLETE!")
print("=" * 70)

# Final stats
try:
    final_count = supabase.table("domains").select("count", count="exact").execute().count
    high_score = supabase.table("domains").select("count", count="exact").gte("score", 70).execute().count
    
    print(f"\n📊 Final Database Stats:")
    print(f"   Total domains: {final_count}")
    print(f"   High score (70+): {high_score}")
    print(f"   Successfully imported: {total_imported}")
    print(f"   Failed: {failed}")
    
except Exception as e:
    print(f"❌ Error getting final stats: {e}")

print("\n🚀 Your dashboard should now show the domains!")
print("   If not, refresh your Streamlit app")
