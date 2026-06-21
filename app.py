import streamlit as st
import pandas as pd
import uuid
from datetime import date
from db.database import get_fresh_domains, mark_as_served, get_stats

# ====== For Cloud Deployment - Scheduler is DISABLED ======
# The scheduler runs on your local machine via Windows Task Scheduler
# Do NOT enable this on Streamlit Cloud
# from scheduler import launch_background_scheduler
# launch_background_scheduler()

st.set_page_config(
    page_title="Domain Research Tool",
    page_icon="🔍",
    layout="wide"
)

# ====== Header ======
st.title("🔍 Domain Research Tool")
st.caption(f"Auto-scrapes daily at 6AM (on local machine) | Today: {date.today()}")

# ====== Stats ======
stats = get_stats()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📊 Total Domains", stats["total"])
c2.metric("⭐ High Score (70+)", stats["high_score"])
c3.metric("✅ Available Now", stats["available"])
c4.metric("📤 Served Today", stats["served_today"])
c5.metric("🔄 Last Scrape", stats["last_scrape"])

st.divider()

# ====== Filters ======
st.subheader("⚙️ Filters")
col1, col2, col3 = st.columns(3)
min_score = col1.slider("Minimum Score", 0, 100, 70)
domain_count = col2.slider("Domains to Fetch", 10, 100, 50)
cooldown = col3.slider("Cooldown Days (no repeats)", 0, 90, 1)

st.divider()

# ====== Get Domains Button ======
if st.button("🚀 Get Fresh Domains", type="primary", use_container_width=True):
    with st.spinner("Fetching fresh domains..."):
        rows = get_fresh_domains(domain_count, min_score, cooldown)

    if not rows:
        st.warning("""
        No fresh domains available. Try:
        - Lowering the Minimum Score
        - Reducing Cooldown Days to 0 or 1
        - Waiting for the daily scrape to run
        """)
    else:
        df = pd.DataFrame(rows)
        batch_id = str(uuid.uuid4())[:8]
        mark_as_served(df["domain_name"].tolist(), batch_id)

        st.success(f"✅ {len(df)} fresh domains fetched — Batch ID: {batch_id}")

        # Display dataframe with color coding
        try:
            st.dataframe(
                df.style.background_gradient(subset=["score"], cmap="RdYlGn"),
                use_container_width=True
            )
        except Exception as e:
            st.dataframe(df, use_container_width=True)

        # Download CSV
        st.download_button(
            label="📥 Download CSV",
            data=df.to_csv(index=False),
            file_name=f"domains_{date.today()}_{batch_id}.csv",
            mime="text/csv"
        )

        # Show detailed stats
        with st.expander("📊 Score Distribution"):
            if len(df) > 0 and "score" in df.columns:
                score_dist = df["score"].value_counts().sort_index()
                st.bar_chart(score_dist)

st.divider()

# ====== Email Generator Section ======
st.subheader("📧 Generate Emails from Domains")

st.markdown("""
Generate email addresses for your high-score domains using common local parts 
(info@, contact@, sales@, etc.) - similar to FindMassLeads!
""")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    email_domain_count = st.number_input("Number of Domains", 10, 500, 100, step=10)

with col2:
    email_min_score = st.slider("Min Score for Emails", 0, 100, 70, key="email_min_score")

with col3:
    email_cooldown = st.slider("Cooldown for Emails", 0, 90, 1, key="email_cooldown")

if st.button("📧 Generate Emails", type="secondary", use_container_width=True):
    with st.spinner("Generating emails from high-score domains..."):
        try:
            # Get high-score domains
            rows = get_fresh_domains(email_domain_count, email_min_score, email_cooldown)
            
            if not rows:
                st.warning("No domains found matching your criteria. Try lowering the minimum score.")
            else:
                domains = [r['domain_name'] for r in rows]
                
                # Import email generator
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from email_generator import generate_emails_for_domains, COMMON_LOCAL_PARTS
                
                # Generate emails
                emails = generate_emails_for_domains(domains)
                
                st.success(f"✅ Generated {len(emails)} emails from {len(domains)} domains")
                
                # Show stats
                st.info(f"📊 {len(domains)} domains × {len(COMMON_LOCAL_PARTS)} local parts = {len(emails)} total emails")
                
                # Show sample emails
                with st.expander("📧 Sample Emails (first 20)"):
                    sample_emails = emails[:20]
                    st.write("\n".join(sample_emails))
                
                # Create DataFrame for download
                df_emails = pd.DataFrame(emails, columns=['Email'])
                
                # Download button
                st.download_button(
                    label="📥 Download Emails CSV",
                    data=df_emails.to_csv(index=False),
                    file_name=f"emails_{date.today()}_{uuid.uuid4().hex[:8]}.csv",
                    mime="text/csv"
                )
                
                # Also show domains used
                with st.expander("📋 Domains Used"):
                    st.write("\n".join(domains[:20]))
                    if len(domains) > 20:
                        st.write(f"... and {len(domains) - 20} more")
                        
        except Exception as e:
            st.error(f"Error generating emails: {e}")
            st.info("Make sure email_generator.py exists in your project folder.")

