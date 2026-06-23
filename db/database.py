import os
from supabase import create_client
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def save_domain(data):
    """Save or update domain in database"""
    try:
        # Add expiry date (7 days from now)
        data["score_expiry"] = str(date.today() + timedelta(days=7))
        supabase.table("domains").upsert(data, on_conflict="domain_name").execute()
    except Exception as e:
        print(f"DB save error: {e}")

# ... rest of the file remains the same ...