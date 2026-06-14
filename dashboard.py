"""WC 2026 bet tracker dashboard generator.

Reads data/bets.csv, legs.csv, deposits.csv, fixtures.csv (optional);
writes dashboard.html. Run: & 'C:\\Python314\\python.exe' dashboard.py
"""
import csv
import html
import json
import os
import random
from datetime import datetime, date

HERE = os.path.dirname(os.path.abspath(__file__))
TOTAL_WC_GAMES = 104
MC_SIMS = 2000

ALIASES = {
    "bosnia and herzegovina": "bosnia", "bosnia-herzegovina": "bosnia",
    "united states": "usa", "korea republic": "south korea",
    "cote d'ivoire": "ivory coast", "côte d'ivoire": "ivory coast",
    "republic of ireland": "ireland", "czech republic": "czechia",
}

SVG_CHECK = ('<svg class="ic ok" viewBox="0 0 16 16" fill="none"><path d="M3 8.5 6.5 12 13 4.5" '
             'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
SVG_X = ('<svg class="ic bad" viewBox="0 0 16 16" fill="none"><path d="M4 4l8 8M12 4l-8 8" '
         'stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')
SVG_DOT = ('<svg class="ic dim" viewBox="0 0 16 16"><circle cx="8" cy="8" r="3" fill="currentColor"/></svg>')
SVG_BALL = ('<svg class="logo" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" '
            'stroke="currentColor" stroke-width="1.5"/><path d="M12 7l4.4 3.2-1.7 5.2H9.3L7.6 10.2 12 7z" '
            'stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>'
            '<path d="M12 2v5M21.5 9.5l-5.1.7M18.5 19.8l-3.8-4.4M5.5 19.8l3.8-4.4M2.5 9.5l5.1.7" '
            'stroke="currentColor" stroke-width="1.5"/></svg>')


def norm(team):
    t = team.strip().lower()
    return ALIASES.get(t, t)


def read_csv(name):
    path = os.path.join(HERE, "data", name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def money(x):
    return f"-£{abs(x):,.2f}" if x < 0 else f"£{x:,.2f}"


def main():
    bets = read_csv("bets.csv")
    legs = read_csv("legs.csv")
    deposits = read_csv("deposits.csv")
    fixtures = read_csv("fixtures.csv")
    today = date.today()

    for b in bets:
        b["stake_f"] = float(b["stake"])
        b["odds_f"] = float(b["odds_decimal"])
        b["pl_f"] = float(b["profit_loss"]) if b["profit_loss"] else 0.0
        b["ret_f"] = float(b["actual_return"]) if b["actual_return"] else 0.0
        b["pot_f"] = float(b["potential_return"])
        b["legs"] = [l for l in legs if l["bet_id"] == b["bet_id"]]
        b["key"] = (norm(b["home_team"]), norm(b["away_team"]))

    settled = sorted([b for b in bets if b["status"] in ("Won", "Lost", "Void", "Cashed Out")],
                     key=lambda x: x["kickoff"])
    open_bets = [b for b in bets if b["status"] == "Open"]
    won = [b for b in settled if b["status"] == "Won"]

    total_staked = sum(b["stake_f"] for b in bets)
    settled_stake = sum(b["stake_f"] for b in settled)
    returns_settled = sum(b["ret_f"] for b in settled)
    pl = sum(b["pl_f"] for b in settled)
    roi = pl / settled_stake if settled_stake else 0.0
    open_stake = sum(b["stake_f"] for b in open_bets)
    open_potential = sum(b["pot_f"] for b in open_bets)
    deposited = sum(float(d["amount"]) for d in deposits)
    balance = deposited - total_staked + returns_settled
    avg_odds = sum(b["odds_f"] for b in settled) / len(settled) if settled else 0
    breakeven = 1 / avg_odds if avg_odds else 0
    strike = len(won) / len(settled) if settled else 0

    # ---- Bankroll curve (anchored at 0) + Monte Carlo no-edge band + open cone
    curve_labels = ["Start"] + [datetime.strptime(b["kickoff"][:10], "%Y-%m-%d").strftime("%d %b")
                                for b in settled]
    curve_vals, run = [0.0], 0.0
    for b in settled:
        run += b["pl_f"]
        curve_vals.append(round(run, 2))

    random.seed(42)
    p10, p90 = [0.0], [0.0]
    if settled:
        sims = []
        for _ in range(MC_SIMS):
            c, path = 0.0, []
            for b in settled:
                c += (b["stake_f"] * (b["odds_f"] - 1)
                      if random.random() < 1 / b["odds_f"] else -b["stake_f"])
                path.append(c)
            sims.append(path)
        for i in range(len(settled)):
            col = sorted(s[i] for s in sims)
            p10.append(round(col[int(MC_SIMS * .1)], 2))
            p90.append(round(col[int(MC_SIMS * .9)], 2))

    n = len(curve_vals)
    cone_labels = curve_labels + ["Open settle"]
    cone_hi = [None] * (n - 1) + [curve_vals[-1], round(curve_vals[-1] + open_potential - open_stake, 2)]
    cone_lo = [None] * (n - 1) + [curve_vals[-1], round(curve_vals[-1] - open_stake, 2)]

    # ---- Strike rate vs break-even
    strike_vals, w = [], 0
    for i, b in enumerate(settled, 1):
        w += 1 if b["status"] == "Won" else 0
        strike_vals.append(round(100 * w / i, 1))
    needed_vals = [round(100 * breakeven, 1)] * len(strike_vals)

    # ---- Leg analysis
    leg_stats = {}
    for b in settled:
        blegs = b["legs"]
        losers = [l for l in blegs if l["result"] == "Lost"]
        for l in blegs:
            s = leg_stats.setdefault(l["market_type"], dict(won=0, lost=0, killer=0, pl=0.0))
            if l["result"] == "Won":
                s["won"] += 1
            elif l["result"] == "Lost":
                s["lost"] += 1
                if len(losers) == 1:
                    s["killer"] += 1
            if b["status"] == "Won" and blegs:
                s["pl"] += b["pl_f"] / len(blegs)
            elif b["status"] == "Lost" and l["result"] == "Lost" and losers:
                s["pl"] += b["pl_f"] / len(losers)

    # ---- Near-miss accounting
    near_misses, nm_stake, cf_extra = [], 0.0, 0.0
    for b in settled:
        if b["status"] != "Lost":
            continue
        losers = [l for l in b["legs"] if l["result"] == "Lost"]
        survived = len([l for l in b["legs"] if l["result"] == "Won"])
        if len(losers) == 1:
            n_legs = len(b["legs"])
            est_ret = b["stake_f"] * (b["odds_f"] ** ((n_legs - 1) / n_legs))
            near_misses.append(dict(bet=b, survived=survived, n=n_legs,
                                    killer=losers[0], est_ret=est_ret))
            nm_stake += b["stake_f"]
            cf_extra += est_ret
    cf_pl = pl + cf_extra

    # ---- Super Sub tracker
    ss_legs = []
    for b in bets:
        for l in b["legs"]:
            if l["super_sub"] == "yes":
                ss_legs.append((b, l))

    # ---- Kickoff-time split
    def bucket(kick):
        h = int(kick[11:13])
        if h < 7:
            return "Late night (00–07)"
        if h < 18:
            return "Daytime (07–18)"
        return "Evening (18–24)"

    time_stats = {}
    for b in settled:
        s = time_stats.setdefault(bucket(b["kickoff"]), dict(n=0, won=0, pl=0.0))
        s["n"] += 1
        s["won"] += 1 if b["status"] == "Won" else 0
        s["pl"] += b["pl_f"]

    # ---- Archetypes
    arch_stats = {}
    for b in settled:
        a = b.get("archetype") or "unclassified"
        s = arch_stats.setdefault(a, dict(n=0, won=0, pl=0.0, staked=0.0))
        s["n"] += 1
        s["won"] += 1 if b["status"] == "Won" else 0
        s["pl"] += b["pl_f"]
        s["staked"] += b["stake_f"]

    # ---- Fixtures: coverage map + needs-a-bet
    bet_by_key = {b["key"]: b for b in bets}
    coverage_html, needs_html, missed = "", "", 0
    if fixtures:
        for fx in fixtures:
            fx["key"] = (norm(fx["home_team"]), norm(fx["away_team"]))
            fx["d"] = datetime.strptime(fx["date"], "%Y-%m-%d").date()
            b = bet_by_key.get(fx["key"]) or bet_by_key.get((fx["key"][1], fx["key"][0]))
            if b:
                fx["cls"] = {"Won": "c-won", "Lost": "c-lost", "Open": "c-open"}.get(b["status"], "c-open")
            elif fx["d"] < today:
                fx["cls"] = "c-missed"
                missed += 1
            else:
                fx["cls"] = "c-future"
        by_date = {}
        for fx in sorted(fixtures, key=lambda x: (x["date"], x["kickoff_uk"])):
            by_date.setdefault(fx["date"], []).append(fx)
        rows = []
        for d, fxs in by_date.items():
            cells = "".join(
                f'<div class="cell {fx["cls"]}" tabindex="0" title="{html.escape(fx["home_team"])} v '
                f'{html.escape(fx["away_team"])} · {fx["kickoff_uk"]} · {html.escape(fx["stage"])}'
                f'{(" " + fx["group"]) if fx["group"] else ""}"></div>' for fx in fxs)
            day = datetime.strptime(d, "%Y-%m-%d").strftime("%a %d %b")
            rows.append(f'<div class="cov-row"><span class="cov-date">{day}</span>'
                        f'<div class="cov-cells">{cells}</div></div>')
        legend = ('<div class="cov-legend">'
                  '<span><i class="cell c-won"></i>won</span><span><i class="cell c-lost"></i>lost</span>'
                  '<span><i class="cell c-open"></i>open</span><span><i class="cell c-future"></i>no bet yet</span>'
                  '<span><i class="cell c-missed"></i>missed</span></div>')
        coverage_html = legend + "".join(rows)

        upcoming = [fx for fx in sorted(fixtures, key=lambda x: (x["date"], x["kickoff_uk"]))
                    if fx["cls"] == "c-future"][:10]
        if upcoming:
            needs_html = "".join(
                f'<tr><td class="num">{datetime.strptime(fx["date"], "%Y-%m-%d").strftime("%a %d %b")} '
                f'{fx["kickoff_uk"]}</td><td>{html.escape(fx["home_team"])} v {html.escape(fx["away_team"])}</td>'
                f'<td class="muted">{html.escape(fx["stage"])}{(" " + fx["group"]) if fx["group"] else ""}</td></tr>'
                for fx in upcoming)
    bet_games = len({b["key"] for b in bets})

    # ---- HTML assembly
    pl_sign = "pos" if pl >= 0 else "neg"

    def kpi(label, value, sub="", cls="", raw=None):
        d = f' data-count="{raw}"' if raw is not None else ""
        return (f'<div class="kpi"><div class="kpi-label">{label}</div>'
                f'<div class="kpi-value num {cls}"{d}>{value}</div>'
                f'<div class="kpi-sub">{sub}</div></div>')

    peak, max_dd = 0.0, 0.0
    for v in curve_vals:
        peak = max(peak, v)
        max_dd = max(max_dd, peak - v)
    worst_run, run_l = 0, 0
    for b in settled:
        run_l = run_l + 1 if b["status"] == "Lost" else 0
        worst_run = max(worst_run, run_l)

    net_vs_dep = balance - deposited
    kpis = "".join([
        kpi("Deposited", money(deposited), "own money in"),
        kpi("Account balance", money(balance),
            f"{money(net_vs_dep)} vs deposits", "pos" if net_vs_dep >= 0 else "neg"),
        kpi("Record", f"{len(won)}–{len(settled) - len(won)}",
            f"strike {strike:.0%} · need {breakeven:.0%} @ {avg_odds:.2f}",
            "pos" if strike >= breakeven else "neg"),
        kpi("In flight", money(open_stake), f"returns up to {money(open_potential)}"),
        kpi("Max drawdown", money(max_dd), f"worst losing run {worst_run}",
            "neg" if max_dd > 0 else ""),
        kpi("Coverage", f"{bet_games}/{TOTAL_WC_GAMES}",
            f"{missed} missed" if fixtures else "add fixtures.csv"),
    ])

    def leg_rows():
        rows = []
        for mt, s in sorted(leg_stats.items(), key=lambda kv: kv[1]["pl"]):
            tot = s["won"] + s["lost"]
            wr = f"{s['won']/tot:.0%}" if tot else "–"
            cls = "pos" if s["pl"] >= 0 else "neg"
            rows.append(f"<tr><td>{html.escape(mt)}</td><td class='num'>{s['won']}</td>"
                        f"<td class='num'>{s['lost']}</td><td class='num'>{wr}</td>"
                        f"<td class='num'>{s['killer']}</td>"
                        f"<td class='num {cls}'>{money(s['pl'])}</td></tr>")
        return "".join(rows)

    def arch_rows():
        rows = []
        for a, s in sorted(arch_stats.items(), key=lambda kv: -kv[1]["pl"]):
            cls = "pos" if s["pl"] >= 0 else "neg"
            roi_a = s["pl"] / s["staked"] if s["staked"] else 0
            rows.append(f"<tr><td>{html.escape(a)}</td><td class='num'>{s['won']}/{s['n']}</td>"
                        f"<td class='num {cls}'>{money(s['pl'])}</td>"
                        f"<td class='num {cls}'>{roi_a:+.0%}</td></tr>")
        return "".join(rows)

    nm_rows = "".join(
        f'<tr><td>{html.escape(m["bet"]["match"])}</td><td class="num">{m["survived"]}/{m["n"]}</td>'
        f'<td>{html.escape(m["killer"]["selection"])} — {html.escape(m["killer"]["market_detail"])}</td>'
        f'<td class="num">{money(m["est_ret"])}</td></tr>' for m in near_misses) or \
        '<tr><td colspan="4" class="muted">No one-leg losses yet</td></tr>'

    ss_rows = "".join(
        f'<tr><td>{html.escape(b["match"])}</td><td>{html.escape(l["selection"])}</td>'
        f'<td class="{ {"Won": "pos", "Lost": "neg"}.get(l["result"], "muted") }">{l["result"]}</td>'
        f'<td class="muted">{html.escape(l["notes"])}</td></tr>' for b, l in ss_legs) or \
        '<tr><td colspan="4" class="muted">None yet</td></tr>'

    time_rows = "".join(
        f'<tr><td>{html.escape(t)}</td><td class="num">{s["won"]}/{s["n"]}</td>'
        f'<td class="num {"pos" if s["pl"] >= 0 else "neg"}">{money(s["pl"])}</td></tr>'
        for t, s in sorted(time_stats.items())) or \
        '<tr><td colspan="3" class="muted">No settled bets</td></tr>'

    def bet_card(b):
        badge = {"Won": "won", "Lost": "lost", "Open": "open"}.get(b["status"], "open")
        legs_html = ""
        for l in b["legs"]:
            mark = {"Won": SVG_CHECK, "Lost": SVG_X}.get(l["result"], SVG_DOT)
            ss = ' <span class="ss">SS</span>' if l["super_sub"] == "yes" else ""
            legs_html += (f'<div class="leg">{mark}<span class="leg-sel">'
                          f'{html.escape(l["selection"])}</span>'
                          f'<span class="leg-mkt">{html.escape(l["market_detail"])}</span>{ss}</div>')
        ret = money(b["ret_f"]) if b["status"] != "Open" else money(b["pot_f"])
        ret_label = "returned" if b["status"] != "Open" else "potential"
        kick = datetime.strptime(b["kickoff"], "%Y-%m-%d %H:%M").strftime("%a %d %b · %H:%M")
        return (f'<div class="slip s-{badge}"><div class="slip-head">'
                f'<span class="badge {badge}">{b["status"]}</span>'
                f'<div class="slip-title"><strong>{html.escape(b["match"])}</strong>'
                f'<span class="muted">{kick} · {html.escape(b.get("archetype") or "")}</span></div>'
                f'<div class="slip-odds"><span class="chip num">{b["odds_fractional"]}</span>'
                f'<span class="num muted">{money(b["stake_f"])} → {ret} {ret_label}</span></div>'
                f'</div><div class="slip-legs">{legs_html}</div></div>')

    cards = "".join(bet_card(b) for b in sorted(bets, key=lambda x: x["kickoff"], reverse=True))

    leg_sorted = sorted(leg_stats.items(), key=lambda kv: kv[1]["pl"])
    needs_panel = (f'<section><h2>Needs a bet — next up</h2><div class="panel">'
                   f'<div class="tw"><table><tr><th>Kickoff (UK)</th><th>Match</th><th>Stage</th></tr>'
                   f'{needs_html}</table></div></div></section>') if needs_html else ""
    coverage_panel = (f'<section><h2>Tournament coverage — all {len(fixtures)} games</h2>'
                      f'<div class="panel">{coverage_html}</div></section>') if fixtures else ""

    # ---- Ghost ledger (paper trades; never touches real money) ----
    ghost_bets = read_csv("ghost_bets.csv")
    ghost_panel = ""
    if ghost_bets:
        for g in ghost_bets:
            g["pl_f"] = float(g["profit_loss"]) if g["profit_loss"] else 0.0
            g["stake_f"] = float(g["notional_stake"]) if g.get("notional_stake") else 0.0
        g_set = [g for g in ghost_bets if g["status"] in ("Won", "Lost")]
        g_won = [g for g in g_set if g["status"] == "Won"]
        g_pl = sum(g["pl_f"] for g in g_set)
        g_stake = sum(g["stake_f"] for g in g_set)
        g_strike = len(g_won) / len(g_set) if g_set else 0
        tier_stats = {}
        for g in g_set:
            s = tier_stats.setdefault(g["builder_label"], dict(n=0, won=0, pl=0.0))
            s["n"] += 1
            s["won"] += 1 if g["status"] == "Won" else 0
            s["pl"] += g["pl_f"]
        tier_order = ["new-method 3-leg soft spine", "base 3-leg sans optional",
                      "Safer", "Balanced-Best rec", "Aggressive"]
        order_key = lambda kv: tier_order.index(kv[0]) if kv[0] in tier_order else 99
        ghost_tier_rows = "".join(
            f'<tr><td>{html.escape(t)}</td><td class="num">{s["won"]}/{s["n"]}</td>'
            f'<td class="num">{s["won"]/s["n"]:.0%}</td>'
            f'<td class="num {"pos" if s["pl"] >= 0 else "neg"}">{money(s["pl"])}</td></tr>'
            for t, s in sorted(tier_stats.items(), key=order_key))
        ghost_panel = (
            f'<section><h2>Ghost ledger — unplaced builds (paper)</h2><div class="panel">'
            f'<p class="note">Pre-registered builds from each pre-match read, settled BLIND on paper — '
            f'not real money, pure A/B data. Overall <b class="num">{len(g_won)}–{len(g_set) - len(g_won)}</b> '
            f'(strike {g_strike:.0%}), paper P/L <b class="num {"pos" if g_pl >= 0 else "neg"}">{money(g_pl)}</b> '
            f'on £{g_stake:.0f} notional. The comparison that matters is by build type below — the new-method '
            f'spine leads every old tier. Odds estimated where no board price; n is small.</p>'
            f'<div class="tw"><table><tr><th>Build type</th><th>Won</th><th>Strike</th><th>Paper P/L</th></tr>'
            f'{ghost_tier_rows}</table></div></div></section>')

    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WC 2026 Bet Tracker</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Fira+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root {{
    --bg-deep:#020203; --bg-base:#0a0a0f; --surface:rgba(255,255,255,.04);
    --surface-hi:rgba(255,255,255,.07); --line:rgba(255,255,255,.08);
    --text:#ededf2; --muted:#8a8f9c;
    --green:#22c55e; --green-soft:rgba(34,197,94,.14);
    --red:#ef4444; --red-soft:rgba(239,68,68,.14);
    --accent:#5e6ad2; --accent-soft:rgba(94,106,210,.16);
    --gold:#e8c84a; --radius:16px;
    --ease:cubic-bezier(.16,1,.3,1);
    --sans:'Fira Sans',system-ui,sans-serif; --mono:'Fira Code',ui-monospace,monospace;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ margin:0; color:var(--text); font:14px/1.55 var(--sans); font-weight:400;
          background:linear-gradient(180deg,var(--bg-base) 0%,var(--bg-deep) 100%);
          background-attachment:fixed; min-height:100vh; padding:32px clamp(14px,4vw,48px) 64px; }}
  .blob {{ position:fixed; border-radius:50%; filter:blur(70px); pointer-events:none; z-index:0; }}
  .blob.b1 {{ width:480px; height:480px; top:-160px; right:-100px;
              background:radial-gradient(circle,rgba(94,106,210,.13),transparent 70%);
              animation:drift 24s var(--ease) infinite alternate; }}
  .blob.b2 {{ width:420px; height:420px; bottom:-140px; left:-120px;
              background:radial-gradient(circle,rgba(34,197,94,.09),transparent 70%);
              animation:drift 30s var(--ease) infinite alternate-reverse; }}
  @keyframes drift {{ from {{ transform:translate(0,0); }} to {{ transform:translate(-50px,40px); }} }}
  @media (prefers-reduced-motion: reduce) {{
    .blob {{ animation:none; }} * {{ transition:none !important; }}
  }}
  main {{ position:relative; z-index:1; max-width:1280px; margin:0 auto; }}

  /* ---- hero ---- */
  .hero {{ display:flex; align-items:flex-end; justify-content:space-between;
           gap:24px; flex-wrap:wrap; margin-bottom:28px; }}
  .brand {{ display:flex; gap:14px; align-items:center; }}
  .logo {{ width:42px; height:42px; color:var(--gold); flex:none; }}
  .eyebrow {{ font-size:11px; letter-spacing:.22em; text-transform:uppercase;
              color:var(--gold); font-weight:600; }}
  h1 {{ font-size:clamp(22px,3.4vw,30px); margin:2px 0 0; font-weight:700; letter-spacing:-.01em; }}
  .stamp {{ color:var(--muted); font-size:12px; margin-top:4px; }}
  .hero-pl {{ text-align:right; }}
  .hero-pl .lbl {{ font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:var(--muted); }}
  .hero-pl .val {{ font:600 clamp(34px,5vw,48px)/1.1 var(--mono); font-variant-numeric:tabular-nums; }}
  .hero-pl .val.pos {{ color:var(--green); text-shadow:0 0 24px rgba(34,197,94,.35); }}
  .hero-pl .val.neg {{ color:var(--red); text-shadow:0 0 24px rgba(239,68,68,.35); }}
  .hero-pl .sub {{ font-size:12px; color:var(--muted); }}

  /* ---- surfaces ---- */
  .panel, .kpi, .slip {{ background:var(--surface); border:1px solid var(--line);
    border-radius:var(--radius); position:relative;
    box-shadow:inset 0 1px 0 rgba(255,255,255,.05), 0 8px 28px rgba(0,0,0,.35);
    transition:border-color .2s var(--ease), background .2s var(--ease), transform .25s var(--ease); }}
  .panel {{ padding:18px; }}
  .panel:hover, .kpi:hover {{ border-color:rgba(255,255,255,.15); background:var(--surface-hi); }}

  h2 {{ font-size:12px; color:var(--muted); text-transform:uppercase;
        letter-spacing:.14em; margin:34px 0 12px; font-weight:600; }}
  section:first-of-type h2 {{ margin-top:0; }}
  .pos {{ color:var(--green); }} .neg {{ color:var(--red); }} .muted {{ color:var(--muted); }}
  .num {{ font-family:var(--mono); font-variant-numeric:tabular-nums; }}

  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; }}
  .kpi {{ padding:16px; }}
  .kpi-label {{ font-size:10px; color:var(--muted); text-transform:uppercase;
                letter-spacing:.14em; font-weight:600; }}
  .kpi-value {{ font-size:24px; font-weight:600; margin:4px 0 2px; }}
  .kpi-sub {{ font-size:12px; color:var(--muted); }}

  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  @media (max-width:900px) {{ .grid2 {{ grid-template-columns:1fr; }} }}

  .tw {{ overflow-x:auto; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th {{ text-align:left; color:var(--muted); font-weight:500; font-size:10px;
        text-transform:uppercase; letter-spacing:.1em; padding:7px 10px;
        border-bottom:1px solid var(--line); white-space:nowrap; }}
  td {{ padding:8px 10px; border-bottom:1px solid var(--line); }}
  tr:last-child td {{ border-bottom:none; }}
  tbody tr, table tr {{ transition:background .15s var(--ease); }}
  table tr:hover td {{ background:rgba(255,255,255,.03); }}
  .note {{ color:var(--muted); font-size:12px; margin:10px 0 0; }}

  /* ---- betslips ---- */
  .slips {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(min(440px,100%),1fr)); gap:14px; }}
  .slip {{ padding:0; overflow:hidden; }}
  .slip::before {{ content:''; position:absolute; inset:0 auto 0 0; width:3px; }}
  .slip.s-won::before {{ background:var(--green); }}
  .slip.s-lost::before {{ background:var(--red); }}
  .slip.s-open::before {{ background:var(--accent); }}
  .slip:hover {{ transform:translateY(-2px); border-color:rgba(255,255,255,.16); }}
  .slip-head {{ display:flex; gap:12px; align-items:center; padding:14px 16px 10px; flex-wrap:wrap; }}
  .slip-title {{ display:flex; flex-direction:column; min-width:0; }}
  .slip-title .muted {{ font-size:11.5px; }}
  .slip-odds {{ margin-left:auto; display:flex; flex-direction:column; align-items:flex-end; gap:3px;
                font-size:12px; }}
  .chip {{ background:var(--accent-soft); color:#aab3f5; border:1px solid rgba(94,106,210,.35);
           border-radius:20px; padding:1px 10px; font-size:12px; font-weight:600; }}
  .badge {{ font-size:10px; font-weight:700; padding:3px 9px; border-radius:20px;
            text-transform:uppercase; letter-spacing:.08em; flex:none; }}
  .badge.won {{ background:var(--green-soft); color:var(--green); }}
  .badge.lost {{ background:var(--red-soft); color:var(--red); }}
  .badge.open {{ background:var(--accent-soft); color:#aab3f5; }}
  .slip-legs {{ padding:4px 16px 14px; }}
  .leg {{ display:flex; align-items:baseline; gap:8px; padding:4px 0; font-size:13px;
          border-top:1px dashed rgba(255,255,255,.06); }}
  .leg:first-child {{ border-top:none; }}
  .ic {{ width:13px; height:13px; flex:none; align-self:center; }}
  .ic.ok {{ color:var(--green); }} .ic.bad {{ color:var(--red); }} .ic.dim {{ color:var(--muted); }}
  .leg-sel {{ font-weight:500; }}
  .leg-mkt {{ color:var(--muted); font-size:12px; }}
  .ss {{ font:600 9px/1 var(--mono); background:rgba(232,200,74,.14); color:var(--gold);
         border:1px solid rgba(232,200,74,.3); padding:2px 5px; border-radius:4px;
         letter-spacing:.05em; align-self:center; }}

  canvas {{ max-height:280px; }}

  /* ---- coverage ---- */
  .cov-row {{ display:flex; align-items:center; gap:10px; padding:3px 0; }}
  .cov-date {{ width:94px; flex:none; font-size:11.5px; color:var(--muted); font-family:var(--mono); }}
  .cov-cells {{ display:flex; gap:5px; flex-wrap:wrap; }}
  .cell {{ width:17px; height:17px; border-radius:5px; display:inline-block; cursor:pointer;
           transition:transform .15s var(--ease), box-shadow .15s var(--ease); }}
  .cell:hover, .cell:focus-visible {{ transform:scale(1.35); z-index:2; }}
  .c-won {{ background:var(--green); box-shadow:0 0 8px rgba(34,197,94,.5); }}
  .c-lost {{ background:var(--red); box-shadow:0 0 8px rgba(239,68,68,.4); }}
  .c-open {{ background:var(--accent); box-shadow:0 0 8px rgba(94,106,210,.5); }}
  .c-future {{ background:rgba(255,255,255,.08); }}
  .c-missed {{ background:rgba(239,68,68,.10); border:1px dashed rgba(239,68,68,.45); }}
  .cov-legend {{ display:flex; gap:18px; font-size:12px; color:var(--muted);
                 margin-bottom:12px; align-items:center; flex-wrap:wrap; }}
  .cov-legend span {{ display:flex; align-items:center; gap:6px; }}
  .cov-legend .cell {{ width:12px; height:12px; cursor:default; }}
  .cov-legend .cell:hover {{ transform:none; }}

  :focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; border-radius:4px; }}
