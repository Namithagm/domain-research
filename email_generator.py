import csv
import sys
import re
sys.path.insert(0, r'C:\Users\Namitha\Downloads\domain-research')

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# Common local parts (like FindMassLeads)
COMMON_LOCAL_PARTS = [
    # Business
    "info", "contact", "hello", "support", "sales", "help", "careers",
    "admin", "office", "business", "team", "inbox", "mail",
    
    # Professional
    "hr", "finance", "marketing", "pr", "media", "press", "editor",
    "enquiries", "partners", "affiliates", "customerservice",
    
    # Names
    "abigail", "admin", "alex", "alexander", "alexis", "alice", "allison",
    "amanda", "amber", "amy", "andrew", "angela", "anna", "anne",
    "anthony", "april", "ashley", "audrey", "austin", "barbara",
    "benjamin", "betty", "beverly", "brandon", "brian", "carol",
    "carolyn", "catherine", "charles", "cheryl", "christine",
    "christopher", "cindy", "daniel", "david", "debra", "dennis",
    "donald", "donna", "dorothy", "edward", "elizabeth", "emily",
    "eric", "evelyn", "frank", "george", "gerald", "gloria",
    "gregory", "harold", "helen", "henry", "jack", "jacob",
    "james", "janet", "janice", "jason", "jean", "jeffrey",
    "jennifer", "jessica", "john", "johnny", "jonathan", "jose",
    "joseph", "joshua", "joyce", "judith", "julia", "justin",
    "karen", "kathleen", "katherine", "kathryn", "kathy", "keith",
    "kenneth", "kevin", "kimberly", "larry", "laura", "linda",
    "lisa", "logan", "lori", "luke", "madison", "margaret",
    "maria", "marie", "martha", "martin", "mary", "matthew",
    "megan", "melissa", "michael", "michelle", "nancy", "natalie",
    "nathan", "nicole", "noah", "olivia", "owen", "pamela",
    "patricia", "patrick", "paul", "peter", "philip", "rae",
    "raymond", "rebecca", "richard", "robert", "roger", "ronald",
    "rose", "ruby", "russell", "ryan", "samuel", "sandra",
    "sarah", "sharon", "shirley", "stephanie", "steven", "susan",
    "teresa", "terry", "thomas", "timothy", "todd", "trevor",
    "tyler", "victoria", "vincent", "virginia", "walter", "wayne",
    "wendy", "william", "willie", "zachary",
    
    # Common variants
    "lead", "leads", "new", "main", "director", "ceo", "founder",
    "owner", "manager", "head", "general", "info", "inquiry",
    "queries", "questions", "billing", "accounts", "order", "orders",
    "returns", "refund", "claims", "warranty", "repairs", "service",
    "legal", "compliance", "security", "privacy", "abuse", "dmca",
    "cfo", "cto", "coo", "cio", "cmo", "cpo", "cso", "svp", "vp"
]

# Sample related domains for popular domains (like FindMassLeads)
SAMPLE_RELATED = {
    'square-enix.com': ['square-enix-games.com', 'squareenix.com', 'square-enix.co.uk', 'square-enix.net'],
    'google.com': ['google.co.uk', 'google.ca', 'google.com.au', 'google.fr', 'google.de'],
    'microsoft.com': ['microsoft.co.uk', 'microsoft.ca', 'microsoft.net', 'microsoft.org'],
    'amazon.com': ['amazon.co.uk', 'amazon.ca', 'amazon.de', 'amazon.fr', 'amazon.in'],
    'apple.com': ['apple.co.uk', 'apple.ca', 'apple.com.au', 'apple.de'],
    'facebook.com': ['facebook.co.uk', 'facebook.ca', 'facebook.net'],
    'twitter.com': ['twitter.co.uk', 'twitter.ca', 'twitter.com.au'],
    'linkedin.com': ['linkedin.co.uk', 'linkedin.ca', 'linkedin.com.au'],
    'youtube.com': ['youtube.co.uk', 'youtube.ca', 'youtube.com.au'],
    'instagram.com': ['instagram.co.uk', 'instagram.ca', 'instagram.com.au'],
    'github.com': ['github.io', 'github.co.uk', 'githubusercontent.com'],
    'stackoverflow.com': ['stackoverflow.co.uk', 'stackexchange.com'],
    'reddit.com': ['reddit.co.uk', 'reddit.ca', 'reddit.com.au'],
    'netflix.com': ['netflix.co.uk', 'netflix.ca', 'netflix.com.au'],
    'spotify.com': ['spotify.co.uk', 'spotify.ca', 'spotify.com.au'],
    'adobe.com': ['adobe.co.uk', 'adobe.ca', 'adobe.com.au'],
    'salesforce.com': ['salesforce.co.uk', 'salesforce.ca', 'salesforce.com.au'],
    'oracle.com': ['oracle.co.uk', 'oracle.ca', 'oracle.com.au'],
    'ibm.com': ['ibm.co.uk', 'ibm.ca', 'ibm.com.au'],
    'cisco.com': ['cisco.co.uk', 'cisco.ca', 'cisco.com.au'],
    'intel.com': ['intel.co.uk', 'intel.ca', 'intel.com.au'],
    'nvidia.com': ['nvidia.co.uk', 'nvidia.ca', 'nvidia.com.au'],
    'amd.com': ['amd.co.uk', 'amd.ca', 'amd.com.au'],
    'dell.com': ['dell.co.uk', 'dell.ca', 'dell.com.au'],
    'hp.com': ['hp.co.uk', 'hp.ca', 'hp.com.au'],
    'paypal.com': ['paypal.co.uk', 'paypal.ca', 'paypal.com.au'],
    'stripe.com': ['stripe.co.uk', 'stripe.ca', 'stripe.com.au'],
    'shopify.com': ['shopify.co.uk', 'shopify.ca', 'shopify.com.au'],
    'wordpress.com': ['wordpress.org', 'wordpress.co.uk', 'wordpress.ca'],
    'wix.com': ['wix.co.uk', 'wix.ca', 'wix.com.au'],
    'squarespace.com': ['squarespace.co.uk', 'squarespace.ca', 'squarespace.com.au'],
    'godaddy.com': ['godaddy.co.uk', 'godaddy.ca', 'godaddy.com.au'],
    'namecheap.com': ['namecheap.co.uk', 'namecheap.ca', 'namecheap.com.au'],
    'bluehost.com': ['bluehost.co.uk', 'bluehost.ca', 'bluehost.com.au'],
    'hostgator.com': ['hostgator.co.uk', 'hostgator.ca', 'hostgator.com.au'],
    'siteground.com': ['siteground.co.uk', 'siteground.ca', 'siteground.com.au'],
}

