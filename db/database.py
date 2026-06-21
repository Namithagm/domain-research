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
        supabase.table("domains").upsert(data, on_conflict="domain_name").execute()
    except Exception as e:
        print(f"DB save error: {e}")

def get_fresh_domains(count=50, min_score=70, cooldown=30, max_age_years=7):
    """Get fresh domains that haven't been served recently and are older than specified years"""
    try:
        result = supabase.rpc("get_fresh_domains", {
            "min_score": min_score,
            "domain_count": count,
            "cooldown_days": cooldown,
            "max_age_years": max_age_years
        }).execute()
        return result.data
    except Exception as e:
        print(f"DB fetch error: {e}")
        return []

def mark_as_served(domains, batch_id):
    """Mark domains as served with batch ID"""
    try:
        today = str(date.today())
        for domain in domains:
            # First get current times_served
            result = supabase.table("domains").select("times_served").eq("domain_name", domain).execute()
            current_times = result.data[0]["times_served"] if result.data else 0
            
            # Update with incremented value (NO .raw()!)
            supabase.table("domains").update({
                "last_served": today,
                "times_served": current_times + 1
            }).eq("domain_name", domain).execute()
            
            # Log the served domain
            supabase.table("served_log").insert({
                "domain_name": domain,
                "served_date": today,
                "batch_id": batch_id
            }).execute()
    except Exception as e:
        print(f"Mark served error: {e}")

def get_stats():
    """Get dashboard statistics"""
    try:
        total = supabase.table("domains").select("*", count="exact").execute().count
        high = supabase.table("domains").select("*", count="exact").gte("score", 70).execute().count
        available = supabase.table("domains").select("*", count="exact").gte("score", 70).eq("is_blacklisted", False).execute().count
        served = supabase.table("served_log").select("*", count="exact").eq("served_date", str(date.today())).execute().count
        
        last = supabase.table("scrape_log").select("scrape_date").order("scrape_date", desc=True).limit(1).execute()
        
        # Get old domains count (before 2019)
        old_domains = supabase.table("domains").select("*", count="exact").gte("domain_age_years", 7).execute().count
        
        return {
            "total": total,
            "high_score": high,
            "available": available,
            "served_today": served,
            "last_scrape": last.data[0]["scrape_date"] if last.data else "Never",
            "old_domains": old_domains
        }
    except Exception as e:
        print(f"Stats error: {e}")
        return {"total": 0, "high_score": 0, "available": 0, "served_today": 0, "last_scrape": "Never", "old_domains": 0}

def log_scrape(fetched, stored, status):
    """Log scraping activity"""
    try:
        supabase.table("scrape_log").insert({
            "scrape_date": str(date.today()),
            "domains_fetched": fetched,
            "domains_stored": stored,
            "status": status
        }).execute()
    except Exception as e:
        print(f"Log scrape error: {e}")

def get_old_domains_count(min_age=7):
    """Get count of domains older than specified years"""
    try:
        result = supabase.table("domains").select("*", count="exact").gte("domain_age_years", min_age).execute()
        return result.count
    except Exception as e:
        print(f"Get old domains error: {e}")
        return 0

def get_domain_by_name(domain_name):
    """Get a single domain by name"""
    try:
        result = supabase.table("domains").select("*").eq("domain_name", domain_name).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Get domain error: {e}")
        return None

def update_domain(domain_name, data):
    """Update a specific domain"""
    try:
        supabase.table("domains").update(data).eq("domain_name", domain_name).execute()
        return True
    except Exception as e:
        print(f"Update domain error: {e}")
        return False

def delete_old_domains(days=30):
    """Delete domains older than specified days (for cleanup)"""
    try:
        result = supabase.table("domains").delete().lt("date_added", date.today() - timedelta(days=days)).execute()
        return len(result.data) if result.data else 0
    except Exception as e:
        print(f"Delete old domains error: {e}")
        return 0

def get_domains_with_age(min_age=7, limit=100):
    """Get domains with age greater than specified years"""
    try:
        result = supabase.table("domains").select("domain_name, score, domain_age_years, dmarc_policy, spamhaus_clean").gte("domain_age_years", min_age).order("score", desc=True).limit(limit).execute()
        return result.data
    except Exception as e:
        print(f"Get domains with age error: {e}")
        return []

def get_domains_without_age(limit=100):
    """Get domains without age"""
    try:
        result = supabase.table("domains").select("domain_name").is_("domain_age_years", "null").limit(limit).execute()
        return result.data
    except Exception as e:
        print(f"Get domains without age error: {e}")
        return []

def count_domains_without_age():
    """Count domains without age"""
    try:
        result = supabase.table("domains").select("*", count="exact").is_("domain_age_years", "null").execute()
        return result.count
    except Exception as e:
        print(f"Count domains without age error: {e}")
        return 0

def reset_all_served():
    """Reset all served status (for testing)"""
    try:
        supabase.table("domains").update({
            "last_served": None,
            "times_served": 0
        }).execute()
        supabase.table("served_log").delete().execute()
        return True
    except Exception as e:
        print(f"Reset served error: {e}")
        return False

def check_domain_exists(domain_name):
    """Check if a domain already exists in the database"""
    try:
        result = supabase.table("domains").select("domain_name").eq("domain_name", domain_name).execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"Check domain error: {e}")
        return False