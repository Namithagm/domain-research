from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# Count domains without age
result = supabase.table('domains').select('count', count='exact').is_('domain_age_years', 'null').execute()
count = result.count

print(f"📊 Found {count} domains without age")

if count > 0:
    print("⚠️ WARNING: This will permanently delete these domains!")
    confirm = input("Type 'yes' to continue: ")
    
    if confirm.lower() == 'yes':
        # Delete domains without age
        result = supabase.table('domains').delete().is_('domain_age_years', 'null').execute()
        print(f"✅ Deleted {len(result.data)} domains without age")
    else:
        print("❌ Cancelled")
else:
    print("✅ No domains without age found!")