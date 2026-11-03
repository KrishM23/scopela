"""Regenerate PNG figures in outputs/ from data/district_oral_health.json."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "district_oral_health.json"
OUT = ROOT / "outputs"

FOCUS_COLOR = "#B45309"
OTHER = "#94A3B8"
CITY_COLOR = "#0F766E"
DANGER = "#B91C1C"
OK = "#166534"


def main() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )
    OUT.mkdir(exist_ok=True)
    payload = json.loads(DATA.read_text())
    districts = payload["districts"]
    city = payload["city"]
    focus_ids = {8, 9, 10}

    fig, ax = plt.subplots(figsize=(9, 6.2))
    ordered = sorted(districts, key=lambda d: d["dental_visit_pct"])
    names = [d["name"] for d in ordered]
    vals = [d["dental_visit_pct"] for d in ordered]
    colors = [FOCUS_COLOR if d["district"] in focus_ids else OTHER for d in ordered]
    bars = ax.barh(names, vals, color=colors, height=0.72)
    ax.axvline(
        city["dental_visit_pct"],
        color=CITY_COLOR,
        linestyle="--",
        linewidth=1.4,
        label=f"City avg {city['dental_visit_pct']}%",
    )
    ax.set_xlabel("Adults with a dental visit in the past year (%)")
    ax.set_title(
        "Oral health utilization gap across LA City Council Districts\n"
        "CD 9 is last citywide; CD 8 and CD 10 also below average"
    )
    ax.set_xlim(0, 80)
    for bar, v, d in zip(bars, vals, ordered):
        if d["district"] in focus_ids:
            ax.text(
                v + 0.6,
                bar.get_y() + bar.get_height() / 2,
                f"{v}%",
                va="center",
                fontsize=9,
                fontweight="bold",
                color=FOCUS_COLOR,
            )
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "01_dental_visits_by_district.png", dpi=160)
    plt.close()

    fig, ax = plt.subplots(figsize=(8.2, 6.2))
    for d in districts:
        c = FOCUS_COLOR if d["district"] in focus_ids else OTHER
        s = 80 + d["clinician_occ_pct"] * 90
        ax.scatter(
            d["food_insecurity_pct"],
            d["dental_visit_pct"],
            s=s,
            color=c,
            alpha=0.9,
            edgecolors="white",
            linewidths=0.6,
            zorder=3,
        )
        if d["district"] in focus_ids or d["district"] in (11, 4, 5):
            ax.annotate(
                d["name"],
                (d["food_insecurity_pct"] + 0.4, d["dental_visit_pct"] + 0.4),
                fontsize=9,
                color=c,
                fontweight="bold" if d["focus"] else "normal",
            )
    ax.axhline(city["dental_visit_pct"], color=CITY_COLOR, linestyle=":", linewidth=1)
    ax.axvline(city["food_insecurity_pct"], color=CITY_COLOR, linestyle=":", linewidth=1)
    ax.set_xlabel("Adult food insecurity (%)")
    ax.set_ylabel("Adult dental visit in past year (%)")
    ax.set_title(
        "Food insecurity co-moves with low dental utilization\n"
        "Bubble size = share of workers who are health diagnosing/treating practitioners"
    )
    fig.tight_layout()
    fig.savefig(OUT / "02_food_vs_dental_workforce.png", dpi=160)
    plt.close()

    fig, axes = plt.subplots(1, 4, figsize=(11, 4.2), sharey=True)
    metrics = [
        ("dental_visit_pct", "Dental visit\n(%)", True),
        ("food_insecurity_pct", "Food insecurity\n(%)", False),
        ("clinician_occ_pct", "Clinician\nworkforce (%)", True),
        ("transport_barrier_pct", "Transport barrier\nto care (%)", False),
    ]
    focus = [d for d in districts if d["focus"]]
    for ax, (key, label, higher_better) in zip(axes, metrics):
        vals_f = [d[key] for d in focus]
        city_v = city[key]
        cols = [
            OK if (v >= city_v if higher_better else v < city_v) else DANGER for v in vals_f
        ]
        ax.bar([d["name"] for d in focus], vals_f, color=cols, width=0.65)
        ax.axhline(city_v, color=CITY_COLOR, linestyle="--", linewidth=1)
        ax.set_title(label, fontsize=10)
        for i, v in enumerate(vals_f):
            ax.text(i, v + max(vals_f) * 0.02, f"{v:g}", ha="center", fontsize=8)
    axes[0].set_ylabel("Percent")
    fig.suptitle("CD 8–10 vs city average (teal dashed)", fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "03_focus_district_scorecard.png", dpi=160, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4.2))
    labels = {
        "clinician_occ_pct": "Local clinician workforce",
        "food_insecurity_pct": "Food insecurity",
        "transport_barrier_pct": "Transport barriers to care",
        "poverty_pct": "Poverty rate",
    }
    items = sorted(
        ((k, payload["correlations_with_dental_visit"][k]) for k in labels),
        key=lambda kv: abs(kv[1]),
        reverse=True,
    )
    ys = [labels[k] for k, _ in items]
    rs = [v for _, v in items]
    cols = [OK if v > 0 else DANGER for v in rs]
    ax.barh(ys, rs, color=cols, height=0.55)
    ax.axvline(0, color="#333", linewidth=0.8)
    ax.set_xlim(-1.05, 1.05)
    ax.set_xlabel("Pearson r with adult dental visit rate (n=15 districts)")
    ax.set_title("Associations with dental visit rates across LA council districts")
    for y, r in zip(ys, rs):
        ax.text(
            r + (0.03 if r > 0 else -0.03),
            y,
            f"{r:+.2f}",
            va="center",
            ha="left" if r > 0 else "right",
            fontsize=9,
        )
    fig.tight_layout()
    fig.savefig(OUT / "04_correlations.png", dpi=160)
    plt.close()

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    resid_labels = [
        "Clinician workforce\n(after poverty)",
        "Food insecurity\n(after poverty)",
        "Transport barriers\n(after poverty)",
    ]
    resid_vals = [
        payload["residual_correlations_after_poverty"]["clinician_occ_pct"],
        payload["residual_correlations_after_poverty"]["food_insecurity_pct"],
        payload["residual_correlations_after_poverty"]["transport_barrier_pct"],
    ]
    cols = [OK if v > 0 else DANGER for v in resid_vals]
    ax.bar(resid_labels, resid_vals, color=cols, width=0.55)
    ax.axhline(0, color="#333", linewidth=0.8)
    ax.set_ylabel("Correlation of OLS residuals with dental visits")
    ax.set_title(
        "After accounting for poverty, clinician workforce still aligns with dental visits\n"
        "CD 9 has higher supermarket proximity than CD 8, yet worse utilization"
    )
    for i, v in enumerate(resid_vals):
        ax.text(i, v + (0.02 if v >= 0 else -0.04), f"{v:+.2f}", ha="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "05_beyond_poverty.png", dpi=160)
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 4.2))
    stages = [
        "LA dentists\nenrolled in\nMedi-Cal",
        "LA dentists\nseeing 100+\nMedi-Cal pts",
        "CA dentists\nmeaningful\nadult Medi-Cal\n(UCSF)",
    ]
    vals_w = [55, 39, 15]
    ax.bar(stages, vals_w, color=["#0F766E", "#B45309", "#B91C1C"], width=0.6)
    ax.set_ylabel("Share of dentists (%)")
    ax.set_title("Workforce composition — not headcount — drives usable dental access")
    for i, v in enumerate(vals_w):
        ax.text(i, v + 1.5, f"{v}%", ha="center", fontweight="bold")
    ax.set_ylim(0, 70)
    fig.tight_layout()
    fig.savefig(OUT / "06_workforce_funnel.png", dpi=160)
    plt.close()

    print(f"Wrote figures to {OUT}")


if __name__ == "__main__":
    main()
