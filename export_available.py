import sys
sys.path.insert(0, r'C:\Users\Namitha\Downloads\domain-research')

from supabase import create_client
import os
from dotenv import load_dotenv
import csv

load_dotenv()

supabase = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_KEY')
)

# Get all available domains (score >= 70, not served)
result = supabase.table('domains').select(
    'domain_name, score, dmarc_policy, domain_age_years, spamhaus_clean, talos_score, vt_clean, abuse_score'
).gte('score', 70).is_('last_served', 'null').order('score', desc=True).execute()

print(f'Found {len(result.data)} available domains')
print('Exporting to CSV...')

# Export to CSV
with open('available_domains.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Domain', 'Score', 'DMARC', 'Age', 'Spamhaus', 'Talos', 'VT Clean', 'Abuse Score'])
    
    for r in result.data:
        writer.writerow([
            r['domain_name'],
            r['score'],
            r['dmarc_policy'],
            r['domain_age_years'],
            r['spamhaus_clean'],
            r['talos_score'],
            r['vt_clean'],
            r['abuse_score']
        ])

print(f'✅ Exported {len(result.data)} domains to available_domains.csv')
print('File location: C:\\Users\\Namitha\\Downloads\\domain-research\\available_domains.csv')