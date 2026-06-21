-- Run this in Supabase SQL Editor

-- ====== Main Domains Table ======
CREATE TABLE domains (
    id SERIAL PRIMARY KEY,
    domain_name TEXT UNIQUE NOT NULL,
    score INTEGER DEFAULT 0,
    dmarc_policy TEXT,
    has_mx BOOLEAN DEFAULT FALSE,
    has_spf BOOLEAN DEFAULT FALSE,
    is_blacklisted BOOLEAN DEFAULT FALSE,
    surbl_listed BOOLEAN,
    uribl_listed BOOLEAN,
    spamhaus_clean BOOLEAN,
    spamhaus_class TEXT,
    talos_score TEXT,
    talos_category TEXT,
    talos_clean BOOLEAN,
    barracuda_clean BOOLEAN,
    barracuda_status TEXT,
    vt_clean BOOLEAN,
    vt_malicious_count INTEGER,
    vt_total_scans INTEGER,
    abuse_score INTEGER,
    abuse_clean BOOLEAN,
    abuse_reports INTEGER,
    urlvoid_clean BOOLEAN,
    last_checked DATE,
    last_served DATE,
    times_served INTEGER DEFAULT 0,
    date_added DATE DEFAULT CURRENT_DATE
);

-- ====== Served Log Table ======
CREATE TABLE served_log (
    id SERIAL PRIMARY KEY,
    domain_name TEXT,
    served_date DATE,
    batch_id TEXT
);

-- ====== Scrape Log Table ======
CREATE TABLE scrape_log (
    id SERIAL PRIMARY KEY,
    scrape_date DATE,
    domains_fetched INTEGER,
    domains_stored INTEGER,
    status TEXT
);

-- ====== Function to Get Fresh Domains ======
CREATE OR REPLACE FUNCTION get_fresh_domains(
    min_score INT DEFAULT 70,
    domain_count INT DEFAULT 50,
    cooldown_days INT DEFAULT 30
)
RETURNS TABLE(
    domain_name TEXT,
    score INTEGER,
    dmarc_policy TEXT,
    has_mx BOOLEAN,
    has_spf BOOLEAN,
    spamhaus_clean BOOLEAN,
    spamhaus_class TEXT,
    talos_score TEXT,
    barracuda_status TEXT,
    vt_clean BOOLEAN,
    abuse_score INTEGER,
    urlvoid_clean BOOLEAN,
    last_checked DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.domain_name, d.score, d.dmarc_policy,
        d.has_mx, d.has_spf, d.spamhaus_clean,
        d.spamhaus_class, d.talos_score,
        d.barracuda_status, d.vt_clean,
        d.abuse_score, d.urlvoid_clean,
        d.last_checked
    FROM domains d
    WHERE
        d.score >= min_score
        AND d.dmarc_policy != 'reject'
        AND d.is_blacklisted = FALSE
        AND d.spamhaus_clean != FALSE
        AND (d.talos_clean IS NULL OR d.talos_clean = TRUE)
        AND (d.barracuda_clean IS NULL OR d.barracuda_clean = TRUE)
        AND (d.vt_clean IS NULL OR d.vt_clean = TRUE)
        AND (d.abuse_clean IS NULL OR d.abuse_clean = TRUE)
        AND (d.urlvoid_clean IS NULL OR d.urlvoid_clean = TRUE)
        AND (
            d.last_served IS NULL
            OR d.last_served < CURRENT_DATE - (cooldown_days || ' days')::INTERVAL
        )
    ORDER BY d.score DESC, d.last_served ASC NULLS FIRST
    LIMIT domain_count;
END;
$$ LANGUAGE plpgsql;