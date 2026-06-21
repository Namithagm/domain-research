from supabase import create_client
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# Get all domains with date_added
result = supabase.table('domains').select('date_added').execute()

# Count by date
date_counts = {}
for r in result.data:
    date = r['date_added']
    if date:
        date_counts[date] = date_counts.get(date, 0) + 1

print("📊 Domains by Date Added:")
print("-" * 40)
for date, count in sorted(date_counts.items(), reverse=True):
    print(f"{date}: {count} domains")