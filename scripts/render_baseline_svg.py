"""Render a dependency-free SVG from the committed baseline summaries."""

from __future__ import annotations

from collections import defaultdict
from html import escape
from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ROOT / "artifacts" / "baseline" / "new.csv",
    ROOT / "artifacts" / "baseline" / "aged.csv",
]
OUTPUT = ROOT / "docs" / "assets" / "baseline-endurance.svg"


def read_full_charge_rows() -> dict[str, dict[str, float]]:
    values: dict[str, dict[str, float]] = defaultdict(dict)
    for source in SOURCES:
        with source.open(newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                if row["initial_soc"] == "1.00":
                    values[row["scenario"]][row["battery"]] = float(row["tte_hours"])
    return values


def main() -> None:
    values = read_full_charge_rows()
    scenarios = ["reading-dark", "mixed-day", "streaming", "gaming"]
    max_value = max(value for scenario in values.values() for value in scenario.values())
    width, height = 980, 520
    left, right, top, bottom = 95, 35, 70, 90
    chart_width = width - left - right
    chart_height = height - top - bottom
    group_width = chart_width / len(scenarios)
    bar_width = 46
    colors = {"new-demo": "#2563eb", "aged-demo": "#f97316"}

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">VoltCast baseline endurance comparison</title>',
        '<desc id="desc">Time-to-empty for four synthetic smartphone workloads using new and aged demonstration batteries.</desc>',
        '<rect width="100%" height="100%" rx="18" fill="#f8fafc"/>',
        '<text x="95" y="38" font-family="system-ui,sans-serif" font-size="24" font-weight="700" fill="#0f172a">Full-charge endurance across synthetic workloads</text>',
        f'<line x1="{left}" y1="{top + chart_height}" x2="{left + chart_width}" y2="{top + chart_height}" stroke="#64748b"/>',
    ]

    for tick in range(0, int(max_value) + 6, 5):
        y = top + chart_height - chart_height * tick / (max_value * 1.08)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + chart_width}" y2="{y:.1f}" stroke="#cbd5e1" stroke-dasharray="4 5"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-family="system-ui,sans-serif" font-size="13" fill="#475569">{tick}h</text>')

    for index, scenario in enumerate(scenarios):
        center = left + group_width * (index + 0.5)
        for offset, battery in ((-bar_width / 2, "new-demo"), (bar_width / 2, "aged-demo")):
            value = values[scenario][battery]
            bar_height = chart_height * value / (max_value * 1.08)
            x = center + offset - bar_width / 2
            y = top + chart_height - bar_height
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width}" height="{bar_height:.1f}" rx="6" fill="{colors[battery]}"/>')
            parts.append(f'<text x="{x + bar_width / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" font-weight="600" fill="#0f172a">{value:.1f}h</text>')
        label = escape(scenario.replace("-", " ").title())
        parts.append(f'<text x="{center:.1f}" y="{top + chart_height + 32}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="#334155">{label}</text>')

    legend_y = height - 25
    for x, battery, label in ((310, "new-demo", "New demo battery"), (530, "aged-demo", "Aged demo battery")):
        parts.append(f'<rect x="{x}" y="{legend_y - 13}" width="18" height="18" rx="4" fill="{colors[battery]}"/>')
        parts.append(f'<text x="{x + 27}" y="{legend_y + 1}" font-family="system-ui,sans-serif" font-size="14" fill="#334155">{label}</text>')
    parts.append('</svg>')
    OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
