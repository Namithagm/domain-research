import dns.resolver
import dns.exception

def check_mx(domain):
    """Check if domain has MX record with timeout"""
    try:
        dns.resolver.resolve(domain, "MX", lifetime=3)
        return True
    except dns.exception.Timeout:
        return False
    except:
        return False

def check_spf(domain):
    """Check if domain has SPF record and return the actual SPF text"""
    try:
        txts = dns.resolver.resolve(domain, "TXT", lifetime=3)
        for r in txts:
            txt = r.to_text()
            if "v=spf1" in txt:
                return txt  # Return the actual SPF record
        return None
    except dns.exception.Timeout:
        return None
    except:
        return None

def check_dmarc(domain):
    """Check DMARC policy with timeout"""
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
    except dns.exception.Timeout:
        return "missing"
    except:
        return "missing"

def check_dns(domain):
    """Combined DNS check - now stores full SPF record"""
    spf_record = check_spf(domain)
    return {
        "domain_name": domain,
        "has_mx": check_mx(domain),
        "has_spf": spf_record is not None,
        "spf_record": spf_record,  # Store the full SPF text
        "dmarc_policy": check_dmarc(domain)
    }