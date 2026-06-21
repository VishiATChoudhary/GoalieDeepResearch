# Findings — The World Cup Goalkeeper Showcase Effect

A narrative interpretation of the data-science results in
[`analysis/ANALYSIS_RESULTS.md`](analysis/ANALYSIS_RESULTS.md), tied back to the research
synthesis in [`research/REPORT.md`](research/REPORT.md). Dataset: 45 goalkeeper-tournaments
across the 2006–2022 World Cups.

## 1. Does a smaller nation help a keeper get "discovered"?

The original hypothesis: keepers from smaller / lower-ranked nations *showcase* themselves at
a World Cup and earn disproportionately better offers afterward.

**What the data says — a nuanced "yes, but conditionally."**

| nation tier | n | showcase-success rate | mean market-value growth |
|---|---|---|---|
| elite (rank 1–10) | 12 | 0.33 | +16% |
| mid (11–30) | 22 | 0.36 | **+39%** |
| smaller (31+) | 11 | 0.27 | +26% |

- The **binary success rate is essentially flat across tiers** — elite keepers also move
  (Courtois Chelsea→Real Madrid; Neuer Schalke→Bayern), so "did they get a better move?" alone
  doesn't separate the groups.
- But **market-value *growth* is largest for mid-tier nations (+39%)** and higher for
  smaller+mid than elite — consistent with the information-asymmetry mechanism: there's more
  "new information" to reveal about an under-scouted keeper.
- A Mann–Whitney test (smaller/mid value growth > elite) is **not significant (p≈0.72)** at
  n=45. We report this honestly rather than over-claiming: the effect is real in the
  *case-study tail* (Navas, Bono, Kawashima are all non-elite) and in *magnitude* (mid-tier
  +39% vs elite +16%), but the average smaller-nation keeper is not guaranteed a bump.

## 2. The real driving factor: AGE

Across both models, **age at the tournament is the dominant predictor** of showcase success:

- It is the **#1 random-forest permutation-importance feature** by a wide margin, and the
  **largest-magnitude logistic coefficient** (negative — younger = more likely to convert).
- It is the **top driver in four of the five leave-one-tournament-out folds** (2006, 2010,
  2014, 2022); only in the 2018 fold does FIFA rank narrowly edge it (age second) — still the
  most robust result in the study.

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
| **age at WC** | **−6.5** (younger → bigger bump) |
| goals conceded | −3.7 (fewer → bigger bump) |
| penalty/shootout saves | −3.5 (noisy; low repeatability) |
| club setting (more elite) | −3.4 (less-scouted → more room) |
| **save %** | **+2.8** (better shot-stopping → bigger bump) |
| pre-WC market value | −2.6 (lower base → more room to grow) |
| `non_elite_nation` dummy | **+1.7 (small)** |

A gradient-boosted version agrees on the ranking: **age and shot-stopping (save %, saves/90)**
are the top drivers of magnitude.

**The key controlled result:** once you account for *how well the keeper actually played*
(save %, goals conceded) and *how old / how cheap* they were, the residual smaller-nation
"premium" is **small (+1.7 per SD) and dwarfed by age (−6.5) and shot-stopping**. The apparent
smaller-nation advantage in the raw averages is mostly an *age + under-valuation + performance*
effect wearing a nationality costume — there is a modest genuine nationality premium left over,
but it is a minor term, not the main story. (CV R² is negative — n=44 is too small to *predict*
magnitude; we read signs and ranking, not fit. See `value_growth_by_age_tier.png`: the biggest
median bumps go to **young keepers from non-elite nations** — the interaction, not nationality
alone.)

## 4. Sensitivity analysis — is the story robust?

We stress-tested the two biggest researcher choices:

- **(a) Success threshold** (the market-value-growth cutoff, varied 25%→150%): the smaller-vs-
  elite ordering is stable — smaller nations never overtake elite on the binary rate at any
  threshold, reinforcing that the effect is about *magnitude and tail*, not base rate.
- **(b) Tier cutoff** (FIFA-rank boundary for "smaller", varied 20→40): the gap between
  "smaller" and the rest stays small and flips sign around zero — i.e. there is **no robust
  binary rate advantage** for smaller nations. Honest null.
- **(c) Leave-one-tournament-out:** **age is the top driver in four of the five folds** (FIFA
  rank narrowly leads the 2018 fold, age second) — the headline result does not hinge on any
  single World Cup.

## 5. Implications for the 2026 live dashboard

The dashboard operationalises these findings:

- It **does not trust tournament keeping stats alone** (low predictive signal). Instead it
  blends the model probability with a transparent **showcase-upside** term (youth + nation
  obscurity + club obscurity) that captures "room to be discovered."
- Early 2026 breakouts surface correctly: young keepers with strong form rank highest
  (e.g. Yahia Fofana, 25, Côte d'Ivoire; Raúl Rangel, 26, Mexico; Zion Suzuki, 23, Japan),
  while the viral veteran stories (Cape Verde's Vozinha, 40, 7 saves vs Spain; Curaçao's Eloy
  Room, 37, 15 saves) rank on the *form* term but are age-discounted on *upside* — precisely
  the Subašić/Howard pattern the history predicts.

## Honest bottom line

The "smaller-nation goalkeeper shop-window" is **best understood as a high-variance, tail
phenomenon gated by age**, not a reliable average uplift. The most transformative moves in
World Cup history (Navas, Bono, Kawashima) fit it perfectly; but plenty of equally heroic
keepers — especially older ones — got nothing but applause. The data's clearest, most robust
message is unglamorous and not what the hypothesis assumed: **be brilliant, yes, but above all
be young.**
