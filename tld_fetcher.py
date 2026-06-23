import sys
sys.path.insert(0, r'C:\Users\Namitha\Downloads\domain-research')

from supabase import create_client
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import date, timedelta

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def fetch_domains_by_tld(tld, limit=100, min_score=0, cooldown_days=30):
    """Fetch domains by TLD from database with cooldown"""
    try:
        # Clean TLD input
        tld = tld.strip().lower()
        if not tld.startswith('.'):
            tld = '.' + tld
        
        # Calculate cooldown date
        cooldown_date = date.today() - timedelta(days=cooldown_days)
        
        # Query Supabase with cooldown filter
        result = supabase.table('domains').select(
            'domain_name, score, dmarc_policy, spamhaus_clean, domain_age_years, last_served'
        ).ilike('domain_name', f'%{tld}').gte('score', min_score).order('score', desc=True).limit(limit).execute()
        
        # Filter domains not served within cooldown period
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
            # Get current times_served
            result = supabase.table('domains').select('times_served').eq('domain_name', domain).execute()
            current_times = result.data[0]['times_served'] if result.data else 0
            
            # Update with incremented value
            supabase.table('domains').update({
                "last_served": today,
                "times_served": current_times + 1
            }).eq('domain_name', domain).execute()
            
            # Log the served domain
            supabase.table('served_log').insert({
                "domain_name": domain,
                "served_date": today,
                "batch_id": batch_id
            }).execute()
    except Exception as e:
        print(f"Mark served error: {e}")

def get_tld_stats():
    """Get statistics for TLDs in the database"""
    try:
        result = supabase.table('domains').select('domain_name').execute()
        
        tld_counts = {}
        for r in result.data:
            domain = r['domain_name']
            if '.' in domain:
                tld = '.' + domain.split('.')[-1]
                tld_counts[tld] = tld_counts.get(tld, 0) + 1
        
        sorted_tlds = sorted(tld_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tlds
    except Exception as e:
        print(f"Error getting TLD stats: {e}")
        return []

if __name__ == "__main__":
    tld = input("Enter TLD (e.g., .com, .org): ").strip()
    limit = int(input("Number of domains to fetch: ") or 100)
    cooldown = int(input("Cooldown days: ") or 30)
    
    domains = fetch_domains_by_tld(tld, limit, min_score=0, cooldown_days=cooldown)
    
    print(f"\n📊 Found {len(domains)} domains for TLD {tld}")
    for d in domains[:20]:
        print(f"  {d['domain_name']} (Score: {d['score']}, Last Served: {d.get('last_served', 'Never')})")