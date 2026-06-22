import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import whois
from datetime import datetime

def get_emails_from_url(url):
    """Extract emails from a single URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, response.text)
        return list(set(emails))
    except Exception as e:
        return []

def find_impressum(domain):
    """Find impressum/legal pages (common in Europe)"""
    paths = [
        '/impressum', '/legal', '/imprint', '/about/legal',
        '/page/impressum', '/de/impressum', '/en/impressum'
    ]
    for path in paths:
        url = f"https://{domain}{path}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return url
        except:
            pass
    return None

def search_google_for_emails(domain):
    """Search Google for emails (using free API or scraping)"""
    try:
        # Using DuckDuckGo as free alternative
        import urllib.parse
        query = f'site:{domain} "@{domain}"'
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, response.text)
        return list(set([e for e in emails if domain in e]))
    except:
        return []

def get_whois_email(domain):
    """Get email from WHOIS registration"""
    try:
        w = whois.whois(domain)
        emails = []
        if w.emails:
            if isinstance(w.emails, list):
                emails.extend(w.emails)
            else:
                emails.append(w.emails)
        return list(set(emails))
    except:
        return []

def crawl_website(domain, max_pages=30):
    """Crawl website for emails"""
    all_emails = []
    visited = set()
    to_visit = [f"https://{domain}"]
    
    priority_paths = [
        '/contact', '/about', '/team', '/support', '/help',
        '/company', '/press', '/media', '/community',
        '/careers', '/jobs', '/legal', '/privacy', '/terms'
    ]
    
    for path in priority_paths:
        to_visit.append(f"https://{domain}{path}")
    
    count = 0
    while to_visit and count < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        
        visited.add(url)
        count += 1
        
        emails = get_emails_from_url(url)
        if emails:
            all_emails.extend(emails)
        
        # Find more links
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/'):
                    full_url = urljoin(url, href)
                    if domain in full_url and full_url not in visited:
                        to_visit.append(full_url)
        except:
            pass
        
        time.sleep(0.3)
    
    return list(set(all_emails))

def discover_emails_for_domain(domain):
    """Main function - finds ALL possible emails"""
    print(f"\n🔍 Advanced Email Discovery for: {domain}")
    print("=" * 50)
    
    all_emails = []
    sources = []
    
    # 1. Crawl website
    print("1️⃣ Crawling website...")
    web_emails = crawl_website(domain, max_pages=30)
    if web_emails:
        all_emails.extend(web_emails)
        sources.append("Website crawl")
        print(f"   ✅ Found {len(web_emails)} emails")
    
    # 2. Check impressum/legal
    print("2️⃣ Checking impressum/legal pages...")
    impressum_url = find_impressum(domain)
    if impressum_url:
        impressum_emails = get_emails_from_url(impressum_url)
        if impressum_emails:
            all_emails.extend(impressum_emails)
            sources.append("Impressum/Legal page")
            print(f"   ✅ Found {len(impressum_emails)} emails")
    
    # 3. Search engine
    print("3️⃣ Searching search engines...")
    search_emails = search_google_for_emails(domain)
    if search_emails:
        all_emails.extend(search_emails)
        sources.append("Search engine")
        print(f"   ✅ Found {len(search_emails)} emails")
    
    # 4. WHOIS
    print("4️⃣ Checking WHOIS registration...")
    whois_emails = get_whois_email(domain)
    if whois_emails:
        all_emails.extend(whois_emails)
        sources.append("WHOIS registration")
        print(f"   ✅ Found {len(whois_emails)} emails")
    
    # Remove duplicates
    all_emails = list(set(all_emails))
    
    # Filter only domain-specific emails
    domain_emails = [e for e in all_emails if domain in e or '.de' in e]
    
    return {
        'domain': domain,
        'emails': domain_emails,
        'all_emails': all_emails,
        'sources': sources
    }

if __name__ == "__main__":
    domain = input("Enter domain to search: ").strip()
    results = discover_emails_for_domain(domain)
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS for: {domain}")
    print("=" * 50)
    print(f"Sources checked: {', '.join(results['sources'])}")
    print(f"\n✅ Found {len(results['emails'])} domain-specific emails:")
    for email in results['emails']:
        print(f"  {email}")
    
    if results['all_emails'] and len(results['all_emails']) > len(results['emails']):
        print(f"\n📌 Found {len(results['all_emails'])} total emails (including non-domain)")