import dns.resolver
import requests

def check_spamhaus(domain):
    """Check Spamhaus with timeout to prevent hanging"""
    try:
        # DNS check with timeout (3 seconds)
        dns.resolver.resolve(f"{domain}.dbl.spamhaus.org", "A", lifetime=3)
        return {"spamhaus_clean": False, "spamhaus_class": "listed"}
    except dns.resolver.NXDOMAIN:
        return {"spamhaus_clean": True, "spamhaus_class": "clean"}
    except dns.resolver.Timeout:
        return {"spamhaus_clean": None, "spamhaus_class": "timeout"}
    except Exception as e:
        return {"spamhaus_clean": None, "spamhaus_class": "error"}