def extract_keywords(domain):
    """Extract keywords from domain name"""
    # Remove TLD (.com, .org, etc.)
    name = re.sub(r'\.[a-z]+$', '', domain)
    # Split by dots and hyphens
    parts = re.split(r'[\.\-]', name)
    return parts

def find_related_domains_from_db(domain, limit=20):
    """Find domains related to the given domain from database"""
    keywords = extract_keywords(domain)
    
    related = []
    for keyword in keywords:
        if len(keyword) > 2:  # Skip short words
            try:
                result = supabase.table('domains').select('domain_name, score').like('domain_name', f'%{keyword}%').order('score', desc=True).limit(limit).execute()
                related.extend(result.data)
            except:
                pass
    
    # Remove duplicates and self
    seen = set()
    unique = []
    for r in related:
        if r['domain_name'] != domain and r['domain_name'] not in seen:
            seen.add(r['domain_name'])
            unique.append(r)
    
    return unique[:limit]

def get_related_domains_from_sample(domain, limit=5):
    """Get related domains from sample data"""
    # Check exact match
    if domain in SAMPLE_RELATED:
        return SAMPLE_RELATED[domain][:limit]
    
    # Check partial match
    for key, related in SAMPLE_RELATED.items():
        if key in domain or domain in key:
            return related[:limit]
    
    # Try TLD variations
    base = domain.replace('.com', '').replace('.org', '').replace('.net', '').replace('.co.uk', '')
    tld_variations = ['.com', '.co.uk', '.org', '.net', '.io', '.gov', '.edu']
    related = []
    for tld in tld_variations:
        variant = base + tld
        if variant != domain:
            related.append(variant)
    
    return related[:limit]

def find_related_domains(domain, limit=10):
    """Find domains related to the given domain (combines sample + database)"""
    related_domains = []
    
    # 1. Try sample data first
    sample_related = get_related_domains_from_sample(domain, limit)
    related_domains.extend(sample_related)
    
    # 2. Try database if more needed
    if len(related_domains) < limit:
        db_related = find_related_domains_from_db(domain, limit - len(related_domains))
        for r in db_related:
            if r['domain_name'] not in related_domains:
                related_domains.append(r['domain_name'])
    
    return related_domains[:limit]

def generate_emails(domain, local_parts=None):
    """Generate emails for a domain using common local parts"""
    if local_parts is None:
        local_parts = COMMON_LOCAL_PARTS
    return [f"{part}@{domain}" for part in local_parts]

def generate_emails_for_domains(domains, local_parts=None):
    """Generate emails for multiple domains"""
    if local_parts is None:
        local_parts = COMMON_LOCAL_PARTS
    all_emails = []
    for domain in domains:
        emails = generate_emails(domain, local_parts)
        all_emails.extend(emails)
    return all_emails

def get_emails_with_related(domain, local_parts=None):
    """Get emails for domain + related domains (FindMassLeads style)"""
    if local_parts is None:
        local_parts = COMMON_LOCAL_PARTS
    
    all_results = []
    
    # 1. Emails for exact domain (top 10 local parts, show 5)
    exact_emails = generate_emails(domain, local_parts[:10])
    for email in exact_emails[:5]:
        all_results.append((domain, email))
    
    # 2. Find related domains
    related_domains = find_related_domains(domain, limit=5)
    
    # 3. Generate emails for related domains (top 3 each)
    for related_domain in related_domains:
        if related_domain != domain:
            emails = generate_emails(related_domain, local_parts[:10])
            for email in emails[:3]:
                all_results.append((related_domain, email))
    
    return all_results

def export_emails_to_csv(emails, filename="generated_emails.csv"):
    """Export emails to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Email'])
        for email in emails:
            writer.writerow([email])
    print(f"✅ Exported {len(emails)} emails to {filename}")

def export_emails_with_domains(domains, emails, filename="domains_with_emails.csv"):
    """Export domains with their generated emails"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Domain', 'Generated_Emails'])
        for i, domain in enumerate(domains):
            if i < len(emails):
                writer.writerow([domain, emails[i]])
    print(f"✅ Exported to {filename}")

if __name__ == "__main__":
    # Example: Get high-score domains from database
    result = supabase.table('domains').select('domain_name').gte('score', 70).limit(100).execute()
    domains = [r['domain_name'] for r in result.data]
    
    print(f"📊 Found {len(domains)} high-score domains")
    print("🔄 Generating emails...")
    
    # Generate emails for each domain
    all_emails = []
    for domain in domains:
        emails = generate_emails(domain)
        all_emails.extend(emails)
        if len(all_emails) % 100 == 0:
            print(f"  Generated {len(all_emails)} emails...")
    
    # Export to CSV
    export_emails_to_csv(all_emails, "generated_emails.csv")
    print(f"📊 Total emails generated: {len(all_emails)}")