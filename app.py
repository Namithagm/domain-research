import streamlit as st
import pandas as pd
import uuid
from datetime import date
from db.database import get_fresh_domains, mark_as_served, get_stats
from scheduler import launch_background_scheduler

# Auto-launch background scraper
launch_background_scheduler()

st.set_page_config(
    page_title="Domain Research Tool",
    page_icon="🔍",
    layout="wide"
)

# ====== Header ======
st.title("🔍 Domain Research Tool")
st.caption(f"Auto-scrapes daily at 6AM | Today: {date.today()}")

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
cooldown = col3.slider("Cooldown Days (no repeats)", 1, 90, 30)

st.divider()

# ====== Get Domains Button ======
if st.button("🚀 Get Fresh Domains", type="primary", use_container_width=True):
    with st.spinner("Fetching fresh domains..."):
        rows = get_fresh_domains(domain_count, min_score, cooldown)

    if not rows:
        st.warning("No fresh domains available. Scraper may still be running. Try again in a few minutes.")
    else:
        df = pd.DataFrame(rows)
        batch_id = str(uuid.uuid4())[:8]
        mark_as_served(df["domain_name"].tolist(), batch_id)

        st.success(f"✅ {len(df)} fresh domains fetched — Batch ID: {batch_id}")

        # Color code scores
        st.dataframe(
            df.style.background_gradient(subset=["score"], cmap="RdYlGn"),
            use_container_width=True
        )

        # Download CSV
        st.download_button(
            label="📥 Download CSV",
            data=df.to_csv(index=False),
            file_name=f"domains_{date.today()}_{batch_id}.csv",
            mime="text/csv"
        )

        # Show detailed stats
        with st.expander("📊 Score Distribution"):
            score_dist = df["score"].value_counts().sort_index()
            st.bar_chart(score_dist)

st.divider()

# ====== Info Section ======
with st.expander("ℹ️ How It Works"):
    st.markdown("""
    **Input Sources:**
    - Majestic Million → 1M popular domains
    - Tranco List → Research-grade domain ranking
    - DNS Checks → MX, SPF, DMARC records
    - Spamhaus → Domain reputation
    - Talos Intelligence → Cisco reputation
    - Barracuda Central → Email reputation
    - VirusTotal → 70+ security vendors
    - AbuseIPDB → Abuse reports
    - URLVoid → Multi-engine checks
    
    **Scoring:**
    - DMARC: none=60, quarantine/missing=50
    - Spamhaus: clean=40, unknown=25
    - Talos: good=30, unknown=10
    - Barracuda: good=20, unknown=10
    - VirusTotal: clean=25, unknown=10
    - URLVoid: clean=15, unknown=5
    
    **Minimum pass: 70/100**
    
    **No repeats:** 30-day cooldown per domain
    """)

with st.expander("🛠️ Third Party Sources Used"):
    st.markdown("""
    | Source | Type | API Key | Limit |
    |--------|------|---------|-------|
    | Majestic Million | CSV Download | No | Unlimited |
    | Tranco List | ZIP Download | No | Unlimited |
    | Spamhaus DBL | DNS + HTTP | No | Unlimited |
    | SURBL | DNS Query | No | Unlimited |
    | URIBL | DNS Query | No | Unlimited |
    | Talos Intelligence | HTTP Lookup | No | Unlimited |
    | Barracuda Central | HTTP Lookup | No | Unlimited |
    | VirusTotal | HTTP API | Yes (free) | 500/day |
    | AbuseIPDB | HTTP API | Yes (free) | 1000/day |
    | URLVoid | HTTP Scrape | No | Unlimited |
    """)