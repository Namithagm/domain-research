import os
import logging
from supabase import create_client
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

logger = logging.getLogger(__name__)


def _validated_rows(data):
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict) and row.get("domain_name")]


def _safe_count(query, label):
    try:
        result = query.execute()
        return int(getattr(result, "count", 0) or 0)
    except Exception as e:
        logger.exception("Count query failed for %s: %s", label, e)
        return 0

def save_domain(data):
    """Save or update domain in database"""
    try:
        # Add expiry date (7 days from now)
        data["score_expiry"] = str(date.today() + timedelta(days=7))
        supabase.table("domains").upsert(data, on_conflict="domain_name").execute()
    except Exception as e:
        print(f"DB save error: {e}")

def get_fresh_domains(count=50, min_score=70, cooldown=1, max_age_years=7):
    """Get fresh domains that haven't been served recently"""
    rpc_params = {
        "min_score": min_score,
        "domain_count": count,
        "cooldown_days": cooldown,
        "max_age_years": max_age_years
    }

    try:
        result = supabase.rpc("get_fresh_domains", rpc_params).execute()
        rows = _validated_rows(getattr(result, "data", None))
        if rows:
            return rows
        logger.warning("RPC get_fresh_domains returned no usable rows; falling back to table query")
    except Exception as e:
        logger.exception("RPC get_fresh_domains failed; falling back to table query: %s", e)

    today = date.today()
    cooldown_cutoff = str(today - timedelta(days=cooldown))

    try:
        query = (
            supabase.table("domains")
            .select("domain_name, score, dmarc_policy, has_mx, has_spf, spamhaus_clean, spamhaus_class, talos_score, barracuda_status, vt_clean, abuse_score, urlvoid_clean, last_checked, domain_age_years, last_served")
            .gte("score", min_score)
            .neq("dmarc_policy", "reject")
            .eq("is_blacklisted", False)
            .or_("last_served.is.null,last_served.lt." + cooldown_cutoff)
            .order("score", desc=True)
            .limit(count)
        )

        if max_age_years is not None:
            query = query.or_(f"domain_age_years.is.null,domain_age_years.lte.{max_age_years}")

        result = query.execute()
        return _validated_rows(getattr(result, "data", None))
    except Exception as e:
        logger.exception("Direct get_fresh_domains query failed: %s", e)
        return []

def mark_as_served(domains, batch_id):
    """Mark domains as served with batch ID"""
    try:
        if not isinstance(domains, list) or not domains:
            logger.info("mark_as_served called with no domains")
            return

        today = str(date.today())
        unique_domains = list(dict.fromkeys(d for d in domains if d))
        if not unique_domains:
            logger.info("mark_as_served had no valid domain names")
            return

        current = (
            supabase.table("domains")
            .select("domain_name, times_served")
            .in_("domain_name", unique_domains)
            .execute()
        )
        current_rows = getattr(current, "data", None) if hasattr(current, "data") else None
        current_map = {
            row.get("domain_name"): int(row.get("times_served") or 0)
            for row in (current_rows or [])
            if isinstance(row, dict) and row.get("domain_name")
        }

        updates = [
            {
                "domain_name": domain,
                "last_served": today,
                "times_served": current_map.get(domain, 0) + 1
            }
            for domain in unique_domains
        ]
        supabase.table("domains").upsert(updates, on_conflict="domain_name").execute()

        served_logs = [
            {"domain_name": domain, "served_date": today, "batch_id": batch_id}
            for domain in unique_domains
        ]
        supabase.table("served_log").insert(served_logs).execute()
    except Exception as e:
        logger.exception("Mark served error: %s", e)

def get_stats():
    """Get dashboard statistics"""
    stats = {"total": 0, "high_score": 0, "available": 0, "served_today": 0, "last_scrape": "Never", "old_domains": 0}

    stats["total"] = _safe_count(
        supabase.table("domains").select("count", count="exact"),
        "total domains"
    )
    stats["high_score"] = _safe_count(
        supabase.table("domains").select("count", count="exact").gte("score", 70),
        "high score domains"
    )
    stats["available"] = _safe_count(
        supabase.table("domains").select("count", count="exact").eq("is_blacklisted", False).gte("score", 70),
        "available domains"
    )
    stats["served_today"] = _safe_count(
        supabase.table("served_log").select("count", count="exact").eq("served_date", str(date.today())),
        "served today"
    )
    stats["old_domains"] = _safe_count(
        supabase.table("domains").select("count", count="exact").lte("domain_age_years", 7),
        "old domains"
    )

    try:
        last = supabase.table("scrape_log").select("scrape_date").order("scrape_date", desc=True).limit(1).execute()
        data = getattr(last, "data", None)
        if isinstance(data, list) and data and isinstance(data[0], dict) and data[0].get("scrape_date"):
            stats["last_scrape"] = data[0]["scrape_date"]
    except Exception as e:
        logger.exception("Last scrape query failed: %s", e)

    return stats

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

def reset_all_served():
    """Reset all served status (for testing)"""
    try:
        supabase.table("domains").update({
            "last_served": None,
            "times_served": 0
        }).neq("domain_name", "").execute()
        supabase.table("served_log").delete().neq("domain_name", "").execute()
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