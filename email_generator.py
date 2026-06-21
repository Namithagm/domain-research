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
    
    # 1. Emails for exact domain (top 5 local parts)
    exact_emails = generate_emails(domain, local_parts[:10])
    for email in exact_emails[:5]:
        all_results.append((domain, email))
    
    # 2. Emails for related domains (top 3 domains, top 3 emails each)
    related = find_related_domains(domain, limit=10)
    for r in related[:3]:  # Top 3 related
        emails = generate_emails(r['domain_name'], local_parts[:10])
        for email in emails[:3]:  # Top 3 emails each
            all_results.append((r['domain_name'], email))
    
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