# WC 2026 Bet Tracker — Claude Context

A screenshot-driven tracker + pick engine for World Cup 2026 bet builders
(Paddy Power, £5/bet, GBP, UK time). Goal: a bet on every one of the 104 WC
games, rich stats, a learnings vault, zero manual data entry for the user.

Live dashboard: https://emptycornmeal.github.io/wc2026-bets/
Repo: EmptyCornmeal/wc2026-bets (public). Every push auto-rebuilds the site.

The user runs this from two places — behave identically in both:
- **Desktop (Windows)**: Python is at `C:\Python314\python.exe` (plain
  `python` is NOT on PATH). `gh` is at `C:\Program Files\GitHub CLI\gh.exe`.
- **Mobile via claude.ai/code (Linux cloud)**: plain `python3 dashboard.py`
  works. Commit and push as normal; the Action deploys.

---

## How the user works with this tool

- Concise and direct. No padding, no "Great question!", no trailing recaps.
  Lead with the answer or the action.
- Opinionated picks. "No bet" is a valid output. Never vibes-only, never
  guarantees, no responsible-gambling filler.
- Lists over prose for options and analysis. Copy-paste-ready slips.
- The user's only jobs: ask for picks, place bets, paste screenshots, and
  deposit money. Everything else (parsing, filing, settling, learnings,
  regenerating, pushing) is Claude's job — do it without asking permission.
- When the user pastes a screenshot, act on it immediately: identify whether
  it's an open-bets page (→ log) or settled-bets page (→ settle).
