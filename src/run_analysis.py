import csv
import json
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "patient_visits.csv")
DB_PATH = os.path.join(BASE_DIR, "output", "clinical_ops.db")
JSON_PATH = os.path.join(BASE_DIR, "output", "clinical_metrics.json")


def query_dicts(conn, sql):
    conn.row_factory = sqlite3.Row
    return [dict(r) for r in conn.execute(sql).fetchall()]


def main():
    os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS patient_visits;")
    cur.execute("""
        CREATE TABLE patient_visits (
            visit_id TEXT PRIMARY KEY,
            visit_date TEXT NOT NULL,
            arrival_hour INTEGER NOT NULL,
            department TEXT NOT NULL,
            payer_type TEXT NOT NULL,
            check_in_method TEXT NOT NULL,
            wait_time_mins REAL NOT NULL,
            consult_mins REAL NOT NULL,
            claim_submission_days REAL NOT NULL,
            claim_status TEXT NOT NULL,
            claim_amount_idr INTEGER NOT NULL,
            patient_csat INTEGER NOT NULL
        );
    """)

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = [
            (
                r["visit_id"], r["visit_date"], int(r["arrival_hour"]),
                r["department"], r["payer_type"], r["check_in_method"],
                float(r["wait_time_mins"]), float(r["consult_mins"]),
                float(r["claim_submission_days"]), r["claim_status"],
                int(r["claim_amount_idr"]), int(r["patient_csat"])
            )
            for r in csv.DictReader(f)
        ]

    cur.executemany("INSERT INTO patient_visits VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", rows)
    conn.commit()

    executive = query_dicts(conn, """
        SELECT
            COUNT(*) AS total_visits,
            ROUND(AVG(wait_time_mins), 2) AS avg_wait_mins,
            ROUND(100.0 * SUM(CASE WHEN wait_time_mins <= 60 THEN 1 ELSE 0 END) / COUNT(*), 2) AS sla_60m_pct,
            ROUND(AVG(patient_csat), 2) AS avg_csat,
            SUM(claim_amount_idr) AS total_claim_idr
        FROM patient_visits;
    """)[0]

    by_department = query_dicts(conn, """
        SELECT
            department,
            COUNT(*) AS visits,
            ROUND(AVG(wait_time_mins), 2) AS avg_wait_mins,
            ROUND(100.0 * SUM(CASE WHEN wait_time_mins <= 60 THEN 1 ELSE 0 END) / COUNT(*), 2) AS sla_60m_pct,
            ROUND(AVG(patient_csat), 2) AS avg_csat
        FROM patient_visits
        GROUP BY department
        ORDER BY avg_wait_mins DESC;
    """)

    by_checkin = query_dicts(conn, """
        SELECT
            check_in_method,
            COUNT(*) AS visits,
            ROUND(AVG(wait_time_mins), 2) AS avg_wait_mins,
            ROUND(100.0 * SUM(CASE WHEN wait_time_mins <= 60 THEN 1 ELSE 0 END) / COUNT(*), 2) AS sla_60m_pct,
            ROUND(AVG(patient_csat), 2) AS avg_csat
        FROM patient_visits
        GROUP BY check_in_method;
    """)

    bpjs_claims = query_dicts(conn, """
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
    """)

    hourly_wave = query_dicts(conn, """
        SELECT
            arrival_hour,
            COUNT(*) AS total_visits,
            ROUND(AVG(wait_time_mins), 2) AS avg_wait_mins
        FROM patient_visits
        GROUP BY arrival_hour
        ORDER BY arrival_hour;
    """)

    output = {
        "executive": executive,
        "by_department": by_department,
        "by_checkin": by_checkin,
        "bpjs_claims": bpjs_claims,
        "hourly_wave": hourly_wave,
    }

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    conn.close()
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
