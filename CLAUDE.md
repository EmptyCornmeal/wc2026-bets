# WC 2026 Bet Tracker — Claude Context

A screenshot-driven tracker + pick engine for World Cup 2026 bet builders
(Paddy Power, £5/bet, GBP). Goal: a bet on every one of the 104 WC games,
rich stats, a learnings vault, zero manual data entry.

## The full match lifecycle

1. **Pick** — the user asks for bets on upcoming fixtures (often pasting their
   bookmaker board with prices). Run the bet-maker process (below), create
   `matches/<date>-<home>-<away>.md` from `matches/TEMPLATE.md` with the
   pre-match read, recommended builders, confidence (1–5) and
   `predicted_weakest_leg` in frontmatter.
2. **Log** — the user places a bet and pastes a screenshot of their open-bets
   page. Parse each slip into `data/bets.csv` + `data/legs.csv`, add a £5 row
   to `data/deposits.csv` if the user deposited for it (their convention: £5
   deposited per game bet), and fill "The bet" in the match file
   (status: placed, bet_id).
3. **Settle** — the user pastes their settled-bets screenshot. Read per-leg
   W/L markers + Returns; update both CSVs, then write "Result" and
   "Learnings" in the match file (status: won/lost). Learnings must say
   whether `predicted_weakest_leg` was the actual killer, and end with one
   transferable, #tagged lesson.
4. **Regenerate** after any data change:
   ```powershell
   & 'C:\Python314\python.exe' dashboard.py
   ```
   Output: `dashboard.html` (dark self-contained page, Chart.js CDN).

## The bet-maker process (picks)

- Establish match state first (check system clock vs kickoff — pre-match,
  imminent, or live). Then web-research: lineups, injuries, form, tactics,
  venue (altitude/heat), referee card averages, player prop lines, odds.
- Estimate true probabilities, compare vs implied from board prices; only
  recommend plausible edge. "No bet" is a valid output.
- Builders: 2–4 per match, tiered Safer / Balanced-Best / Aggressive. One
  game script per slip — correlated legs only. Every rec carries minimum
  odds, the weakest leg, and "what kills it". Always include an Avoid list.
- Before picking, **read the Learnings sections of settled match files** and
  honour the #tagged rules (e.g. #clean-sheet-legs: never stack a
  team-scores-zero leg on match odds + match unders). The vault is the
  feedback loop — picks must get smarter as it grows.
- Direct, opinionated tone; copy-paste-ready slips; no responsible-gambling filler.

## Data model (`data/`, parent/child keyed on bet_id)

- **bets.csv** — one row per slip. `bet_id` = bookmaker's Bet ID.
  `odds_fractional` verbatim; `odds_decimal` = a/b + 1.
  `status`: Open / Won / Lost / Void / Cashed Out.
  `profit_loss` = actual_return − stake (blank while Open).
  `archetype`: favourite control / cagey unders / cards & fouls /
  corners pressure / siege script.
- **legs.csv** — one row per leg. `market_type` taxonomy (keep consistent):
  Match Odds, Goalscorer, Total Goals O/U, Team Goals O/U, BTTS, Corners,
  Cards, Player Shots. `market_detail` = bookmaker's market name verbatim.
  `super_sub: yes` when the badge shows; note player swaps in notes.
- **deposits.csv** — own money in: date, amount, note.
- **fixtures.csv** — all 104 WC fixtures (match_id, date, kickoff_uk, stage,
  group, home_team, away_team, city). Drives the coverage map and
  "needs a bet" panel. Knockout rows use placeholders until teams known —
  update them as the bracket fills in.

## matches/ — the learnings vault

One markdown file per fixture bet on, named `YYYY-MM-DD-home-away.md`
(lowercase, hyphenated). Frontmatter drives future tipster-grading:
`confidence`, `predicted_weakest_leg`, `status: analysed|placed|won|lost`.
Pre-match read is written before kickoff and never edited after — it's the
honest record of what we believed.

## Parsing rules

- Fractional → decimal: `a/b → a/b + 1` (e.g. 2.54/1 → 3.54).
- Settled slips show green W / red L per leg — read these for leg results.
- A lost bet's killer leg(s) = its losing legs; sole killers are tracked.
- Cashed-out: status Cashed Out, actual_return = cash-out amount.
- **Super Sub is a red herring**: settled slips always display the substitute
  next to the original pick, whether or not the sub mattered. On settlement,
  check actual match data (goalscorers, player shot stats) to determine if the
  original player landed the leg or the sub genuinely saved it; record the
  verified outcome in the leg's notes and the match file.

## Analysis conventions

- ROI = P/L ÷ settled stake (not total staked).
- Leg P/L attribution: won bets spread P/L evenly across legs; lost bets
  charge the loss only to the losing leg(s).
- Account balance = deposits − total staked + settled returns.
- Near-miss counterfactual estimates per-leg odds geometrically
  (leg ≈ total^(1/n)) — labelled as an estimate, not truth.

## Related

- `C:\Users\myles\football-predictor` — last season's Poisson/Kelly project; not used here.
