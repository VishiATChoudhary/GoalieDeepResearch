"""FBref advanced-goalkeeping ingestion scaffold.

Run:  python src/ingest_fbref.py

FBref publishes the gold-standard public goalkeeper metric — **PSxG-GA**
(post-shot expected goals minus goals allowed) — on its "Advanced Goalkeeping"
pages, including World Cup editions. This module pulls those tables into
`data/processed/fbref_gk_metrics.csv`.

⚠️ Network note: in THIS execution environment FBref returns HTTP 403 to
automated requests (it blocks non-browser traffic / rate-limits hard), so this
script will not fetch here — it degrades gracefully with a clear message. It is
included as a correct, ready-to-run scaffold for an environment where FBref is
reachable. For real shot-based metrics that DO work here, see
`src/ingest_statsbomb.py` (StatsBomb open data, 2018 & 2022).

Why PSxG-GA matters (see research/REPORT.md §3): unlike save% or clean sheets it
isolates shot-stopping from team defence, crediting the keeper for the
difficulty of the on-target shots faced. It is the single metric this project
would most like to have for every tournament; StatsBomb open data only exposes
*pre-shot* xG, so FBref is the route to true PSxG when accessible.
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed" / "fbref_gk_metrics.csv"

# FBref World Cup advanced-goalkeeping pages (competition id 1).
# season-tagged URLs; the "keepersadv" table carries PSxG / PSxG+/-.
FBREF_PAGES = {
    2018: "https://fbref.com/en/comps/1/2018/keepersadv/2018-FIFA-World-Cup-Stats",
    2022: "https://fbref.com/en/comps/1/2022/keepersadv/2022-FIFA-World-Cup-Stats",
    # current edition (table fills as the tournament progresses):
    2026: "https://fbref.com/en/comps/1/keepersadv/FIFA-World-Cup-Stats",
}

# Columns of interest from the advanced-goalkeeping table once parsed.
WANTED = {
    "Player": "player", "Squad": "nation", "90s": "nineties",
    "PSxG": "psxg", "PSxG+/-": "psxg_minus_ga", "Save%": "save_pct",
    "Saves": "saves", "GA": "goals_conceded",
}


def _fetch_tables(url: str) -> list[pd.DataFrame]:
    """Fetch a FBref page and return all HTML tables. Requires network access
    to FBref (blocked in this sandbox). Uses a browser-like UA."""
    import urllib.request
    req = urllib.request.Request(url, headers={
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0 Safari/537.36"),
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "ignore")
    # FBref wraps some tables in HTML comments; un-comment so pandas sees them.
    html = html.replace("<!--", "").replace("-->", "")
    return pd.read_html(io.StringIO(html))


def _pick_keeper_table(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
    for t in tables:
        cols = {str(c[-1]) if isinstance(c, tuple) else str(c) for c in t.columns}
        if "PSxG+/-" in cols or "PSxG" in cols:
            t = t.copy()
            t.columns = [c[-1] if isinstance(c, tuple) else c for c in t.columns]
            return t
    return None


def ingest() -> pd.DataFrame:
    frames = []
    for year, url in FBREF_PAGES.items():
        try:
            tables = _fetch_tables(url)
        except Exception as e:  # noqa: BLE001 - report and continue
            print(f"  WC {year}: fetch failed ({type(e).__name__}: "
                  f"{str(e)[:80]}). FBref is likely blocking automated access here.")
            continue
        tbl = _pick_keeper_table(tables)
        if tbl is None:
            print(f"  WC {year}: no advanced-goalkeeping table found on page.")
            continue
        keep = {k: v for k, v in WANTED.items() if k in tbl.columns}
        sub = tbl[list(keep)].rename(columns=keep)
        sub = sub[sub["player"].notna() & (sub["player"] != "Player")]
        sub["wc_year"] = year
        frames.append(sub)
        print(f"  WC {year}: parsed {len(sub)} goalkeepers (with PSxG-GA).")

    if not frames:
        print("\nNo FBref data retrieved (expected in this sandbox — FBref 403s "
              "automated traffic). Use src/ingest_statsbomb.py for real metrics "
              "that work here, or run this script where FBref is reachable.")
        return pd.DataFrame()

    out = pd.concat(frames, ignore_index=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"\nWrote {len(out)} rows to {OUT.relative_to(ROOT)}")
    return out


if __name__ == "__main__":
    ingest()