</style></head><body>
<div class="blob b1"></div><div class="blob b2"></div>
<main>
<header class="hero">
  <div class="brand">{SVG_BALL}
    <div>
      <div class="eyebrow">World Cup 2026</div>
      <h1>Bet Tracker</h1>
      <div class="stamp">Generated {datetime.now().strftime('%a %d %b %Y, %H:%M')} · Paddy Power · £5 builders</div>
    </div>
  </div>
  <div class="hero-pl">
    <div class="lbl">Settled P/L</div>
    <div class="val num {pl_sign}" data-count="{pl:.2f}">{money(pl)}</div>
    <div class="sub num">Yield {roi:+.1%} on £{settled_stake:.2f} settled · staked £{total_staked:.2f} total</div>
  </div>
</header>

<div class="kpis">{kpis}</div>

<div class="grid2">
  {needs_panel}
  <section><h2>Near-miss accounting</h2><div class="panel">
    <div class="tw"><table><tr><th>Lost by one leg</th><th>Legs</th><th>Killer leg</th><th>Est. missed return</th></tr>
    {nm_rows}</table></div>
    <p class="note">P/L if every sole killer leg were dropped (per-leg odds estimated geometrically):
      <b class="num {'pos' if cf_pl >= 0 else 'neg'}">{money(cf_pl)}</b> vs actual {money(pl)}.
      £{nm_stake:.2f} of stakes died one leg short.</p>
  </div></section>