st.divider()

# ====== FindMassLeads Style Email Finder ======
st.subheader("🔍 FindMassLeads Style - Email Finder")

st.markdown("""
Find emails for a domain AND related domains (like FindMassLeads!).
Enter a domain and we'll find emails for it and similar domains.
""")

search_domain = st.text_input("Enter a domain (e.g., ashford.gov.uk)", placeholder="domain.com")

if st.button("🔍 Find Emails with Related Domains", type="secondary"):
    if search_domain:
        with st.spinner(f"Searching for emails related to {search_domain}..."):
            try:
                from email_generator import get_emails_with_related, COMMON_LOCAL_PARTS
                
                results = get_emails_with_related(search_domain, COMMON_LOCAL_PARTS)
                
                if results:
                    st.success(f"✅ Found {len(results)} emails")
                    
                    # Group by domain
                    data = []
                    for domain, email in results:
                        data.append({'Domain': domain, 'Email': email})
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download CSV
                    st.download_button(
                        label="📥 Download Emails CSV",
                        data=df.to_csv(index=False),
                        file_name=f"emails_related_{search_domain}_{date.today()}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No emails found. Try another domain.")
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Make sure email_generator.py exists in your project folder.")
    else:
        st.warning("Please enter a domain.")

st.divider()

# ====== Combined Email Finder ======
st.subheader("🔍 Advanced Email Finder")

st.markdown("""
Find emails for your high-score domains AND related domains.
This combines both features in one click!
""")

if st.button("🚀 Find All Emails (Domains + Related)", type="primary"):
    with st.spinner("Finding emails from high-score domains and related domains..."):
        try:
            # 1. Get high-score domains
            rows = get_fresh_domains(50, 70, 1)
            
            if rows:
                domains = [r['domain_name'] for r in rows]
                all_results = []
                
                # 2. For each domain, find related emails
                from email_generator import get_emails_with_related, COMMON_LOCAL_PARTS
                
                for domain in domains[:10]:  # Limit to 10 domains for speed
                    results = get_emails_with_related(domain, COMMON_LOCAL_PARTS)
                    all_results.extend(results)
                
                # 3. Display results
                df = pd.DataFrame(all_results, columns=['Domain', 'Email'])
                st.success(f"✅ Found {len(df)} emails from {len(domains)} domains")
                st.dataframe(df, use_container_width=True)
                
                st.download_button(
                    label="📥 Download All Emails CSV",
                    data=df.to_csv(index=False),
                    file_name=f"all_emails_{date.today()}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No high-score domains found.")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# ====== Info Section ======
with st.expander("ℹ️ How It Works"):
    st.markdown("""
    **How Domains Are Collected:**
    1. **Local machine** scrapes domains daily at 6 AM
    2. Domains are saved to **Supabase** (cloud database)
    3. This dashboard reads from **Supabase** in real-time

    **Scoring System:**
    - **DMARC:** none=60, quarantine/missing=50, reject=0 (filtered out)
    - **Spamhaus:** clean=40, unknown=25, flagged=0
    - **Domain Age:** 10+ yrs=15, 5-10 yrs=10, 2-5 yrs=5, unknown=5
    - **Minimum pass:** 70/100

    **No Repeats:** Domains are marked as "served" and won't appear again for the cooldown period.

    **Email Generator Features:**
    - **Generate Emails from Domains:** Uses your high-score domains
    - **FindMassLeads Style:** Search any domain + related domains
    - **Advanced Email Finder:** Combines both features in one click
    - All features export to CSV
    """)

with st.expander("🛠️ Third Party Sources Used"):
    st.markdown("""
    | Source | What It Does | API Key |
    |--------|--------------|---------|
    | **Majestic Million** | Top 1M domains list | No |
    | **Tranco List** | Research-grade ranking | No |
    | **Spamhaus DBL** | Domain blacklist check | No |
    | **SURBL** | URI blacklist check | No |
    | **URIBL** | URI blacklist check | No |
    | **WHOIS** | Domain age verification | No |

    *All sources are free and publicly available.*
    """)