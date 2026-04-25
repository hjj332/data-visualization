from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = ROOT / "data" / "raw"
DEFAULT_INTERMEDIATE_DIR = ROOT / "data" / "intermediate"
DEFAULT_JSON = ROOT / "data" / "processed" / "lockdown_dashboard_data.json"
DEFAULT_CSV = ROOT / "data" / "processed" / "lockdown_dashboard_table.csv"
BAD_TEXT_FRAGMENTS = ["閳?,", "鈥?,", "\ufeff"]

YEARS = [
    ("2018-19", "hosp-epis-stat-admi-diag-2018-19-tab.xlsx"),
    ("2019-20", "hosp-epis-stat-admi-diag-2019-20-tab supp.xlsx"),
    ("2020-21", "hosp-epis-stat-admi-diag-2020-21-tab.xlsx"),
    ("2021-22", "hosp-epis-stat-admi-diag-2021-22-tab.xlsx"),
    ("2022-23", "hosp-epis-stat-admi-diag-2022-23-tab_V2.xlsx"),
    ("2023-24", "hosp-epis-stat-admi-diag-2023-24-tab.xlsx"),
]

SELECTED = [
    (
        "Resilient / rising",
        [
            "I26-I28",
            "I80-I89",
            "K70-K77",
            "I10-I15",
        ],
    ),
    (
        "Sharp declines",
        [
            "J20-J22",
            "J00-J06",
            "B25-B34",
            "J09-J18",
        ],
    ),
]

DISPLAY_DESCRIPTION = {
    "I26-I28": "Pulmonary circulation disorders",
    "I80-I89": "Veins & lymphatic disorders",
    "K70-K77": "Diseases of liver",
    "I10-I15": "Hypertensive diseases",
    "J20-J22": "Acute lower respiratory infections",
    "J00-J06": "Acute upper respiratory infections",
    "B25-B34": "Other viral diseases",
    "J09-J18": "Influenza & pneumonia",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract the dashboard dataset from the raw NHS workbooks."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Directory containing the raw NHS Excel workbooks.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=DEFAULT_JSON,
        help="Path for the processed JSON payload.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=DEFAULT_CSV,
        help="Path for the flat processed CSV export.",
    )
    parser.add_argument(
        "--intermediate-dir",
        type=Path,
        default=DEFAULT_INTERMEDIATE_DIR,
        help="Directory for intermediate extracted tables.",
    )
    return parser.parse_args()


def clean_text(value: object) -> str:
    text = str(value)
    for fragment in BAD_TEXT_FRAGMENTS:
        text = text.replace(fragment, "")
    return text.strip()


def load_summary(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name="Primary Diagnosis Summary", header=None)
    header_idx = next(
        i
        for i in range(min(20, len(raw)))
        if any(
            "Primary diagnosis" in str(x) and "description" in str(x)
            for x in raw.iloc[i].tolist()
        )
    )
    df = pd.read_excel(path, sheet_name="Primary Diagnosis Summary", header=header_idx)
    emergency_col = next(c for c in df.columns if "Emergency" in str(c))

    out = df[[df.columns[0], df.columns[1], emergency_col]].copy()
    out.columns = ["code", "description", "emergency"]
    out = out.dropna(subset=["code"])
    out = out[out["code"] != "Total"]
    out["code"] = out["code"].map(clean_text)
    out["description"] = out["description"].map(clean_text)
    out["emergency"] = pd.to_numeric(out["emergency"], errors="coerce")
    return out.dropna(subset=["emergency"])


def extract_all_years(source_dir: Path) -> pd.DataFrame:
    missing = [filename for _, filename in YEARS if not (source_dir / filename).exists()]
    if missing:
        missing_list = "\n".join(f"- {name}" for name in missing)
        raise FileNotFoundError(
            f"Missing raw NHS workbooks in {source_dir}:\n{missing_list}"
        )

    frames = []
    for year, filename in YEARS:
        df = load_summary(source_dir / filename)
        df["year"] = year
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def build_wide_table(all_df: pd.DataFrame) -> pd.DataFrame:
    wide = all_df.pivot_table(
        index=["code", "description"],
        columns="year",
        values="emergency",
        aggfunc="first",
    )
    wide["baseline"] = wide[["2018-19", "2019-20"]].mean(axis=1)
    wide = wide[wide["baseline"] > 0].copy()

    for year, _ in YEARS:
        wide[f"{year}_pct"] = (wide[year] - wide["baseline"]) / wide["baseline"] * 100

    return wide


