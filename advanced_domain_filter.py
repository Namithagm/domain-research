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

def search_domains_by_keyword(keyword, limit=100):
    """
    Simple search: Return domains that contain the keyword
    """
    try:
        keyword = keyword.strip().lower()
        
        # Search for domains containing the keyword
        result = supabase.table('domains').select(
            'domain_name, score, dmarc_policy, spamhaus_clean, domain_age_years, has_spf, has_mx'
        ).ilike('domain_name', f'%{keyword}%').order('score', desc=True).limit(limit).execute()
        
        return result.data
    except Exception as e:
        print(f"Error searching domains: {e}")
        return []

if __name__ == "__main__":
    keyword = input("Enter keyword to search: ").strip()
    results = search_domains_by_keyword(keyword, limit=50)
    
    print(f"\n📊 Found {len(results)} domains containing '{keyword}'")
    for d in results[:20]:
        print(f"  {d['domain_name']} (Score: {d['score']})")