from db.database import get_fresh_domains, mark_as_served
import uuid

# Get 5 fresh domains
domains = get_fresh_domains(5, 70, 30, 7)
print(f'Found {len(domains)} domains')

if domains:
    # Extract domain names
    domain_names = [d['domain_name'] for d in domains]
    print(f'Domains: {domain_names}')
    
    # Generate batch ID
    batch_id = str(uuid.uuid4())[:8]
    
    # Mark as served
    mark_as_served(domain_names, batch_id)
    print(f'✅ Marked {len(domains)} domains as served with batch {batch_id}')
else:
    print('No domains found')