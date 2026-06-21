import csv
import sys
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

def generate_emails(domain, local_parts=None):
    """Generate emails for a domain using common local parts"""
    if local_parts is None:
        local_parts = COMMON_LOCAL_PARTS
    return [f"{part}@{domain}" for part in local_parts]

def generate_emails_for_domains(domains, local_parts=None):
    """Generate emails for multiple domains"""
    all_emails = []
    for domain in domains:
        emails = generate_emails(domain, local_parts)
        all_emails.extend(emails)
    return all_emails

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