</div>

<div class="grid2">
  <section><h2>Bankroll vs luck</h2><div class="panel"><canvas id="curve"></canvas>
    <p class="note">Shaded band = 10th–90th percentile of a no-edge bettor placing your exact bets
    ({MC_SIMS:,} simulations). Dashed cone = open-bet range.</p>
  </div></section>
  <section><h2>Strike rate vs break-even</h2><div class="panel"><canvas id="strike"></canvas>
    <p class="note">At your average odds ({avg_odds:.2f}) you need {breakeven:.0%} winners to break even.</p>
  </div></section>
</div>

{coverage_panel}

{ghost_panel}

<div class="grid2">
  <section><h2>Leg analysis — what's killing me</h2><div class="panel">
    <div class="tw"><table><tr><th>Market type</th><th>W</th><th>L</th><th>Strike</th><th>Sole killer</th><th>Attr. P/L</th></tr>
    {leg_rows()}</table></div></div></section>
  <section><h2>Leg P/L attribution</h2><div class="panel"><canvas id="legchart"></canvas></div></section>
</div>

<div class="grid2">
  <section><h2>Builder archetypes</h2><div class="panel">
    <div class="tw"><table><tr><th>Archetype</th><th>Won</th><th>P/L</th><th>ROI</th></tr>
    {arch_rows()}</table></div></div>
    <h2>Kickoff time</h2><div class="panel">
    <div class="tw"><table><tr><th>Slot (UK)</th><th>Won</th><th>P/L</th></tr>{time_rows}</table></div></div></section>
  <section><h2>Super Sub tracker</h2><div class="panel">
    <div class="tw"><table><tr><th>Match</th><th>Pick</th><th>Result</th><th>Verified outcome</th></tr>
    {ss_rows}</table></div></div></section>
