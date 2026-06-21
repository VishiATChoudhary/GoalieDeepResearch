"""Feature engineering for the World Cup goalkeeper showcase study.

Pure, dependency-light transforms over the raw goalkeeper table defined in
`data/DATA_DICTIONARY.md`. Kept separate from modelling so the same logic is
reused by the analysis scripts and the live 2026 dashboard.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Ordinal mapping for how far a team advanced.
STAGE_RANK = {
    "group": 1,
    "r16": 2,
    "qf": 3,
    "sf": 4,
    "final": 5,
    "winner": 6,
}

# Club setting strength, used as a control: a keeper already at a top-5-league
# club has less "room" to be discovered than one at a small domestic club.
CLUB_TIER_RANK = {
    "non_euro": 0,
    "domestic_small": 1,
    "other_euro": 2,
    "top5": 3,
}


def assign_nation_tier(fifa_rank: float) -> str:
    """Bucket a nation by its pre-tournament FIFA ranking."""
    if pd.isna(fifa_rank):
        return "unknown"
    if fifa_rank <= 10:
        return "elite"
    if fifa_rank <= 30:
        return "mid"
    return "smaller"


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add tiering, stage ordinals, per-90 rates, and the showcase target.

    The function is idempotent and tolerant of missing optional columns so it
    can run on both the historical table and the in-progress 2026 table.
    """
    df = df.copy()

    # --- Nation tier (from FIFA rank) ---
    if "nation_tier" not in df.columns or df["nation_tier"].isna().any():
        df["nation_tier"] = df["fifa_rank_pre"].apply(assign_nation_tier)

    # --- Stage ordinal ---
    if "team_stage" in df.columns:
        df["team_stage_rank"] = df["team_stage"].map(STAGE_RANK)

    # --- Club setting ordinal ---
    if "club_pre_tier" in df.columns:
        df["club_pre_tier_rank"] = df["club_pre_tier"].map(CLUB_TIER_RANK)

    # --- Per-90 rate stats (robust to zero minutes) ---
    mins = df.get("minutes")
    if mins is not None:
        nineties = (mins / 90.0).replace(0, np.nan)
        if "saves" in df.columns:
            df["saves_per90"] = df["saves"] / nineties
        if "goals_conceded" in df.columns:
            df["ga_per90"] = df["goals_conceded"] / nineties

    # --- Save% proxy ---
    # True save% needs shots-on-target faced, which is not available for older
    # World Cups. We approximate it as saves / (saves + goals conceded), i.e.
    # treating conceded goals as on-target shots that beat the keeper. Where an
    # official save_pct was supplied we keep it; otherwise we fill the proxy.
    if {"saves", "goals_conceded"}.issubset(df.columns):
        denom = (df["saves"] + df["goals_conceded"]).replace(0, np.nan)
        proxy = 100.0 * df["saves"] / denom
        if "save_pct" in df.columns:
            df["save_pct"] = df["save_pct"].fillna(proxy)
        else:
            df["save_pct"] = proxy

    # --- Market-value deltas / target (historical table only) ---
    if {"mv_pre_eur_m", "mv_post_eur_m"}.issubset(df.columns):
        df["mv_delta_eur_m"] = df["mv_post_eur_m"] - df["mv_pre_eur_m"]
        df["mv_growth_pct"] = np.where(
            df["mv_pre_eur_m"] > 0,
            100.0 * df["mv_delta_eur_m"] / df["mv_pre_eur_m"],
            np.nan,
        )
        move_up = df.get("move_up", pd.Series(0, index=df.index)).fillna(0)
        growth = df["mv_growth_pct"].fillna(0)
        df["showcase_success"] = ((move_up == 1) | (growth >= 50)).astype(int)

    return df


# Features used by the model to explain / predict showcase success.
# Deliberately excludes post-WC market-value columns (which would leak the target).
MODEL_FEATURES = [
    "age_at_wc",
    "fifa_rank_pre",
    "team_stage_rank",
    "matches",
    "minutes",
    "goals_conceded",
    "clean_sheets",
    "saves",
    "save_pct",
    "psxg_minus_ga",
    "pen_saves",
    "saves_per90",
    "ga_per90",
    "club_pre_tier_rank",
    "mv_pre_eur_m",
]


def build_feature_matrix(df: pd.DataFrame, max_missing: float = 0.6):
    """Return (X, feature_names) using available MODEL_FEATURES columns.

    Columns that are more than `max_missing` fraction NaN are dropped, so we
    never feed an (almost) empty feature to the imputer/model. This is how we
    honestly handle metrics like PSxG-GA that are not reliably published for
    World Cups — they are simply excluded rather than fabricated.
    """
    feats = []
    for c in MODEL_FEATURES:
        if c in df.columns and df[c].notna().mean() >= (1 - max_missing):
            feats.append(c)
    X = df[feats].copy()
    return X, feats
