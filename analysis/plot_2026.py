"""Charts for the live 2026 World Cup goalkeeper tracker.

Run from repo root:  python analysis/plot_2026.py

Reads data/goalkeepers_2026.csv (refreshed 2026-07-04) and writes:
  * analysis/figures/wc2026_saves_leaderboard.png  — saves by keeper, coloured by nation tier
  * analysis/figures/wc2026_tier_summary.png       — total saves & clean sheets by tier

The thesis of the whole project is that a World Cup is a *showcase* that lifts
keepers from smaller nations. These live charts show it happening in real time:
the saves leaderboard is topped by keepers from the smallest footballing nations.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from features import assign_nation_tier  # noqa: E402

FIG_DIR = ROOT / "analysis" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

TIER_COLOR = {"elite": "#0072B2", "mid": "#E69F00", "smaller": "#009E73"}
TIER_ORDER = ["elite", "mid", "smaller"]
AS_OF = "as of 2026-07-04"

plt.rcParams.update({
    "figure.autolayout": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
})


def load() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "goalkeepers_2026.csv")
    # Tier is stored per keeper but recompute from FIFA rank to be safe/consistent.
    df["tier"] = df["fifa_rank_pre"].apply(assign_nation_tier)
    return df


def saves_leaderboard(df: pd.DataFrame, top: int = 16) -> None:
    d = df.sort_values("saves", ascending=False).head(top).iloc[::-1]
    labels = [f"{p} · {n}" for p, n in zip(d["player"], d["nation"])]
    colors = [TIER_COLOR[t] for t in d["tier"]]

    fig, ax = plt.subplots(figsize=(9, 7.5))
    ax.barh(labels, d["saves"], color=colors)
    ax.bar_label(ax.containers[0], padding=3, fontsize=9)
    ax.set_xlabel("Total saves at WC 2026")
    ax.set_title(f"WC 2026 goalkeeper saves leaderboard\n({AS_OF})")
    ax.margins(x=0.10)

    legend = [Patch(facecolor=TIER_COLOR[t], label=f"{t} nation") for t in TIER_ORDER]
    ax.legend(handles=legend, frameon=False, loc="lower right", title="FIFA-rank tier")
    fig.savefig(FIG_DIR / "wc2026_saves_leaderboard.png", dpi=120)
    plt.close(fig)


def tier_summary(df: pd.DataFrame) -> None:
    g = (df.groupby("tier")
           .agg(keepers=("player", "size"),
                total_saves=("saves", "sum"),
                clean_sheets=("clean_sheets", "sum"))
           .reindex(TIER_ORDER))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.4))
    for ax, col, ylab in [(ax1, "total_saves", "Total saves"),
                          (ax2, "clean_sheets", "Total clean sheets")]:
        ax.bar(g.index, g[col], color=[TIER_COLOR[t] for t in g.index], width=0.6)
        ax.bar_label(ax.containers[0], padding=3, fontsize=10)
        ax.set_ylabel(ylab)
        ax.set_xticks(range(len(g.index)))
        ax.set_xticklabels([f"{t}\n(n={int(g.loc[t, 'keepers'])})" for t in g.index])
        ax.margins(y=0.15)
    fig.suptitle(f"Saves & clean sheets by nation tier — WC 2026 ({AS_OF})",
                 fontsize=13, fontweight="bold")
    fig.savefig(FIG_DIR / "wc2026_tier_summary.png", dpi=120)
    plt.close(fig)


def main() -> None:
    df = load()
    saves_leaderboard(df)
    tier_summary(df)
    print("Wrote WC 2026 figures to analysis/figures/")


if __name__ == "__main__":
    main()
