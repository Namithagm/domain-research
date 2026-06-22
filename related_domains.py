import re
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def extract_keywords(domain):
    """Extract keywords from domain name"""
    # Remove TLD (.com, .org, etc.)
    name = re.sub(r'\.[a-z]+$', '', domain)
    # Split by dots and hyphens
    parts = re.split(r'[\.\-]', name)
    return parts

def find_related_domains(domain, limit=20):
    """Find domains related to the given domain"""
    keywords = extract_keywords(domain)
    
    related = []
    for keyword in keywords:
        if len(keyword) > 2:  # Skip short words
            # Search for domains containing this keyword
            result = supabase.table('domains').select('domain_name, score').like('domain_name', f'%{keyword}%').order('score', desc=True).limit(limit).execute()
            related.extend(result.data)
    
    # Remove duplicates and self
    seen = set()
    unique = []
    for r in related:
        if r['domain_name'] != domain and r['domain_name'] not in seen:
            seen.add(r['domain_name'])
            unique.append(r)
    
    return unique[:limit]

def get_emails_with_related(domain, local_parts=None):
    """Get emails for domain + related domains"""
    from email_generator import generate_emails, COMMON_LOCAL_PARTS
    
    if local_parts is None:
        local_parts = COMMON_LOCAL_PARTS
    
    all_emails = []
    
    # 1. Emails for exact domain
    exact_emails = generate_emails(domain, local_parts)
    all_emails.extend([(domain, email) for email in exact_emails[:5]])  # Top 5
    
    # 2. Emails for related domains
    related = find_related_domains(domain, limit=10)
    for r in related[:3]:  # Top 3 related
        emails = generate_emails(r['domain_name'], local_parts)
        all_emails.extend([(r['domain_name'], email) for email in emails[:3]])  # Top 3 each
    
    return all_emails