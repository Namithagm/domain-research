from scraper.scorer import get_domain_age
from supabase import create_client
import os
from dotenv import load_dotenv
import time

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# Get domains without age
result = supabase.table('domains').select('domain_name').is_('domain_age_years', 'null').execute()
domains = [r['domain_name'] for r in result.data]

print(f"📊 Found {len(domains)} domains without age")
print("-" * 50)

updated = 0
for i, d in enumerate(domains):
    try:
        age = get_domain_age(d)
        if age:
            supabase.table('domains').update({'domain_age_years': age}).eq('domain_name', d).execute()
            print(f"✅ {i+1}/{len(domains)} {d}: {age} years")
            updated += 1
        else:
            print(f"⚠️ {i+1}/{len(domains)} {d}: Not found")
        time.sleep(0.3)
    except Exception as e:
        print(f"❌ {i+1}/{len(domains)} {d}: Error")

print(f"\n✅ Updated: {updated} domains")