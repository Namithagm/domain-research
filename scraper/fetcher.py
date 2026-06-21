import requests
import pandas as pd
from io import StringIO
import zipfile
import io

def fetch_majestic(limit=3000, offset=0):
    """Fetch Majestic domains with offset"""
    try:
        url = "https://downloads.majestic.com/majestic_million.csv"
        r = requests.get(url, timeout=30)
        df = pd.read_csv(StringIO(r.text))
        all_domains = df["Domain"].tolist()
        
        # Apply offset and limit
        if offset > 0:
            return all_domains[offset:offset+limit]
        else:
            return all_domains[:limit]
            
    except Exception as e:
        print(f"Majestic failed: {e}")
        return []

def fetch_tranco(limit=2000):
    """Fetch domains from Tranco List"""
    try:
        url = "https://tranco-list.eu/top-1m.csv.zip"
        r = requests.get(url, timeout=30)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        df = pd.read_csv(
            z.open(z.namelist()[0]),
            header=None,
            names=["rank", "domain"]
        )
        return df["domain"].tolist()[:limit]
    except Exception as e:
        print(f"Tranco failed: {e}")
        return []

def get_all_domains(limit=5000, offset=0):
    """Combine both sources with offset support"""
    domains = fetch_majestic(limit, offset)
    
    # If not enough domains from Majestic, supplement with Tranco
    if len(domains) < limit:
        tranco_limit = limit - len(domains)
        domains += fetch_tranco(tranco_limit)
    
    return list(set(domains))  # Deduplicate

def fetch_majestic_with_offset(limit=5000, offset=0):
    """Fetch Majestic domains with offset (dedicated function)"""
    try:
        url = "https://downloads.majestic.com/majestic_million.csv"
        r = requests.get(url, timeout=30)
        df = pd.read_csv(StringIO(r.text))
        all_domains = df["Domain"].tolist()
        
        # Apply offset and limit
        start = offset
        end = offset + limit
        
        # Handle cases where offset exceeds total domains
        if start >= len(all_domains):
            print(f"⚠️ Offset {offset} exceeds total domains {len(all_domains)}")
            return []
            
        return all_domains[start:end]
        
    except Exception as e:
        print(f"Majestic with offset failed: {e}")
        return []