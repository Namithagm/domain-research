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

def search_domains_by_spf(keyword, limit=100):
    """
    Search for domains where SPF record contains the keyword
    """
    try:
        keyword = keyword.strip().lower()
        
        # Search for domains where SPF record contains the keyword
        result = supabase.table('domains').select(
            'domain_name, score, dmarc_policy, spamhaus_clean, domain_age_years, has_spf, spf_record'
        ).not_.is_('spf_record', 'null').ilike('spf_record', f'%{keyword}%').order('score', desc=True).limit(limit).execute()
        
        return result.data
    except Exception as e:
        print(f"Error searching SPF: {e}")
        return []

def search_domains_by_keyword(keyword, limit=100):
    """
    Simple search: Return domains that contain the keyword in domain name
    """
    try:
        keyword = keyword.strip().lower()
        
        result = supabase.table('domains').select(
            'domain_name, score, dmarc_policy, spamhaus_clean, domain_age_years, has_spf, spf_record'
        ).ilike('domain_name', f'%{keyword}%').order('score', desc=True).limit(limit).execute()
        
        return result.data
    except Exception as e:
        print(f"Error searching domains: {e}")
        return []

if __name__ == "__main__":
    keyword = input("Enter keyword to search in SPF: ").strip()
    results = search_domains_by_spf(keyword, limit=50)
    
    print(f"\n📊 Found {len(results)} domains with '{keyword}' in SPF")
    for d in results[:20]:
        spf = d.get('spf_record', 'N/A')
        print(f"  {d['domain_name']} (SPF: {spf[:50]}...)" if len(spf) > 50 else f"  {d['domain_name']} (SPF: {spf})")