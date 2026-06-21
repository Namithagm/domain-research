import os
from dotenv import load_dotenv

loaded = load_dotenv()
print("load_dotenv() found a .env file:", loaded)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print("SUPABASE_URL:", repr(url))
print("SUPABASE_KEY length:", len(key) if key else "None")
print("SUPABASE_KEY starts with:", key[:15] if key else "None")
print("SUPABASE_KEY ends with:", key[-10:] if key else "None")

# JWT keys (anon/service_role) have exactly 2 dots and start with "eyJ"
if key:
    print("Looks like a JWT (starts with eyJ):", key.startswith("eyJ"))
    print("Number of '.' in key (should be 2 for JWT):", key.count("."))