import dns.resolver

def check_mx(domain):
    """Check if domain has MX record"""
    try:
        dns.resolver.resolve(domain, "MX", lifetime=3)
        return True
    except:
        return False

def check_spf(domain):
    """Check if domain has SPF record"""
    try:
        txts = dns.resolver.resolve(domain, "TXT", lifetime=3)
        return any("v=spf1" in r.to_text() for r in txts)
    except:
        return False

def check_dmarc(domain):
    """Check DMARC policy: none, quarantine, reject, or missing"""
    try:
        records = dns.resolver.resolve(f"_dmarc.{domain}", "TXT", lifetime=3)
        for r in records:
            txt = r.to_text()
            if "p=reject" in txt:
                return "reject"
            elif "p=quarantine" in txt:
                return "quarantine"
            elif "p=none" in txt:
                return "none"
        return "missing"
    except:
        return "missing"

def check_dns(domain):
    """Combined DNS check"""
    return {
        "domain_name": domain,
        "has_mx": check_mx(domain),
        "has_spf": check_spf(domain),
        "dmarc_policy": check_dmarc(domain)
    }