"""Real goalkeeper-metric ingestion from StatsBomb open data.

Run:  python src/ingest_statsbomb.py

StatsBomb publishes free event data for the 2018 and 2022 men's World Cups
(competition_id 43). This module downloads it (cached under data/raw/statsbomb/)
and computes *real* shot-based goalkeeper metrics per keeper-tournament:

  shots_on_target_faced, saves, goals_conceded, save_pct,
  xg_faced (sum of pre-shot xG of on-target shots faced),
  xg_prevented (xg_faced - goals_conceded), pen_saves, matches

Output: data/processed/statsbomb_gk_metrics.csv

Honesty notes
-------------
* `xg_prevented` uses StatsBomb *pre-shot* xG (the open data does not expose a
  post-shot xG / PSxG value), so it is a real but coarser cousin of PSxG-GA. It
  is labelled `xg_prevented` (not `psxg_minus_ga`) to avoid overstating it.
* FBref's PSxG pages are 403-blocked in this environment; this StatsBomb route
  is the accessible source for genuine shot-level numbers. Only 2018 & 2022 are
  covered, so the historical CSV keeps its researched values for 2006-2014.

For data sources where Python egress is blocked (FBref/Transfermarkt), see
`src/ingest_fbref.py` for the documented scaffold.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "statsbomb"
BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

# competition_id 43 = FIFA World Cup; season_id -> tournament year
SEASONS = {3: 2018, 106: 2022}

# Shot outcomes that put the ball on target (require a save or are a goal).
ON_TARGET = {"Goal", "Saved", "Saved to Post", "Saved Off Target"}


def _get(url: str, cache_path: Path) -> object:
    """Fetch JSON with on-disk caching."""
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode("utf-8")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(raw)
    return json.loads(raw)


def _starting_gks(events: list) -> dict:
    """Map team_name -> starting goalkeeper name from Starting XI events."""
    gks = {}
    for ev in events:
        if ev.get("type", {}).get("name") == "Starting XI":
            team = ev.get("team", {}).get("name")
            for p in ev.get("tactics", {}).get("lineup", []):
                if p.get("position", {}).get("name") == "Goalkeeper":
                    gks[team] = p.get("player", {}).get("name")
    return gks


def process_match(match_id: int) -> list[dict]:
    """Return per-goalkeeper stat dicts for one match."""
    events = _get(f"{BASE}/events/{match_id}.json", CACHE / "events" / f"{match_id}.json")
    teams = list({ev.get("team", {}).get("name") for ev in events
                  if ev.get("team")} - {None})
    if len(teams) != 2:
        return []
    cur_gk = _starting_gks(events)
    opponent = {teams[0]: teams[1], teams[1]: teams[0]}
    # accumulator keyed by (gk_name, gk_team)
    acc: dict[tuple, dict] = {}

    def slot(gk, team):
        key = (gk, team)
        return acc.setdefault(key, dict(player=gk, nation=team, sot=0, saves=0,
                                        goals_conceded=0, xg_faced=0.0,
                                        pen_saves=0, so_pen_saves=0))

    for ev in events:
        etype = ev.get("type", {}).get("name")
        # keep goalkeeper assignment current through substitutions
        if etype == "Substitution":
            off = ev.get("player", {}).get("name")
            team = ev.get("team", {}).get("name")
            repl = ev.get("substitution", {}).get("replacement", {}).get("name")
            if cur_gk.get(team) == off and repl:
                cur_gk[team] = repl
            continue
        if etype != "Shot":
            continue
        shot = ev.get("shot", {})
        outcome = shot.get("outcome", {}).get("name")
        if outcome not in ON_TARGET:
            continue
        atk_team = ev.get("team", {}).get("name")
        def_team = opponent.get(atk_team)
        gk = cur_gk.get(def_team)
        if not gk:
            continue
        rec = slot(gk, def_team)
        is_pen = shot.get("type", {}).get("name") == "Penalty"
        # period 5 = penalty shootout: credit saves separately, but keep
        # shootout kicks OUT of the open-play save%/xG (standard convention).
        if ev.get("period") == 5:
            if outcome != "Goal":
                rec["so_pen_saves"] += 1
            continue
        rec["sot"] += 1
        rec["xg_faced"] += float(shot.get("statsbomb_xg", 0) or 0)
        if outcome == "Goal":
            rec["goals_conceded"] += 1
        else:
            rec["saves"] += 1
            if is_pen:
                rec["pen_saves"] += 1
    return list(acc.values())


def main() -> None:
    rows: list[dict] = []
    for season_id, year in SEASONS.items():
        matches = _get(f"{BASE}/matches/43/{season_id}.json",
                       CACHE / "matches" / f"43_{season_id}.json")
        print(f"WC {year}: {len(matches)} matches")
        for m in matches:
            for rec in process_match(m["match_id"]):
                rec["wc_year"] = year
                rows.append(rec)

    df = pd.DataFrame(rows)
    agg = (df.groupby(["player", "nation", "wc_year"], as_index=False)
             .agg(matches=("sot", "size"), sot_faced=("sot", "sum"),
                  saves=("saves", "sum"), goals_conceded=("goals_conceded", "sum"),
                  xg_faced=("xg_faced", "sum"), pen_saves=("pen_saves", "sum"),
                  so_pen_saves=("so_pen_saves", "sum")))
    agg["save_pct"] = (100 * agg["saves"] / agg["sot_faced"]).round(1)
    agg["xg_prevented"] = (agg["xg_faced"] - agg["goals_conceded"]).round(2)
    agg = agg.sort_values(["wc_year", "xg_prevented"], ascending=[True, False])

    out = ROOT / "data" / "processed" / "statsbomb_gk_metrics.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(out, index=False)
    print(f"Wrote {len(agg)} goalkeeper-tournaments to {out.relative_to(ROOT)}")
    print(agg.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
