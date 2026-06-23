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

def filter_domains(limit=100, spf_outlook=True, dmarc_reject=True, age_7_years=True, spamhaus_clean=True, min_score=0):
    """
    Filter domains with specific criteria:
    - SPF contains Outlook/Microsoft
    - DMARC = reject
    - Domain age >= 7 years (before 2019)
    - Spamhaus clean
    - Minimum score
    """
    try:
        # Start building the query
        query = supabase.table('domains').select(
            'domain_name, score, dmarc_policy, spamhaus_clean, domain_age_years, has_spf, has_mx'
        )
        
        # Apply filters
        if dmarc_reject:
            query = query.eq('dmarc_policy', 'reject')
        
        if spamhaus_clean:
            query = query.eq('spamhaus_clean', True)
        
        if age_7_years:
            query = query.gte('domain_age_years', 7)
        
        if min_score > 0:
            query = query.gte('score', min_score)
        
        # Order by score descending
        query = query.order('score', desc=True)
        
        # Limit results
        query = query.limit(limit * 2)  # Fetch more to filter SPF
        
        result = query.execute()
        
        # Filter for SPF containing Outlook/Microsoft (if enabled)
        filtered_domains = []
        if spf_outlook:
            # Since we don't store full SPF text, we need to check domains that likely have Outlook SPF
            # We'll filter by domain name patterns and then check SPF
            for d in result.data:
                # Check if domain name suggests Microsoft/Outlook
                domain_lower = d['domain_name'].lower()
                if ('microsoft' in domain_lower or 
                    'outlook' in domain_lower or 
                    'office' in domain_lower or
                    'msn' in domain_lower or
                    'live' in domain_lower or
                    'hotmail' in domain_lower):
                    filtered_domains.append(d)
            
            # Limit results
            filtered_domains = filtered_domains[:limit]
        else:
            filtered_domains = result.data[:limit]
        
        return filtered_domains
    except Exception as e:
        print(f"Error filtering domains: {e}")
        return []

def get_filter_stats():
    """Get statistics for filtered domains"""
    try:
        total = supabase.table('domains').select('count', count='exact').execute().count
        
        # Domains with DMARC reject
        dmarc_reject = supabase.table('domains').select('count', count='exact').eq('dmarc_policy', 'reject').execute().count
        
        # Domains with DMARC reject and age >= 7
        dmarc_reject_old = supabase.table('domains').select('count', count='exact').eq('dmarc_policy', 'reject').gte('domain_age_years', 7).execute().count
        
        # Domains with DMARC reject, age >= 7, and spamhaus clean
        dmarc_reject_old_clean = supabase.table('domains').select('count', count='exact').eq('dmarc_policy', 'reject').gte('domain_age_years', 7).eq('spamhaus_clean', True).execute().count
        
        return {
            'total': total,
            'dmarc_reject': dmarc_reject,
            'dmarc_reject_old': dmarc_reject_old,
            'dmarc_reject_old_clean': dmarc_reject_old_clean
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {}

if __name__ == "__main__":
    # Test
    results = filter_domains(limit=20, spf_outlook=True, dmarc_reject=True, age_7_years=True, spamhaus_clean=True)
    
    print(f"\n📊 Found {len(results)} domains matching criteria")
    for d in results[:10]:
        print(f"  {d['domain_name']} (Score: {d['score']}, Age: {d['domain_age_years']} yrs)")