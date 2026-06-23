import sys
sys.path.insert(0, r'C:\Users\Namitha\Downloads\domain-research')

from supabase import create_client
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def fetch_domains_by_tld(tld, limit=100, min_score=0):
    """Fetch domains by TLD from database"""
    try:
        # Clean TLD input
        tld = tld.strip().lower()
        if not tld.startswith('.'):
            tld = '.' + tld
        
        # Query Supabase
        result = supabase.table('domains').select(
            'domain_name, score, dmarc_policy, spamhaus_clean, domain_age_years'
        ).ilike('domain_name', f'%{tld}').gte('score', min_score).order('score', desc=True).limit(limit).execute()
        
        return result.data
    except Exception as e:
        print(f"Error fetching domains by TLD: {e}")
        return []

def fetch_domains_by_multiple_tlds(tlds, limit_per_tld=50, min_score=0):
    """Fetch domains for multiple TLDs"""
    all_domains = []
    for tld in tlds:
        domains = fetch_domains_by_tld(tld, limit_per_tld, min_score)
        all_domains.extend(domains)
    return all_domains

def get_tld_stats():
    """Get statistics for TLDs in the database"""
    try:
        # Get all domains
        result = supabase.table('domains').select('domain_name').execute()
        
        # Count TLDs
        tld_counts = {}
        for r in result.data:
            domain = r['domain_name']
            if '.' in domain:
                tld = '.' + domain.split('.')[-1]
                tld_counts[tld] = tld_counts.get(tld, 0) + 1
        
        # Sort by count
        sorted_tlds = sorted(tld_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tlds
    except Exception as e:
        print(f"Error getting TLD stats: {e}")
        return []

if __name__ == "__main__":
    # Test
    tld = input("Enter TLD (e.g., .com, .org): ").strip()
    limit = int(input("Number of domains to fetch: ") or 100)
    
    domains = fetch_domains_by_tld(tld, limit, min_score=0)
    
    print(f"\n📊 Found {len(domains)} domains for TLD {tld}")
    for d in domains[:20]:
        print(f"  {d['domain_name']} (Score: {d['score']})")