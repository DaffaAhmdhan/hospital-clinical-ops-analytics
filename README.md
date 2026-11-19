# Hospital Clinical Operations, Polyclinic Queue & BPJS E-Klaim Analytics

Healthcare operational BI project analyzing **8,400 outpatient and emergency visits** (Rp 11.28B billing volume) across 6 hospital departments (`Internal Medicine`, `Cardiology`, `Orthopedics`, `Pediatrics`, `Radiology / DICOM`, `Emergency / IGD`) using **SQL (SQLite)**, **Python**, and an interactive **What-If Queue & Staffing Simulator Dashboard**.

## Business Questions
1. Which clinical departments fail the 60-minute outpatient wait-time SLA, and what hours drive congestion?
2. How much faster is **BPJS Fingerprint Biometric** check-in compared to **Manual Counter** registration?
3. How much **BPJS Kesehatan INA-CBG E-Klaim** revenue is stalled in `Pending / Revision` or `Delayed >7d`?

## Key Findings (Verified from `output/clinical_metrics.json`)
- **Morning Arrival Surge:** **59.7%** of daily visits (5,014 / 8,400) arrive between **07:00 and 10:00 AM**, pushing **Cardiology (78.62 min, 16.82% SLA)** and **Internal Medicine (75.32 min, 22.45% SLA)** well past the 60-minute threshold.
- **Biometric Check-In Impact:** **BPJS Fingerprint Biometric** check-ins average **46.28 min** (**73.3% SLA**, **3.70 CSAT**) versus **71.94 min** (**26.06% SLA**, **2.79 CSAT**) at manual counters—saving **25.66 minutes** per patient.
- **BPJS INA-CBG Cashflow Exposure:** **81.87%** (4,959 claims) clear First-Pass in **3.14 days**, while **13.14%** (**Rp 1.10B**, 796 claims) stall in `Pending / Revision` for an average of **9.83 days**.

## How to Run
```bash
python data/generate_data.py
python src/run_analysis.py
```
Open `dashboard.html` in any browser to use the interactive Queue & Biometric Kiosk Simulator.
