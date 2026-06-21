from scraper.scorer import get_domain_age
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# Domains to update
domains = ['asp.net', 'ubc.ca', 'loc.gov', 'hellomagazine.com', 'bluehost.com', 'msnbc.com']

print("Updating domain ages...")
print("-" * 40)

for d in domains:
    try:
        age = get_domain_age(d)
        if age:
            supabase.table('domains').update({'domain_age_years': age}).eq('domain_name', d).execute()
            print(f"✅ {d}: {age} years updated")
        else:
            print(f"⚠️ {d}: Age not found")
    except Exception as e:
        print(f"❌ {d}: Error - {e}")