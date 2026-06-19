#!/usr/bin/env python3
"""
clv.py — Closing-Line Value tracker for the WC2026 bet tracker.

Measures, for every bet's ANCHOR legs (Match Odds, Double Chance, Total Goals
O/U 2.5), how the de-vigged market price for OUR selection moved between the
first snapshot and the last pre-kickoff snapshot in data/odds_snapshots.csv.

Honest scope (read this before trusting a number):
  * Builder-level CLV is unmeasurable (opaque correlation pricing). We only do
    LEG-level, and only for legs that exist in the odds feed — Match Odds, DC
    (derived from 1X2), and Total Goals 2.5. Player SOT / corners / cards are
    NOT in the feed, so they have no CLV here.
  * We don't (yet) store our per-leg TAKEN odds, and we place ~1h pre-kickoff
    (≈ the close). So this is OPEN→CLOSE market drift on our selections — a
    READ-ALIGNMENT proxy ("did the market move toward our pick?"), not literal
    taken-vs-close CLV. Positive = our anchor reads lead the market.
  * To get TRUE taken-vs-close CLV: record per-leg entry odds at placement
    (the slip singles prices are visible on the screenshots) and/or place
    earlier when we spot value. Flagged as the next process upgrade.

Stdlib only. Run: python3 clv.py
"""
import csv, statistics
from collections import defaultdict
from datetime import datetime

SNAP = "data/odds_snapshots.csv"
BETS = "data/bets.csv"
LEGS = "data/legs.csv"

# snapshot team-name aliases -> as they appear in our legs
TEAM_ALIAS = {"turkiye": "turkey"}


def norm(s):
    return (s or "").lower().replace(" & herzegovina", "").replace("&", "") \
        .replace("-", " ").replace("  ", " ").strip()


def load_snapshots():
    """match -> list of (ts, kickoff, market, outcome, point, price)"""
    rows = defaultdict(list)
    with open(SNAP) as f:
        for r in csv.DictReader(f):
            if r["market"] not in ("h2h", "totals"):
                continue
            try:
                price = float(r["price"])
            except (ValueError, KeyError):
                continue
            rows[r["match"]].append((r["ts_utc"], r["kickoff_utc"], r["market"],
                                     r["outcome"], r["point"], price))
    return rows


def snap_match_for(bet_match, snap_keys):
    nb = norm(bet_match)
    if nb in snap_keys:
        return snap_keys[nb]
    for k, orig in snap_keys.items():
        if nb in k or k in nb:
            return orig
    return None


def devig(price_map):
    """{outcome: median_price} -> {outcome: fair_prob} (normalised 1/price)."""
    impl = {o: 1.0 / p for o, p in price_map.items() if p > 0}
    tot = sum(impl.values())
    return {o: v / tot for o, v in impl.items()} if tot else {}


def prices_at(rows, ts, market, point=None):
    """median price per outcome across books at one timestamp+market."""
    bucket = defaultdict(list)
    for (t, ko, m, outcome, pt, price) in rows:
        if t == ts and m == market and (point is None or pt == point):
            bucket[outcome].append(price)
    return {o: statistics.median(v) for o, v in bucket.items()}


def fair_prob(rows, ts, leg_market, selection, home, away):
    """fair prob of OUR selection at timestamp ts."""
    if leg_market in ("Match Odds_h2h", "Double Chance"):
        pm = prices_at(rows, ts, "h2h")
        if len(pm) < 3:
            return None
        fp = devig(pm)
        if leg_market == "Double Chance":
            team = selection.lower().split(" and ")[0].strip()
            team = TEAM_ALIAS.get(team, team)
            tkey = _match_outcome(team, fp.keys())
            if not tkey:
                return None
            draw = next((o for o in fp if o.lower() == "draw"), None)
            return fp[tkey] + (fp.get(draw, 0) if draw else 0)
        else:  # straight match odds
            team = TEAM_ALIAS.get(selection.lower(), selection.lower())
            tkey = _match_outcome(team, fp.keys())
            return fp.get(tkey) if tkey else None
    if leg_market == "Total Goals":
        pm = prices_at(rows, ts, "totals", "2.5")
        ov = next((o for o in pm if o.lower() == "over"), None)
        un = next((o for o in pm if o.lower() == "under"), None)
        if not (ov and un):
            return None
        fp = devig({ov: pm[ov], un: pm[un]})
        want = "over" if selection.lower().startswith("over") else "under"
        key = ov if want == "over" else un
        return fp.get(key)
    return None


