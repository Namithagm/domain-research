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

# ====== Check Your Own Domain ======
st.subheader("🔍 Check Your Own Domain")

st.markdown("""
Check the reputation of your own domains using the same powerful scoring system!
- **Single domain:** Enter one domain
- **Bulk upload:** Upload a CSV or TXT file with one domain per line
""")

tab1, tab2 = st.tabs(["📌 Single Domain", "📂 Bulk Upload"])

with tab1:
    own_domain = st.text_input("Enter a domain to check", placeholder="example.com")
    
    if st.button("🔍 Check Domain", type="primary"):
        if own_domain:
            with st.spinner(f"Checking {own_domain}..."):
                try:
                    from domain_checker import check_single_domain
                    result = check_single_domain(own_domain)
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        # Display results
                        st.success(f"✅ Check complete for {own_domain}")
                        
                        # Score with color
                        score = result.get('score', 0)
                        if score >= 70:
                            st.success(f"⭐ Score: {score}/100 - Good reputation")
                        elif score >= 50:
                            st.warning(f"⚠️ Score: {score}/100 - Average reputation")
                        else:
                            st.error(f"❌ Score: {score}/100 - Poor reputation")
                        
                        # Show details in table
                        details = {
                            "Domain": result.get('domain_name'),
                            "Score": result.get('score'),
                            "DMARC Policy": result.get('dmarc_policy'),
                            "Has MX": result.get('has_mx'),
                            "Has SPF": result.get('has_spf'),
                            "Spamhaus Clean": result.get('spamhaus_clean'),
                            "Domain Age": f"{result.get('domain_age_years', 'Unknown')} years" if result.get('domain_age_years') else "Unknown",
                            "Blacklisted": result.get('is_blacklisted'),
                            "Talos Score": result.get('talos_score'),
                            "Barracuda Status": result.get('barracuda_status'),
                            "VirusTotal Clean": result.get('vt_clean'),
                            "Abuse Score": result.get('abuse_score')
                        }
                        
                        df_details = pd.DataFrame([details])
                        st.dataframe(df_details.T, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a domain.")

with tab2:
    st.write("Upload a CSV or TXT file with one domain per line")
    
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'txt'])
    
    if uploaded_file is not None:
        # Read file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            domains = df.iloc[:, 0].tolist()
        else:
            domains = uploaded_file.read().decode('utf-8').splitlines()
        
        domains = [d.strip() for d in domains if d.strip()]
        st.info(f"📊 Found {len(domains)} domains")
        
        # Show first 10 domains
        with st.expander("📋 Preview Domains"):
            st.write(domains[:10])
            if len(domains) > 10:
                st.write(f"... and {len(domains) - 10} more")
        
        if st.button("🚀 Check All Domains", type="primary"):
            with st.spinner(f"Checking {len(domains)} domains..."):
                try:
                    from domain_checker import check_bulk_domains
                    results_df = check_bulk_domains(domains)
                    
                    st.success(f"✅ Checked {len(results_df)} domains")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Download button
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Report CSV",
                        data=csv,
                        file_name=f"domain_report_{date.today()}.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error: {e}")

st.divider()

# ====== Legitimate Email Finder ======
st.subheader("✅ Legitimate Email Finder")

st.markdown("""
**No guessing!** This feature finds REAL emails from the domain's website:
- Searches contact/about pages
- Extracts emails from public pages
- No random generation
- Only verified sources
""")

legit_domain = st.text_input("Enter a domain to find real emails", placeholder="example.com")

if st.button("🔍 Find Real Emails", type="primary"):
    if legit_domain:
        with st.spinner(f"Searching for real emails on {legit_domain}..."):
            try:
                from legitimate_email_finder import discover_emails_for_domain
                results = discover_emails_for_domain(legit_domain)
                
                if results['emails']:
                    st.success(f"✅ Found {len(results['emails'])} real emails")
                    
                    # Display emails
                    df = pd.DataFrame(results['emails'], columns=['Email'])
                    st.dataframe(df, use_container_width=True)
                    
                    # Show sources
                    with st.expander("📋 Sources"):
                        st.write(results['sources'])
                    
                    # Download
                    st.download_button(
                        label="📥 Download Real Emails CSV",
                        data=df.to_csv(index=False),
                        file_name=f"real_emails_{legit_domain}_{date.today()}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning(f"No emails found on {legit_domain}.")
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Make sure legitimate_email_finder.py exists in your project folder.")
    else:
        st.warning("Please enter a domain.")

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

    **Check Your Own Domain:**
    - Enter any domain or upload a list
    - Get full reputation report
    - Same scoring system as the research tool
    - Export results to CSV

    **Legitimate Email Finder:**
    - Finds REAL emails from websites (no guessing!)
    - Searches contact pages, about pages, and team pages
    - Only returns emails that are publicly available
    - Export results to CSV
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