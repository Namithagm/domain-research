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

def get_base_query():
    """Return base query with all filters applied"""
    return supabase.table('domains').select(
        'domain_name, score, dmarc_policy, spamhaus_clean, domain_age_years, has_spf, spf_record, has_mx'
    ).neq('dmarc_policy', 'reject').gte('domain_age_years', 5).eq('spamhaus_clean', True)

def search_domains_by_spf(keyword, limit=100):
    """
    Search for domains where SPF record contains the keyword
    Filters: DMARC != reject, Age >= 5 years (before 2021), Spamhaus Clean
    """
    try:
        keyword = keyword.strip().lower()
        
        result = get_base_query().ilike('spf_record', f'%{keyword}%').order('score', desc=True).limit(limit).execute()
        
        return result.data
    except Exception as e:
        print(f"Error searching SPF: {e}")
        return []

def search_domains_by_keyword(keyword, limit=100):
    """
    Search for domains that contain the keyword in domain name
    Filters: DMARC != reject, Age >= 5 years (before 2021), Spamhaus Clean
    """
    try:
        keyword = keyword.strip().lower()
        
        result = get_base_query().ilike('domain_name', f'%{keyword}%').order('score', desc=True).limit(limit).execute()
        
        return result.data
    except Exception as e:
        print(f"Error searching domains: {e}")
        return []

def fetch_domains_by_tld(tld, limit=100, min_score=0, cooldown_days=30):
    """
    Fetch domains by TLD
    Filters: DMARC != reject, Age >= 5 years (before 2021), Spamhaus Clean
    """
    try:
        tld = tld.strip().lower()
        if not tld.startswith('.'):
            tld = '.' + tld
        
        # Calculate cooldown date
        from datetime import date, timedelta
        cooldown_date = date.today() - timedelta(days=cooldown_days)
        
        # Get domains with filters
        result = get_base_query().ilike('domain_name', f'%{tld}').order('score', desc=True).limit(limit).execute()
        
        # Apply cooldown filter
        filtered_domains = []
        for d in result.data:
            last_served = d.get('last_served')
            if last_served is None:
                filtered_domains.append(d)
            else:
                try:
                    last_served_date = datetime.strptime(last_served, '%Y-%m-%d').date()
                    if last_served_date < cooldown_date:
                        filtered_domains.append(d)
                except:
                    filtered_domains.append(d)
        
        return filtered_domains
    except Exception as e:
        print(f"Error fetching domains by TLD: {e}")
        return []

def mark_domains_as_served(domains, batch_id):
    """Mark fetched domains as served"""
    try:
        today = str(date.today())
        for domain in domains:
            result = supabase.table('domains').select('times_served').eq('domain_name', domain).execute()
            current_times = result.data[0]['times_served'] if result.data else 0
            
            supabase.table('domains').update({
                "last_served": today,
                "times_served": current_times + 1
            }).eq('domain_name', domain).execute()
            
            supabase.table('served_log').insert({
                "domain_name": domain,
                "served_date": today,
                "batch_id": batch_id
            }).execute()
    except Exception as e:
        print(f"Mark served error: {e}")

def get_filter_stats():
    """Get statistics for filtered domains"""
    try:
        total = supabase.table('domains').select('count', count='exact').execute().count
        
        # Count domains meeting all filters
        result = get_base_query().execute()
        filtered_count = len(result.data)
        
        return {
            'total': total,
            'filtered': filtered_count,
            'filtered_percentage': round((filtered_count / total) * 100, 2) if total > 0 else 0
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {}

if __name__ == "__main__":
    # Test
    stats = get_filter_stats()
    print(f"📊 Filter Statistics:")
    print(f"  Total domains: {stats['total']}")
    print(f"  Matching filters: {stats['filtered']}")
    print(f"  Percentage: {stats['filtered_percentage']}%")