def select_categories(wide: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group_name, codes in SELECTED:
        for code in codes:
            match = wide.reset_index().query("code == @code")
            if match.empty:
                continue
            record = match.iloc[0].to_dict()
            record["group"] = group_name
            rows.append(record)

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("No selected diagnosis groups were found in the extracted data.")
    return df


def write_intermediate_outputs(
    all_df: pd.DataFrame,
    wide: pd.DataFrame,
    selected: pd.DataFrame,
    intermediate_dir: Path,
) -> None:
    yearly_dir = intermediate_dir / "yearly"
    yearly_dir.mkdir(parents=True, exist_ok=True)

    long_df = all_df.copy()
    long_df = long_df.sort_values(["year", "code"]).reset_index(drop=True)
    long_df.to_csv(
        intermediate_dir / "primary_diagnosis_emergency_long.csv",
        index=False,
        encoding="utf-8",
    )

    for year, _ in YEARS:
        year_df = long_df[long_df["year"] == year].copy()
        year_df.to_csv(
            yearly_dir / f"primary_diagnosis_emergency_{year}.csv",
            index=False,
            encoding="utf-8",
        )

    wide_df = wide.reset_index().sort_values("code").reset_index(drop=True)
    wide_df.to_csv(
        intermediate_dir / "primary_diagnosis_emergency_wide.csv",
        index=False,
        encoding="utf-8",
    )

    selected_df = selected.copy().sort_values(["group", "code"]).reset_index(drop=True)
    selected_df.to_csv(
        intermediate_dir / "selected_lockdown_categories.csv",
        index=False,
        encoding="utf-8",
    )


def build_payload(df: pd.DataFrame) -> dict:
    year_labels = [year for year, _ in YEARS]
    rows = []
    for row in df.to_dict("records"):
        rows.append(
            {
                "code": row["code"],
                "description": DISPLAY_DESCRIPTION.get(row["code"], row["description"]),
                "full_description": row["description"],
                "group": row["group"],
                "baseline": int(round(row["baseline"])),
                "years": {
                    year: {
                        "emergency": int(round(row[year])),
                        "pct": round(float(row[f"{year}_pct"]), 1),
                    }
                    for year in year_labels
                },
            }
        )

    return {
        "title": "Emergency admissions change vs pre-lockdown baseline",
        "metric": "Emergency admissions",
        "question": "Question 1",
        "year_labels": year_labels,
        "baseline_rule": "Average of 2018-19 and 2019-20 values",
        "rows": rows,
    }


def build_flat_table(payload: dict) -> pd.DataFrame:
    flat_rows = []
    for row in payload["rows"]:
        flat = {
            "code": row["code"],
            "display_description": row["description"],
            "full_description": row["full_description"],
            "group": row["group"],
            "baseline": row["baseline"],
        }
        for year, values in row["years"].items():
            flat[f"{year}_emergency"] = values["emergency"]
            flat[f"{year}_pct"] = values["pct"]
        flat_rows.append(flat)
    return pd.DataFrame(flat_rows)


def main() -> None:
    args = parse_args()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.intermediate_dir.mkdir(parents=True, exist_ok=True)

    all_df = extract_all_years(args.source_dir)
    wide = build_wide_table(all_df)
    selected = select_categories(wide)
    write_intermediate_outputs(all_df, wide, selected, args.intermediate_dir)
    payload = build_payload(selected)
    flat = build_flat_table(payload)

    args.output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    flat.to_csv(args.output_csv, index=False, encoding="utf-8")


if __name__ == "__main__":
    main()
