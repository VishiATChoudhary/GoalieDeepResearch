"""End-to-end analysis for the World Cup goalkeeper showcase study.

Run from the repo root:  python analysis/run_analysis.py

Outputs:
  * analysis/figures/*.png        — charts
  * analysis/ANALYSIS_RESULTS.md  — written summary of findings
  * data/processed/goalkeepers_processed.csv

Sections:
  1. Descriptive: showcase-success rate by nation tier (the core hypothesis)
  2. Driving factors: logistic coefficients + random-forest permutation importance
  3. Sensitivity analysis: how the smaller-nation effect & feature ranking respond
     to (a) the success threshold, (b) tier cutoffs, (c) leave-one-tournament-out
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from features import add_derived_columns, assign_nation_tier  # noqa: E402
import model as M  # noqa: E402

FIG_DIR = ROOT / "analysis" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def load() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "goalkeepers_worldcups.csv")
    df = add_derived_columns(df)
    out = ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "goalkeepers_processed.csv", index=False)
    return df


def section_descriptive(df: pd.DataFrame, lines: list[str]) -> None:
    lines.append("## 1. Showcase success by nation tier\n")
    tier_order = ["elite", "mid", "smaller"]
    g = (df.groupby("nation_tier")
           .agg(n=("player", "size"),
                success_rate=("showcase_success", "mean"),
                mean_mv_growth=("mv_growth_pct", "mean"))
           .reindex(tier_order))
    lines.append(g.round(3).to_markdown())
    lines.append("")

    # Mann-Whitney-style comparison: smaller+mid vs elite on MV growth.
    from scipy.stats import mannwhitneyu
    small = df.loc[df.nation_tier.isin(["smaller", "mid"]), "mv_growth_pct"].dropna()
    elite = df.loc[df.nation_tier == "elite", "mv_growth_pct"].dropna()
    if len(small) > 3 and len(elite) > 3:
        u, p = mannwhitneyu(small, elite, alternative="greater")
        lines.append(f"*Mann–Whitney U test (smaller/mid MV growth > elite):* "
                     f"U={u:.0f}, p={p:.3f}, n_small={len(small)}, n_elite={len(elite)}\n")

    # Plot
    fig, ax = plt.subplots(figsize=(6, 4))
    g["success_rate"].plot(kind="bar", ax=ax, color=["#4C72B0", "#55A868", "#C44E52"])
    ax.set_ylabel("Showcase-success rate")
    ax.set_title("Post-WC showcase success by nation tier")
    ax.set_ylim(0, 1)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "success_by_tier.png", dpi=120)
    plt.close(fig)


def section_drivers(df: pd.DataFrame, lines: list[str]) -> M.TrainedModels:
    lines.append("## 2. Driving factors\n")
    models = M.train(df)
    lines.append("### Cross-validated performance (honest, small-sample)\n")
    lines.append("```")
    for name, m in models.cv_metrics.items():
        lines.append(f"{name:7s}  acc={m['accuracy']:.2f}  roc_auc={m.get('roc_auc', float('nan')):.2f}"
                     f"  base_rate={m['base_rate']:.2f}  n={m['n']}")
    lines.append("```\n")

    lines.append("### Logistic-regression coefficients (standardized; sign = direction)\n")
    lines.append(models.logit_coefs.round(3).to_markdown(index=False))
    lines.append("")
    lines.append("### Random-forest permutation importance (ROC-AUC drop)\n")
    lines.append(models.perm_importance.round(4).to_markdown(index=False))
    lines.append("")

    # Plot permutation importance
    pi = models.perm_importance.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(pi["feature"], pi["perm_importance"], xerr=pi["perm_std"], color="#4C72B0")
    ax.set_xlabel("Permutation importance (mean ROC-AUC drop)")
    ax.set_title("Driving factors for goalkeeper showcase success")
    plt.tight_layout()
    fig.savefig(FIG_DIR / "feature_importance.png", dpi=120)
    plt.close(fig)
    return models


def section_sensitivity(df: pd.DataFrame, lines: list[str]) -> None:
    lines.append("## 3. Sensitivity analysis\n")

    # (a) Success-threshold sensitivity: vary the MV-growth cutoff.
    lines.append("### (a) Success definition — vary the market-value growth threshold\n")
    rows = []
    for thr in [25, 50, 75, 100, 150]:
        move_up = df.get("move_up", pd.Series(0, index=df.index)).fillna(0)
        succ = ((move_up == 1) | (df["mv_growth_pct"].fillna(0) >= thr)).astype(int)
        tmp = df.assign(_s=succ)
        by_tier = tmp.groupby("nation_tier")["_s"].mean()
        rows.append({
            "threshold_%": thr,
            "overall": succ.mean(),
            "smaller": by_tier.get("smaller", np.nan),
            "mid": by_tier.get("mid", np.nan),
            "elite": by_tier.get("elite", np.nan),
        })
    sens_thr = pd.DataFrame(rows)
    lines.append(sens_thr.round(3).to_markdown(index=False))
    lines.append("")

    # (b) Tier-cutoff sensitivity: vary the FIFA-rank boundary for "smaller".
    lines.append("### (b) Tier cutoff — vary the FIFA-rank boundary defining 'smaller'\n")
    rows = []
    for cut in [20, 25, 30, 35, 40]:
        is_small = df["fifa_rank_pre"] > cut
        rate_small = df.loc[is_small, "showcase_success"].mean()
        rate_big = df.loc[~is_small, "showcase_success"].mean()
        rows.append({
            "smaller_if_rank>": cut,
            "n_smaller": int(is_small.sum()),
            "success_smaller": rate_small,
            "success_rest": rate_big,
            "gap": rate_small - rate_big,
        })
    lines.append(pd.DataFrame(rows).round(3).to_markdown(index=False))
    lines.append("")

    # (c) Leave-one-tournament-out: is the feature ranking stable across editions?
    lines.append("### (c) Leave-one-tournament-out — stability of the top driver\n")
    rows = []
    for yr in sorted(df["wc_year"].unique()):
        sub = df[df["wc_year"] != yr]
        if sub["showcase_success"].nunique() < 2:
            continue
        m = M.train(sub)
        top = m.perm_importance.iloc[0]
        rows.append({"held_out_year": yr, "top_feature": top["feature"],
                     "importance": round(float(top["perm_importance"]), 4)})
    lines.append(pd.DataFrame(rows).to_markdown(index=False))
    lines.append("")

    # Plot threshold sensitivity
    fig, ax = plt.subplots(figsize=(7, 4))
    for col, c in [("smaller", "#C44E52"), ("mid", "#55A868"), ("elite", "#4C72B0")]:
        ax.plot(sens_thr["threshold_%"], sens_thr[col], marker="o", label=col, color=c)
    ax.set_xlabel("MV-growth success threshold (%)")
    ax.set_ylabel("Showcase-success rate")
    ax.set_title("Sensitivity of the smaller-nation effect to success definition")
    ax.legend()
    plt.tight_layout()
    fig.savefig(FIG_DIR / "sensitivity_threshold.png", dpi=120)
    plt.close(fig)


def main() -> None:
    df = load()
    lines = ["# Analysis Results — World Cup Goalkeeper Showcase Effect\n",
             f"Dataset: {len(df)} goalkeeper-tournament rows across "
             f"{df['wc_year'].nunique()} World Cups ({df['wc_year'].min()}–{df['wc_year'].max()}).\n"]
    section_descriptive(df, lines)
    section_drivers(df, lines)
    section_sensitivity(df, lines)
    (ROOT / "analysis" / "ANALYSIS_RESULTS.md").write_text("\n".join(lines))
    print("Wrote analysis/ANALYSIS_RESULTS.md and figures to analysis/figures/")


if __name__ == "__main__":
    main()
