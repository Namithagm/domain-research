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
        
        # Debug: Show how many domains were found
        st.write(f"🔍 Found {len(rows)} domains matching your criteria")

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

        # Display dataframe with color coding (if matplotlib available)
        try:
            st.dataframe(
                df.style.background_gradient(subset=["score"], cmap="RdYlGn"),
                use_container_width=True
            )
        except Exception as e:
            # Fallback if matplotlib not installed
            st.dataframe(df, use_container_width=True)
            st.info("💡 Install matplotlib for color-coded scores: `pip install matplotlib`")

        # Download CSV
        st.download_button(
            label="📥 Download CSV",
            data=df.to_csv(index=False),
            file_name=f"domains_{date.today()}_{batch_id}.csv",
            mime="text/csv"
        )

        # Show detailed stats
        with st.expander("📊 Score Distribution"):
            if len(df) > 0:
                score_dist = df["score"].value_counts().sort_index()
                st.bar_chart(score_dist)
            else:
                st.info("No data to display")

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