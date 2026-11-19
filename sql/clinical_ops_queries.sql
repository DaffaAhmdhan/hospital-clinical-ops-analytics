-- ============================================================================
-- Hospital Clinical Operations & BPJS E-Klaim SLA Queries (SQLite)
-- ============================================================================

-- 1. Executive Clinical Summary (Outpatient 60-Min Ministry SLA & E-Klaim)
SELECT
    COUNT(*) AS total_visits,
    ROUND(AVG(wait_time_mins), 2) AS avg_wait_mins,
    ROUND(100.0 * SUM(CASE WHEN wait_time_mins <= 60 THEN 1 ELSE 0 END) / COUNT(*), 2) AS sla_60m_pct,
    ROUND(AVG(patient_csat), 2) AS avg_csat,
    SUM(claim_amount_idr) AS total_claim_idr
FROM patient_visits;

-- 2. Department Wait Time vs. 60-Min SLA Standard
SELECT
    department,
    COUNT(*) AS visits,
    ROUND(AVG(wait_time_mins), 2) AS avg_wait_mins,
    ROUND(100.0 * SUM(CASE WHEN wait_time_mins <= 60 THEN 1 ELSE 0 END) / COUNT(*), 2) AS sla_60m_pct,
    ROUND(AVG(patient_csat), 2) AS avg_csat
FROM patient_visits
GROUP BY department
ORDER BY avg_wait_mins DESC;

-- 3. BPJS Fingerprint Biometric vs. Manual Counter Registration Speed
SELECT
    check_in_method,
    COUNT(*) AS visits,
    ROUND(AVG(wait_time_mins), 2) AS avg_wait_mins,
    ROUND(100.0 * SUM(CASE WHEN wait_time_mins <= 60 THEN 1 ELSE 0 END) / COUNT(*), 2) AS sla_60m_pct,
    ROUND(AVG(patient_csat), 2) AS avg_csat
FROM patient_visits
GROUP BY check_in_method;

-- 4. BPJS Kesehatan INA-CBG E-Klaim Turnaround & Revenue at Risk
SELECT
    claim_status,
    COUNT(*) AS claim_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM patient_visits WHERE payer_type = 'BPJS Kesehatan'), 2) AS pct_of_bpjs,
    ROUND(AVG(claim_submission_days), 2) AS avg_turnaround_days,
    SUM(claim_amount_idr) AS claim_value_idr
FROM patient_visits
WHERE payer_type = 'BPJS Kesehatan'
GROUP BY claim_status
ORDER BY claim_count DESC;

-- 5. Hourly Arrival Wave (06:00 - 17:00)
SELECT
    arrival_hour,
    COUNT(*) AS total_visits,
    ROUND(AVG(wait_time_mins), 2) AS avg_wait_mins
FROM patient_visits
GROUP BY arrival_hour
ORDER BY arrival_hour;
