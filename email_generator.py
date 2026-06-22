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
    "hr", "finance", "marketing", "pr", "media", "press", "editor",
    "enquiries", "partners", "affiliates", "customerservice",
    # Names
    "aaron", "abby", "abigail", "adam", "adrian", "aiden", "alan", "albert",
    "alex", "alexander", "alexis", "alice", "allison", "amanda", "amber",
    "amy", "andrew", "angela", "anna", "anne", "anthony", "april", "ashley",
    "audrey", "austin", "barbara", "benjamin", "betty", "beverly", "brandon",
    "brian", "carol", "carolyn", "catherine", "charles", "cheryl", "christine",
    "christopher", "cindy", "daniel", "david", "debra", "dennis", "donald",
    "donna", "dorothy", "edward", "elizabeth", "emily", "eric", "evelyn",
    "frank", "george", "gerald", "gloria", "gregory", "harold", "helen",
    "henry", "jack", "jacob", "james", "janet", "janice", "jason", "jean",
    "jeffrey", "jennifer", "jessica", "john", "johnny", "jonathan", "jose",
    "joseph", "joshua", "joyce", "judith", "julia", "justin", "karen",
    "kathleen", "katherine", "kathryn", "kathy", "keith", "kenneth", "kevin",
    "kimberly", "larry", "laura", "linda", "lisa", "logan", "lori", "luke",
    "madison", "margaret", "maria", "marie", "martha", "martin", "mary",
    "matthew", "megan", "melissa", "michael", "michelle", "nancy", "natalie",
    "nathan", "nicole", "noah", "olivia", "owen", "pamela", "patricia",
    "patrick", "paul", "peter", "philip", "rae", "raymond", "rebecca",
    "richard", "robert", "roger", "ronald", "rose", "ruby", "russell",
    "ryan", "samuel", "sandra", "sarah", "sharon", "shirley", "stephanie",
    "steven", "susan", "teresa", "terry", "thomas", "timothy", "todd",
    "trevor", "tyler", "victoria", "vincent", "virginia", "walter", "wayne",
    "wendy", "william", "willie", "zachary",
    # Common variants
    "lead", "leads", "new", "main", "director", "ceo", "founder",
    "owner", "manager", "head", "general", "inquiry", "queries",
    "questions", "billing", "accounts", "order", "orders",
    "returns", "refund", "claims", "warranty", "repairs", "service",
    "legal", "compliance", "security", "privacy", "abuse", "dmca",
    "cfo", "cto", "coo", "cio", "cmo", "cpo", "cso", "svp", "vp"
]

# All TLDs to generate variations
TLD_LIST = [
    '.com', '.org', '.net', '.io', '.gov', '.edu',
    '.uk', '.co.uk', '.de', '.fr', '.es', '.it', '.nl', '.se', '.no', '.dk', '.fi',
    '.pl', '.cz', '.hu', '.ro', '.bg', '.gr', '.pt', '.at', '.ch', '.be',
    '.in', '.co.in', '.sg', '.com.sg', '.my', '.com.my', '.ph', '.vn', '.th', '.id',
    '.com.au', '.au', '.nz', '.co.nz',
    '.br', '.com.br', '.ar', '.com.ar', '.mx', '.com.mx', '.cl', '.co', '.pe',
    '.ve', '.uy', '.py', '.ca',
    '.tr', '.com.tr', '.il', '.co.il', '.sa', '.com.sa', '.ae', '.eg',
    '.ru', '.ua', '.kz', '.za', '.co.za', '.eu', '.asia',
    '.info', '.biz', '.me', '.tv'
]

