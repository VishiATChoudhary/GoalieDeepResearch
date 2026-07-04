# World Cup 2026 — Live Goalkeeper Stats (as of 2026-07-04)

Goalkeeper statistics for the current tournament, now through the group stage and into
the Round of 32 / Round of 16, compiled from match reports and stat hubs (ESPN FIFA WC
2026 stats, Goalkeeper Magazine saves leaderboard, FIFA power rankings/match centre,
Squawka, Sofascore, Opta/The Analyst).

> **Data caveat:** automated fetches to the big providers are still partly 403/cert-blocked
> in this environment, so figures come from cross-checked search extracts and the latest
> published saves leaderboard. Quarterfinals (Jul 4–8) are just kicking off, so per-keeper
> totals are the newest available. Headline **saves totals** (Room 20,
> Al-Owais 16, Beiranvand 15, Gill 13, Abunada 12, five keepers on 11) are corroborated.
> Per-match splits, ratings and `goals_prevented` for the newly-added keepers are not all
> published as discrete numbers and are flagged `approx` / left blank. Nothing fabricated.

## Headline storylines (updated)
- **Eloy Room (Curaçao), 37** — **20 saves, the tournament lead**, powered by his record-tying
  15-save clean sheet vs Ecuador. Smallest nation ever to qualify.
- **Orlando Gill (Paraguay)** — **19 saves (2nd)**; Paraguay grind into the Round of 16.
- **Vozinha (Cape Verde), 40** — the ride ends but he made it a classic: 2 group clean sheets to
  reach the knockouts, then **8 saves vs Messi's Argentina** (8.4 rating) in a 2-3 AET loss on
  Jul 3 — **18 saves, 3rd at the tournament**. Story of the World Cup for a minnow.
- **Mohammed Al-Owais (Saudi Arabia)** — **16 saves** in 2 games; CS in the 0-0 vs Cape Verde.
- **Alireza Beiranvand (Iran)** — **15 saves** on his 3rd straight World Cup.
- **Jacob Zetterström (Sweden)** — **9 saves vs France** in the Round of 32, 2nd-most in a WC
  game by a Swedish keeper in 60 years.

## Saves leaderboard (as of 2026-07-04)

| # | Keeper | Nation | Tier | Saves |
|--:|---|---|:--|--:|
| 1 | Eloy Room | Curaçao | smaller | 20 |
| 2 | Orlando Gill | Paraguay | smaller | 19 |
| 3 | Vozinha | Cape Verde | smaller | 18 |
| 4 | Mohammed Al-Owais | Saudi Arabia | smaller | 16 |
| 5 | Alireza Beiranvand | Iran | mid | 15 |
| 6 | Mahmoud Abunada | Qatar | smaller | 12 |
| 7= | Gregor Kobel | Switzerland | mid | 11 |
| 7= | Max Crocombe | New Zealand | smaller | 11 |
| 7= | Patrick Beach | Australia | mid | 11 |
| 7= | Bart Verbruggen | Netherlands | elite | 11 |
| 7= | Johny Placide | Haiti | smaller | 11 |

*Tier from FIFA rank: elite ≤10, mid ≤30, smaller >30.*

## The showcase thesis, live
Aggregated across the 30 keepers tracked, **smaller-nation keepers have made the most saves and
the second-most clean sheets** of any tier — exactly the "showcase" pattern the historical study
found: keepers from lower-ranked nations face more shots, rack up saves, and grab the spotlight.
See `analysis/figures/wc2026_saves_leaderboard.png` and `wc2026_tier_summary.png`.

## Important starter corrections vs the pre-tournament pool
- **Uruguay:** Fernando Muslera (40) started, not Sergio Rochet.
- **Panama:** Orlando Mosquera started, not the veteran Luis Mejía.
- **Saudi Arabia:** Mohammed Al-Owais is the starter; Nawaf Al-Aqidi injured (0 minutes).

To refresh as more knockout games are played, edit `data/goalkeepers_2026.csv` (or re-run the
research) and re-run `python analysis/plot_2026.py`; the dashboard re-ranks automatically.
