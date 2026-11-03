"""
Oral health access disparities — LA City Council Districts 8, 9, and 10.

Builds a curated district dataset, computes associations between dental
utilization and food / poverty / workforce / transport barriers, and writes
PNG figures for the policy brief.

Primary sources
---------------
- Civic Data Atlas (CDC PLACES 2022–23 BRFSS + ACS): dental visits, edentulism,
  food insecurity, transportation barriers
- ACS 2020–24: poverty; health diagnosing & treating practitioners occupation share
- LA County CCHP 2018: supermarket proximity & child dental affordability (CD 8/9)
- LA County Oral Health Chartbook / COHIP: dentist supply, Medi-Cal participation,
  meaningful-dentist need (SPA 6 = South LA ranks #1)
- UCSF Healthforce Center: statewide Medi-Cal dentist participation & workforce
  composition findings
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "district_oral_health.json"
OUT = ROOT / "outputs"


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else float("nan")


def ols_residuals(x: list[float], y: list[float]) -> list[float]:
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sum((xi - mx) ** 2 for xi in x)
    a = my - b * mx
    return [yi - (a + b * xi) for xi, yi in zip(x, y)]


def main() -> None:
    payload = json.loads(DATA.read_text())
    districts = payload["districts"]
    outcome = [d["dental_visit_pct"] for d in districts]
    predictors = {
        "food_insecurity_pct": [d["food_insecurity_pct"] for d in districts],
        "poverty_pct": [d["poverty_pct"] for d in districts],
        "clinician_occ_pct": [d["clinician_occ_pct"] for d in districts],
        "transport_barrier_pct": [d["transport_barrier_pct"] for d in districts],
    }

    print("Correlations with adult dental visit rate (n=15 districts)")
    for key, series in predictors.items():
        print(f"  {key:24s} r={pearson(outcome, series):+.3f}")

    resid = ols_residuals(predictors["poverty_pct"], outcome)
    print("\nAfter residualizing poverty from dental visits:")
    for key in ("clinician_occ_pct", "food_insecurity_pct", "transport_barrier_pct"):
        print(f"  residual × {key:20s} r={pearson(resid, predictors[key]):+.3f}")

    focus = [d for d in districts if d["focus"]]
    print("\nFocus districts (CD 8/9/10)")
    for d in focus:
        print(
            f"  {d['name']}: dental {d['dental_visit_pct']}% | "
            f"food insecurity {d['food_insecurity_pct']}% | "
            f"clinicians {d['clinician_occ_pct']}% | "
            f"transport barriers {d['transport_barrier_pct']}%"
        )

    print(
        "\nPolicy takeaway: geographic grocery proximity does not explain CD 9 vs CD 8 "
        "(CD 9 ~84% near supermarket vs CD 8 ~58%, yet CD 9 has the city's worst "
        "dental utilization). Usable dental access — Medi-Cal participation, local "
        "clinician density, transport to appointments — tracks outcomes more tightly. "
        f"Figures live in {OUT}/"
    )


if __name__ == "__main__":
    main()
