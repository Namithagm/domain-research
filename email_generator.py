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
    # Names (A-Z)
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
    # Original domains
    '.com', '.org', '.net', '.io', '.gov', '.edu',
    # European
    '.uk', '.co.uk', '.de', '.fr', '.es', '.it', '.nl', '.se', '.no', '.dk', '.fi',
    '.pl', '.cz', '.hu', '.ro', '.bg', '.gr', '.pt', '.at', '.ch', '.be',
    # Asia Pacific
    '.in', '.co.in', '.sg', '.com.sg', '.my', '.com.my', '.ph', '.vn', '.th', '.id',
    '.com.au', '.au', '.nz', '.co.nz',
    # Americas
    '.br', '.com.br', '.ar', '.com.ar', '.mx', '.com.mx', '.cl', '.co', '.pe',
    '.ve', '.uy', '.py', '.ca',
    # Middle East
    '.tr', '.com.tr', '.il', '.co.il', '.sa', '.com.sa', '.ae', '.eg',
    # Others
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
        'google.no', 'google.pt', 'google.gr', 'google.sk', 'google.bg',
        'google.hr', 'google.si', 'google.lt', 'google.lv', 'google.ee',
        'google.com.ph', 'google.com.my', 'google.co.id', 'google.com.bd',
        'google.com.pk', 'google.com.ng', 'google.com.pe', 'google.com.ve',
        'google.com.co', 'google.cl', 'google.com.uy', 'google.com.py'
    ],
    'microsoft.com': [
        'microsoft.co.uk', 'microsoft.ca', 'microsoft.com.au', 'microsoft.fr',
        'microsoft.de', 'microsoft.es', 'microsoft.it', 'microsoft.nl',
        'microsoft.se', 'microsoft.pl', 'microsoft.cz', 'microsoft.hu',
        'microsoft.ro', 'microsoft.br', 'microsoft.ar', 'microsoft.com.mx',
        'microsoft.cl', 'microsoft.co.in', 'microsoft.com.sg', 'microsoft.eu',
        'microsoft.ch', 'microsoft.at', 'microsoft.be', 'microsoft.dk',
        'microsoft.fi', 'microsoft.no', 'microsoft.pt', 'microsoft.gr',
        'microsoft.ru', 'microsoft.ua', 'microsoft.tr', 'microsoft.co.il',
        'microsoft.ae', 'microsoft.co.za', 'microsoft.com.ph', 'microsoft.com.my',
        'microsoft.co.id', 'microsoft.com.bd', 'microsoft.com.pk', 'microsoft.com.ng'
    ],
    'amazon.com': [
        'amazon.co.uk', 'amazon.ca', 'amazon.com.au', 'amazon.fr', 'amazon.de',
        'amazon.es', 'amazon.it', 'amazon.nl', 'amazon.se', 'amazon.pl',
        'amazon.cz', 'amazon.hu', 'amazon.ro', 'amazon.br', 'amazon.ar',
        'amazon.com.mx', 'amazon.cl', 'amazon.co.in', 'amazon.com.sg',
        'amazon.ae', 'amazon.eu', 'amazon.ch', 'amazon.at', 'amazon.be',
        'amazon.dk', 'amazon.fi', 'amazon.no', 'amazon.pt', 'amazon.gr',
        'amazon.com.tr', 'amazon.co.il', 'amazon.co.za', 'amazon.com.ph',
        'amazon.com.my', 'amazon.co.id', 'amazon.com.bd'
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
        'facebook.com.tr', 'facebook.co.il', 'facebook.com.ph',
        'facebook.com.my', 'facebook.co.id'
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
    'whatsapp.com': [
        'whatsapp.co.uk', 'whatsapp.ca', 'whatsapp.fr', 'whatsapp.de',
        'whatsapp.es', 'whatsapp.it', 'whatsapp.nl', 'whatsapp.pl',
        'whatsapp.br', 'whatsapp.ar', 'whatsapp.com.mx', 'whatsapp.co.in',
        'whatsapp.com.sg', 'whatsapp.eu', 'whatsapp.ch', 'whatsapp.at'
    ],
    'netflix.com': [
        'netflix.co.uk', 'netflix.ca', 'netflix.fr', 'netflix.de',
        'netflix.es', 'netflix.it', 'netflix.nl', 'netflix.pl',
        'netflix.br', 'netflix.ar', 'netflix.com.mx', 'netflix.co.in',
        'netflix.com.sg', 'netflix.eu', 'netflix.ch', 'netflix.at'
    ],
    'spotify.com': [
        'spotify.co.uk', 'spotify.ca', 'spotify.fr', 'spotify.de',
        'spotify.es', 'spotify.it', 'spotify.nl', 'spotify.pl',
        'spotify.br', 'spotify.ar', 'spotify.com.mx', 'spotify.co.in',
        'spotify.com.sg', 'spotify.eu', 'spotify.ch', 'spotify.at'
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
    'square.com': [
        'square.co.uk', 'square.ca', 'square.fr', 'square.de',
        'square.es', 'square.it', 'square.nl', 'square.pl',
        'square.br', 'square.ar', 'square.com.mx', 'square.co.in',
        'square.com.sg', 'square.eu'
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
    'hostgator.com': [
        'hostgator.co.uk', 'hostgator.ca', 'hostgator.fr', 'hostgator.de',
        'hostgator.es', 'hostgator.it', 'hostgator.nl', 'hostgator.pl',
        'hostgator.br', 'hostgator.ar', 'hostgator.com.mx', 'hostgator.co.in',
        'hostgator.com.sg', 'hostgator.eu'
    ],
    'siteground.com': [
        'siteground.co.uk', 'siteground.ca', 'siteground.fr', 'siteground.de',
        'siteground.es', 'siteground.it', 'siteground.nl', 'siteground.pl',
        'siteground.br', 'siteground.ar', 'siteground.com.mx', 'siteground.co.in',
        'siteground.com.sg', 'siteground.eu'
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
    'reuters.com': [
        'reuters.co.uk', 'reuters.ca', 'reuters.fr', 'reuters.de',
        'reuters.es', 'reuters.it', 'reuters.nl', 'reuters.pl',
        'reuters.br', 'reuters.ar', 'reuters.com.mx', 'reuters.co.in',
        'reuters.com.sg', 'reuters.eu'
    ],
    'bloomberg.com': [
        'bloomberg.co.uk', 'bloomberg.ca', 'bloomberg.fr', 'bloomberg.de',
        'bloomberg.es', 'bloomberg.it', 'bloomberg.nl', 'bloomberg.pl',
        'bloomberg.br', 'bloomberg.ar', 'bloomberg.com.mx', 'bloomberg.co.in',
        'bloomberg.com.sg', 'bloomberg.eu'
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
    'alibaba.com': [
        'alibaba.co.uk', 'alibaba.ca', 'alibaba.fr', 'alibaba.de',
        'alibaba.es', 'alibaba.it', 'alibaba.nl', 'alibaba.pl',
        'alibaba.br', 'alibaba.ar', 'alibaba.com.mx', 'alibaba.co.in',
        'alibaba.com.sg', 'alibaba.eu'
    ],
    'aliexpress.com': [
        'aliexpress.co.uk', 'aliexpress.ca', 'aliexpress.fr', 'aliexpress.de',
        'aliexpress.es', 'aliexpress.it', 'aliexpress.nl', 'aliexpress.pl',
        'aliexpress.br', 'aliexpress.ar', 'aliexpress.com.mx', 'aliexpress.co.in',
        'aliexpress.com.sg', 'aliexpress.eu'
    ],
    # ====== Education ======
    'harvard.edu': [
        'harvard.com', 'harvard.org', 'harvard.co.uk', 'harvard.ca',
        'harvard.fr', 'harvard.de', 'harvard.es', 'harvard.it',
        'harvard.nl', 'harvard.pl', 'harvard.br', 'harvard.ar',
        'harvard.com.mx', 'harvard.co.in', 'harvard.com.sg', 'harvard.eu'
    ],
    'stanford.edu': [
        'stanford.com', 'stanford.org', 'stanford.co.uk', 'stanford.ca',
        'stanford.fr', 'stanford.de', 'stanford.es', 'stanford.it',
        'stanford.nl', 'stanford.pl', 'stanford.br', 'stanford.ar',
        'stanford.com.mx', 'stanford.co.in', 'stanford.com.sg', 'stanford.eu'
    ],
    'mit.edu': [
        'mit.com', 'mit.org', 'mit.co.uk', 'mit.ca',
        'mit.fr', 'mit.de', 'mit.es', 'mit.it',
        'mit.nl', 'mit.pl', 'mit.br', 'mit.ar',
        'mit.com.mx', 'mit.co.in', 'mit.com.sg', 'mit.eu'
    ],
    'oxford.ac.uk': [
        'oxford.com', 'oxford.org', 'oxford.co.uk', 'oxford.ca',
        'oxford.fr', 'oxford.de', 'oxford.es', 'oxford.it',
        'oxford.nl', 'oxford.pl', 'oxford.br', 'oxford.ar',
        'oxford.com.mx', 'oxford.co.in', 'oxford.com.sg', 'oxford.eu'
    ],
    'cambridge.org': [
        'cambridge.com', 'cambridge.co.uk', 'cambridge.ca',
        'cambridge.fr', 'cambridge.de', 'cambridge.es', 'cambridge.it',
        'cambridge.nl', 'cambridge.pl', 'cambridge.br', 'cambridge.ar',
        'cambridge.com.mx', 'cambridge.co.in', 'cambridge.com.sg', 'cambridge.eu'
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
    'tumblr.com': [
        'tumblr.co.uk', 'tumblr.ca', 'tumblr.fr', 'tumblr.de',
        'tumblr.es', 'tumblr.it', 'tumblr.nl', 'tumblr.pl',
        'tumblr.br', 'tumblr.ar', 'tumblr.com.mx', 'tumblr.co.in',
        'tumblr.com.sg', 'tumblr.eu'
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
    'coca-cola.com': [
        'coca-cola.co.uk', 'coca-cola.ca', 'coca-cola.fr', 'coca-cola.de',
        'coca-cola.es', 'coca-cola.it', 'coca-cola.nl', 'coca-cola.pl',
        'coca-cola.br', 'coca-cola.ar', 'coca-cola.com.mx', 'coca-cola.co.in',
        'coca-cola.com.sg', 'coca-cola.eu'
    ],
    'pepsi.com': [
        'pepsi.co.uk', 'pepsi.ca', 'pepsi.fr', 'pepsi.de',
        'pepsi.es', 'pepsi.it', 'pepsi.nl', 'pepsi.pl',
        'pepsi.br', 'pepsi.ar', 'pepsi.com.mx', 'pepsi.co.in',
        'pepsi.com.sg', 'pepsi.eu'
    ],
    'mcdonalds.com': [
        'mcdonalds.co.uk', 'mcdonalds.ca', 'mcdonalds.fr', 'mcdonalds.de',
        'mcdonalds.es', 'mcdonalds.it', 'mcdonalds.nl', 'mcdonalds.pl',
        'mcdonalds.br', 'mcdonalds.ar', 'mcdonalds.com.mx', 'mcdonalds.co.in',
        'mcdonalds.com.sg', 'mcdonalds.eu'
    ],
    'starbucks.com': [
        'starbucks.co.uk', 'starbucks.ca', 'starbucks.fr', 'starbucks.de',
        'starbucks.es', 'starbucks.it', 'starbucks.nl', 'starbucks.pl',
        'starbucks.br', 'starbucks.ar', 'starbucks.com.mx', 'starbucks.co.in',
        'starbucks.com.sg', 'starbucks.eu'
    ],
    # ====== Automobile ======
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
        'bmw.com.sg', 'bm