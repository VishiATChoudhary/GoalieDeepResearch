# GoalieDeepResearch 🧤

**How goalkeepers from smaller / lower-ranked footballing nations use the FIFA World Cup as a
shop window to earn better club moves — researched, quantified, and tracked live for 2026.**

This repo combines (1) a cited deep-research synthesis, (2) a curated dataset of goalkeeper
performances and transfer outcomes across the last five World Cups (2006–2022), (3) a
data-science analysis with feature-importance and sensitivity testing, and (4) a live 2026
World Cup dashboard ranking which keepers are likeliest to break out.

## TL;DR findings

1. **Age is the single dominant driver** of whether a World Cup performance converts into a
   better move — more than any on-pitch stat. It is the top feature in the random forest and
   tops four of five leave-one-tournament-out folds. Equally heroic *older* keepers
   (Subašić 33, Howard 35, Akinfeev 32, Gonda 33) got reputation but **no move**; the
   converters were young/marketable (Navas 27, Kawashima 27, Neuer 24, Ospina 25).
2. **The smaller-nation "shop window" is real but conditional — and mostly a proxy.** The
   mechanism (information asymmetry — an under-scouted keeper's value moves more on new
   information) is strongly supported by case studies (Keylor Navas → Real Madrid; Bono →
   Al-Hilal ~€21m; Kawashima → Belgium). But in our n=45 sample the *binary* success rate is
   similar across tiers (~27–36%), the smaller-vs-elite value-growth gap is **not** significant
   (Mann–Whitney p≈0.72), and in a Ridge model of value-growth *magnitude* the controlled
   `non_elite_nation` effect is **small (+1.7 per SD), dwarfed by age, base value, and actual
   shot-stopping (save %, goals conceded)**. In other words the "smaller-nation premium" is
   mostly an *age + under-valuation + performance* effect wearing a nationality costume, with a
   minor genuine premium left over; the real bumps go to **young, cheap, well-performing**
   keepers — who happen, in the tail, to be from non-elite nations.
3. **Tournament keeping has low predictive signal** (model ROC-AUC ≈ 0.55). This is itself a
   documented finding (shot-stopping barely repeats season-to-season), and it is exactly the
   market inefficiency the shop-window effect exploits — markets overweight a few vivid saves.

See [`research/REPORT.md`](research/REPORT.md) for the full cited synthesis and
[`analysis/ANALYSIS_RESULTS.md`](analysis/ANALYSIS_RESULTS.md) for the generated numbers.

## Repository layout

```
research/REPORT.md            Cited deep-research synthesis (mechanism, metrics, case studies)
data/
  DATA_DICTIONARY.md          Schema + nation-tiering rules + sourcing notes
  goalkeepers_worldcups.csv   45 keeper-tournaments, 2006–2022 (built by src/build_dataset.py)
  goalkeepers_2026.csv        Live 2026 keeper pool with current group-stage stats
  WC2026_current_stats.md     Live 2026 goalkeeper stats table + per-keeper sourcing
  fifa_rankings.csv           Pre-tournament nation ranks used for tiering
  processed/
    statsbomb_gk_metrics.csv  REAL shot-based GK metrics (2018 & 2022) from StatsBomb open data
src/
  features.py                 Tiering, derived columns, save% proxy, feature matrix
  model.py                    Logistic + random-forest models, permutation importance, scoring
  ingest_statsbomb.py         Downloads StatsBomb open data → real saves/save%/xG-prevented (2018/22)
  ingest_fbref.py             Documented FBref scaffold (403-blocked here; for when network allows)
  build_dataset.py            Builds the CSVs; overlays real StatsBomb metrics onto 2018/22 rows
analysis/
  run_analysis.py             End-to-end analysis (descriptive, drivers, sensitivity)
  ANALYSIS_RESULTS.md         Generated results
  figures/                    Generated charts
dashboard/
  app.py                      Streamlit live 2026 breakout tracker
FINDINGS.md                   Narrative write-up of the data-science results
```

## Quickstart

```bash
pip install -r requirements.txt

# 1. (Re)build the datasets from the research synthesis
python src/build_dataset.py

# 2. Run the analysis (writes analysis/ANALYSIS_RESULTS.md + figures/)
python analysis/run_analysis.py

# 3. Launch the live 2026 dashboard
streamlit run dashboard/app.py
```

## Method in brief

- **Target — `showcase_success`:** 1 if a keeper earned a clear step-up move *or* a ≥50%
  market-value jump within ~18 months of the tournament. (Both the threshold and the tier
  cutoffs are stress-tested in the sensitivity analysis — the qualitative story is stable.)
- **Nation tiers** from pre-tournament FIFA rank: `elite` (1–10), `mid` (11–30),
  `smaller` (31+).
- **Models:** an interpretable logistic regression (coefficient signs) plus a random forest
  with permutation importance, ensembled for the live score. Cross-validated honestly given
  the small sample.
- **Live score (dashboard):** blends the model probability with a transparent *showcase-upside*
  term (youth + nation obscurity + club obscurity = "room to be discovered") and an
  early-tournament *form* term, because the model alone has low signal.

## Data honesty & limitations

**Real-data layer.** The 2018 and 2022 keeper rows are enriched with *measured* shot-based
metrics (saves, save%, goals conceded, shootout saves, and a real `xg_prevented`) computed
from **StatsBomb open event data** via `src/ingest_statsbomb.py` — these rows are flagged
`data_confidence = "high (StatsBomb)"`. FBref's PSxG pages (the ideal metric) are 403-blocked
in this environment, so `src/ingest_fbref.py` is provided as a ready-to-run scaffold for where
FBref is reachable. The **2026 rows carry live group-stage stats** (see
`data/WC2026_current_stats.md`).

The remaining figures (2006–2014 performance, all market values/transfers) are a
**curated, research-backed dataset**, not a scrape — Transfermarkt and most data aggregators
block automated fetching, so they come from a cross-checked research pass over
FIFA/Wikipedia/journalism (see every agent's sources in `research/REPORT.md`). Specifically:

- Match counts, clean sheets, goals conceded, team stage, penalty/shootout saves, and the
  headline transfer outcomes are well-sourced.
- Raw `saves` totals for 2006–2010 are **low-confidence estimates** (FIFA didn't publish
  per-keeper save tallies then) and are flagged `data_confidence=low`. `save_pct` is a
  proxy = saves/(saves+goals conceded), since shots-on-target aren't available historically.
- **PSxG-GA ("goals prevented")** — the best shot-stopping metric — is **not reliably
  published for World Cups**, so it is left `NaN` and the model drops it rather than
  fabricating values.
- Market values are approximate and used only for a coarse growth signal; the analysis is
  stress-tested against the value threshold.

n=45 is small; treat the modelling as *explanatory and ranking-oriented*, not predictive.
