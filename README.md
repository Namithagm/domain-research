# Domain Research Tool 🔍

A fully automated domain reputation research tool that collects, analyzes, and scores domains from public sources.

## Features

- ✅ Collects domains from Majestic Million and Tranco List
- ✅ Checks DNS records: MX, SPF, DMARC
- ✅ Checks blacklists: SURBL, URIBL
- ✅ Checks reputation: Spamhaus, Talos, Barracuda, VirusTotal, AbuseIPDB, URLVoid
- ✅ Scores domains 0-100 with custom algorithm
- ✅ No repeats: 30-day cooldown
- ✅ Daily automatic scraping at 6AM
- ✅ Streamlit dashboard with CSV export
- ✅ Deployable for free on Hugging Face Spaces

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt