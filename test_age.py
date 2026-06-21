from scraper.scorer import get_domain_age

domains = ['asp.net', 'loc.gov', 'ubc.ca', 'pastebin.com', 'google.com', 'stripe.com']
print("Domain Age Check:")
print("-" * 40)
for d in domains:
    age = get_domain_age(d)
    print(f"{d:20} {age} years")