def _match_outcome(team, outcomes):
    tn = norm(team)
    for o in outcomes:
        if o.lower() == "draw":
            continue
        no = norm(o)
        if tn == no or tn in no or no in tn:
            return o
    return None


def classify(leg):
    mt, md = leg["market_type"], leg["market_detail"]
    if mt == "Match Odds":
        return "Double Chance" if "Double Chance" in md else "Match Odds_h2h"
    if mt == "Total Goals O/U":
        return "Total Goals"
    return None


def main():
    snaps = load_snapshots()
    snap_keys = {norm(k): k for k in snaps}
    bets = {b["bet_id"]: b for b in csv.DictReader(open(BETS))}
    legs = list(csv.DictReader(open(LEGS)))

    rows_out = []
    for leg in legs:
        kind = classify(leg)
        if not kind:
            continue
        bet = bets.get(leg["bet_id"])
        if not bet:
            continue
        sm = snap_match_for(bet["match"], snap_keys)
        if not sm:
            continue
        rows = snaps[sm]
        kickoff_iso = rows[0][1]
        ts_all = sorted({t for (t, *_rest) in rows})
        pre = [t for t in ts_all if t <= kickoff_iso] or ts_all
        t_open, t_close = ts_all[0], pre[-1]
        if t_open == t_close:
            continue
        parts = bet["match"].split(" v ")
        home, away = (parts + ["", ""])[:2]
        op = fair_prob(rows, t_open, kind, leg["selection"], home, away)
        cl = fair_prob(rows, t_close, kind, leg["selection"], home, away)
        if op is None or cl is None or op <= 0:
            continue
        clv_pct = cl / op - 1.0          # >0 => market moved toward our pick
        rows_out.append({
            "bet": leg["bet_id"][-4:], "match": bet["match"], "kind": kind,
            "sel": leg["selection"], "result": leg["result"],
            "open_p": op, "close_p": cl, "dpp": (cl - op) * 100,
            "clv": clv_pct * 100,
        })

    if not rows_out:
        print("No CLV rows computed.")
        return

    # |CLV|>40% open->close swings are almost always thin early-market data
    # artifacts, not real line moves. Flag them and report a robust median +
    # trimmed mean (median is the honest headline at this n).
    ART = 40.0
    for r in rows_out:
        r["artifact"] = abs(r["clv"]) > ART

    print(f"\nLEG-LEVEL CLV (open->close market drift on our anchor picks) — n={len(rows_out)}")
    print("Positive = the de-vigged market moved TOWARD our selection by kickoff.")
    print(f"(median is the headline; mean shown trimmed of |CLV|>{ART:.0f}% data artifacts)\n")
    by = defaultdict(list)
    for r in rows_out:
        by[r["kind"]].append(r)
    print(f"  {'leg type':16} {'n':>3} {'median':>8} {'trim-mean':>10} {'% to-us':>9}")

    def line(label, rs):
        clean = [r["clv"] for r in rs if not r["artifact"]]
        allc = [r["clv"] for r in rs]
        if not allc:
            return
        med = statistics.median(allc)
        tm = statistics.mean(clean) if clean else float("nan")
        pos = sum(1 for x in allc if x > 0) / len(allc) * 100
        print(f"  {label:16} {len(allc):>3} {med:>+7.1f}% {tm:>+9.1f}% {pos:>8.0f}%")

    for k in ("Match Odds_h2h", "Double Chance", "Total Goals"):
        if by.get(k):
            line(k, by[k])
    line("ALL", rows_out)
    nart = sum(1 for r in rows_out if r["artifact"])
    print(f"\n  ({nart} legs flagged as |CLV|>{ART:.0f}% thin-market artifacts, "
          f"excluded from trim-mean, kept in median/%)")

    print("\nPER-LEG detail (most recent last):")
    print(f"  {'bet':>4} {'kind':14} {'selection':22} {'open%':>6} {'close%':>7} {'CLV%':>7} res")
    for r in rows_out:
        flag = " ⚠artifact" if r["artifact"] else ""
        print(f"  {r['bet']:>4} {r['kind']:14} {r['sel'][:22]:22} "
              f"{r['open_p']*100:>5.0f}% {r['close_p']*100:>6.0f}% {r['clv']:>+6.1f}% {r['result']}{flag}")

    print("\nNOTE: open->close drift, not literal taken-vs-close (we place ~1h pre-KO "
          "≈ close, and don't yet store per-leg entry odds). Read-alignment proxy on "
          "anchor legs only; SOT/corners/cards aren't in the odds feed.")


if __name__ == "__main__":
    main()
