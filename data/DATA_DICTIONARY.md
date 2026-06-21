# Data Dictionary

This project studies **goalkeepers from smaller / lower-ranked footballing nations** and
how a FIFA World Cup acts as a *showcase* that lets them earn better club moves and higher
market valuations afterward.

## Tables

### `goalkeepers_worldcups.csv`
One row per **goalkeeper × World Cup** appearance (primary keepers and notable backups who
played meaningful minutes), for the last five completed tournaments: **2006, 2010, 2014,
2018, 2022**.

| column | type | description |
|---|---|---|
| `player` | str | Goalkeeper name |
| `nation` | str | National team |
| `wc_year` | int | World Cup edition (2006–2022) |
| `age_at_wc` | int | Age during that tournament |
| `fifa_rank_pre` | int | Nation's FIFA ranking just before the tournament |
| `nation_tier` | str | `elite` / `mid` / `smaller` — bucketed from `fifa_rank_pre` (see below) |
| `team_stage` | str | How far the team advanced: `group`, `r16`, `qf`, `sf`, `final`, `winner` |
| `team_stage_rank` | int | Ordinal of stage: group=1, r16=2, qf=3, sf=4, final=5, winner=6 |
| `matches` | int | Matches the keeper played |
| `minutes` | int | Minutes played |
| `goals_conceded` | int | Goals conceded while on pitch |
| `clean_sheets` | int | Clean sheets |
| `saves` | int | Total saves made |
| `save_pct` | float | Save percentage (saves / shots on target faced), 0–100 |
| `psxg_minus_ga` | float | Post-shot xG minus goals allowed ("goals prevented"); NaN where unavailable (sparse pre-2018) |
| `pen_saves` | int | Penalties saved (in-game + shootout), tournament total |
| `shootout_wins` | int | Shootouts won where keeper made decisive save(s) |
| `golden_glove` | int | 1 if won the tournament's best-GK award |
| `club_pre` | str | Club immediately before the World Cup |
| `league_pre` | str | League of `club_pre` |
| `club_pre_tier` | str | `top5`, `other_euro`, `domestic_small`, `non_euro` — strength of pre-WC club setting |
| `mv_pre_eur_m` | float | Transfermarkt market value (€M) shortly before the WC |
| `club_post` | str | Club within ~18 months after the WC (same club if no move) |
| `moved` | int | 1 if changed clubs within ~18 months after the WC |
| `move_up` | int | 1 if the post-WC move was a clear step up in league/club tier |
| `transfer_fee_eur_m` | float | Fee of the post-WC transfer (€M); 0 for free; NaN if none/unknown |
| `mv_post_eur_m` | float | Transfermarkt market value (€M) ~6–12 months after the WC |
| `notes` | str | Short context / sourcing note |

#### Derived/target columns (created in processing)
| column | type | description |
|---|---|---|
| `mv_delta_eur_m` | float | `mv_post_eur_m - mv_pre_eur_m` |
| `mv_growth_pct` | float | Percentage market-value change after the WC |
| `showcase_success` | int | **Primary target.** 1 if the keeper earned a clear post-WC upgrade — defined as `move_up==1` OR `mv_growth_pct >= 50` |

### `fifa_rankings.csv`
Reference of FIFA rankings used to bucket nations into tiers per tournament.

### `goalkeepers_2026.csv`
The 2026 World Cup goalkeeper pool (current tournament) used by the live dashboard. Same
performance columns as above where available, plus pre-tournament context (club, age, MV,
nation FIFA rank). Performance fields update as the tournament progresses.

## Nation tiering (`nation_tier`)
Buckets are assigned from the nation's pre-tournament FIFA ranking:
- `elite`  — FIFA rank 1–10 (traditional powers / favourites)
- `mid`    — FIFA rank 11–30
- `smaller`— FIFA rank 31+ (the "smaller / less good countries" the study focuses on)

The "smaller nations" hypothesis is tested primarily on `nation_tier in {smaller, mid}`.

## Sourcing
Values are compiled from Transfermarkt (market values, transfer fees, clubs), FBref /
StatsBomb and FIFA technical reports (tournament performance stats), and reputable football
journalism. Advanced metrics (PSxG-GA, save%) are well-populated for 2018 and 2022 and
sparser for 2006–2014; missing values are encoded as `NaN` and handled explicitly in
analysis. Each row carries a short `notes` provenance tag. See `research/REPORT.md` for the
cited research synthesis underpinning these figures.