# ====== SAMPLE_RELATED - Full List ======
SAMPLE_RELATED = {
    # ====== Tech Giants ======
    'google.com': [
        'google.co.uk', 'google.ca', 'google.com.au', 'google.fr', 'google.de',
        'google.es', 'google.it', 'google.nl', 'google.se', 'google.pl',
        'google.cz', 'google.hu', 'google.ro', 'google.br', 'google.ar',
        'google.com.mx', 'google.cl', 'google.co.in', 'google.com.sg',
        'google.ru', 'google.ua', 'google.tr', 'google.co.il', 'google.ae',
        'google.co.za', 'google.eg', 'google.eu', 'google.info', 'google.biz',
        'google.ch', 'google.at', 'google.be', 'google.dk', 'google.fi',
        'google.no', 'google.pt', 'google.gr'
    ],
    'microsoft.com': [
        'microsoft.co.uk', 'microsoft.ca', 'microsoft.com.au', 'microsoft.fr',
        'microsoft.de', 'microsoft.es', 'microsoft.it', 'microsoft.nl',
        'microsoft.se', 'microsoft.pl', 'microsoft.cz', 'microsoft.hu',
        'microsoft.ro', 'microsoft.br', 'microsoft.ar', 'microsoft.com.mx',
        'microsoft.cl', 'microsoft.co.in', 'microsoft.com.sg', 'microsoft.eu',
        'microsoft.ch', 'microsoft.at', 'microsoft.be', 'microsoft.dk',
        'microsoft.fi', 'microsoft.no', 'microsoft.pt', 'microsoft.gr',
        'microsoft.ru', 'microsoft.ua', 'microsoft.tr', 'microsoft.co.il'
    ],
    'amazon.com': [
        'amazon.co.uk', 'amazon.ca', 'amazon.com.au', 'amazon.fr', 'amazon.de',
        'amazon.es', 'amazon.it', 'amazon.nl', 'amazon.se', 'amazon.pl',
        'amazon.cz', 'amazon.hu', 'amazon.ro', 'amazon.br', 'amazon.ar',
        'amazon.com.mx', 'amazon.cl', 'amazon.co.in', 'amazon.com.sg',
        'amazon.ae', 'amazon.eu', 'amazon.ch', 'amazon.at', 'amazon.be',
        'amazon.dk', 'amazon.fi', 'amazon.no', 'amazon.pt', 'amazon.gr',
        'amazon.com.tr', 'amazon.co.il', 'amazon.co.za'
    ],
    'apple.com': [
        'apple.co.uk', 'apple.ca', 'apple.com.au', 'apple.fr', 'apple.de',
        'apple.es', 'apple.it', 'apple.nl', 'apple.se', 'apple.pl',
        'apple.cz', 'apple.hu', 'apple.ro', 'apple.br', 'apple.ar',
        'apple.com.mx', 'apple.cl', 'apple.co.in', 'apple.com.sg',
        'apple.eu', 'apple.ch', 'apple.at', 'apple.be', 'apple.dk',
        'apple.fi', 'apple.no', 'apple.pt', 'apple.gr', 'apple.ae',
        'apple.co.za', 'apple.com.tr', 'apple.co.il'
    ],
    'facebook.com': [
        'facebook.co.uk', 'facebook.ca', 'facebook.fr', 'facebook.de',
        'facebook.es', 'facebook.it', 'facebook.nl', 'facebook.pl',
        'facebook.cz', 'facebook.hu', 'facebook.ro', 'facebook.br',
        'facebook.ar', 'facebook.com.mx', 'facebook.cl', 'facebook.co.in',
        'facebook.com.sg', 'facebook.eu', 'facebook.ch', 'facebook.at',
        'facebook.be', 'facebook.dk', 'facebook.fi', 'facebook.no',
        'facebook.pt', 'facebook.gr', 'facebook.ae', 'facebook.co.za',
        'facebook.com.tr', 'facebook.co.il'
    ],
    'twitter.com': [
        'twitter.co.uk', 'twitter.ca', 'twitter.fr', 'twitter.de',
        'twitter.es', 'twitter.it', 'twitter.nl', 'twitter.pl',
        'twitter.cz', 'twitter.hu', 'twitter.ro', 'twitter.br',
        'twitter.ar', 'twitter.com.mx', 'twitter.cl', 'twitter.co.in',
        'twitter.com.sg', 'twitter.eu', 'twitter.ch', 'twitter.at',
        'twitter.be', 'twitter.dk', 'twitter.fi', 'twitter.no',
        'twitter.pt', 'twitter.gr', 'twitter.ae', 'twitter.co.za',
        'twitter.com.tr', 'twitter.co.il'
    ],
    'linkedin.com': [
        'linkedin.co.uk', 'linkedin.ca', 'linkedin.fr', 'linkedin.de',
        'linkedin.es', 'linkedin.it', 'linkedin.nl', 'linkedin.pl',
        'linkedin.cz', 'linkedin.hu', 'linkedin.ro', 'linkedin.br',
        'linkedin.ar', 'linkedin.com.mx', 'linkedin.cl', 'linkedin.co.in',
        'linkedin.com.sg', 'linkedin.eu', 'linkedin.ch', 'linkedin.at',
        'linkedin.be', 'linkedin.dk', 'linkedin.fi', 'linkedin.no',
        'linkedin.pt', 'linkedin.gr', 'linkedin.ae', 'linkedin.co.za',
        'linkedin.com.tr', 'linkedin.co.il'
    ],
    'instagram.com': [
        'instagram.co.uk', 'instagram.ca', 'instagram.fr', 'instagram.de',
        'instagram.es', 'instagram.it', 'instagram.nl', 'instagram.pl',
        'instagram.cz', 'instagram.hu', 'instagram.ro', 'instagram.br',
        'instagram.ar', 'instagram.com.mx', 'instagram.cl', 'instagram.co.in',
        'instagram.com.sg', 'instagram.eu', 'instagram.ch', 'instagram.at',
        'instagram.be', 'instagram.dk', 'instagram.fi', 'instagram.no',
        'instagram.pt', 'instagram.gr', 'instagram.ae', 'instagram.co.za',
        'instagram.com.tr', 'instagram.co.il'
    ],
    'youtube.com': [
        'youtube.co.uk', 'youtube.ca', 'youtube.fr', 'youtube.de',
        'youtube.es', 'youtube.it', 'youtube.nl', 'youtube.pl',
        'youtube.cz', 'youtube.hu', 'youtube.ro', 'youtube.br',
        'youtube.ar', 'youtube.com.mx', 'youtube.cl', 'youtube.co.in',
        'youtube.com.sg', 'youtube.eu', 'youtube.ch', 'youtube.at',
        'youtube.be', 'youtube.dk', 'youtube.fi', 'youtube.no',
        'youtube.pt', 'youtube.gr', 'youtube.ae', 'youtube.co.za',
        'youtube.com.tr', 'youtube.co.il'
    ],
    # ====== Tech Companies ======
    'adobe.com': [
        'adobe.co.uk', 'adobe.ca', 'adobe.fr', 'adobe.de',
        'adobe.es', 'adobe.it', 'adobe.nl', 'adobe.pl',
        'adobe.br', 'adobe.ar', 'adobe.com.mx', 'adobe.co.in',
        'adobe.com.sg', 'adobe.eu'
    ],
    'salesforce.com': [
        'salesforce.co.uk', 'salesforce.ca', 'salesforce.fr', 'salesforce.de',
        'salesforce.es', 'salesforce.it', 'salesforce.nl', 'salesforce.pl',
        'salesforce.br', 'salesforce.ar', 'salesforce.com.mx', 'salesforce.co.in',
        'salesforce.com.sg', 'salesforce.eu'
    ],
    'oracle.com': [
        'oracle.co.uk', 'oracle.ca', 'oracle.fr', 'oracle.de',
        'oracle.es', 'oracle.it', 'oracle.nl', 'oracle.pl',
        'oracle.br', 'oracle.ar', 'oracle.com.mx', 'oracle.co.in',
        'oracle.com.sg', 'oracle.eu'
    ],
    'ibm.com': [
        'ibm.co.uk', 'ibm.ca', 'ibm.fr', 'ibm.de',
        'ibm.es', 'ibm.it', 'ibm.nl', 'ibm.pl',
        'ibm.br', 'ibm.ar', 'ibm.com.mx', 'ibm.co.in',
        'ibm.com.sg', 'ibm.eu'
    ],
    'cisco.com': [
        'cisco.co.uk', 'cisco.ca', 'cisco.fr', 'cisco.de',
        'cisco.es', 'cisco.it', 'cisco.nl', 'cisco.pl',
        'cisco.br', 'cisco.ar', 'cisco.com.mx', 'cisco.co.in',
        'cisco.com.sg', 'cisco.eu'
    ],
    'intel.com': [
        'intel.co.uk', 'intel.ca', 'intel.fr', 'intel.de',
        'intel.es', 'intel.it', 'intel.nl', 'intel.pl',
        'intel.br', 'intel.ar', 'intel.com.mx', 'intel.co.in',
        'intel.com.sg', 'intel.eu'
    ],
    'nvidia.com': [
        'nvidia.co.uk', 'nvidia.ca', 'nvidia.fr', 'nvidia.de',
        'nvidia.es', 'nvidia.it', 'nvidia.nl', 'nvidia.pl',
        'nvidia.br', 'nvidia.ar', 'nvidia.com.mx', 'nvidia.co.in',
        'nvidia.com.sg', 'nvidia.eu'
    ],
    'amd.com': [
        'amd.co.uk', 'amd.ca', 'amd.fr', 'amd.de',
        'amd.es', 'amd.it', 'amd.nl', 'amd.pl',
        'amd.br', 'amd.ar', 'amd.com.mx', 'amd.co.in',
        'amd.com.sg', 'amd.eu'
    ],
    'dell.com': [
        'dell.co.uk', 'dell.ca', 'dell.fr', 'dell.de',
        'dell.es', 'dell.it', 'dell.nl', 'dell.pl',
        'dell.br', 'dell.ar', 'dell.com.mx', 'dell.co.in',
        'dell.com.sg', 'dell.eu'
    ],
    'hp.com': [
        'hp.co.uk', 'hp.ca', 'hp.fr', 'hp.de',
        'hp.es', 'hp.it', 'hp.nl', 'hp.pl',
        'hp.br', 'hp.ar', 'hp.com.mx', 'hp.co.in',
        'hp.com.sg', 'hp.eu'
    ],
    # ====== Financial Services ======
    'paypal.com': [
        'paypal.co.uk', 'paypal.ca', 'paypal.fr', 'paypal.de',
        'paypal.es', 'paypal.it', 'paypal.nl', 'paypal.pl',
        'paypal.br', 'paypal.ar', 'paypal.com.mx', 'paypal.co.in',
        'paypal.com.sg', 'paypal.eu'
    ],
    'stripe.com': [
        'stripe.co.uk', 'stripe.ca', 'stripe.fr', 'stripe.de',
        'stripe.es', 'stripe.it', 'stripe.nl', 'stripe.pl',
        'stripe.br', 'stripe.ar', 'stripe.com.mx', 'stripe.co.in',
        'stripe.com.sg', 'stripe.eu'
    ],
    'shopify.com': [
        'shopify.co.uk', 'shopify.ca', 'shopify.fr', 'shopify.de',
        'shopify.es', 'shopify.it', 'shopify.nl', 'shopify.pl',
        'shopify.br', 'shopify.ar', 'shopify.com.mx', 'shopify.co.in',
        'shopify.com.sg', 'shopify.eu'
    ],
    # ====== Hosting & Domains ======
    'wordpress.com': [
        'wordpress.org', 'wordpress.co.uk', 'wordpress.ca', 'wordpress.fr',
        'wordpress.de', 'wordpress.es', 'wordpress.it', 'wordpress.nl',
        'wordpress.pl', 'wordpress.br', 'wordpress.ar', 'wordpress.com.mx',
        'wordpress.co.in', 'wordpress.com.sg', 'wordpress.eu'
    ],
    'wix.com': [
        'wix.co.uk', 'wix.ca', 'wix.fr', 'wix.de',
        'wix.es', 'wix.it', 'wix.nl', 'wix.pl',
        'wix.br', 'wix.ar', 'wix.com.mx', 'wix.co.in',
        'wix.com.sg', 'wix.eu'
    ],
    'squarespace.com': [
        'squarespace.co.uk', 'squarespace.ca', 'squarespace.fr', 'squarespace.de',
        'squarespace.es', 'squarespace.it', 'squarespace.nl', 'squarespace.pl',
        'squarespace.br', 'squarespace.ar', 'squarespace.com.mx', 'squarespace.co.in',
        'squarespace.com.sg', 'squarespace.eu'
    ],
    'godaddy.com': [
        'godaddy.co.uk', 'godaddy.ca', 'godaddy.fr', 'godaddy.de',
        'godaddy.es', 'godaddy.it', 'godaddy.nl', 'godaddy.pl',
        'godaddy.br', 'godaddy.ar', 'godaddy.com.mx', 'godaddy.co.in',
        'godaddy.com.sg', 'godaddy.eu'
    ],
    'namecheap.com': [
        'namecheap.co.uk', 'namecheap.ca', 'namecheap.fr', 'namecheap.de',
        'namecheap.es', 'namecheap.it', 'namecheap.nl', 'namecheap.pl',
        'namecheap.br', 'namecheap.ar', 'namecheap.com.mx', 'namecheap.co.in',
        'namecheap.com.sg', 'namecheap.eu'
    ],
    'bluehost.com': [
        'bluehost.co.uk', 'bluehost.ca', 'bluehost.fr', 'bluehost.de',
        'bluehost.es', 'bluehost.it', 'bluehost.nl', 'bluehost.pl',
        'bluehost.br', 'bluehost.ar', 'bluehost.com.mx', 'bluehost.co.in',
        'bluehost.com.sg', 'bluehost.eu'
    ],
    # ====== News & Media ======
    'cnn.com': [
        'cnn.co.uk', 'cnn.ca', 'cnn.fr', 'cnn.de',
        'cnn.es', 'cnn.it', 'cnn.nl', 'cnn.pl',
        'cnn.br', 'cnn.ar', 'cnn.com.mx', 'cnn.co.in',
        'cnn.com.sg', 'cnn.eu'
    ],
    'bbc.com': [
        'bbc.co.uk', 'bbc.ca', 'bbc.fr', 'bbc.de',
        'bbc.es', 'bbc.it', 'bbc.nl', 'bbc.pl',
        'bbc.br', 'bbc.ar', 'bbc.com.mx', 'bbc.co.in',
        'bbc.com.sg', 'bbc.eu'
    ],
    'nytimes.com': [
        'nytimes.co.uk', 'nytimes.ca', 'nytimes.fr', 'nytimes.de',
        'nytimes.es', 'nytimes.it', 'nytimes.nl', 'nytimes.pl',
        'nytimes.br', 'nytimes.ar', 'nytimes.com.mx', 'nytimes.co.in',
        'nytimes.com.sg', 'nytimes.eu'
    ],
    # ====== E-commerce ======
    'ebay.com': [
        'ebay.co.uk', 'ebay.ca', 'ebay.fr', 'ebay.de',
        'ebay.es', 'ebay.it', 'ebay.nl', 'ebay.pl',
        'ebay.br', 'ebay.ar', 'ebay.com.mx', 'ebay.co.in',
        'ebay.com.sg', 'ebay.eu'
    ],
    'etsy.com': [
        'etsy.co.uk', 'etsy.ca', 'etsy.fr', 'etsy.de',
        'etsy.es', 'etsy.it', 'etsy.nl', 'etsy.pl',
        'etsy.br', 'etsy.ar', 'etsy.com.mx', 'etsy.co.in',
        'etsy.com.sg', 'etsy.eu'
    ],
    # ====== Social Media ======
    'tiktok.com': [
        'tiktok.co.uk', 'tiktok.ca', 'tiktok.fr', 'tiktok.de',
        'tiktok.es', 'tiktok.it', 'tiktok.nl', 'tiktok.pl',
        'tiktok.br', 'tiktok.ar', 'tiktok.com.mx', 'tiktok.co.in',
        'tiktok.com.sg', 'tiktok.eu'
    ],
    'snapchat.com': [
        'snapchat.co.uk', 'snapchat.ca', 'snapchat.fr', 'snapchat.de',
        'snapchat.es', 'snapchat.it', 'snapchat.nl', 'snapchat.pl',
        'snapchat.br', 'snapchat.ar', 'snapchat.com.mx', 'snapchat.co.in',
        'snapchat.com.sg', 'snapchat.eu'
    ],
    'pinterest.com': [
        'pinterest.co.uk', 'pinterest.ca', 'pinterest.fr', 'pinterest.de',
        'pinterest.es', 'pinterest.it', 'pinterest.nl', 'pinterest.pl',
        'pinterest.br', 'pinterest.ar', 'pinterest.com.mx', 'pinterest.co.in',
        'pinterest.com.sg', 'pinterest.eu'
    ],
    'reddit.com': [
        'reddit.co.uk', 'reddit.ca', 'reddit.fr', 'reddit.de',
        'reddit.es', 'reddit.it', 'reddit.nl', 'reddit.pl',
        'reddit.br', 'reddit.ar', 'reddit.com.mx', 'reddit.co.in',
        'reddit.com.sg', 'reddit.eu'
    ],
    # ====== Major Brands ======
    'nike.com': [
        'nike.co.uk', 'nike.ca', 'nike.fr', 'nike.de',
        'nike.es', 'nike.it', 'nike.nl', 'nike.pl',
        'nike.br', 'nike.ar', 'nike.com.mx', 'nike.co.in',
        'nike.com.sg', 'nike.eu'
    ],
    'adidas.com': [
        'adidas.co.uk', 'adidas.ca', 'adidas.fr', 'adidas.de',
        'adidas.es', 'adidas.it', 'adidas.nl', 'adidas.pl',
        'adidas.br', 'adidas.ar', 'adidas.com.mx', 'adidas.co.in',
        'adidas.com.sg', 'adidas.eu'
    ],
    'starbucks.com': [
        'starbucks.co.uk', 'starbucks.ca', 'starbucks.fr', 'starbucks.de',
        'starbucks.es', 'starbucks.it', 'starbucks.nl', 'starbucks.pl',
        'starbucks.br', 'starbucks.ar', 'starbucks.com.mx', 'starbucks.co.in',
        'starbucks.com.sg', 'starbucks.eu'
    ],
    'tesla.com': [
        'tesla.co.uk', 'tesla.ca', 'tesla.fr', 'tesla.de',
        'tesla.es', 'tesla.it', 'tesla.nl', 'tesla.pl',
        'tesla.br', 'tesla.ar', 'tesla.com.mx', 'tesla.co.in',
        'tesla.com.sg', 'tesla.eu'
    ],
    'toyota.com': [
        'toyota.co.uk', 'toyota.ca', 'toyota.fr', 'toyota.de',
        'toyota.es', 'toyota.it', 'toyota.nl', 'toyota.pl',
        'toyota.br', 'toyota.ar', 'toyota.com.mx', 'toyota.co.in',
        'toyota.com.sg', 'toyota.eu'
    ],
    'ford.com': [
        'ford.co.uk', 'ford.ca', 'ford.fr', 'ford.de',
        'ford.es', 'ford.it', 'ford.nl', 'ford.pl',
        'ford.br', 'ford.ar', 'ford.com.mx', 'ford.co.in',
        'ford.com.sg', 'ford.eu'
    ],
    'bmw.com': [
        'bmw.co.uk', 'bmw.ca', 'bmw.fr', 'bmw.de',
        'bmw.es', 'bmw.it', 'bmw.nl', 'bmw.pl',
        'bmw.br', 'bmw.ar', 'bmw.com.mx', 'bmw.co.in',
        'bmw.com.sg', 'bmw.eu'
    ]
}

