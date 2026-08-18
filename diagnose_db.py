#!/usr/bin/env python3
"""
Diagnostic script to check Supabase connection and data
Run this to find why domains are not showing
"""

import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import date

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

print("=" * 70)
print("🔍 DATABASE DIAGNOSTIC REPORT")
print("=" * 70)

# Check credentials
print("\n1️⃣  CHECKING CREDENTIALS:")
print(f"   SUPABASE_URL: {'✅ SET' if SUPABASE_URL else '❌ MISSING'}")
print(f"   SUPABASE_KEY: {'✅ SET' if SUPABASE_KEY else '❌ MISSING'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n❌ FATAL: Missing Supabase credentials in .env")
    print("   Add these to your .env file:")
    print("   SUPABASE_URL=your_url_here")
    print("   SUPABASE_KEY=your_key_here")
    exit(1)

# Connect to Supabase
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("   ✅ Supabase client created successfully")
except Exception as e:
    print(f"   ❌ Failed to create Supabase client: {e}")
    exit(1)

# Check domains table
print("\n2️⃣  CHECKING 'domains' TABLE:")
try:
    result = supabase.table("domains").select("count", count="exact").execute()
    total = result.count
    print(f"   ✅ Table exists")
    print(f"   📊 Total domains: {total}")
    
    if total == 0:
        print("   ⚠️  WARNING: Database is empty!")
    else:
        print(f"   ✅ Found {total} domains")
except Exception as e:
    print(f"   ❌ Error accessing domains table: {e}")
    print("   Make sure the 'domains' table exists in Supabase")

# Check scrape_log table
print("\n3️⃣  CHECKING 'scrape_log' TABLE:")
try:
    result = supabase.table("scrape_log").select("*").limit(1).execute()
    if result.data:
        print(f"   ✅ Table exists")
        print(f"   📊 Latest scrape: {result.data[0]}")
    else:
        print(f"   ⚠️  Table exists but is EMPTY (no scrape_log entries)")
except Exception as e:
    print(f"   ❌ Error accessing scrape_log table: {e}")

# Check sample domain data
print("\n4️⃣  CHECKING SAMPLE DOMAIN DATA:")
try:
    result = supabase.table("domains").select("*").limit(3).execute()
    if result.data:
        print(f"   ✅ Found sample domains:")
        for domain in result.data:
            domain_name = domain.get('domain_name', 'N/A')
            score = domain.get('score', 'N/A')
            print(f"      - {domain_name}: score={score}")
    else:
        print(f"   ❌ No domains found in database")
except Exception as e:
    print(f"   ❌ Error fetching sample domains: {e}")

# Check domain score distribution
print("\n5️⃣  CHECKING SCORE DISTRIBUTION:")
try:
    high = supabase.table("domains").select("count", count="exact").gte("score", 70).execute().count
    medium = supabase.table("domains").select("count", count="exact").gte("score", 50).lt("score", 70).execute().count
    low = supabase.table("domains").select("count", count="exact").lt("score", 50).execute().count
    
    print(f"   High (70+):   {high} domains")
    print(f"   Medium (50-69): {medium} domains")
    print(f"   Low (<50):    {low} domains")
except Exception as e:
    print(f"   ❌ Error checking scores: {e}")

# Check DMARC distribution
print("\n6️⃣  CHECKING DMARC DISTRIBUTION:")
try:
    for policy in ['none', 'quarantine', 'reject', 'missing']:
        count = supabase.table("domains").select("count", count="exact").eq("dmarc_policy", policy).execute().count
        print(f"   {policy.upper():12} {count:5} domains")
except Exception as e:
    print(f"   ❌ Error checking DMARC: {e}")

# Check Spamhaus status
print("\n7️⃣  CHECKING SPAMHAUS STATUS:")
try:
    clean = supabase.table("domains").select("count", count="exact").eq("spamhaus_clean", True).execute().count
    flagged = supabase.table("domains").select("count", count="exact").eq("spamhaus_clean", False).execute().count
    unknown = supabase.table("domains").select("count", count="exact").is_("spamhaus_clean", "null").execute().count
    
    print(f"   Clean:   {clean} domains")
    print(f"   Flagged: {flagged} domains")
    print(f"   Unknown: {unknown} domains")
except Exception as e:
    print(f"   ❌ Error checking Spamhaus: {e}")

# Test get_fresh_domains query
print("\n8️⃣  TESTING get_fresh_domains QUERY:")
try:
    from datetime import timedelta
    today = date.today()
    cooldown_cutoff = str(today - timedelta(days=1))
    
    query = (
        supabase.table("domains")
        .select("domain_name, score")
        .gte("score", 70)
        .neq("dmarc_policy", "reject")
        .eq("is_blacklisted", False)
        .or_(f"last_served.is.null,last_served.lt.{cooldown_cutoff}")
        .order("score", desc=True)
        .limit(5)
    )
    result = query.execute()
    
    if result.data:
        print(f"   ✅ Query works! Found {len(result.data)} fresh domains:")
        for domain in result.data:
            print(f"      - {domain['domain_name']}: score={domain['score']}")
    else:
        print(f"   ⚠️  Query returned 0 results")
        print("   This could mean:")
        print("      1. No domains have score >= 70")
        print("      2. All domains are blacklisted")
        print("      3. All domains have DMARC policy = reject")
except Exception as e:
    print(f"   ❌ Error in query: {e}")

print("\n" + "=" * 70)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 70)
print("\nNext steps:")
print("1. If total domains = 0, your scraper never ran or data wasn't saved")
print("2. If total > 0 but fresh domains = 0, check DMARC/score filters")
print("3. If scores are all NULL, run the scraper to process domains")
print("4. Check scraper_report.py for detailed statistics")
