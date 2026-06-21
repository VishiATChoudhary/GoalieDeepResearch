# The World Cup Goalkeeper Showcase Effect — Research Synthesis

*How goalkeepers from smaller / lower-ranked footballing nations use the FIFA World Cup
as a shop window to earn better club moves and higher valuations.*

This report synthesizes a multi-source, fact-checked research pass (Transfermarkt-derived
values, FBref/StatsBomb/Opta metric definitions, sports-economics literature, and reputable
journalism). It underpins the dataset and the data-science analysis in this repo. Source
links are listed per section. **A transparency note up front:** Transfermarkt and several
data aggregators return HTTP 403 to automated fetching, so exact dated market-value series
were drawn from search-result extracts and journalism. Figures used as load-bearing inputs
to the dataset are tagged in `data/goalkeepers_worldcups.csv` `notes` and the weakest are
flagged `approx`.

---

## 1. The thesis, in one paragraph

A World Cup is a synchronized, globally scouted stage that compresses years of scouting into
a month. For a goalkeeper already at a top-5-league club, the market's prior is "tight" — a
good tournament adds little new information. For a keeper from a weak league/nation, scouts
rarely watch his domestic games, so the market's prior is "diffuse" and a few high-leverage
moments (a shootout, a clean sheet against a giant) deliver a large information update that
moves valuation and unlocks a transfer. Goalkeeping is unusually suited to this because (a) a
single save can define a reputation, and (b) the keeper market is thin and still priced on
crude signals (clean sheets, vivid moments), so it overreacts to tournament narratives.

---

## 2. Mechanism (why the effect is *disproportionate* for smaller nations)

1. **Shop-window / exposure shock.** A peer-reviewed study (Frontiers in Psychology, 2019,
   "Player Migration and Soccer Performance", 1994–2018, 243 countries) documents a
   "shop-window effect": players who shine while their national team does well are bought by
   higher-ranked leagues, with causality running *from* tournament performance *to*
   migration. It explicitly expects migration to "increase when players from countries with
   lower-quality domestic leagues are in the spotlight immediately after a World Cup."
2. **Signaling / information asymmetry (Spence).** Signals matter most where an information
   gap exists. An under-scouted keeper benefits far more from the same performance than a
   continuously-observed one. (Theory-driven; no paper cleanly isolates the
   "performance × prior obscurity" interaction — flagged as an evidence gap.)
3. **Recency / availability bias.** Clubs overweight vivid recent moments, *inflating* the
   premium beyond the rational information update.
4. **Position-specific leverage.** A keeper can flip his reputation with one save/shootout;
   the keeper market is thin, opaque, and priced on "clean-sheet counts, a relic of low-tech
   scouting" — so it overreacts to tournament signals.
5. **Survivorship / deep-run effect — with a caveat.** Visibility concentrates in knockout
   games against strong opponents; awards typically require reaching ≥ quarter-finals. But
   the "busiest keeper myth" matters: the keeper *perfectly protected for 85 minutes who then
   makes one impossible save* is rewarded more than the one facing 15 shots behind a leaky
   defense. So it is **deep run + a few decontextualized elite moments**, not raw shot
   volume, that drives the boost.

**Quantification:** No single canonical "World Cup premium %" exists in peer-reviewed work
(flagged). The best analogue — Bell, Brooks & Brooks (*Applied Economics*, 2024), 5,760
transfers — finds an ~40% fee premium and ~25% wage premium for English players driven by
*exposure/demand*, independent of ability: the same family of effect. Transfermarkt crowd
valuations also predict international results better than FIFA ranking/Elo (Peeters; Herm et
al., 2018), confirming values update on national-team performance.

*Contested:* one note suggests players from teams that "barely qualified" gained value but
less than those from dominant teams — i.e., the asymmetry is **conditioned on a deep run**,
not automatic for any weak-nation keeper.

