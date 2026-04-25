# COMP4037 Lockdown Dashboard

Files used to build the dashboard for **COMP4037 Research Methods**, Question 1.

The dashboard compares selected NHS primary diagnosis summary groups across `2018-19` to `2023-24`. The main view is a time-series heatmap based on emergency admissions, with the pre-lockdown baseline defined as the average of `2018-19` and `2019-20`.

## Files

- `src/extract_lockdown_data.py`
  - Reads the NHS workbooks and writes the intermediate and processed tables.
- `src/build_dashboard.py`
  - Builds the HTML dashboard from the processed JSON file.
- `data/intermediate/`
  - Year-level extracts plus the combined long and wide tables.
- `data/processed/lockdown_dashboard_data.json`
  - Processed payload used by the dashboard.
- `data/processed/lockdown_dashboard_table.csv`
  - Flat table version of the same processed data.
- `docs/index.html`
  - Dashboard page for local viewing or GitHub Pages.

## Structure

```text
comp4037-lockdown-dashboard/
- data/
  - intermediate/
    - README.md
    - primary_diagnosis_emergency_long.csv
    - primary_diagnosis_emergency_wide.csv
    - selected_lockdown_categories.csv
    - yearly/
      - primary_diagnosis_emergency_2018-19.csv
      - ...
  - raw/
    - README.md
  - processed/
    - lockdown_dashboard_data.json
    - lockdown_dashboard_table.csv
- docs/
  - .nojekyll
  - index.html
- src/
  - build_dashboard.py
  - extract_lockdown_data.py
- .gitignore
- README.md
- requirements.txt
```

## Run the dashboard

Install dependencies:

```bash
pip install -r requirements.txt
```

Build the HTML page from the processed data already included in the repository:

```bash
python src/build_dashboard.py
```

This writes:

```text
docs/index.html
```

## Rebuild the data from raw NHS files

The raw Excel workbooks are not included here. Put them in:

```text
data/raw/
```

with the filenames listed in [data/raw/README.md](data/raw/README.md).

Then run:

```bash
python src/extract_lockdown_data.py --source-dir data/raw
python src/build_dashboard.py
```

The extraction step also writes intermediate tables to:

```text
data/intermediate/
```

This regenerates:

- `data/intermediate/yearly/*.csv`
- `data/intermediate/primary_diagnosis_emergency_long.csv`
- `data/intermediate/primary_diagnosis_emergency_wide.csv`
- `data/intermediate/selected_lockdown_categories.csv`
- `data/processed/lockdown_dashboard_data.json`
- `data/processed/lockdown_dashboard_table.csv`
- `docs/index.html`

## GitHub notes

This folder can be uploaded as a standalone repository:

1. Create a new GitHub repository.
2. Upload the contents of this folder.
3. If you want to publish the page, point GitHub Pages to `docs/`.

The processed data is included, so the dashboard can be rebuilt without the raw Excel files. The raw workbooks stay out of version control through `.gitignore`.

## Dependencies

- `pandas`
- `openpyxl`
- `plotly`

## Data note

The dashboard uses a selected set of diagnosis groups to show the contrast between categories that stayed nearer to baseline during lockdown and categories that dropped sharply. The metric shown is emergency admissions rather than total admissions.
