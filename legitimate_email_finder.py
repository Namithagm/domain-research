import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# Common legitimate TLDs
VALID_TLDS = ['.com', '.org', '.net', '.eu', '.nl', '.de', '.fr', '.uk', '.co.uk', '.io', '.gov', '.edu', '.ca', '.au', '.in', '.co.jp', '.jp']

def get_emails_from_url(url, retries=2):
    """Extract emails from a single URL with retry logic"""
    for attempt in range(retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=8)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Email regex
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, response.text)
            
            # Mailto links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0].strip()
                    if email and '@' in email:
                        emails.append(email)
            
            # Remove duplicates
            emails = list(set(emails))
            valid_emails = [e for e in emails if len(e) < 100 and len(e) > 3 and '@' in e]
            
            return valid_emails
            
        except requests.Timeout:
            if attempt < retries - 1:
                print(f"    ⏳ Timeout, retry {attempt+2} for {url}")
                time.sleep(1)
            else:
                return []
        except Exception as e:
            if attempt < retries - 1:
                print(f"    ⏳ Error, retry {attempt+2} for {url}")
                time.sleep(1)
            else:
                return []
    
    return []

def get_emails_with_selenium(url):
    """Extract emails from JavaScript-heavy websites using Selenium (optimized)"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print(f"  🌐 Using Selenium for: {url}")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--page-load-strategy=eager')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        driver.set_page_load_timeout(10)
        driver.get(url)
        
        time.sleep(2)
        
        html = driver.page_source
        driver.quit()
        
        # Extract emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, html)
        
        # Also look for mailto links
        mailto_pattern = r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        mailto_emails = re.findall(mailto_pattern, html)
        emails.extend(mailto_emails)
        
        return list(set(emails))
    except Exception as e:
        print(f"  ⚠️ Selenium error: {e}")
        return []

def search_emails_on_site(domain, max_pages=10, use_selenium=False):
    """Search site for emails with timeout limits"""
    all_emails = []
    visited = set()
    
    # Priority pages
    priority_paths = [
        f"https://{domain}",
        f"https://{domain}/contact",
        f"https://{domain}/contact-us",
        f"https://{domain}/about",
        f"https://{domain}/about-us",
        f"https://{domain}/team",
        f"https://{domain}/support",
        f"https://{domain}/help",
        f"https://{domain}/company",
        f"https://{domain}/press",
        f"https://{domain}/impressum",
        f"https://{domain}/imprint",
        f"https://{domain}/legal",
        f"https://{domain}/privacy",
        f"https://{domain}/careers",
        f"https://{domain}/contact.html",
        f"https://{domain}/about.html",
    ]
    
    to_visit = priority_paths
    count = 0
    
    while to_visit and count < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        
        print(f"  🔍 Checking: {url}")
        visited.add(url)
        count += 1
        
        # Use Selenium if requested, otherwise use requests
        if use_selenium:
            emails = get_emails_with_selenium(url)
        else:
            emails = get_emails_from_url(url, retries=2)
        
        if emails:
            print(f"    ✅ Found {len(emails)} emails")
            all_emails.extend(emails)
        
        # Try to find more links but limit
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            link_count = 0
            for a in soup.find_all('a', href=True):
                if link_count > 5:
                    break
                href = a['href']
                if href.startswith('/') and not href.startswith('/#'):
                    full_url = urljoin(url, href)
                    if domain in full_url and full_url not in visited and full_url not in to_visit:
                        to_visit.append(full_url)
                        link_count += 1
        except:
            pass
        
        time.sleep(0.2)
    
    # Remove duplicates
    all_emails = list(set(all_emails))
    return all_emails

def discover_emails_for_domain(domain):
    """Main function to find legitimate emails with TLD fallback and Selenium support"""
    print(f"\n🔍 Searching for emails on: {domain}")
    print("-" * 40)
    
    # Step 1: Try with regular requests (faster)
    print("  📡 Trying with Requests...")
    emails = search_emails_on_site(domain, max_pages=12, use_selenium=False)
    
    # Step 2: If no emails, try .co.jp fallback for .jp domains
    if not emails and domain.endswith('.jp') and not domain.endswith('.co.jp'):
        alternative = domain.replace('.jp', '.co.jp')
        print(f"  ⏳ No emails on {domain}, trying {alternative} with Requests...")
        emails = search_emails_on_site(alternative, max_pages=12, use_selenium=False)
    
    # Step 3: If still no emails and domain is .jp or .co.jp, try Selenium
    if not emails and (domain.endswith('.jp') or domain.endswith('.co.jp')):
        print(f"  ⏳ No emails found with Requests, trying Selenium for Japanese domain...")
        emails = search_emails_on_site(domain, max_pages=10, use_selenium=True)
        
        # Also try .co.jp with Selenium if domain is .jp
        if not emails and domain.endswith('.jp') and not domain.endswith('.co.jp'):
            alternative = domain.replace('.jp', '.co.jp')
            print(f"  ⏳ Trying {alternative} with Selenium...")
            emails = search_emails_on_site(alternative, max_pages=10, use_selenium=True)
    
    # Filter: Keep domain emails AND legitimate related domain emails
    filtered_emails = []
    for e in emails:
        # Keep if domain is in email (e.g., info@zonnet.nl)
        if domain in e:
            filtered_emails.append(e)
        # Also keep if email has a legitimate TLD and looks valid
        elif any(e.endswith(tld) for tld in VALID_TLDS):
            # Don't keep obviously fake or disposable emails
            if not any(bad in e.lower() for bad in ['test', 'demo', 'example', 'fake', 'temp', 'spam', 'noreply']):
                filtered_emails.append(e)
    
    # Remove duplicates
    filtered_emails = list(set(filtered_emails))
    
    results = {
        'domain': domain,
        'emails': filtered_emails,
        'sources': [f"https://{domain} and crawled pages"]
    }
    
    return results

if __name__ == "__main__":
    domain = input("Enter domain to search: ").strip()
    results = discover_emails_for_domain(domain)
    
    print(f"\n📊 Results for: {domain}")
    print(f"Found {len(results['emails'])} emails")
    for email in results['emails']:
        print(f"  {email}")
    print(f"\nSources: {results['sources']}")