Sources: [Frontiers 2019](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.00616/full) ·
[PMC mirror](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6440484/) ·
[Peeters/Herm 2018](https://www.sciencedirect.com/science/article/abs/pii/S0169207017300754) ·
[Bell, Brooks & Brooks 2024 (PDF)](https://centaur.reading.ac.uk/111320/1/Are%20English%20football%20players%20overvalued.pdf) ·
[bwin shop-window](https://www.bwin.com/en/news/how-does-the-world-cup-affect-the-transfer-market/) ·
[CIES Football Observatory](https://football-observatory.com/-Value-) ·
[Analytics FC — goalkeeping market](https://analyticsfc.co.uk/blog/2023/10/12/what-can-we-learn-about-the-goalkeeping-market-from-data/) ·
[SI — best GKs 2026 / busiest-keeper myth](https://www.si.com/soccer/best-goalkeepers-2026-world-cup-ranked)

---

## 3. Which goalkeeper stats actually drive reputation & value

The analytics consensus (FBref, StatsBomb/Hudl, Opta/The Analyst): **traditional counting
stats are heavily team-dependent, so the field moved to post-shot expected-goals models — but
warns loudly about sample size.**

| Metric | What it measures | Limitation |
|---|---|---|
| **PSxG − GA / goals prevented / xGOT − GA** | Individual shot-stopping vs. expectation, per on-target shot, credited for placement difficulty | Excludes positioning *by design* (rewards reflexes over anticipation); noisy in small samples |
| **GSAA% = (PSxG − GA)/shots faced** | Goals saved above average, rate form | Same noise |
| **Save %** | Crude stop rate | Ignores shot quality (~85% saved from outside box vs ~60% inside) |
| **Clean sheets / goals conceded** | Team defensive outcome | Heavily team-dependent — a chunk "travels with the club" |
| **Penalty / shootout saves** | Spot-kick outcomes | Tiny sample (~16.8% base save rate); almost no predictive signal — but huge narrative weight |
| **Distribution** (Launch%, completion, Long Ball%, Pass-into-Danger%) | Style & risk on the ball | System-dependent, not quality per se |
| **Sweeping** (OPA, aggressive distance) | Proactivity off the line | Reflects tactical role |
| **Cross-claiming** (Stp%, CCAA%) | Command of the box | Volume varies by team |

**The crucial sample-size caveat (directly relevant to this study):** StatsBomb's foundational
work (Trainor, 2014) shows shot-stopping barely repeats season-to-season (~150 on-target
shots/season is already a small sample). A handful of saves across a 6–7 game tournament
therefore carries **essentially no predictive signal** — it is narrative, not evidence. This
gap between what markets reward (vivid tournament moments) and what predicts future
performance (pooled multi-season PSxG) is exactly the inefficiency the showcase effect
exploits — and a core reason the dashboard model treats tournament stats as a *showcase /
visibility* signal rather than a true-talent estimate.

Sources: [FBref PSxG](https://www.sports-reference.com/blog/2020/01/post-shot-xg-for-goalkeepers-now-on-fbref/) ·
[StatsBomb PSxG](https://statsbomb.com/articles/soccer/a-new-way-to-measure-keepers-shot-stopping-post-shot-expected-goals/) ·
[StatsBomb repeatability (Trainor)](https://blogarchive.statsbomb.com/articles/soccer/goalkeepers-how-repeatable-are-shot-saving-performances/) ·
[Opta xGOT](https://theanalyst.com/articles/what-are-expected-goals-on-target-xgot) ·
[Analytics FC — GK stats team vs individual](https://analyticsfc.co.uk/blog/2023/08/22/do-goalkeeper-statistics-reflect-individual-ability-or-team-performance/) ·
[American Soccer Analysis](https://www.americansocceranalysis.com/home/2015/7/13/5pk9cq7lhvnntea57r2zwsz0ixzw57)

---

## 4. Case studies (the canonical breakout keepers)

| Player | WC | Nation (tier) | Before → After | Tournament headline | Value/fee signal |
|---|---|---|---|---|---|
| **Keylor Navas** | 2014 | Costa Rica (smaller) | Levante → **Real Madrid** (€10m buyout, Aug 2014) | 3 CS in 5 games, R16 shootout save vs Greece, MotM ×3, QF run, Golden Glove finalist | The archetype: modest fee, massive career/value jump |
| **Guillermo Ochoa** | 2014 | Mexico (mid) | Ajaccio (relegated, free agent) → **Málaga (La Liga)**, free | MotM 0–0 vs hosts Brazil (≈4 world-class saves), CS vs Cameroon, R16 | TM value peaked ~€4m at the WC; "free agent to million-dollar baby" |
| **Yassine Bono** | 2022 | Morocco (mid/smaller) | Sevilla → **Al-Hilal** (~€21m, Aug 2023) | 4th place (1st African SF), 2 shootout saves vs Spain, ~1 open-play goal conceded all tourney | ~€21m fee directly attributed to the run (pre-WC TM ~€15m) |
| **Dominik Livaković** | 2022 | Croatia (mid) | Dinamo Zagreb → **Fenerbahçe** (€6.65m, Aug 2023) | 3 shootout saves vs Japan, 11 saves + pen vs Brazil, 3rd place, MotM ×2 | TM ~€10m sustained through the move; run credited as trigger |
| **Vincent Enyeama** | 2010/14 | Nigeria (mid) | Hapoel Tel Aviv → **Lille (Ligue 1)**, 2011 (free) | 6 saves vs Argentina (2010); 2 CS + R16 (2014); 21 CS season at Lille | Move *followed* 2010 WC; WC amplified rather than first-triggered |
| **Alireza Beiranvand** | 2018 | Iran (smaller) | Persepolis → **Royal Antwerp** (2020, delayed) | Saved Ronaldo penalty; group exit | Move came ~2 years later; values `approx` (TM blocked) |
| **Hannes Halldórsson** | 2018 | Iceland (smaller) | Randers → **Qarabağ** (Jul 2018) | Saved Messi penalty + MotM; group exit | Clearest "save → immediate move"; modest profile step-up |
| **Mathew Ryan** | 2014 | Australia (smaller) | Club Brugge → **Valencia** (~€7m, 2015) | Started all 3, group exit | First Europe move *predated* the WC; WC amplified |
| **Tim Krul** | 2014 | Netherlands (elite) | Newcastle → Newcastle (no move) | 2 penalty saves vs Costa Rica (sub'd on for shootout) | **Counter-example:** strong nation, no resulting move — supports the asymmetry thesis |

**Reading the table:** the cleanest "smaller nation → big upgrade" cases (Navas, Ochoa, Bono,
Halldórsson) all combine a *deep run or an elite-opponent highlight* with a *modest pre-WC
club setting*. The elite-nation counter-example (Krul) had an equally dramatic moment but no
move — consistent with the information-asymmetry mechanism.

**The age/contract moderator (important).** A second, strong pattern emerged from the
counterexamples: the keepers who *converted* heroics into a bigger move were young/marketable
and movable (Navas 27, Bono 31 into a cash-rich market, Ospina, Sommer), whereas equally — or
more — heroic *older* keepers got reputation but **no move**: Danijel Subašić (Croatia 2018,
age 33, 4 penalty saves, reached the final — stayed at Monaco, left free in 2020), Tim Howard
(USA 2014, age 35, record 15 saves vs Belgium — stayed at Everton on an already-signed
extension), Igor Akinfeev (Russia 2018 host, saved 2 vs Spain — one-club career at CSKA),
Kasper Schmeichel (Denmark 2018). So the showcase bounce is **conditioned on age + contract
status + a deep run**, not on heroics alone. This directly informs the dashboard (age is a
feature) and the analysis (we test it).

Additional documented cases folded into the dataset: **Keylor Navas (Costa Rica 2014 →
Real Madrid, €10m buyout)** — the single strongest example; **Raïs M'Bolhi (Algeria 2014 →
Philadelphia Union, ~€350k DP)** — a modest WC-enabled move; **David Ospina (Colombia 2014 →
Arsenal)**; **Thibaut Courtois (Belgium 2018 → Real Madrid, ~€35m)** — an *elite-nation* mover
showing the effect is not exclusive to smaller nations, just rarer-per-capita there; and the
no-move counterexamples above.

Sources: [Keylor Navas](https://en.wikipedia.org/wiki/Keylor_Navas) ·
[Ochoa→Málaga (Sky)](https://www.skysports.com/football/news/11800/9403318/) ·
[Bono→Al-Hilal](https://m.allfootballapp.com/news/EPL/OFFICIAL-Al-Hilal-sign-Moroccan-goalkeeper-Bono-from-Sevilla-for-%C2%A317.9m/3153784) ·
[Livaković](https://en.wikipedia.org/wiki/Dominik_Livakovi%C4%87) ·
[Enyeama at Lille](https://www.goal.com/en/news/vincent-enyeama-at-losc-lille-the-highs-and-lows/1mtftnsubtmfi180ia2symhzec) ·
[Halldórsson→Qarabağ](https://www.fourfourtwo.com/news/halldorsson-joins-qarabag-after-heroics-against-messi) ·
[Ryan→Valencia](https://www.espn.com.au/football/story/_/id/37425420/) ·
[Krul](https://en.wikipedia.org/wiki/Tim_Krul)

---

## 5. Implications for the analysis & dashboard

- **Define a "showcase success" target** from observable post-WC outcomes (a clear club/league
  step-up OR a large market-value jump), since that is what the thesis is about.
- **Expect deep-run (`team_stage`), elite-opponent highlight moments (penalty/shootout saves),
  and a modest pre-WC club setting to be the driving factors** — not raw save volume.
- **Treat tournament shot-stopping as a visibility/showcase signal, not true talent** (sample
  size). The dashboard ranks *likelihood of a showcase breakout*, blending current form
  (market value, club tier, age) with the structural ingredients above.
- **Test robustness** to the success definition and tier cutoffs (sensitivity analysis),
  because both are researcher choices.
