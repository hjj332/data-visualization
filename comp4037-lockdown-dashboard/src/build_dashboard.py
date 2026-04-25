from __future__ import annotations

import argparse
import json
from pathlib import Path

from plotly.offline.offline import get_plotlyjs


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "data" / "processed" / "lockdown_dashboard_data.json"
DEFAULT_HTML = ROOT / "docs" / "index.html"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the HTML page for the lockdown dashboard."
    )
    parser.add_argument(
        "--input-json",
        type=Path,
        default=DEFAULT_JSON,
        help="Processed dashboard JSON payload.",
    )
    parser.add_argument(
        "--output-html",
        type=Path,
        default=DEFAULT_HTML,
        help="Output HTML path.",
    )
    return parser.parse_args()


def load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_html(payload: dict) -> str:
    rows_json = json.dumps(payload["rows"], ensure_ascii=False)
    year_labels_json = json.dumps(payload["year_labels"])
    plotly_js = get_plotlyjs()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>COMP4037 Lockdown Matrix</title>
  <style>
    :root {{
      --bg: #f2eadc;
      --panel: #fbf7f0;
      --panel-2: #efe0c8;
      --text: #243243;
      --muted: #607081;
      --line: #d8c5ab;
      --accent-1: #bf6a3c;
      --accent-2: #346d84;
      --accent-3: #8d7458;
      --shadow: 0 16px 34px rgba(70, 51, 34, 0.06);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(191, 106, 60, 0.08), transparent 28%),
        radial-gradient(circle at bottom right, rgba(52, 109, 132, 0.08), transparent 24%),
        var(--bg);
      color: var(--text);
      font-family: "Trebuchet MS", "Gill Sans MT", Verdana, sans-serif;
    }}
    .page {{
      max-width: 1540px;
      margin: 0 auto;
      padding: 24px 28px 26px;
    }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--muted);
      margin-bottom: 16px;
    }}
    .hero {{
      padding: 8px 0 20px;
      border-bottom: 1px solid var(--line);
    }}
    .hero-kicker {{
      display: inline-block;
      margin-bottom: 12px;
      padding-left: 14px;
      border-left: 3px solid var(--accent-1);
      font-size: 12px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--accent-3);
    }}
    .hero h1 {{
      margin: 0 0 12px;
      max-width: 980px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 54px;
      line-height: 1.02;
      letter-spacing: -0.03em;
      font-weight: 700;
    }}
    .hero p {{
      margin: 0;
      font-size: 19px;
      line-height: 1.45;
      color: var(--muted);
      max-width: 900px;
    }}
    .dashboard {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 340px;
      gap: 24px;
      margin-top: 24px;
      align-items: start;
    }}
    .main-panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px 28px 8px 8px;
      border-top: 5px solid var(--accent-2);
      padding: 20px 22px 16px;
      box-shadow: var(--shadow);
    }}
    .panel-head {{
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 16px;
      margin-bottom: 10px;
    }}
    .chart-kicker {{
      margin-bottom: 6px;
      font-size: 12px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--accent-3);
    }}
    .panel-head h2 {{
      margin: 0 0 6px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 28px;
      line-height: 1.08;
    }}
    .panel-head p {{
      margin: 0;
      font-size: 14px;
      color: var(--muted);
      line-height: 1.45;
    }}
    .lockdown-pill {{
      background: linear-gradient(135deg, rgba(191, 106, 60, 0.16), rgba(191, 106, 60, 0.08));
      border: 1px solid rgba(191, 106, 60, 0.28);
      border-radius: 999px;
      padding: 9px 14px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.05em;
      color: var(--accent-3);
      white-space: nowrap;
    }}
    #chart {{
      height: 790px;
      width: 100%;
    }}
    .chart-foot {{
      margin-top: 10px;
      font-size: 13px;
      color: var(--muted);
      line-height: 1.4;
    }}
    .sidebar {{
      display: flex;
      flex-direction: column;
      gap: 16px;
      position: sticky;
      top: 18px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px 18px 6px 6px;
      border-top: 3px solid rgba(52, 109, 132, 0.26);
      padding: 16px 16px 15px;
      box-shadow: var(--shadow);
    }}
    .card h3 {{
      margin: 0 0 10px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 24px;
      line-height: 1.1;
    }}
    .card p {{
      margin: 0;
      font-size: 14px;
      line-height: 1.5;
      color: var(--muted);
    }}
    .filter-list {{
      display: flex;
      flex-direction: column;
      gap: 9px;
      max-height: 280px;
      overflow: auto;
      padding-right: 4px;
    }}
    .filter-list::-webkit-scrollbar {{
      width: 10px;
    }}
    .filter-list::-webkit-scrollbar-thumb {{
      background: rgba(141, 116, 88, 0.22);
      border-radius: 999px;
      border: 2px solid transparent;
      background-clip: padding-box;
    }}
    .filter-item {{
      display: flex;
      align-items: start;
      gap: 10px;
      font-size: 14px;
      color: var(--text);
      padding: 7px 8px;
      border-radius: 8px;
      background: rgba(239, 224, 200, 0.28);
    }}
    .filter-item strong {{
      display: block;
      line-height: 1.2;
    }}
    .filter-item small {{
      display: block;
      color: var(--muted);
      margin-top: 2px;
      line-height: 1.28;
    }}
    .filter-actions {{
      display: flex;
      gap: 8px;
      margin-top: 12px;
      flex-wrap: wrap;
    }}
    .filter-actions button {{
      border: 1px solid var(--line);
      background: linear-gradient(180deg, #f7f0e4, #ecdfca);
      color: var(--text);
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 12px;
      cursor: pointer;
      transition: transform 120ms ease, border-color 120ms ease, background 120ms ease;
    }}
    .filter-actions button:hover {{
      transform: translateY(-1px);
      border-color: rgba(191, 106, 60, 0.34);
      background: linear-gradient(180deg, #faefe3, #ead6bc);
    }}
    .legend-wrap {{
      display: grid;
      grid-template-columns: 20px 1fr;
      gap: 14px;
      align-items: stretch;
    }}
    .legend-bar {{
      width: 20px;
      height: 180px;
      border-radius: 10px;
      background: linear-gradient(180deg, #bf6a3c 0%, #f3ede3 50%, #346d84 100%);
      border: 1px solid #d9ccb8;
    }}
    .legend-scale {{
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      font-size: 13px;
      color: var(--muted);
    }}
    .detail-grid {{
      display: grid;
      grid-template-columns: 104px 1fr;
      gap: 9px 12px;
      font-size: 13px;
      line-height: 1.34;
    }}
    .detail-grid strong {{
      color: var(--text);
      font-weight: 700;
    }}
    .detail-placeholder {{
      font-size: 14px;
      color: var(--muted);
      line-height: 1.5;
    }}
    .observation {{
      background:
        linear-gradient(135deg, rgba(191, 106, 60, 0.12), rgba(52, 109, 132, 0.05)),
        #f2e7d5;
      border-top-color: rgba(191, 106, 60, 0.3);
    }}
    footer {{
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px solid rgba(216, 197, 171, 0.85);
      font-size: 13px;
      color: var(--muted);
      line-height: 1.45;
    }}
    @media (max-width: 1200px) {{
      .dashboard {{
        grid-template-columns: 1fr;
      }}
      .sidebar {{
        position: static;
      }}
      #chart {{
        height: 700px;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="topbar">
      <div><strong>COMP4037 Coursework 2</strong> | NHS admissions dashboard</div>
      <div>England NHS admitted patient care</div>
    </div>

    <section class="hero">
      <div class="hero-kicker">Emergency admissions / primary diagnosis summary / 2018-2024</div>
      <h1>Emergency admissions change vs pre-lockdown baseline</h1>
      <p>Selected primary diagnosis summary groups, England NHS admitted patient care, 2018-19 to 2023-24.</p>
    </section>

    <div class="dashboard">
      <section class="main-panel">
        <div class="panel-head">
          <div>
            <div class="chart-kicker">Matrix view of divergence</div>
            <h2>Emergency admissions change vs pre-lockdown baseline</h2>
            <p>Primary diagnosis summary groups, England NHS admitted patient care, 2018-19 to 2023-24.</p>
          </div>
          <div class="lockdown-pill">2020-21 highlighted as the lockdown year</div>
        </div>
        <div id="chart"></div>
        <div class="chart-foot">Warm tones sit above the pre-lockdown baseline; cool tones fall below it. Baseline = average of 2018-19 and 2019-20 emergency admissions.</div>
      </section>

      <aside class="sidebar">
        <section class="card">
          <h3>Filter by pattern</h3>
          <div class="filter-list" id="group-filters"></div>
          <div class="filter-actions">
            <button type="button" id="show-all-groups">Select all</button>
            <button type="button" id="show-rises">Only resilient / rising</button>
            <button type="button" id="show-declines">Only sharp declines</button>
          </div>
        </section>

        <section class="card">
          <h3>Choose categories</h3>
          <div class="filter-list" id="diagnosis-filters"></div>
          <div class="filter-actions">
            <button type="button" id="select-all-codes">Select all</button>
            <button type="button" id="clear-all-codes">Clear all</button>
          </div>
        </section>

        <section class="card">
          <h3>Inspect a cell</h3>
          <div id="hover-details" class="detail-placeholder">
            Hover over a square to see the diagnosis-year pair, its baseline volume, and the percentage change.
          </div>
        </section>

        <section class="card">
          <h3>Colour scale</h3>
          <div class="legend-wrap">
            <div class="legend-bar"></div>
            <div class="legend-scale">
              <div><strong style="color:#243243;">Rise</strong><br><span>above baseline</span></div>
              <div><strong style="color:#243243;">Baseline</strong><br><span>roughly 0% change</span></div>
              <div><strong style="color:#243243;">Collapse</strong><br><span>below baseline</span></div>
            </div>
          </div>
        </section>

        <section class="card observation">
          <h3>Observation</h3>
          <p>
            The strongest split appears in 2020-21: respiratory and viral pathways drop sharply, while pulmonary-circulation, venous, liver and hypertensive categories stay much closer to baseline.
          </p>
        </section>
      </aside>
    </div>

    <footer>
      Data: NHS Hospital Admitted Patient Care Activity, Primary Diagnosis Summary, 2018-19 to 2023-24.
      Metric shown: emergency admissions. Baseline = average of 2018-19 and 2019-20.
    </footer>
  </div>

  <script>
    {plotly_js}
  </script>
  <script>
    const RAW_ROWS = {rows_json};
    const YEAR_LABELS = {year_labels_json};
    const GROUP_ORDER = ["Resilient / rising", "Sharp declines"];
    const state = {{
      groups: new Set(GROUP_ORDER),
      codes: new Set(RAW_ROWS.map(r => r.code))
    }};

    const groupContainer = document.getElementById("group-filters");
    const codeContainer = document.getElementById("diagnosis-filters");
    const hoverDetails = document.getElementById("hover-details");
    const defaultHoverText = '<div class="detail-placeholder">Hover over a square to see the diagnosis-year pair, its baseline volume, and the percentage change.</div>';
    let chartEventsBound = false;

    function buildFilters() {{
      GROUP_ORDER.forEach(group => {{
        const label = document.createElement("label");
        label.className = "filter-item";
        label.innerHTML = `<input type="checkbox" checked data-group="${{group}}"> <span><strong>${{group}}</strong></span>`;
        groupContainer.appendChild(label);
      }});

      RAW_ROWS.forEach(row => {{
        const label = document.createElement("label");
        label.className = "filter-item";
        label.innerHTML = `<input type="checkbox" checked data-code="${{row.code}}"> <span><strong>${{row.code}}</strong><small>${{row.description}}</small></span>`;
        codeContainer.appendChild(label);
      }});

      groupContainer.addEventListener("change", event => {{
        const input = event.target;
        if (!input.matches("[data-group]")) return;
        if (input.checked) state.groups.add(input.dataset.group);
        else state.groups.delete(input.dataset.group);
        render();
      }});

      codeContainer.addEventListener("change", event => {{
        const input = event.target;
        if (!input.matches("[data-code]")) return;
        if (input.checked) state.codes.add(input.dataset.code);
        else state.codes.delete(input.dataset.code);
        render();
      }});

      document.getElementById("show-all-groups").onclick = () => {{
        state.groups = new Set(GROUP_ORDER);
        groupContainer.querySelectorAll("input[data-group]").forEach(el => el.checked = true);
        render();
      }};
      document.getElementById("show-rises").onclick = () => {{
        state.groups = new Set(["Resilient / rising"]);
        groupContainer.querySelectorAll("input[data-group]").forEach(el => {{
          el.checked = el.dataset.group === "Resilient / rising";
        }});
        render();
      }};
      document.getElementById("show-declines").onclick = () => {{
        state.groups = new Set(["Sharp declines"]);
        groupContainer.querySelectorAll("input[data-group]").forEach(el => {{
          el.checked = el.dataset.group === "Sharp declines";
        }});
        render();
      }};
      document.getElementById("select-all-codes").onclick = () => {{
        state.codes = new Set(RAW_ROWS.map(r => r.code));
        codeContainer.querySelectorAll("input[data-code]").forEach(el => el.checked = true);
        render();
      }};
      document.getElementById("clear-all-codes").onclick = () => {{
        state.codes = new Set();
        codeContainer.querySelectorAll("input[data-code]").forEach(el => el.checked = false);
        render();
      }};
    }}

    function filteredRows() {{
      const rows = RAW_ROWS.filter(row => state.groups.has(row.group) && state.codes.has(row.code));
      const grouped = [];
      GROUP_ORDER.forEach(group => {{
        const slice = rows.filter(row => row.group === group).sort((a, b) => {{
          return group === "Resilient / rising"
            ? b.years["2020-21"].pct - a.years["2020-21"].pct
            : a.years["2020-21"].pct - b.years["2020-21"].pct;
        }});
        grouped.push(...slice);
      }});
      return grouped;
    }}

    function detailHTML(cell) {{
      return `
        <div class="detail-grid">
          <strong>Code</strong><div>${{cell.code}}</div>
          <strong>Description</strong><div>${{cell.description}}</div>
          <strong>Pattern</strong><div>${{cell.group}}</div>
          <strong>Year</strong><div>${{cell.year}}</div>
          <strong>Emergency</strong><div>${{cell.emergency.toLocaleString()}}</div>
          <strong>Baseline avg</strong><div>${{cell.baseline.toLocaleString()}}</div>
          <strong>% vs baseline</strong><div>${{cell.pct > 0 ? "+" : ""}}${{cell.pct.toFixed(1)}}%</div>
        </div>
      `;
    }}

    function bindChartEvents() {{
      if (chartEventsBound) return;
      const chartEl = document.getElementById("chart");
      chartEl.on("plotly_hover", event => {{
        const cell = event.points[0].customdata;
        hoverDetails.innerHTML = detailHTML(cell);
      }});
      chartEl.on("plotly_unhover", () => {{
        hoverDetails.innerHTML = defaultHoverText;
      }});
      chartEventsBound = true;
    }}

    function render() {{
      const rows = filteredRows();
      if (!rows.length) {{
        Plotly.purge("chart");
        hoverDetails.innerHTML = '<div class="detail-placeholder">No diagnosis categories are currently selected.</div>';
        chartEventsBound = false;
        return;
      }}

      const yValues = rows.map((_, i) => i);
      const yText = rows.map(row => `${{row.code}}<br>${{row.description}}`);
      const z = rows.map(row => YEAR_LABELS.map(year => row.years[year].pct));
      const custom = rows.map(row =>
        YEAR_LABELS.map(year => ({{
          code: row.code,
          description: row.full_description,
          group: row.group,
          year,
          emergency: row.years[year].emergency,
          baseline: row.baseline,
          pct: row.years[year].pct
        }}))
      );

      const heatmap = {{
        type: "heatmap",
        z,
        x: [0, 1, 2, 3, 4, 5],
        y: yValues,
        customdata: custom,
        hovertemplate:
          "<b>%{{customdata.code}}</b><br>" +
          "%{{customdata.description}}<br>" +
          "Pattern: %{{customdata.group}}<br>" +
          "Year: %{{customdata.year}}<br>" +
          "Emergency admissions: %{{customdata.emergency:,}}<br>" +
          "Baseline avg: %{{customdata.baseline:,}}<br>" +
          "Change vs baseline: %{{customdata.pct:+.1f}}%<extra></extra>",
        colorscale: [
          [0.00, "#2f6f8d"],
          [0.50, "#f1ece3"],
          [1.00, "#c96d42"]
        ],
        zmin: -75,
        zmax: 20,
        zmid: 0,
        xgap: 6,
        ygap: 6,
        showscale: false,
        xaxis: "x",
        yaxis: "y"
      }};

      const annotations = [];
      rows.forEach((row, idx) => {{
        annotations.push(
          {{
            x: 0.875,
            y: idx,
            xref: "paper",
            yref: "y",
            text: `${{Math.round(row.baseline / 1000)}}k`,
            showarrow: false,
            font: {{size: 16, color: "#516170"}}
          }},
          {{
            x: 2,
            y: idx,
            xref: "x",
            yref: "y",
            text: `<b>${{row.years["2020-21"].pct > 0 ? "+" : ""}}${{Math.round(row.years["2020-21"].pct)}}%</b>`,
            showarrow: false,
            font: {{size: 15, color: "white"}}
          }},
          {{
            x: 5,
            y: idx,
            xref: "x",
            yref: "y",
            text: `<b>${{row.years["2023-24"].pct > 0 ? "+" : ""}}${{Math.round(row.years["2023-24"].pct)}}%</b>`,
            showarrow: false,
            font: {{
              size: 14,
              color: Math.abs(row.years["2023-24"].pct) >= 15 ? "white" : "#243243"
            }}
          }}
        );
      }});

      const shapes = [
        {{
          type: "rect",
          xref: "x",
          yref: "paper",
          x0: 1.5,
          x1: 2.5,
          y0: 0.03,
          y1: 0.98,
          line: {{color: "#8d7458", width: 2}},
          fillcolor: "rgba(191, 106, 60, 0.04)"
        }}
      ];

      const riseCount = rows.filter(row => row.group === "Resilient / rising").length;
      if (riseCount > 0 && riseCount < rows.length) {{
        shapes.push({{
          type: "line",
          xref: "paper",
          yref: "y",
          x0: 0,
          x1: 0.93,
          y0: riseCount - 0.5,
          y1: riseCount - 0.5,
          line: {{color: "#d5c2a9", width: 2}}
        }});
      }}

      const layout = {{
        paper_bgcolor: "#fbf7f0",
        plot_bgcolor: "#fbf7f0",
        margin: {{l: 232, r: 38, t: 78, b: 42}},
        font: {{family: "Trebuchet MS, Gill Sans MT, Verdana, sans-serif", color: "#243243"}},
        hoverlabel: {{
          bgcolor: "#fffaf3",
          bordercolor: "#d8c5ab",
          font: {{family: "Trebuchet MS, Gill Sans MT, Verdana, sans-serif", size: 13, color: "#243243"}}
        }},
        xaxis: {{
          domain: [0.00, 0.80],
          tickmode: "array",
          tickvals: [0, 1, 2, 3, 4, 5],
          ticktext: YEAR_LABELS,
          side: "top",
          tickfont: {{size: 15, color: "#243243"}},
          ticklen: 0,
          showgrid: false,
          zeroline: false,
          fixedrange: true
        }},
        yaxis: {{
          domain: [0.03, 0.98],
          tickmode: "array",
          tickvals: yValues,
          ticktext: yText,
          tickfont: {{size: 13, color: "#243243"}},
          autorange: "reversed",
          automargin: true,
          fixedrange: true
        }},
        annotations: annotations.concat([
          {{
            x: 2,
            y: 1.08,
            xref: "x",
            yref: "paper",
            text: "<b>Lockdown year</b>",
            showarrow: false,
            font: {{size: 15, color: "#8d7458"}}
          }},
          {{
            x: 0.875,
            y: 1.08,
            xref: "paper",
            yref: "paper",
            text: "<b>Baseline avg</b>",
            showarrow: false,
            font: {{size: 15, color: "#243243"}}
          }}
        ]),
        shapes: shapes
      }};

      Plotly.react("chart", [heatmap], layout, {{
        displaylogo: false,
        responsive: true,
        scrollZoom: false
      }}).then(() => {{
        bindChartEvents();
      }});
    }}

    buildFilters();
    hoverDetails.innerHTML = defaultHoverText;
    render();
  </script>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    payload = load_payload(args.input_json)
    args.output_html.parent.mkdir(parents=True, exist_ok=True)
    args.output_html.write_text(build_html(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
