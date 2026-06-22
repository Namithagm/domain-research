import whois
from datetime import datetime, timezone
import pytz
import threading
import queue

def get_domain_age_with_timeout(domain, timeout=5):
    """Get domain age with timeout to prevent hanging"""
    result_queue = queue.Queue()
    
    def worker():
        try:
            w = whois.whois(domain)
            if w.creation_date:
                if isinstance(w.creation_date, list):
                    creation_date = w.creation_date[0]
                else:
                    creation_date = w.creation_date
                
                if hasattr(creation_date, 'tzinfo') and creation_date.tzinfo is not None:
                    creation_date = creation_date.astimezone(timezone.utc).replace(tzinfo=None)
                
                now = datetime.utcnow()
                age = (now - creation_date).days / 365.25
                result_queue.put(round(age, 1))
            else:
                result_queue.put(None)
        except:
            result_queue.put(None)
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        return None
    
    try:
        return result_queue.get_nowait()
    except:
        return None

def get_domain_age(domain):
    """Get domain age with 5-second timeout"""
    return get_domain_age_with_timeout(domain, timeout=5)

def get_age_points(age):
    """Convert domain age to points"""
    if age is None:
        return 5  # Unknown = neutral
    elif age >= 10:
        return 15  # Very old, trusted
    elif age >= 5:
        return 10  # Established
    elif age >= 2:
        return 5   # Average
    else:
        return 0   # New domain

def score_domain(data):
    """Calculate final domain score out of 100"""
    score = 0
    max_possible = 0

    # ====== DMARC Score (max 60) ======
    dmarc = data.get("dmarc_policy", "missing")
    if dmarc == "none":
        score += 60
    elif dmarc == "quarantine":
        score += 50
    elif dmarc == "missing":
        score += 50
    max_possible += 60

    # ====== Spamhaus Score (max 40) ======
    spamhaus = data.get("spamhaus_clean")
    if spamhaus == True:
        score += 40
    elif spamhaus is None:
        score += 25
    max_possible += 40

    # ====== Talos Score (max 30) ======
    talos = data.get("talos_clean")
    if talos == True:
        score += 30
    elif talos is None:
        score += 10
    max_possible += 30

    # ====== Barracuda Score (max 20) ======
    barracuda = data.get("barracuda_clean")
    if barracuda == True:
        score += 20
    elif barracuda is None:
        score += 10
    max_possible += 20

    # ====== VirusTotal Score (max 25) ======
    vt = data.get("vt_clean")
    if vt == True:
        score += 25
    elif vt is None:
        score += 10
    max_possible += 25

    # ====== AbuseIPDB Score (max 15) ======
    abuse = data.get("abuse_clean")
    if abuse == True:
        score += 15
    elif abuse is None:
        score += 5
    max_possible += 15

    # ====== URLVoid Score (max 10) ======
    urlvoid = data.get("urlvoid_clean")
    if urlvoid == True:
        score += 10
    elif urlvoid is None:
        score += 5
    max_possible += 10

    # ====== Domain Age Score (max 15) ======
    age = data.get("domain_age_years")
    age_points = get_age_points(age)
    score += age_points
    max_possible += 15

    if max_possible == 0:
        return 0

    return round((score / max_possible) * 100)