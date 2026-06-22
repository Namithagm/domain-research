import dns.resolver
import dns.exception
import requests

def check_spamhaus(domain):
    """Check Spamhaus with timeout"""
    try:
        # DNS check with timeout
        dns.resolver.resolve(f"{domain}.dbl.spamhaus.org", "A", lifetime=3)
        return {"spamhaus_clean": False, "spamhaus_class": "listed"}
    except dns.resolver.NXDOMAIN:
        return {"spamhaus_clean": True, "spamhaus_class": "clean"}
    except dns.exception.Timeout:
        return {"spamhaus_clean": None, "spamhaus_class": "timeout"}
    except:
        return {"spamhaus_clean": None, "spamhaus_class": "error"}