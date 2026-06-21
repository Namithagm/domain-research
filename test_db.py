from db.database import get_stats

try:
    stats = get_stats()
    print("✅ Supabase connection successful!")
    print(f"Total domains in DB: {stats['total']}")
    print(f"Available now: {stats['available']}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("Check your SUPABASE_URL and SUPABASE_KEY in .env")