- Surface interesting findings unprompted (e.g. "this is your third corners
  leg failure") — the user wants the tool to get smarter out loud.

---

## The full match lifecycle

### 1. Pick (the bet-maker process)
The user asks for bets on fixtures, often pasting their bookmaker board with
fractional prices. For each fixture:

1. **Establish match state first** — check the clock vs kickoff (UK time).
   Classify pre-match / imminent / live. Live changes everything: re-analyse
   from current score, minute, and stats; state minimum acceptable odds
   instead of quoting stale prices.
2. **Pull live Paddy Power anchor prices first**: run `odds.py` (e.g.
   `python odds.py scotland` or `--hours 36`). It returns PP match odds,
   totals where listed, and BTTS per fixture via The Odds API. These are the
   authoritative anchor prices — never quote research-article odds for
   match-odds/BTTS legs when the board disagrees. Bet-builder leg prices
   (player props, cards, corners) are NOT in the API; those come from web
   research or the user's board screenshot, and minimum-odds floors exist
   precisely because they're estimates.
   Key: `odds-api.local.key` (gitignored — NEVER commit it; the repo is
   public) or `ODDS_API_KEY` env var (set as a repo Actions secret, also
   usable in cloud sessions). Quota discipline: free tier = 500
   credits/month; a bulk board = 2 credits, BTTS lookups (1 each) only
   happen with a team filter or `--btts`. Check the printed quota.
   **Snapshots**: every run appends all prices seen to
   `data/odds_snapshots.csv`, and `.github/workflows/odds-snapshot.yml`
   does this server-side every 6 hours — this builds the closing-line
   record. Future analysis: compare odds at placement vs last pre-kickoff
   snapshot = closing line value (CLV), the honest edge metric. The cron
   bot commits to main; `git pull` before pushing local changes.
3. **Research via web search/fetch**: confirmed or predicted lineups,
   injuries/suspensions, recent form, tactical setups, venue factors
   (altitude, heat, roof, weather), referee card averages, player prop
   lines, market movement, expert/market consensus.
4. **Read the vault first**: scan `matches/*.md` Learnings sections and
   honour every #tagged rule (current rules summarised below). Picks must
   get smarter as the vault grows.
5. **Estimate true probabilities** — with the de-vigged market price as the
   PRIOR. The market is the best single forecaster in the room; any deviation
   from the de-vigged implied probability must cite a concrete reason
   (team news the line hasn't absorbed, referee profile, tactical mismatch).
   State an explicit probability per leg. Then run a **devil's-advocate
   pass**: argue the other side of each slip before finalising; if the
   counter-case is stronger than "variance", cut the leg. Never anchor on
   the user's lean — form the estimate first. Log the builder's estimated
   win probability in the match file frontmatter (`est_win_prob`) so
   calibration (Brier score) can be graded later. Evidence basis:
   docs/community-findings.md — LLM picks lose at the vig without these
   disciplines; calibration, not accuracy, is what pays.
6. **Output 2–4 builders per match**, tiered **Safer / Balanced-Best /
   Aggressive**. Each builder defaults to **3 legs** built from the soft-market
   spine (see House rules leg-selection hierarchy + result-leg policy); a 4th
   leg is opt-in and must itself be a soft/process leg. Each with: legs, target
   odds range, minimum odds floor, stake (units), confidence /10, why the legs
   belong together, weakest leg, what kills it, and pre-match/live validity.
   Then an **Avoid** section, live adjustment rules, and a clean final card.
7. Create `matches/<YYYY-MM-DD>-<home>-<away>.md` from `matches/TEMPLATE.md`
   with the pre-match read and frontmatter (confidence, predicted_weakest_leg,
   min_odds_floor, archetype, status: analysed).

**Placement timing**
- Never place the night before. Nothing is gained: anchors on short
  favourites don't drift up overnight, and team sheets land ~1h before
  kickoff. Lineup-dependent legs (goalscorer, player shots) are the reason
  three of four slips usually hinge on the XI.
- Softener (see docs/paddy-rules.md): a player who NEVER plays voids the
  leg and reprices the builder — it doesn't lose. The real lineup risk is
  a bench start with junk minutes, since any appearance makes the leg live.
- Ideal: one placing session after the earliest game's lineups drop, with
  fresh injury re-check. For overnight kickoffs the user will sleep
  through, either accept named-starter risk on near-nailed players only,
  or take the leg-reduced fallback shape stated on the card.
- Every card must state its fallback (which leg to drop) if the slip
  prices below the floor or a key starter is benched.

**House rules for builders**
- **DEFAULT = 3 LEGS** (changed 14 Jun after 8 settled slips). The habitual 4th
  leg was a failure-mode adder, not filler: across 7 losses, EVERY killer leg was
  an "outcome" leg, while "soft/process" legs went 11–2 (85%). A 4th leg is now
  the exception, not the rule — see the leg-count threshold bullet below.
- **Leg-selection hierarchy** (from the 8-bet leg scoreboard — soft markets win,
  outcome markets lose; mirrors docs/community-findings.md). Build the script
  from the TOP of this list down, not the bottom up:
  1. SOFT / PROCESS legs — the spine: cards (2–0), 1+ shots ON TARGET (3–0),
     corners (1–0), unders that fit the read (3–1), BTTS where the read supports
     it (2–1). These accrue even in a grind and don't depend on who wins.
  2. RESULT leg — see result-leg policy below; demoted, not a free anchor.
  3. BANNED as default legs (lottery / book-defended): anytime goalscorer (1–3),
     "team to score 2+" / team-over-1.5 (1–3, the lone win was a blowout),
     "2+ shots" non-SOT lines (0–1). If an attacking leg is wanted, use **1+ SOT**
     or "score-or-assist for the team's genuine shot/pen monopolist" — never a
     +200 anytime-scorer garnish (#goalscorer-lottery).
- **Result-leg policy** (match odds went 4–4 and killed 4 of 7 losses): include
  straight match-odds ONLY when the favourite is genuinely strong — roughly
  sub-1.6 AND not a two-way game. Otherwise take **double chance**, or DROP the
  result leg and build a pure soft-market script (Brazil proves it: its 3
  non-result legs all won). Any slip with est_win_prob ≤ 0.30 → double chance by
  default (#result-leg-can-kill).
- Unit staking 1–10: 1u small, 2u decent, 3u strong, 5u+ exceptional only.
  Aggressive builders capped at 1u. State total per-day exposure (~7–10u).
- Every rec carries a minimum odds floor; below it, "no builder at this
  price". The floor is enforced AT PLACEMENT — if the user's slip prices
  below the floor, say so before they place it.
- A 4th leg is OPT-IN, not default: it must be another SOFT/PROCESS leg (never a
  lottery leg), share the one game script, clear its own combined-odds threshold,
  AND not introduce a failure mode named in the match's own "what kills it" notes.
  If the only available 4th leg is an outcome/lottery leg, stay at 3.
- Archetypes (also the `archetype` column): favourite control, cagey unders,
  cards & fouls, corners pressure, siege script.
- Live adjustment defaults: 0-0 after 15' → unders/pressure legs strengthen;
  favourite scores early → don't chase short ML, wrap with suppression legs;
  underdog scores first → stand down unless favourite-pressure angles are
  priced; early red card → tear up all pre-match assumptions.

**Vault rules in force (keep this list updated when new learnings land)**
- #process-over-outcome (THE headline rule, 14 Jun, n=8 slips / 32 legs): soft /
  process legs (cards, corners, 1+ SOT, unders, BTTS) went 11–2 (85%); outcome
  legs (match odds, anytime scorer, team-2+, 2+ shots) went 7–12 (37%). In all 7
  losses, every killer was an outcome leg. Build the spine from soft markets;
  treat result + attacking legs as premium legs that must earn their place, not
  defaults. (Small sample, but matches docs/community-findings.md's prior — soft
  markets are where the book is laziest.) Drives the 3-leg default, the
  leg-selection hierarchy, and the result-leg policy in House rules above.
- #goalscorer-lottery: anytime-goalscorer / "2+ shots" props are coin-flips
  gated behind the team scoring at all (David, Pulisic, Akturkoglu, Shankland all
  lost; the only winner, Jimenez, was in the one slip where everything won). 1+
  SOT props went 3–0. Use 1+ SOT or score-or-assist for the monopolist — never a
  +200 anytime garnish.
- #clean-sheet-legs / #leg-redundancy: never stack a team-scores-zero leg on
  top of match odds + match unders — tiny price boost, huge new failure mode.
- #optional-legs: an optional leg must pass a risk test, not just the
  combined-odds price test (see Korea, 12 Jun — base builder won, optional
  leg lost the slip).
- #min-odds-discipline: minimum odds floors only work if checked at the till
  (see USA, 13 Jun — placed at 3.90 vs a 4.00 floor).
- #super-sub: goalscorer/shots legs with Super Sub get a free rescue lane —
  mildly favourable, but a defensive replacement can't rescue an attacking
  prop (USA, 13 Jun: Pulisic→Berhalter). And see the settlement red-herring
  rule below.
- #suppression-legs / #live-entry: after an early favourite goal, the value
  lives in opponent-suppression legs (BTTS No, team unders), not the ML.
- #result-leg-can-kill (SUPERSEDES the old #killer-is-never-the-result): the
  match-odds leg held through the first 3 losses, but on 13 Jun it killed twice
  in one night — Brazil (1-1, SOLE killer on a 1.64 favourite) and Qatar (1-1).
  Do NOT treat the result leg as a free anchor. On low-conviction short
  favourites (sub-~1.7) in genuinely two-way games, or any slip with
  est_win_prob ≤ 0.30, default the result leg to DOUBLE CHANCE unless there is a
  concrete reason the favourite wins outright (the non-result legs all landed in
  Brazil — the win leg was the liability).
- #single-goal-collapse / #correlated-volume-trap: stacking legs that all depend
  on the same scoreline (match-odds + BTTS No + team-goals-over, or over 2.5 +
  team-over-1.5 + a goalscorer leg) is ONE bet wearing multiple hats — a single
  goal (Qatar 90+5) or a single grind (Haiti 1-0) voids them together. Both 13
  Jun multi-leg losses died this way. When the read names a grind/low-scoring
  risk, swap volume legs for PROCESS legs (corners, SOT, cards) that bank even
  in a 1-0 win — the Safer lines in both match files would have won.
- #prop-role-fit / #striker-roulette: price a player prop to the player's
  ACTUAL job. A "2+ shots" line on a creator (Pulisic: 2 assists, rested at
  half) or an anytime-scorer leg in a two-striker side (Canada: David
  assisted, Larin scored) is worse than the price implies. Prefer "score or
  assist", the team's shot/pen monopolist, or a 1+ line.
- #named-kill-condition: if the pre-match read names a specific failure mode,
  don't bet straight through it — anchor with double chance or cut confidence
  (Canada & Korea both died on the exact set-piece risk we wrote down).

### 2. Log (user pastes open-bets screenshot)
- Parse each slip → one row in `data/bets.csv` + one row per leg in
  `data/legs.csv` (schemas below).
- Deposits convention: the user deposits £5 per game bet. Add a row to
  `data/deposits.csv` when they confirm (or batch rows by date).
- Update the match file: fill "The bet" (legs, odds, stake, which analyst
  tier was taken, whether floors/thresholds were respected), set
  frontmatter `bet_id` and `status: placed`.

### 3. Settle (user pastes settled-bets screenshot)
- Read per-leg green **W** / red **L** markers and the Returns figure.
- Update bets.csv (`status`, `actual_return`, `profit_loss`) and legs.csv
  (`result` per leg).
- **Verify against real match data (web search)**: final score, scorers,
  player shot stats, cards, corners. Two reasons: (a) confirm leg readings,
  (b) the Super Sub red herring below.
- Write "Result" and "Learnings" in the match file (`status: won|lost`).
  Learnings MUST state whether `predicted_weakest_leg` was the actual
  killer, and end with one transferable #tagged lesson. If a new rule
  emerges, add it to the "Vault rules in force" list above.

### 4. Regenerate
```
# Windows:  & 'C:\Python314\python.exe' dashboard.py
# Cloud:    python3 dashboard.py
```
Stdlib only, no pip installs. Output: `dashboard.html`.

### 5. Publish
Commit and push after every data/match-file change. The GitHub Action
rebuilds and deploys the live site (~20s). Commit messages: short,
descriptive, e.g. "Settle Canada v Bosnia: won, +£29.79".

---

## Data model (`data/`, parent/child keyed on bet_id)

**bets.csv** — one row per slip:
`bet_id,date_placed,kickoff,match,home_team,away_team,odds_fractional,
odds_decimal,stake,potential_return,status,actual_return,profit_loss,
num_legs,bookmaker,archetype,notes`
- `bet_id` = bookmaker's Bet ID verbatim (e.g. `O/7913296/0000300`).
- `kickoff` = `YYYY-MM-DD HH:MM` UK time.
- `status`: Open / Won / Lost / Void / Cashed Out.
- `profit_loss` = actual_return − stake (blank while Open).

**legs.csv** — one row per leg:
`bet_id,leg_num,market_type,market_detail,selection,result,super_sub,notes`
- `market_type` taxonomy (keep consistent, used by all analysis): Match Odds,
  Goalscorer, Total Goals O/U, Team Goals O/U, BTTS, Corners, Cards,
  Player Shots.
- `market_detail` = bookmaker's market name verbatim.
- `result`: Open / Won / Lost / Void.

**deposits.csv**: `date,amount,note` — own money in.

**fixtures.csv**: `match_id,date,kickoff_uk,stage,group,home_team,away_team,
city` — all 104 fixtures; drives the coverage map and "needs a bet" panel.
Knockout rows use placeholders (1A, W73, "3rd A/B/C/D") — **update them with
real teams as the bracket resolves**.

Team-name matching uses the alias map in `dashboard.py` (`ALIASES`) — extend
it if a bookmaker name doesn't match fixtures.csv (e.g. "Bosnia-Herzegovina"
→ "bosnia").

---

## Parsing rules

- Fractional → decimal: `a/b → a/b + 1` (e.g. 2.54/1 → 3.54; 5.96/1 → 6.96).
- Settled slips: green W / red L icon per leg. A lost bet's killer leg(s) =
  its losing legs; exactly one loser = "sole killer" (tracked in analysis).
- Cashed-out: status Cashed Out, actual_return = cash-out amount.
- **Super Sub is a red herring**: settled slips ALWAYS display the substitute
  beside the original pick, whether or not the sub mattered. On settlement,
  check match data (scorers, shot stats) to determine if the original player
  landed the leg or the sub genuinely saved it. Record the verified outcome
  in the leg's notes ("X scored himself; SS display cosmetic" vs "sub saved
  the leg") and in the match file.

---

## matches/ — the learnings vault

One file per fixture bet on: `YYYY-MM-DD-home-away.md` (lowercase,
hyphenated, UK-date of kickoff). Frontmatter: match, kickoff, stage, bet_id,
archetype, confidence (n/10), predicted_weakest_leg, min_odds_floor,
status (analysed | placed | won | lost).

Sections: **Pre-match read** (written before kickoff, never edited after —
it's the honest record), **The bet**, **Result**, **Learnings**.

---

## Analysis conventions (mirrored in dashboard.py)

- ROI = P/L ÷ settled stake (not total staked).
- Leg P/L attribution: won bets spread P/L evenly across legs; lost bets
  charge the loss only to the losing leg(s).
- Account balance = deposits − total staked + settled returns.
- Break-even strike rate = 1 / average decimal odds of settled bets.
- The bankroll chart's shaded band = Monte Carlo of a no-edge bettor placing
  the same bets at book-implied probability (seeded, deterministic).
- Near-miss counterfactual estimates per-leg odds geometrically
  (leg ≈ total^(1/n)) — always label it an estimate.

---

## Reference docs

- `docs/paddy-rules.md` — Paddy Power settlement rules: void vs lose for
  player legs, Super Sub exact mechanics, Opta gotchas (woodwork ≠ SOT,
  corners taken not awarded, own goals don't count), promos incl. Bet
  Builder Insurance. Consult BEFORE settling and when constructing legs.
- `docs/improvements.md` — research-driven backlog and the honest economics
  of bet builders (15–30% hold; humility required).
- `docs/community-findings.md` — Reddit/forum lived experience (soft markets:
  corners, early props; PP quirks; tilt rules) and the tracked-LLM-betting
  evidence that motivates the de-vig prior, devil's-advocate pass, and
  calibration logging in the pick process.

## Don'ts

- Don't ask permission for steps that are part of the lifecycle — just do
  them and report.
- Don't edit a Pre-match read after kickoff.
- Don't credit a Super Sub without match-data verification.
- Don't recommend a slip below its minimum odds floor without flagging it.
- Don't add optional legs that fail the risk test, whatever the price.
- Don't pip-install anything for dashboard.py — it's stdlib only by design.
- Don't draw conclusions from tiny samples without saying so (n is small
  until the group stage ends).
- Don't touch the user's separate `football-predictor` project (local
  machine only) — last season's Poisson/Kelly system, not part of this repo.
- This repo is PUBLIC. Never commit personal information: no emails, no
  account names beyond this repo's owner, no employer references, no
  local user-profile paths. Chat exports and scratch notes stay local
  (gitignored).