</div>

<section><h2>Bets</h2>
<div class="slips">{cards}</div></section>
</main>

<script>
Chart.defaults.color = '#8a8f9c';
Chart.defaults.borderColor = 'rgba(255,255,255,.06)';
Chart.defaults.font.family = "'Fira Sans', system-ui, sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(10,10,15,.92)';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,.12)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 10;
Chart.defaults.plugins.tooltip.titleFont = {{ family: "'Fira Code', monospace" }};
Chart.defaults.plugins.tooltip.bodyFont = {{ family: "'Fira Code', monospace" }};

const curveCtx = document.getElementById('curve').getContext('2d');
const grad = curveCtx.createLinearGradient(0, 0, 0, 280);
grad.addColorStop(0, 'rgba(34,197,94,.22)'); grad.addColorStop(1, 'rgba(34,197,94,0)');
new Chart(curveCtx, {{
  type: 'line',
  data: {{ labels: {json.dumps(cone_labels)}, datasets: [
    {{ label: 'no-edge p90', data: {json.dumps(p90)}, borderColor: 'transparent',
       backgroundColor: 'rgba(94,106,210,.13)', fill: '+1', pointRadius: 0, tension: .35 }},
    {{ label: 'no-edge p10', data: {json.dumps(p10)}, borderColor: 'transparent',
       fill: false, pointRadius: 0, tension: .35 }},
    {{ label: 'Cumulative P/L (£)', data: {json.dumps(curve_vals)}, borderColor: '#22c55e',
       borderWidth: 2.5, backgroundColor: grad, fill: true, tension: .35,
       pointBackgroundColor: '#22c55e', pointBorderColor: '#0a0a0f', pointBorderWidth: 2, pointRadius: 4 }},
    {{ label: 'if all open win', data: {json.dumps(cone_hi)}, borderColor: '#22c55e',
       borderDash: [5,5], borderWidth: 1.5, pointRadius: 3, fill: false }},
    {{ label: 'if all open lose', data: {json.dumps(cone_lo)}, borderColor: '#ef4444',
       borderDash: [5,5], borderWidth: 1.5, pointRadius: 3, fill: false }}
  ] }},
  options: {{ plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ grid: {{ color: c => c.tick.value === 0 ? 'rgba(255,255,255,.25)' : 'rgba(255,255,255,.06)' }} }} }} }}
}});
new Chart(document.getElementById('strike'), {{
  type: 'line',
  data: {{ labels: {json.dumps(curve_labels[1:])}, datasets: [
    {{ label: 'Actual strike %', data: {json.dumps(strike_vals)}, borderColor: '#22c55e',
       borderWidth: 2.5, tension: .25, fill: false,
       pointBackgroundColor: '#22c55e', pointBorderColor: '#0a0a0f', pointBorderWidth: 2, pointRadius: 4 }},
    {{ label: 'Break-even %', data: {json.dumps(needed_vals)}, borderColor: '#ef4444',
       borderDash: [6,5], borderWidth: 1.5, pointRadius: 0, fill: false }}
  ] }},
  options: {{ plugins: {{ legend: {{ display: true, labels: {{ boxWidth: 18, boxHeight: 2 }} }} }},
              scales: {{ y: {{ min: 0, max: 100 }} }} }}
}});
new Chart(document.getElementById('legchart'), {{
  type: 'bar',
  data: {{ labels: {json.dumps([k for k, _ in leg_sorted])},
           datasets: [{{ data: {json.dumps([round(v['pl'], 2) for _, v in leg_sorted])},
             borderRadius: 7, borderSkipped: false, maxBarThickness: 22,
             backgroundColor: {json.dumps(['rgba(239,68,68,.75)' if v['pl'] < 0 else 'rgba(34,197,94,.75)' for _, v in leg_sorted])} }}] }},
  options: {{ indexAxis: 'y', plugins: {{ legend: {{ display: false }} }} }}
}});

// count-up on the hero P/L (skipped under reduced motion)
if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {{
  document.querySelectorAll('[data-count]').forEach(el => {{
    const target = parseFloat(el.dataset.count);
    if (isNaN(target)) return;
    const fmt = v => (v < 0 ? '-£' : '£') + Math.abs(v).toFixed(2);
    const t0 = performance.now(), dur = 900;
    const tick = now => {{
      const p = Math.min((now - t0) / dur, 1), e = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(target * e);
      if (p < 1) requestAnimationFrame(tick);
    }};
    requestAnimationFrame(tick);
  }});
}}
</script>
</body></html>"""

    out = os.path.join(HERE, "dashboard.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote {out}  ({len(bets)} bets, {len(settled)} settled, balance {money(balance)}, "
          f"P/L {money(pl)}, fixtures {len(fixtures)})")


if __name__ == "__main__":
    main()
