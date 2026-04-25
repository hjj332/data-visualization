# Intermediate data

This folder holds the tables created between the raw NHS workbooks and the final dashboard files.

- `primary_diagnosis_emergency_long.csv`
  - Combined long table for all included years.
- `primary_diagnosis_emergency_wide.csv`
  - Wide table with one row per diagnosis code, plus baseline and percentage-change fields.
- `selected_lockdown_categories.csv`
  - The eight diagnosis groups used in the dashboard.
- `yearly/`
  - One extracted CSV per year from the `Primary Diagnosis Summary` sheet.

These files are included so the processing steps can be checked without rerunning the full extraction.
