"""Live 2026 World Cup goalkeeper 'breakout likelihood' dashboard.

Run:  streamlit run dashboard/app.py

Trains the showcase-success model on the historical 2006-2022 dataset, then
scores the current (2026) goalkeeper pool — emphasising keepers from smaller
nations who have the most to gain from a strong tournament. Update
`data/goalkeepers_2026.csv` as the tournament progresses and the dashboard
re-ranks live (Streamlit caches by file contents).

The score blends a data model with a transparent 'showcase-upside' component,
because (per the research) tournament keeping has low predictive signal on its
own; the upside term captures who has the most room to be 'discovered'.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from features import add_derived_columns, assign_nation_tier  # noqa: E402
import model as M  # noqa: E402

st.set_page_config(page_title="WC2026 Goalie Breakout Tracker", layout="wide")


@st.cache_data
def load_historical() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "goalkeepers_worldcups.csv")
    return add_derived_columns(df)


@st.cache_data
def load_2026() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "goalkeepers_2026.csv")
    return add_derived_columns(df)


@st.cache_resource
def get_models(_hist: pd.DataFrame) -> M.TrainedModels:
    return M.train(_hist)


def showcase_upside(row: pd.Series) -> float:
    """Transparent 0-1 'room to be discovered' term.

    Higher when the keeper is (a) young, (b) from a lower-ranked nation, and
    (c) at a less-scouted club — the conditions under which a strong World Cup
    moves the market most (information-asymmetry mechanism, see research/REPORT.md).
    """
    # Youth: 1.0 at age 22, decaying to ~0 by age 38.
    age = row.get("age_at_wc", 30)
    youth = max(0.0, min(1.0, (38 - age) / 16.0))
    # Obscurity: higher FIFA rank number = more obscure nation.
    rank = row.get("fifa_rank_pre", 30)
    obscurity = max(0.0, min(1.0, (rank - 8) / 75.0))
    # Club setting: non-top-5-league keepers are less scouted.
    tier_rank = row.get("club_pre_tier_rank", 2)
    club_obscurity = {0: 1.0, 1: 0.85, 2: 0.5, 3: 0.15}.get(int(tier_rank), 0.5)
    return round(0.45 * youth + 0.35 * obscurity + 0.20 * club_obscurity, 3)


def main() -> None:
    hist = load_historical()
    pool = load_2026()
    models = get_models(hist)

    st.title("🧤 World Cup 2026 — Goalkeeper Breakout Tracker")
    st.caption(
        "Which goalkeepers are likeliest to *perform well and earn a better move* — "
        "with a focus on keepers from smaller nations using the tournament as a shop window. "
        "Model trained on 2006–2022 keeper-tournaments. See `research/REPORT.md` for methodology."
    )

    # --- Score the pool ---
    pool = pool.copy()
    pool["nation_tier"] = pool["fifa_rank_pre"].apply(assign_nation_tier)
    pool["model_prob"] = M.score_keepers(models, pool)
    pool["upside"] = pool.apply(showcase_upside, axis=1)
    # Current form term from early-tournament save volume (per-90), normalised.
    sp90 = pool.get("saves_per90", pd.Series(0, index=pool.index)).fillna(0)
    pool["form"] = (sp90 / sp90.max()).fillna(0) if sp90.max() > 0 else 0.0
    # Composite breakout score (weights documented in the sidebar).
    w_model, w_upside, w_form = 0.45, 0.35, 0.20
    pool["breakout_score"] = (
        w_model * pool["model_prob"] + w_upside * pool["upside"] + w_form * pool["form"]
    ).round(3)

    # --- Sidebar controls ---
    with st.sidebar:
        st.header("Filters")
        tiers = st.multiselect("Nation tier", ["smaller", "mid", "elite"],
                               default=["smaller", "mid", "elite"])
        max_age = st.slider("Max age", 22, 42, 42)
        only_small = st.checkbox("Smaller/mid nations only (the thesis)", value=False)
        st.markdown("---")
        st.markdown(
            f"**Score weights**\n\n"
            f"- Model probability: `{w_model}`\n"
            f"- Showcase upside: `{w_upside}`\n"
            f"- Early-tournament form: `{w_form}`"
        )
        st.caption("Edit `data/goalkeepers_2026.csv` to refresh as games are played.")

    view = pool[pool["nation_tier"].isin(tiers) & (pool["age_at_wc"] <= max_age)]
    if only_small:
        view = view[view["nation_tier"].isin(["smaller", "mid"])]
    view = view.sort_values("breakout_score", ascending=False)

    # --- Live current-tournament stats (the 2026 World Cup so far) ---
    st.subheader("📡 Live 2026 group-stage stats (as of 2026-06-21)")
    st.caption("Current-tournament goalkeeper performance. See `data/WC2026_current_stats.md` "
               "for per-keeper sourcing. `approx` = some save totals inferred from match context.")
    live_cols = ["player", "nation", "nation_tier", "matches", "saves",
                 "goals_conceded", "clean_sheets", "sofascore_rating",
                 "goals_prevented", "stats_conf"]
    live = view[[c for c in live_cols if c in view.columns]].sort_values(
        "saves", ascending=False)
    st.dataframe(
        live.rename(columns={"goals_conceded": "GC", "clean_sheets": "CS",
                             "sofascore_rating": "Sofascore", "matches": "M",
                             "goals_prevented": "goals prev.", "stats_conf": "conf"}),
        use_container_width=True, hide_index=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Most saves so far", f"{int(live['saves'].max())}",
              live.iloc[0]["player"])
    cs_leader = view.sort_values(["clean_sheets", "saves"], ascending=False).iloc[0]
    c2.metric("Most clean sheets", f"{int(view['clean_sheets'].max())}",
              cs_leader["player"])
    rate_leader = view.sort_values("sofascore_rating", ascending=False).iloc[0]
    c3.metric("Top Sofascore rating", f"{rate_leader['sofascore_rating']:.1f}",
              rate_leader["player"])

    # --- Top-line ranking ---
    st.subheader("🔮 Breakout likelihood ranking")
    show_cols = ["player", "nation", "nation_tier", "age_at_wc", "fifa_rank_pre",
                 "club_pre", "mv_pre_eur_m", "saves", "clean_sheets",
                 "model_prob", "upside", "form", "breakout_score"]
    st.dataframe(
        view[show_cols].rename(columns={
            "age_at_wc": "age", "fifa_rank_pre": "FIFA rank",
            "mv_pre_eur_m": "MV (€M)", "model_prob": "model p",
            "breakout_score": "BREAKOUT"}),
        use_container_width=True, hide_index=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(view.head(12), x="breakout_score", y="player",
                     color="nation_tier", orientation="h",
                     title="Top 12 breakout candidates",
                     labels={"breakout_score": "Breakout score", "player": ""})
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=450)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.scatter(view, x="age_at_wc", y="breakout_score",
                          size="upside", color="nation_tier", hover_name="player",
                          title="Younger + smaller-nation keepers score higher",
                          labels={"age_at_wc": "Age", "breakout_score": "Breakout score"})
        fig2.update_layout(height=450)
        st.plotly_chart(fig2, use_container_width=True)

    # --- Spotlight ---
    st.subheader("📌 Smaller-nation spotlight")
    spot = view[view["nation_tier"].isin(["smaller", "mid"])].head(3)
    cols = st.columns(max(1, len(spot)))
    for c, (_, r) in zip(cols, spot.iterrows()):
        c.metric(f"{r['player']} ({r['nation']})", f"{r['breakout_score']:.2f}",
                 help=str(r.get("storyline", "")))
        c.caption(r.get("storyline", ""))

    # --- Historical context ---
    with st.expander("📊 Historical model context (2006–2022)"):
        st.markdown("**Showcase-success rate by nation tier**")
        g = (hist.groupby("nation_tier")
                 .agg(n=("player", "size"), success_rate=("showcase_success", "mean"),
                      mean_mv_growth=("mv_growth_pct", "mean"))
                 .reindex(["elite", "mid", "smaller"]).round(3))
        st.dataframe(g)
        st.markdown("**Driving factors (random-forest permutation importance)**")
        st.dataframe(models.perm_importance.round(4), hide_index=True)
        st.caption(
            f"Honest small-sample performance — "
            f"logit ROC-AUC={models.cv_metrics.get('logit', {}).get('roc_auc', float('nan')):.2f}, "
            f"forest ROC-AUC={models.cv_metrics.get('forest', {}).get('roc_auc', float('nan')):.2f}, "
            f"n={len(hist)}. Age is the dominant driver; tournament keeping has low predictive signal "
            f"(see research/REPORT.md §3), which is why the score adds a transparent upside term."
        )


if __name__ == "__main__":
    main()
