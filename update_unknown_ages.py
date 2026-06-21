from scraper.scorer import get_domain_age
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

domains = ['rtl.de', 'hetzner.de', 'daad.de', 'continental.com']

print("🔄 Updating Unknown Ages:")
for d in domains:
    age = get_domain_age(d)
    if age:
        supabase.table('domains').update({'domain_age_years': age}).eq('domain_name', d).execute()
        print(f"✅ {d}: {age} years")
    else:
        print(f"⚠️ {d}: Still unknown")