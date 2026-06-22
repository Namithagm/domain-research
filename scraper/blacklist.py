import dns.resolver
import dns.exception

def check_surbl(domain):
    """Check SURBL blacklist via DNS with timeout"""
    try:
        dns.resolver.resolve(f"{domain}.multi.surbl.org", "A", lifetime=3)
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except dns.exception.Timeout:
        return None
    except:
        return None

def check_uribl(domain):
    """Check URIBL blacklist via DNS with timeout"""
    try:
        dns.resolver.resolve(f"{domain}.black.uribl.com", "A", lifetime=3)
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except dns.exception.Timeout:
        return None
    except:
        return None

def check_blacklist(domain):
    """Combined blacklist check"""
    surbl = check_surbl(domain)
    uribl = check_uribl(domain)
    return {
        "surbl_listed": surbl,
        "uribl_listed": uribl,
        "is_blacklisted": (surbl == True) or (uribl == True)
    }