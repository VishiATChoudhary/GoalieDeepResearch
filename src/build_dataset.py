"""Build the curated datasets from the research synthesis in research/REPORT.md.

Run:  python src/build_dataset.py

Emits:
  data/goalkeepers_worldcups.csv   — historical keeper-tournaments, 2006-2022
  data/fifa_rankings.csv           — pre-tournament nation ranks used for tiering
  data/goalkeepers_2026.csv        — the live 2026 pool for the dashboard

Provenance & honesty notes
--------------------------
* Numbers come from the cross-checked research pass (FIFA technical data,
  Wikipedia tournament pages, Transfermarkt-derived values via journalism, FBref
  for recent stats). See research/REPORT.md for the cited synthesis.
* `data_confidence` flags how solid each row's *performance* numbers are. Match
  counts, clean sheets, goals conceded, team stage, penalty/shootout saves and
  the headline transfer outcomes are well-sourced. Raw `saves` totals for
  2006-2010 are low-confidence estimates (FIFA did not publish per-keeper save
  tallies then) and are flagged accordingly.
* Market values are approximate (Transfermarkt history pages block automated
  fetching); they are used only to derive a coarse growth signal, and the
  analysis is stress-tested against the value threshold in the sensitivity step.
* `psxg_minus_ga` is left NaN throughout: post-shot xG is not reliably published
  for World Cups. The modelling code drops it rather than inventing values.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NA = np.nan

# ---------------------------------------------------------------------------
# Historical keeper-tournaments.
# Columns: player, nation, wc_year, age_at_wc, fifa_rank_pre, team_stage,
#   matches, minutes, goals_conceded, clean_sheets, saves, save_pct,
#   pen_saves, shootout_wins, golden_glove, club_pre, league_pre,
#   club_pre_tier, mv_pre_eur_m, club_post, moved, move_up,
#   transfer_fee_eur_m, mv_post_eur_m, data_confidence, notes
# save_pct is given only where an official-ish figure exists; otherwise NaN
# (a proxy is computed downstream). psxg_minus_ga is NaN for all (see header).
# ---------------------------------------------------------------------------
COLS = [
    "player", "nation", "wc_year", "age_at_wc", "fifa_rank_pre", "team_stage",
    "matches", "minutes", "goals_conceded", "clean_sheets", "saves", "save_pct",
    "pen_saves", "shootout_wins", "golden_glove", "club_pre", "league_pre",
    "club_pre_tier", "mv_pre_eur_m", "club_post", "moved", "move_up",
    "transfer_fee_eur_m", "mv_post_eur_m", "data_confidence", "notes",
]

ROWS = [
    # ---- 2006 (Germany) ----
    ["Gianluigi Buffon", "Italy", 2006, 28, 13, "winner", 7, 690, 2, 5, 30, NA,
     0, 0, 1, "Juventus", "Serie A", "top5", 18.0, "Juventus", 0, 0, NA, 18.0,
     "low", "Yashin Award; no open-play goal conceded; stayed despite Juve relegation"],
    ["Jens Lehmann", "Germany", 2006, 36, 19, "sf", 6, 540, 6, 2, 15, NA,
     2, 1, 0, "Arsenal", "Premier League", "top5", 8.0, "Arsenal", 0, 0, NA, 7.0,
     "low", "Host 3rd place; 2 saves in QF shootout vs Argentina; age 36, no move"],
    ["Ricardo", "Portugal", 2006, 30, 7, "sf", 7, 660, 6, 2, 12, NA,
     3, 1, 0, "Sporting CP", "Primeira Liga", "other_euro", 4.0, "Sporting CP", 0, 0, NA, 4.0,
     "low", "First keeper to save 3 in one WC shootout (vs England); 4th place; no move"],
    ["Fabien Barthez", "France", 2006, 35, 8, "final", 7, 660, 3, 4, 15, NA,
     0, 0, 0, "Marseille", "Ligue 1", "top5", 5.0, "retired", 0, 0, NA, NA,
     "low", "Runners-up; retired after tournament"],

    # ---- 2010 (South Africa) ----
    ["Iker Casillas", "Spain", 2010, 29, 2, "winner", 7, 630, 2, 5, 17, NA,
     1, 0, 1, "Real Madrid", "La Liga", "top5", 22.0, "Real Madrid", 0, 0, NA, 22.0,
     "med", "Golden Glove; saved Cardozo pen QF; 4 knockout clean sheets; no move"],
    ["Maarten Stekelenburg", "Netherlands", 2010, 27, 4, "final", 7, 660, 6, 3, 16, NA,
     0, 0, 0, "Ajax", "Eredivisie", "other_euro", 12.0, "AS Roma", 1, 1, 6.3, 13.0,
     "med", "Runners-up; moved Ajax->Roma 2011 (~12mo); step up to Serie A"],
    ["Fernando Muslera", "Uruguay", 2010, 24, 16, "sf", 7, 660, 6, 3, 18, NA,
     0, 1, 0, "Lazio", "Serie A", "top5", 8.0, "Galatasaray", 1, 0, 5.0, 9.0,
     "med", "4th place; shootout win vs Ghana; moved to Turkey 2011 (lateral)"],
    ["Manuel Neuer", "Germany", 2010, 24, 6, "sf", 7, 630, 5, 3, 16, NA,
     0, 0, 0, "Schalke 04", "Bundesliga", "top5", 18.0, "Bayern Munich", 1, 1, 30.0, 30.0,
     "med", "WC debut at 24; 3rd place; moved Schalke->Bayern 2011 (~12mo)"],
    ["Eiji Kawashima", "Japan", 2010, 27, 45, "r16", 4, 390, 4, 1, 17, NA,
     0, 0, 0, "Kawasaki Frontale", "J1 League", "non_euro", 0.8, "Lierse SK", 1, 1, 0.0, 1.5,
     "med", "Strongest small-nation case: J-League -> Belgium (Lierse) free, immediately after WC"],
    ["Vincent Enyeama", "Nigeria", 2010, 27, 21, "group", 3, 270, 5, 0, 10, NA,
     0, 0, 0, "Hapoel Tel Aviv", "Israeli PL", "domestic_small", 1.5, "Lille", 1, 1, 0.0, 4.0,
     "med", "6 saves vs Argentina (4 from Messi); moved to Ligue 1 in 2011 (~12mo)"],
    ["Vladimir Stojkovic", "Serbia", 2010, 26, 15, "group", 3, 270, 3, 1, 9, NA,
     1, 0, 0, "Sporting CP", "Primeira Liga", "other_euro", 4.0, "Partizan", 1, 0, 0.0, 3.0,
     "low", "Saved Podolski pen in 1-0 win vs Germany; moved home to Partizan (down)"],
    ["Richard Kingson", "Ghana", 2010, 31, 32, "qf", 5, 480, 6, 1, 18, NA,
     0, 0, 0, "Wigan Athletic", "Premier League", "top5", 0.5, "Blackpool", 1, 0, 0.0, 0.3,
     "low", "QF run (Suarez handball game); released after WC - opposite of a bump"],

    # ---- 2014 (Brazil) ----
    ["Manuel Neuer", "Germany", 2014, 28, 2, "winner", 7, 630, 4, 4, 21, 84.0,
     0, 0, 1, "Bayern Munich", "Bundesliga", "top5", 45.0, "Bayern Munich", 0, 0, NA, 45.0,
     "high", "Golden Glove; sweeper-keeper; already at top club, no move"],
    ["Keylor Navas", "Costa Rica", 2014, 27, 28, "qf", 5, 480, 2, 3, 21, 92.3,
     1, 1, 0, "Levante", "La Liga", "other_euro", 3.0, "Real Madrid", 1, 1, 10.0, 12.0,
     "high", "THE case: best save% in tourney; €10m buyout by Real Madrid Aug 2014"],
    ["Guillermo Ochoa", "Mexico", 2014, 28, 19, "r16", 4, 360, 3, 2, 20, NA,
     0, 0, 0, "AC Ajaccio", "Ligue 1", "other_euro", 1.0, "Malaga", 1, 1, 0.0, 4.0,
     "high", "Free agent (Ajaccio relegated); 6 saves vs Brazil; free move to La Liga"],
    ["Tim Howard", "USA", 2014, 35, 14, "r16", 4, 390, 5, 1, 27, NA,
     0, 0, 0, "Everton", "Premier League", "top5", 6.0, "Everton", 0, 0, NA, 5.0,
     "high", "Record 16 saves vs Belgium; extension signed pre-WC; age 35, no move"],
    ["Vincent Enyeama", "Nigeria", 2014, 31, 44, "r16", 4, 360, 3, 2, 14, NA,
     0, 0, 0, "Lille", "Ligue 1", "top5", 6.0, "Lille", 0, 0, NA, 6.0,
     "med", "Captain; 2 clean sheets; already at Lille, no new move"],
    ["Rais M'Bolhi", "Algeria", 2014, 28, 22, "r16", 4, 390, 5, 0, 18, NA,
     0, 0, 0, "CSKA Sofia", "Bulgarian PL", "domestic_small", 1.0, "Philadelphia Union", 1, 0, 0.35, 1.2,
     "med", "~11 saves vs Germany; modest WC-enabled move to MLS (DP, lateral)"],
    ["David Ospina", "Colombia", 2014, 25, 8, "qf", 5, 480, 4, 2, 15, NA,
     0, 0, 0, "OGC Nice", "Ligue 1", "top5", 6.0, "Arsenal", 1, 1, 4.0, 9.0,
     "high", "QF run; moved Nice->Arsenal Aug 2014"],
    ["Sergio Romero", "Argentina", 2014, 27, 7, "final", 7, 690, 4, 5, 16, NA,
     2, 1, 0, "AS Monaco", "Ligue 1", "top5", 4.0, "Sampdoria", 1, 0, 0.0, 4.0,
     "med", "2 shootout saves vs NED (SF); runners-up; loan move, no upgrade"],

    # ---- 2018 (Russia) ----
    ["Thibaut Courtois", "Belgium", 2018, 26, 3, "sf", 7, 630, 6, 3, 27, 82.0,
     0, 0, 1, "Chelsea", "Premier League", "top5", 45.0, "Real Madrid", 1, 1, 35.0, 60.0,
     "high", "Golden Glove; 3rd place; moved Chelsea->Real Madrid (~€35m). Elite-nation mover"],
    ["Guillermo Ochoa", "Mexico", 2018, 32, 15, "r16", 4, 360, 5, 1, 25, 83.0,
     0, 0, 0, "Standard Liege", "Belgian PL", "other_euro", 2.0, "Club America", 1, 0, 1.0, 1.5,
     "high", "~9 saves in 1-0 upset of Germany; homecoming move to Liga MX (down)"],
    ["Danijel Subasic", "Croatia", 2018, 33, 20, "final", 7, 690, 9, 2, 20, NA,
     4, 2, 0, "AS Monaco", "Ligue 1", "top5", 4.0, "AS Monaco", 0, 0, NA, 3.0,
     "high", "KEY counterexample: 3 shootout saves vs DEN +1 vs RUS, reached final; age 33, no move"],
    ["Kasper Schmeichel", "Denmark", 2018, 31, 12, "r16", 4, 390, 3, 2, 22, NA,
     3, 0, 0, "Leicester City", "Premier League", "top5", 12.0, "Leicester City", 0, 0, NA, 11.0,
     "high", "Saved Modric ET pen + 2 in shootout vs Croatia; established PL, no move"],
    ["Hannes Halldorsson", "Iceland", 2018, 34, 22, "group", 3, 270, 5, 0, 14, NA,
     1, 0, 0, "Randers FC", "Danish Superliga", "other_euro", 0.4, "Qarabag", 1, 0, 0.0, 0.5,
     "med", "Saved Messi pen in Iceland's first WC game; modest move to Azerbaijan; age 34"],
    ["Alireza Beiranvand", "Iran", 2018, 25, 37, "group", 3, 270, 2, 1, 12, NA,
     1, 0, 0, "Persepolis", "Persian Gulf Pro", "non_euro", 0.5, "Persepolis", 0, 0, NA, 0.8,
     "med", "Saved Ronaldo pen; young & heroic but Antwerp move came ~2yrs later (outside window)"],
    ["Cho Hyun-woo", "South Korea", 2018, 26, 57, "group", 3, 270, 3, 1, 14, NA,
     0, 0, 0, "Daegu FC", "K League 1", "non_euro", 0.5, "Ulsan Hyundai", 1, 0, 1.0, 1.5,
     "med", "MotM in 2-0 win vs Germany; European interest but no move (fee/age/military), domestic move"],
    ["Igor Akinfeev", "Russia", 2018, 32, 70, "qf", 5, 480, 7, 1, 18, NA,
     2, 1, 0, "CSKA Moscow", "Russian PL", "non_euro", 8.0, "CSKA Moscow", 0, 0, NA, 7.0,
     "med", "Host; saved 2 vs Spain in R16 shootout; one-club career, no move"],

    # ---- 2022 (Qatar) ----
    ["Emiliano Martinez", "Argentina", 2022, 30, 3, "winner", 7, 690, 8, 3, 16, 67.0,
     3, 2, 1, "Aston Villa", "Premier League", "top5", 28.0, "Aston Villa", 0, 0, NA, 32.0,
     "high", "Golden Glove; ET save on Kolo Muani + shootout saves; champion but stayed"],
    ["Dominik Livakovic", "Croatia", 2022, 27, 12, "sf", 7, 690, 8, 3, 22, NA,
     3, 2, 0, "Dinamo Zagreb", "Croatian HNL", "non_euro", 10.0, "Fenerbahce", 1, 1, 6.65, 10.0,
     "high", "3 shootout saves vs Japan; 11 saves vs Brazil; 3rd; moved to Fenerbahce"],
    ["Yassine Bono", "Morocco", 2022, 31, 22, "sf", 6, 540, 3, 4, 16, NA,
     2, 1, 0, "Sevilla", "La Liga", "top5", 15.0, "Al-Hilal", 1, 1, 21.0, 18.0,
     "high", "1st African WC semifinal; ~1 open-play goal conceded; ~€21m move to Al-Hilal"],
    ["Wojciech Szczesny", "Poland", 2022, 32, 26, "r16", 4, 360, 5, 2, 18, NA,
     2, 0, 0, "Juventus", "Serie A", "top5", 12.0, "Juventus", 0, 0, NA, 10.0,
     "high", "Saved Messi pen + Saudi pen; established at Juve, no move"],
    ["Mathew Ryan", "Australia", 2022, 30, 38, "r16", 4, 360, 6, 2, 15, NA,
     0, 0, 0, "FC Copenhagen", "Danish Superliga", "other_euro", 2.5, "AZ Alkmaar", 1, 0, 0.0, 2.0,
     "med", "R16 (first since 2006); lateral move, then Roma backup"],
    ["Guillermo Ochoa", "Mexico", 2022, 37, 13, "group", 3, 270, 3, 1, 12, NA,
     1, 0, 0, "Club America", "Liga MX", "non_euro", 1.0, "Salernitana", 1, 1, 0.0, 1.2,
     "high", "Saved Lewandowski pen; age 37 but earned a Serie A move (Liga MX -> Serie A)"],
    ["Andries Noppert", "Netherlands", 2022, 28, 8, "qf", 5, 480, 4, 2, 14, NA,
     0, 0, 0, "SC Heerenveen", "Eredivisie", "other_euro", 1.5, "SC Heerenveen", 0, 0, NA, 2.0,
     "med", "Surprise breakout, QF run; but strong nation & stayed at Heerenveen"],
    ["Mohammed Al-Owais", "Saudi Arabia", 2022, 31, 51, "group", 3, 270, 3, 0, 11, NA,
     0, 0, 0, "Al-Hilal", "Saudi Pro League", "non_euro", 1.5, "Al-Hilal", 0, 0, NA, 1.5,
     "med", "Player of match in 2-1 win over Argentina; SPL foreign-keeper rule blocks export"],
    ["Yann Sommer", "Switzerland", 2022, 33, 15, "r16", 4, 360, 5, 1, 16, NA,
     0, 0, 0, "Borussia M.gladbach", "Bundesliga", "top5", 4.0, "Bayern Munich", 1, 1, 8.0, 6.0,
     "med", "Moved to Bayern Jan 2023 (Neuer injury-driven, not WC); counted as a mover"],
    ["Shuichi Gonda", "Japan", 2022, 33, 24, "r16", 4, 360, 4, 1, 15, NA,
     0, 0, 0, "Shimizu S-Pulse", "J1 League", "non_euro", 0.5, "Shimizu S-Pulse", 0, 0, NA, 0.5,
     "med", "MotM in 2-1 win vs Germany; great tournament but age 33, no move"],
    ["Alexander Dominguez", "Ecuador", 2014, 27, 28, "group", 3, 270, 3, 1, 11, NA,
     0, 0, 0, "LDU Quito", "Ecuadorian Serie A", "non_euro", 1.6, "LDU Quito", 0, 0, NA, 1.6,
     "med", "MotM 0-0 vs France; group exit; modest move to Mexico came in 2016 (outside window)"],
    ["Essam El-Hadary", "Egypt", 2018, 45, 45, "group", 1, 90, 3, 0, 2, NA,
     1, 0, 0, "Al-Taawoun", "Saudi Pro League", "non_euro", 0.1, "Al-Taawoun", 0, 0, NA, 0.1,
     "med", "Oldest player in WC history; saved a pen; age 45, no move"],
]

# ---------------------------------------------------------------------------
# 2026 live pool (subset, emphasising smaller-nation keepers). Performance
# fields reflect early-tournament data as of 2026-06-21 where known, else 0.
# Columns: player, nation, age_at_wc, fifa_rank_pre, club_pre, league_pre,
#   club_pre_tier, mv_pre_eur_m, matches, minutes, goals_conceded,
#   clean_sheets, saves, pen_saves, team_stage, storyline
# ---------------------------------------------------------------------------
COLS_2026 = [
    "player", "nation", "age_at_wc", "fifa_rank_pre", "club_pre", "league_pre",
    "club_pre_tier", "mv_pre_eur_m", "matches", "minutes", "goals_conceded",
    "clean_sheets", "saves", "pen_saves", "team_stage", "storyline",
]

ROWS_2026 = [
    # smaller / debutant nations (the focus)
    ["Vozinha", "Cape Verde", 40, 73, "free agent", "-", "non_euro", 0.1,
     1, 90, 0, 1, 7, 0, "group", "40yo debutant; 7 saves to hold Spain 0-0; viral breakout"],
    ["Eloy Room", "Curacao", 37, 82, "Miami FC", "USL Championship", "non_euro", 0.2,
     2, 180, 7, 1, 15, 0, "group", "Smallest nation ever to qualify; 15 saves in 0-0 vs Ecuador (tied Howard record)"],
    ["Yassine Bono", "Morocco", 35, 11, "Al-Hilal", "Saudi Pro League", "non_euro", 3.5,
     1, 90, 1, 0, 3, 0, "group", "2025 CAF GK of the Year; 2022 semifinal hero"],
    ["Max Crocombe", "New Zealand", 32, 89, "Millwall", "Championship", "other_euro", 1.0,
     1, 90, 1, 0, 4, 0, "group", "Led Championship in save%; OFC's first direct WC berth"],
    ["Yazeed Abulaila", "Jordan", 33, 62, "Al-Hussein", "Jordanian Pro League", "non_euro", 0.3,
     1, 90, 1, 0, 3, 0, "group", "Debutant; reached 2023 Asian Cup final"],
    ["Utkir Yusupov", "Uzbekistan", 35, 57, "Navbahor", "Uzbek Super League", "non_euro", 0.5,
     1, 90, 0, 1, 4, 0, "group", "Debutant; 10 clean sheets in qualifying"],
    ["Lionel Mpasi", "DR Congo", 31, 60, "Le Havre", "Ligue 1", "top5", 0.4,
     1, 90, 1, 0, 5, 0, "group", "DR Congo's return after 52 years; Ligue 1 keeper"],
    ["Ronwen Williams", "South Africa", 34, 58, "Mamelodi Sundowns", "PSL", "non_euro", 0.9,
     1, 90, 1, 0, 4, 0, "group", "Saved 4 pens in AFCON 2024 QF shootout (record)"],
    ["Benjamin Asare", "Ghana", 33, 70, "Hearts of Oak", "Ghana PL", "non_euro", 0.1,
     1, 45, 0, 1, 2, 0, "group", "First home-based GK to feature for Ghana at a WC"],
    ["Luca Zidane", "Algeria", 28, 32, "Granada", "Segunda Division", "other_euro", 1.0,
     1, 90, 1, 0, 3, 0, "group", "Son of Zinedine; switched France->Algeria; wears protective mask"],
    ["Johny Placide", "Haiti", 38, 80, "SC Bastia", "Ligue 2", "other_euro", 0.15,
     1, 90, 1, 0, 4, 0, "group", "Haiti's return after 52 years"],
    ["Camilo Vargas", "Colombia", 37, 13, "Atlas", "Liga MX", "non_euro", 0.5,
     1, 90, 1, 0, 3, 0, "group", "Undisputed #1 since 2023"],
    ["Hernan Galindez", "Ecuador", 39, 24, "Huracan", "Argentine PD", "non_euro", 1.0,
     1, 90, 0, 1, 3, 0, "group", "Kept clean sheet in shock 0-0 vs Curacao"],
    ["Yahia Fofana", "Cote d'Ivoire", 25, 40, "Rizespor", "Super Lig", "other_euro", 5.0,
     1, 90, 1, 0, 4, 0, "group", "Highest-valued African keeper at the tournament"],
    ["Luis Mejia", "Panama", 35, 35, "Club Nacional", "Uruguayan PD", "non_euro", 0.3,
     1, 90, 1, 0, 4, 0, "group", "Panama's 2nd WC; veteran #1"],
    ["Sergio Rochet", "Uruguay", 33, 15, "Internacional", "Brazilian Serie A", "other_euro", 3.5,
     1, 90, 0, 1, 3, 0, "group", "Bielsa's #1; reported Boca target"],
    ["Alireza Beiranvand", "Iran", 33, 21, "Tractor", "Persian Gulf Pro", "non_euro", 0.65,
     1, 90, 1, 0, 4, 0, "group", "3rd straight World Cup; famous penalty saver"],
    ["Nawaf Al-Aqidi", "Saudi Arabia", 26, 58, "Al-Nassr", "Saudi Pro League", "non_euro", 0.7,
     1, 90, 1, 0, 4, 0, "group", "Displaced 2022 hero Al-Owais as #1"],
    # established / elite reference points
    ["Zion Suzuki", "Japan", 23, 19, "Parma", "Serie A", "top5", 24.0,
     1, 90, 2, 0, 5, 0, "group", "Most valuable keeper in the field; first Japanese keeper in Serie A"],
    ["Emiliano Martinez", "Argentina", 33, 1, "Aston Villa", "Premier League", "top5", 15.0,
     1, 90, 1, 0, 3, 0, "group", "Reigning 2022 Golden Glove"],
    ["Alisson", "Brazil", 33, 5, "Liverpool", "Premier League", "top5", 14.0,
     2, 180, 1, 1, 6, 0, "group", "Ancelotti's #1; third World Cup"],
    ["Matt Freese", "USA", 27, 16, "New York City FC", "MLS", "non_euro", 2.0,
     1, 90, 1, 0, 4, 0, "group", "Host nation #1; 3 shootout saves in 2025 Gold Cup"],
    ["Raul Rangel", "Mexico", 26, 17, "Chivas", "Liga MX", "non_euro", 6.5,
     2, 180, 0, 2, 6, 0, "group", "Surprise host #1; two clean sheets to open"],
    ["Maxime Crepeau", "Canada", 32, 30, "Orlando City", "MLS", "non_euro", 1.8,
     1, 90, 1, 0, 4, 0, "group", "Host #1 over MLS GK of the Year St. Clair"],
]


def build_historical() -> pd.DataFrame:
    df = pd.DataFrame(ROWS, columns=COLS)
    assert df[["player", "nation", "wc_year"]].duplicated().sum() == 0, "dup keeper-tournaments"
    return df


def build_rankings(hist: pd.DataFrame) -> pd.DataFrame:
    r = (hist[["nation", "wc_year", "fifa_rank_pre"]]
         .drop_duplicates()
         .sort_values(["wc_year", "fifa_rank_pre"]))
    return r


def build_2026() -> pd.DataFrame:
    df = pd.DataFrame(ROWS_2026, columns=COLS_2026)
    return df


def main() -> None:
    hist = build_historical()
    hist.to_csv(ROOT / "data" / "goalkeepers_worldcups.csv", index=False)
    build_rankings(hist).to_csv(ROOT / "data" / "fifa_rankings.csv", index=False)
    build_2026().to_csv(ROOT / "data" / "goalkeepers_2026.csv", index=False)
    print(f"Wrote {len(hist)} historical keeper-tournaments across "
          f"{hist['wc_year'].nunique()} World Cups.")
    print(f"Wrote {len(ROWS_2026)} goalkeepers for the 2026 live pool.")


if __name__ == "__main__":
    main()