def extract_keywords(domain):
    """Extract keywords from domain name"""
    name = re.sub(r'\.[a-z]+$', '', domain)
    parts = re.split(r'[\.\-]', name)
    return parts

def find_related_domains_from_db(domain, limit=20):
    """Find domains related to the given domain from database"""
    keywords = extract_keywords(domain)
    related = []
    for keyword in keywords:
        if len(keyword) > 2:
            try:
                result = supabase.table('domains').select('domain_name, score').like('domain_name', f'%{keyword}%').order('score', desc=True).limit(limit).execute()
                related.extend(result.data)
            except:
                pass
    seen = set()
    unique = []
    for r in related:
        if r['domain_name'] != domain and r['domain_name'] not in seen:
            seen.add(r['domain_name'])
            unique.append(r)
    return unique[:limit]

def get_related_domains_from_sample(domain, limit=15):
    """Get related domains from sample data with all TLDs"""
    for key, related in SAMPLE_RELATED.items():
        if key in domain or domain in key:
            return related[:limit]
    base = domain.replace('.com', '').replace('.org', '').replace('.net', '')
    base = base.replace('.co.uk', '').replace('.gov.uk', '').replace('.edu', '')
    base = base.replace('.pl.com', '').replace('.pl.co.uk', '')
    related = []
    for tld in TLD_LIST:
        variant = base + tld
        if variant != domain and variant not in related:
            related.append(variant)
    return related[:limit]

def find_related_domains(domain, limit=10):
    """Find domains related to the given domain"""
    related_domains = []
    sample_related = get_related_domains_from_sample(domain, limit)
    related_domains.extend(sample_related)
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
    
    # 1. Emails for exact domain
    exact_emails = generate_emails(domain, local_parts[:10])
    for email in exact_emails[:5]:
        all_results.append((domain, email))
    
    # 2. Find related domains
    related_domains = find_related_domains(domain, limit=10)
    
    # 3. Generate emails for related domains
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

if __name__ == "__main__":
    result = supabase.table('domains').select('domain_name').gte('score', 70).limit(100).execute()
    domains = [r['domain_name'] for r in result.data]
    
    print(f"📊 Found {len(domains)} high-score domains")
    print("🔄 Generating emails...")
    
    all_emails = []
    for domain in domains:
        emails = generate_emails(domain)
        all_emails.extend(emails)
    
    export_emails_to_csv(all_emails, "generated_emails.csv")
    print(f"📊 Total emails generated: {len(all_emails)}")