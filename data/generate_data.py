import csv
import os
import random
from datetime import datetime, timedelta

random.seed(202611)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(OUTPUT_DIR, "patient_visits.csv")

DEPARTMENTS = [
    ("Internal Medicine", 0.24, 58.0, 18.0, 950000),
    ("Cardiology", 0.16, 62.0, 22.0, 1650000),
    ("Orthopedics", 0.15, 49.0, 17.0, 1350000),
    ("Pediatrics", 0.17, 41.0, 15.0, 680000),
    ("Radiology / DICOM", 0.14, 34.0, 12.0, 1150000),
    ("Emergency / IGD", 0.14, 14.0, 24.0, 1850000),
]

HOURS = [
    (6, 0.04), (7, 0.12), (8, 0.18), (9, 0.17), (10, 0.13),
    (11, 0.09), (12, 0.06), (13, 0.07), (14, 0.06), (15, 0.04),
    (16, 0.02), (17, 0.02),
]

PAYERS = [("BPJS Kesehatan", 0.72), ("Private Insurance", 0.16), ("Self-Pay", 0.12)]


def weighted_pick(items):
    r = random.random()
    acc = 0.0
    for item in items:
        acc += item[1]
        if r <= acc:
            return item
    return items[-1]


def main():
    start = datetime(2026, 5, 1)
    rows = []

    for i in range(1, 8401):
        visit_date = start + timedelta(days=random.randint(0, 183))
        hour = weighted_pick(HOURS)[0]
        dept, _, base_wait, base_consult, base_claim = weighted_pick(DEPARTMENTS)
        payer = weighted_pick(PAYERS)[0]

        if payer == "BPJS Kesehatan" and dept != "Emergency / IGD":
            check_in = "BPJS Fingerprint Biometric" if random.random() < 0.62 else "Manual Counter"
        elif dept == "Emergency / IGD":
            check_in = "BPJS Fingerprint Biometric" if random.random() < 0.35 else "Manual Counter"
        else:
            check_in = "Manual Counter"

        # Wait time dynamics
        wait = base_wait
        if check_in == "Manual Counter":
            wait += random.uniform(14.0, 24.0)
        else:
            wait -= random.uniform(6.0, 12.0)

        if 7 <= hour <= 10 and dept != "Emergency / IGD":
            wait += random.uniform(12.0, 22.0)

        wait = round(max(4.0, wait + random.gauss(0, 8.5)), 1)
        consult = round(max(6.0, base_consult + random.gauss(0, 4.0)), 1)

        # Claim workflow (INA-CBG E-Klaim)
        claim_amt = int(round(base_claim * random.uniform(0.75, 1.45), -3))
        if payer == "BPJS Kesehatan":
            r_claim = random.random()
            if dept in ("Cardiology", "Radiology / DICOM") and r_claim < 0.19:
                claim_status = "Pending / Revision"
                claim_days = round(random.uniform(6.5, 14.0), 1)
            elif r_claim < 0.11:
                claim_status = "Pending / Revision"
                claim_days = round(random.uniform(6.0, 13.0), 1)
            elif r_claim < 0.18:
                claim_status = "Delayed >7d"
                claim_days = round(random.uniform(7.2, 11.5), 1)
            else:
                claim_status = "Approved First-Pass"
                claim_days = round(random.uniform(1.5, 4.8), 1)
        else:
            claim_status = "Approved First-Pass" if random.random() < 0.94 else "Pending / Revision"
            claim_days = round(random.uniform(0.5, 2.5), 1)

        # CSAT (1-5) linked strongly to <= 60 min outpatient SLA
        if wait <= 45:
            csat = random.choices([3, 4, 5], weights=[0.08, 0.38, 0.54])[0]
        elif wait <= 60:
            csat = random.choices([2, 3, 4, 5], weights=[0.05, 0.22, 0.48, 0.25])[0]
        else:
            csat = random.choices([1, 2, 3, 4], weights=[0.22, 0.38, 0.28, 0.12])[0]

        rows.append([
            f"VIS-{i:05d}",
            visit_date.strftime("%Y-%m-%d"),
            hour,
            dept,
            payer,
            check_in,
            wait,
            consult,
            claim_days,
            claim_status,
            claim_amt,
            csat,
        ])

    rows.sort(key=lambda r: (r[1], r[2]))
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "visit_id", "visit_date", "arrival_hour", "department", "payer_type",
            "check_in_method", "wait_time_mins", "consult_mins",
            "claim_submission_days", "claim_status", "claim_amount_idr", "patient_csat"
        ])
        w.writerows(rows)

    print(f"Generated {len(rows)} clinical visits at {CSV_PATH}")


if __name__ == "__main__":
    main()
