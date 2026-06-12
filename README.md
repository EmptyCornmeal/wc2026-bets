# WC 2026 Bet Tracker ⚽

A screenshot-driven tracker for World Cup 2026 bet builders. One £5 builder per game,
all 104 games, with the stats to prove whether there's any edge at all.

**Live dashboard:** deployed via GitHub Pages from `dashboard.html` (rebuilt automatically
on every push by the workflow in `.github/workflows/deploy.yml`).

## How it works

- `data/bets.csv` + `data/legs.csv` — parent/child bet store, parsed from bookmaker slip screenshots
- `data/deposits.csv` — own-money ledger
- `data/fixtures.csv` — all 104 WC fixtures (drives the coverage map)
- `matches/` — one markdown file per match: pre-match analysis, the bet, result, learnings
- `dashboard.py` — generates `dashboard.html` (no dependencies, stdlib only)

```
python dashboard.py
```

The full workflow (pick → log → settle → learn) is documented in `CLAUDE.md` and is
designed to be driven by Claude Code — locally or from claude.ai/code on mobile.
