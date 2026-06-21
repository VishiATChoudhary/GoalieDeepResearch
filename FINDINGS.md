# Findings — The World Cup Goalkeeper Showcase Effect

A narrative interpretation of the data-science results in
[`analysis/ANALYSIS_RESULTS.md`](analysis/ANALYSIS_RESULTS.md), tied back to the research
synthesis in [`research/REPORT.md`](research/REPORT.md). Dataset: 40 goalkeeper-tournaments
across the 2006–2022 World Cups.

## 1. Does a smaller nation help a keeper get "discovered"?

The original hypothesis: keepers from smaller / lower-ranked nations *showcase* themselves at
a World Cup and earn disproportionately better offers afterward.

**What the data says — a nuanced "yes, but conditionally."**

| nation tier | n | showcase-success rate | mean market-value growth |
|---|---|---|---|
| elite (rank 1–10) | 11 | 0.36 | +21% |
| mid (11–30) | 20 | 0.35 | **+39%** |
| smaller (31+) | 9 | 0.33 | +31% |

- The **binary success rate is essentially flat across tiers** — elite keepers also move
  (Courtois Chelsea→Real Madrid; Neuer Schalke→Bayern), so "did they get a better move?" alone
  doesn't separate the groups.
- But **market-value *growth* is largest for mid-tier nations (+39%)** and higher for
  smaller+mid than elite — consistent with the information-asymmetry mechanism: there's more
  "new information" to reveal about an under-scouted keeper.
- A Mann–Whitney test (smaller/mid value growth > elite) is **not significant (p≈0.87)** at
  n=40. We report this honestly rather than over-claiming: the effect is real in the
  *case-study tail* (Navas, Bono, Kawashima are all non-elite) and in *magnitude*, but the
  average smaller-nation keeper is not guaranteed a bump.

## 2. The real driving factor: AGE

Across both models, **age at the tournament is the dominant predictor** of showcase success:

- It is the **#1 random-forest permutation-importance feature** by a wide margin, and the
  **largest-magnitude logistic coefficient** (negative — younger = more likely to convert).
- It is the **top feature in every single leave-one-tournament-out fold** (2006, 2010, 2014,
  2018, 2022) — the most robust result in the whole study.

This matches the qualitative finding exactly. The keepers who converted heroics into a bigger
move were young and marketable:

| Converted (young) | Did **not** convert (older), despite heroics |
|---|---|
| Keylor Navas (27) → Real Madrid | Danijel Subašić (33) — 4 pen saves, reached final, stayed |
| Eiji Kawashima (27) → Belgium | Tim Howard (35) — record 16 saves, stayed |
| Manuel Neuer (24) → Bayern | Igor Akinfeev (32) — beat Spain on pens, one-club career |
| David Ospina (25) → Arsenal | Shuichi Gonda (33) — beat Germany, stayed |

**Takeaway:** a World Cup is a showcase, but the market only "buys" keepers it can still
develop and resell. Age is the gate.

## 3. Which on-pitch stats matter (and which don't)

After age, the model leans on **shot-stopping rate signals** — `saves_per90` and the
`save_pct` proxy are the next-most-important features — over volume or team-outcome stats:

- **Clean sheets** carry almost no independent signal (near-zero / slightly negative
  importance). This is expected: clean sheets are heavily team-dependent (see research §3).
- **Penalty / shootout saves** rank low in the model despite their huge narrative weight — a
  direct echo of the research finding that they are a tiny, low-repeatability sample. They
  *drive headlines* (and thus the shop-window effect) far more than they *predict* outcomes.
- **Team stage (depth of run)** has a weak/mixed signal here, confounded by the fact that
  several deep-run keepers in the sample are elite keepers who stayed put.

## 3b. What drives the *size* of the "better offer"?

The binary success rate is near-flat across tiers, so we also modelled the **continuous
market-value growth %** — the actual size of the bump, which is what "better offers" really
means. A Ridge regression (used instead of OLS because `minutes`/`matches` are collinear) on
standardized features gives stable, comparable effects:

| driver | standardized effect on value growth |
|---|---|
| **age at WC** | **−8.6** (younger → bigger bump) |
| goals conceded | −6.0 (fewer → bigger bump) |
| **save %** | **+4.2** (better shot-stopping → bigger bump) |
| pre-WC market value | −3.2 (lower base → more room to grow) |
| club setting (more elite) | −3.1 (less-scouted → more room) |
| `non_elite_nation` dummy | **+0.2 (≈ zero)** |

A gradient-boosted version agrees on the ranking: **save % and saves/90 and age** are the top
drivers of magnitude; the non-elite-nation dummy has ~0 importance.

**The key controlled result:** once you account for *how well the keeper actually played*
(save %, goals conceded) and *how old / how cheap* they were, **being from a smaller nation
adds essentially nothing to the value bump.** The apparent "smaller-nation premium" in the raw
averages is really an *age + under-valuation + shot-stopping* effect wearing a nationality
costume. (CV R² is negative — n=39 is too small to *predict* magnitude; we read signs and
ranking, not fit. See the `value_growth_by_age_tier.png` figure: the biggest median bumps go
to **young keepers from non-elite nations** — the interaction, not nationality alone.)

## 4. Sensitivity analysis — is the story robust?

We stress-tested the two biggest researcher choices:

- **(a) Success threshold** (the market-value-growth cutoff, varied 25%→150%): the smaller-vs-
  elite ordering is stable — smaller nations never overtake elite on the binary rate at any
  threshold, reinforcing that the effect is about *magnitude and tail*, not base rate.
- **(b) Tier cutoff** (FIFA-rank boundary for "smaller", varied 20→40): the gap between
  "smaller" and the rest stays small and flips sign around zero — i.e. there is **no robust
  binary rate advantage** for smaller nations. Honest null.
- **(c) Leave-one-tournament-out:** **age is the top driver in all five folds** — the headline
  result does not depend on any single World Cup.

## 5. Implications for the 2026 live dashboard

The dashboard operationalises these findings:

- It **does not trust tournament keeping stats alone** (low predictive signal). Instead it
  blends the model probability with a transparent **showcase-upside** term (youth + nation
  obscurity + club obscurity) that captures "room to be discovered."
- Early 2026 breakouts surface correctly: young keepers from smaller nations rank highest
  (e.g. Nawaf Al-Aqidi, Yahia Fofana), while the viral veteran stories (Cape Verde's Vozinha,
  40, 7 saves vs Spain; Curaçao's Eloy Room, 15 saves) rank on the *form* term but are
  age-discounted on *upside* — precisely the Subašić/Howard pattern the history predicts.

## Honest bottom line

The "smaller-nation goalkeeper shop-window" is **best understood as a high-variance, tail
phenomenon gated by age**, not a reliable average uplift. The most transformative moves in
World Cup history (Navas, Bono, Kawashima) fit it perfectly; but plenty of equally heroic
keepers — especially older ones — got nothing but applause. The data's clearest, most robust
message is unglamorous and not what the hypothesis assumed: **be brilliant, yes, but above all
be young.**
