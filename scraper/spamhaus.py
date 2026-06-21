import dns.resolver

def check_spamhaus(domain):
    """Check Spamhaus using DNS (more reliable than HTTP)"""
    try:
        # Try DNS lookup first (most reliable)
        dns.resolver.resolve(f"{domain}.dbl.spamhaus.org", "A", lifetime=5)
        return {"spamhaus_clean": False, "spamhaus_class": "listed"}
    except dns.resolver.NXDOMAIN:
        return {"spamhaus_clean": True, "spamhaus_class": "clean"}
    except Exception as e:
        # If DNS fails, try HTTP API as fallback
        try:
            import requests
            url = f"https://apibl.spamhaus.net/lookup/v1/dbl/{domain}"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if r.status_code == 404:
                return {"spamhaus_clean": True, "spamhaus_class": "clean"}
            elif r.status_code == 200:
                data = r.json()
                return {"spamhaus_clean": False, "spamhaus_class": data.get("resp", "flagged")}
            else:
                return {"spamhaus_clean": None, "spamhaus_class": "unknown"}
        except:
            return {"spamhaus_clean": None, "spamhaus_class": "error"}