"""Live Paddy Power odds board + snapshot logger for WC 2026 (The Odds API).

Usage:
  python odds.py                  # board for next 60h, anchors only (~2 credits)
  python odds.py scotland         # filter by team substring + BTTS lookups
  python odds.py --hours 24       # window
  python odds.py --btts           # force BTTS lookups without a filter
  python odds.py --snapshot       # quiet mode: fetch, log to CSV, one summary line

Every run appends all prices seen (next 72h of fixtures) to
data/odds_snapshots.csv — the basis for closing-line-value analysis.

Key: odds-api.local.key (gitignored) or ODDS_API_KEY env var.
Quota: free tier 500 credits/month. Bulk board = 2 credits; each BTTS
event lookup = 1 credit (only fetched with a filter or --btts, capped).
"""
import csv
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SPORT = "soccer_fifa_world_cup"
MARKETS = "h2h,totals"  # btts fetched per-event (additional market)
PREFERRED = "paddypower"
FALLBACKS = ["betfair_ex_uk", "williamhill", "ladbrokes_uk", "coral", "skybet", "unibet_uk"]
MAX_BTTS_LOOKUPS = 8
SNAPSHOT_HOURS = 72
SNAP_PATH = os.path.join(HERE, "data", "odds_snapshots.csv")
SNAP_FIELDS = ["ts_utc", "match", "kickoff_utc", "bookmaker", "market", "outcome", "point", "price"]


def api_key():
    p = os.path.join(HERE, "odds-api.local.key")
    if os.path.exists(p):
        return open(p, encoding="utf-8").read().strip()
    k = os.environ.get("ODDS_API_KEY")
    if k:
        return k
    sys.exit("No API key: create odds-api.local.key or set ODDS_API_KEY")


def to_frac(dec):
    v = dec - 1
    best = (1, 1, 9e9)
    for den in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 17, 20, 25, 33, 50, 100):
        num = round(v * den)
        if num < 1:
            continue
        err = abs(v - num / den)
        if err < best[2]:
            best = (num, den, err)
    n, d, _ = best
    return f"{n}/{d}" if d > 1 else f"{n}/1"


def fmt(price):
    return f"{price:.2f} ({to_frac(price)}, {100/price:.0f}%)"


def snapshot_rows(events, extra_btts):
    """Flatten all bookmaker prices for fixtures within SNAPSHOT_HOURS."""
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M")
    cutoff = now + timedelta(hours=SNAPSHOT_HOURS)
    rows = []
    for ev in events:
        ko = datetime.fromisoformat(ev["commence_time"].replace("Z", "+00:00"))
        if ko > cutoff or ko < now - timedelta(hours=2.5):
            continue
        match = f'{ev["home_team"]} v {ev["away_team"]}'
        books = list(ev.get("bookmakers", [])) + extra_btts.get(ev["id"], [])
        for b in books:
            for m in b.get("markets", []):
                for o in m.get("outcomes", []):
                    rows.append(dict(ts_utc=ts, match=match,
                                     kickoff_utc=ev["commence_time"],
                                     bookmaker=b["key"], market=m["key"],
                                     outcome=o["name"], point=o.get("point", ""),
                                     price=o["price"]))
    return rows


def append_snapshot(rows):
    if not rows:
        return
    new_file = not os.path.exists(SNAP_PATH)
    with open(SNAP_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SNAP_FIELDS)
        if new_file:
            w.writeheader()
        w.writerows(rows)


def main():
    args = list(sys.argv[1:])
    hours, quiet, force_btts = 60, False, False
    if "--snapshot" in args:
        quiet = True
        args.remove("--snapshot")
    if "--btts" in args:
        force_btts = True
        args.remove("--btts")
    if "--hours" in args:
        i = args.index("--hours")
        hours = int(args[i + 1])
        del args[i:i + 2]
    flt = " ".join(args).lower().strip()

    key = api_key()

    def get(url):
        req = urllib.request.Request(url, headers={"User-Agent": "wc2026-bets"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.headers.get("x-requests-remaining", "?"), json.loads(resp.read())

    remaining, events = get(
        f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"
        f"?apiKey={key}&regions=uk&markets={MARKETS}&oddsFormat=decimal")

    extra_btts, btts_done = {}, 0
    want_btts = (flt or force_btts) and not quiet

    def fetch_btts(event_id):
        nonlocal remaining, btts_done
        if not want_btts or btts_done >= MAX_BTTS_LOOKUPS:
            return None
        btts_done += 1
        try:
            remaining, ev = get(
                f"https://api.the-odds-api.com/v4/sports/{SPORT}/events/{event_id}/odds"
                f"?apiKey={key}&regions=uk&markets=btts&oddsFormat=decimal")
            extra_btts[event_id] = ev.get("bookmakers", [])
            return extra_btts[event_id]
        except Exception:
            return None

    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(hours=hours)
    shown = 0
    for ev in sorted(events, key=lambda e: e["commence_time"]):
        ko = datetime.fromisoformat(ev["commence_time"].replace("Z", "+00:00"))
        name = f'{ev["home_team"]} v {ev["away_team"]}'
        if flt and flt not in name.lower():
            continue
        if not flt and (ko > cutoff or ko < now - timedelta(hours=2.5)):
            continue
        if quiet:
            shown += 1
            continue
        live = " [LIVE]" if ko < now else ""
        print(f"\n=== {name} — {ko.astimezone().strftime('%a %d %b %H:%M')}{live} ===")
        books = {b["key"]: b for b in ev.get("bookmakers", [])}
        chosen = books.get(PREFERRED)
        label = "Paddy Power"
        if not chosen:
            for fb in FALLBACKS:
                if fb in books:
                    chosen, label = books[fb], books[fb]["title"] + " (PP unavailable)"
                    break
        if not chosen:
            print("  no UK book prices returned")
            continue
        print(f"  [{label}]")
        for m in chosen.get("markets", []):
            if m["key"] == "h2h":
                o = {x["name"]: x["price"] for x in m["outcomes"]}
                home, away = ev["home_team"], ev["away_team"]
                print(f"  Match odds : {home} {fmt(o.get(home, 0))} | "
                      f"Draw {fmt(o.get('Draw', 0))} | {away} {fmt(o.get(away, 0))}")
            elif m["key"] == "totals":
                for x in sorted(m["outcomes"], key=lambda x: (x.get("point", 0), x["name"])):
                    print(f"  Goals {x['name']} {x.get('point')} : {fmt(x['price'])}")
        bb = fetch_btts(ev["id"])
        if bb:
            books_b = {b["key"]: b for b in bb}
            cb = books_b.get(PREFERRED) or next((books_b[f] for f in FALLBACKS if f in books_b), None)
            if cb:
                for m in cb.get("markets", []):
                    if m["key"] == "btts":
                        o = {x["name"]: x["price"] for x in m["outcomes"]}
                        print(f"  BTTS       : Yes {fmt(o.get('Yes', 0))} | No {fmt(o.get('No', 0))}"
                              + ("" if cb["key"] == PREFERRED else f"  [{cb['title']}]"))
        shown += 1

    rows = snapshot_rows(events, extra_btts)
    append_snapshot(rows)

    if quiet:
        print(f"snapshot: {len(rows)} prices logged across {shown or 'all'} fixtures "
              f"(window {SNAPSHOT_HOURS}h); quota remaining {remaining}")
    else:
        if not shown:
            print("No matching fixtures in window.")
        print(f"\n[{len(rows)} prices snapshotted to data/odds_snapshots.csv · "
              f"quota remaining: {remaining}]")


if __name__ == "__main__":
    main()
