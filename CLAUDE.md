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
   research or the user's board screenshot — they are ESTIMATES until the
   user's slip confirms them, so the value/EV check (House rules) is enforced
   at the board, not at estimate time (see #value-not-floor).
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
   odds range, realistic landing % + honest EV read (true% vs implied price),
   stake (units), confidence /10, why the legs belong together, weakest leg, what
   kills it, and pre-match/live validity.
   Then an **Avoid** section, live adjustment rules, and a clean final card.
7. Create `matches/<YYYY-MM-DD>-<home>-<away>.md` from `matches/TEMPLATE.md`
   with the pre-match read and frontmatter (confidence, predicted_weakest_leg,
   archetype, est_win_prob, status: analysed). `min_odds_floor` is a LEGACY
   field — keep as an optional guidance target, no longer a hard gate
   (#value-not-floor).
8. **Log every generated tier to the ghost ledger** (`data/ghost_bets.csv` +
   `ghost_legs.csv`) as pre-registered ghosts with `status: Open` — the Safer /
   Balanced-Best / Aggressive builds AND the one that gets placed. These are the
   zero-hindsight gold standard; settle them blind when results land (Settle
   step). Schema + integrity rule are in the Ghost ledger section.

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
- Every card must state its fallback (which leg to drop) if the slip prices
  poorly (a dead-weight short leg, or combined below its guidance target) or a
  key starter is benched.

**House rules for builders**
- **⭐ REFINED METHODOLOGY (19 Jun — validated by 4 independent deep-research reports
  [Copilot/Gemini/Perplexity/ChatGPT] cross-checked against our 33-bet dataset; full
  evidence in docs/community-findings.md). This block SUPERSEDES the older rules below
  where they conflict:**
  1. **DEFAULT = 2 LEGS** (DC-or-strong-win + ONE primary-monopolist 1+ SOT). The
     bookmaker hold compounds ~8-10% at 2 legs → ~15-19% at 4, plus a same-game
     correlation tax on top. Our 4-leg record is 0/21 — that's the math, not variance.
  2. **3 LEGS = exception** — only with a genuinely correlated read or a Power Up to
     offset the extra hold. **4+ LEGS BANNED** from the system (free-bet longshots aside).
  3. **Result leg = DOUBLE CHANCE** on any two-way game — but framed honestly as
     VARIANCE CONTROL, not edge. Our 7-0 DC is small-sample variance, NOT proof of
     value (all 4 reports agree). Straight win ONLY for a genuinely strong/underpriced
     favourite (~sub-1.4).
  4. **Legs in ~1.3-1.7.** The band is a discipline/variance heuristic, not an edge.
     NEVER a sub-1.20 dead-weight filler (it adds compounded vig for ~no payout).
  5. **Prop leg = the PRIMARY, nailed, focal shooter's 1+ SOT only** (penalty/set-piece
     duty a plus). Never a secondary striker, sub, or weak-team lone outlet
     (#two-sot-doubles-risk, #prop-role-fit). NEVER two SOT legs.
  6. **🆕 TEST player FOULS / TACKLES as the 3rd-leg market** — flagged by the research
     as softer than SOT (referee + tactics driven, thinly modelled). Cross-reference the
     WC referee's foul/card average + the winger-vs-fullback matchup. Untested by us — log
     results to see if it's a real edge before trusting it.
  7. **Promos = the only realistic path to break-even.** Power Ups → 2-leg CASH bets.
     Free bets are stake-not-returned → deploy on the LONGEST slip (~4.5+ odds; raw EV
     maximised at long odds). Ignore acca insurance if it forces extra legs.
  8. **Super Sub = mild tiebreaker ONLY** (prefer the SS-badged version between equal
     legs). Our data is 0-rescues-in-19; do NOT chase it as a selection driver despite
     one report's enthusiasm (#super-sub).
  9. **Track leg-level CLV** (placement vs last pre-KO snapshot) as the real scorecard —
     builder-level CLV is unmeasurable (opaque correlation pricing). P/L is noise at this n.
  10. **Honest ceiling: −2% to −15% yield; break-even only via promo subsidy.** The goal
      is MINIMISE THE BLEED, not mythical +EV. "Bet every game" is the biggest single EV
      leak (all 4 reports) — kept for now as the project charter, but it IS a known cost.

**House rules for builders (legacy detail — see refined block above; kept for context)**
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
- **No hard min-odds floor** (revised 14 Jun — the floor was a blunt proxy that
  blocked playable coverage bets; the user pushed back and is right). The project
  bets EVERY game, so the gate is not a price threshold. The two real gates are:
  (a) **no dead-weight leg** — drop any leg shorter than ~1.10 that only adds vig
  without payout or a genuine correlation boost (e.g. Havertz 1+ SOT @ 1.07 vs
  Curacao: adds 7% price for 7% bust-risk, ~neutral, cut it); and (b) an honest
  **value/EV check** — state each slip's realistic LANDING % and whether we think
  combined true prob beats the implied price (1/odds). If yes it's a value bet; if
  not it's a coverage/fun bet, placed flat and small and LABELLED as such — never
  dressed up as +EV. A "min target" price can still be quoted as guidance, but it
  is not a hard block. The one genuinely good-value bet is a FREE BET (no stake at
  risk) — always deploy it on the longest-priced slip.
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
- #cards-over-trap (15 Jun, n=2 same night): "Over 4.5 total cards" (5+) is a SWING
  leg, NOT a soft banker — it was the SOLE KILLER of both slips it was in (Ivory
  Coast 4 cards under Oliver; Sweden just 1 card under Falcón Pérez, a 5.3-YC/g
  ref). Referee YC/game averages do NOT imply 5+ cards every game — counts are
  high-variance and ours came in low. The card legs that have WON were "one team
  over 1.5 cards" (2+ from the carded side), short and high-prob — use that, never
  total-5+. Also VERIFY THE REF near kickoff: the IC ref was Oliver, not Letexier
  as researched — a materially less strict whistle that the pre-match read missed.
- #corners-line-swing (15 Jun): against a heavy favourite take the LOWER corners
  line (O8.5/O9.5), not O10.5+. Germany won the corner count 8–1 but only 9 total
  and the O10.5 (11+) leg was the sole killer; the O8.5 ghost won. Dominant sides
  convert pressure into goals, not corners, and coast once ahead.
- #clean-sheet-legs / #leg-redundancy: never stack a team-scores-zero leg on
  top of match odds + match unders — tiny price boost, huge new failure mode.
- #optional-legs: an optional leg must pass a risk test, not just the
  combined-odds price test (see Korea, 12 Jun — base builder won, optional
  leg lost the slip).
- #value-not-floor (supersedes #min-odds-discipline, 14 Jun): a bet "makes money"
  only if true_prob × decimal_odds > 1. Stacking "certain" short legs does NOT
  print — the book bakes a 15–30% builder hold into the price, so each near-certain
  leg is priced at ~its true chance minus margin, and that margin COMPOUNDS per
  leg. Short ≠ safe value. Judge a slip on (true % vs implied price) and
  dead-weight legs, not a fixed floor. Free bets are the exception — house money,
  can only win, so longer odds = more retained value.
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
- #est-prob-gate-violated (15 Jun, 0/4 night): the est_win_prob ≤ 0.30 ⇒ double-chance
  rule (#result-leg-can-kill) is MECHANICAL, not advisory. On 15 Jun we placed straight
  match-odds in BOTH Saudi (est 0.28) and Belgium (est 0.30) builds despite logging
  estimates at/under the gate — and both result legs lost (Uruguay 1-1, Belgium 1-1).
  Three sub-1.6 favourites (Uruguay, Belgium, Spain) all failed to win on the same
  slate. If est_win_prob ≤ 0.30, the placed build's result leg MUST be double chance,
  no "but it's a 1.44 favourite" exception — that exception IS the trap.
- #parked-bus-goals-trap (QUANTIFIED 21 Jun via data/match_stats.csv: 10 of 36 group
  games had a side take 15+ shots for <=1 goal -- ~28%, NOT rare; Spain/Ecuador/Turkey x2/
  Uruguay/Switzerland all featured). Vs a deep block the favourite-WIN and goals-OVER legs
  carry ~1-in-4 shutout risk regardless of shot dominance; only the fav's own SOT survives.
- #parked-bus-goals-trap (15 Jun, Spain 0-0 Cape Verde): vs a deep damage-limitation
  block, NEVER anchor on goals-over or opponent-cards legs. A bus that barely fouls
  (CV: 1 foul ALL GAME, a WC record) gives no cards, and 27 shots can yield zero goals
  when the keeper is inspired. The soft markets that bank are the favourite's OWN
  process — shots on target and team corners. The Safer ghost (Oyarzabal SOT + Spain
  O4.5 corners) WON; our value-reshape INTO Over 3.5 + CV cards lost. Caution on
  #value-not-floor: chasing a longer price by trading siege legs for outcome/volume
  legs turns a winning shape into a loser. Shot volume ≠ goals.
- #unders-need-two-blunt-attacks (16 Jun, Iran 2-2 NZ): an Under 2.5 leg requires BOTH
  sides to be low-output. "NZ fail to score in 6 of 9" was not cover when NZ's Just
  scored a clean brace; the unders thesis (Iran blunt vs blocks + NZ toothless) needed
  to suppress BOTH attacks and only addressed one. Pair unders only when the read can
  realistically silence both teams — otherwise demote to a team-unders or a process leg.
  (The correctly-demoted Iran DC + Taremi SOT both won; the total was the sole killer.)
- #corners-not-a-banker (16-17 Jun, n=4 same slate): the LOW-line O4.5 *team* corners
  leg is a SWING, not the reliable spine anchor I'd treated it as. It went 2-4 across
  the night and was the SOLE KILLER of both losses — Argentina (3-0 win, ≤4 corners)
  and Austria (2-1, just 3 corners) — while landing for France (6, chased until 66')
  and Norway (5+, 4-1 rout). The mechanism extends #corners-line-swing: **a heavy
  favourite that scores early and coasts manages the game instead of generating
  corners; a deep block doesn't auto-concede them either.** Corners need sustained
  pressure (a rout still chasing, or a team behind). Same night, 1+ SOT went 4-4 and
  match-odds 4-4 — so the reliable spine is 1+ SOT (elite) + result-leg-for-strong-favs;
  corners should be treated as the swing leg, not a banker. (Counterweight to the
  "drop the result leg" audit thesis — tonight all favs won and the soft corners leg
  was the villain; sample-dependent, don't over-fit either way.)
- #two-sot-doubles-risk (17 Jun, 0/5 night): the "two 1+ SOT legs" spine I introduced to
  replace corners BUSTED on the second SOT leg in BOTH games it was used — Suárez (2nd
  striker, Colombia, killer) and Bruno/Ronaldo (blunt Portugal, both blanked). Stacking
  two SOT legs does NOT de-risk; it MULTIPLIES exposure (≈0.78² ≈ 60%), and the second
  player (secondary striker, sub, or a weakened team's lone outlet) is usually the worse
  bet. The PRIMARY monopolist SOT is elite (Kane brace, Díaz scored, Rashford+Bellingham
  scored — all won the same night); the MARGINAL SOT is the bust (Suárez, Semenyo of a
  Kudus-less Ghana, Saka off the bench — all lost). Robust shape: ONE primary-monopolist
  1+ SOT + a result/process leg, NOT two SOT. Also #prop-role-fit: a 1+ SOT leg is only
  as good as the player's role AND the team's attacking health.
- #read-dependent-third-leg (17 Jun): across the 0/5 night the placed builds repeatedly
  won their two trusted legs (DC + monopolist SOT) and died on the READ leg — England
  Under 2.5 (4-2 thriller, read was "cautious XI = low-scoring", wrong). The England
  Safer ghost (DC + Kane, no Under) WON, as did several past Safer ghosts. Pattern over
  weeks: the 2-leg "DC + primary SOT" spine keeps cashing while the speculative 3rd leg
  (Under/corners/2nd-SOT) keeps killing. Strongly suggests the PLACED default should be
  the 2-leg Safer spine — flagged for the methodology review (do WITH user at keyboard).

### 2. Log (user pastes open-bets screenshot)
- Parse each slip → one row in `data/bets.csv` + one row per leg in
  `data/legs.csv` (schemas below).
- Deposits convention: the user deposits £5 per game bet. Add a row to
  `data/deposits.csv` when they confirm (or batch rows by date).
- **Free bets** (e.g. Bet Builder Insurance refunds): log with `stake = 0.00`
  (no OWN cash at risk) and `potential_return`/`actual_return` = the slip's
  WINNINGS-ONLY figure (PP shows it; = notional × (odds − 1), no stake back). So
  `profit_loss` is the full return on a win, 0 on a loss. Do NOT add a deposit
  row for a free bet — it is not own money. Put "£X FREE BET" in `notes`. This
  keeps `balance = deposits − staked + returns` honest (verified: a £5 free bet
  must not subtract £5 of cash from the balance).
- In the ghost ledger, the build that got placed was already logged as a ghost
  at analysis time (Pick step 8) — leave the other tiers as Open ghosts to settle
  later.
- Update the match file: fill "The bet" (legs, odds, stake, which tier was
  taken, whether the value/EV bar was respected), set frontmatter `bet_id` and
  `status: placed`.

### 3. Settle (user pastes settled-bets screenshot)
- Read per-leg green **W** / red **L** markers and the Returns figure.
- Update bets.csv (`status`, `actual_return`, `profit_loss`) and legs.csv
  (`result` per leg).
- **Verify against real match data (web search)**: final score, scorers,
  player shot stats, cards, corners. Two reasons: (a) confirm leg readings,
  (b) the Super Sub red herring below.
- **Settle the ghost ledger for this fixture too**: every Open ghost in
  `ghost_bets.csv`/`ghost_legs.csv` settles BLIND from the same verified match
  data — set each ghost leg `result`, then the ghost `status` / `actual_return`
  / `profit_loss`. This is what makes the tier A/B compound. Estimate a ghost's
  odds only where no board price existed, and FLAG it in the note.
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

**match_stats.csv**: per-game stats (shots, SoT, possession, fouls, cards,
corners, winner) for every settled WC game — the CANONICAL source for settling
corners/cards/team-SoT legs and for analysis; do NOT web-guess these. Maintained by
the user; ingested 21 Jun.

**golden_boot.csv**: live scorer list (player, country, goals) — used to confirm a
team's shot MONOPOLIST for SOT legs (top scorers = best 1+ SOT candidates). The
"Entrant" column from the source is DROPPED (colleagues' real names; repo is public).

**Source — user's Google Sheet (READ-ONLY, never edit it).** Both files mirror tabs in
`docs.google.com/spreadsheets/d/1bwXMIDUFiwmr-SjUsHon9vwXwKmpvQV6`. Refresh via the CSV
export endpoint `…/export?format=csv&gid=<GID>` (WebFetch returns a one-time signed
redirect — follow it): **Match Data gid=488320594**, **Golden Boot gid=1094671927**. The
Match Data tab also contains the FULL forward fixture schedule (every game to the Final,
blank rows = upcoming) — use it for upcoming picks + to resolve knockout fixtures.csv
placeholders as the bracket fills in.

**fixtures.csv**: `match_id,date,kickoff_uk,stage,group,home_team,away_team,
city` — all 104 fixtures; drives the coverage map and "needs a bet" panel.
Knockout rows use placeholders (1A, W73, "3rd A/B/C/D") — **update them with
real teams as the bracket resolves**.

**ghost_bets.csv** (paper trades — NEVER affects real P/L or balance):
`ghost_id,date_logged,kickoff,match,basis,builder_label,linked_bet_id,
odds_decimal,notional_stake,status,actual_return,profit_loss,num_legs,note`
- `ghost_id` = `G<betnum>-<tag>` (e.g. `G0304-SAF`, `G0301-NM`).
- `builder_label` (keep EXACT — feeds the dashboard tier table): `Safer` /
  `Balanced-Best rec` / `Aggressive` / `base 3-leg sans optional` /
  `new-method 3-leg soft spine`.
- `basis` = registration type, e.g. `pre-registered tier blind-settle` (gold
  standard) or `retro-method ...` (flag any hindsight).
- `notional_stake` = £5 paper; `odds_decimal` estimated where no board price.

**ghost_legs.csv**: `ghost_id,leg_num,market_type,selection,result,note`
(`result`: Open / Won / Lost / Void).

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
archetype, confidence (n/10), predicted_weakest_leg, est_win_prob,
min_odds_floor (legacy — see #value-not-floor), status (analysed | placed |
won | lost).

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

## Ghost ledger (paper trades for data) — `data/ghost_bets.csv` + `ghost_legs.csv`

We place one real bet per game but generate several builders. The ghost ledger
records the builders we DIDN'T place (other tiers, alternative methods) and
settles them on paper — multiplying the sample for analysis without risking money.
Separate files; NEVER touches bets.csv / balance / real P/L.

**The integrity rule (non-negotiable — without it the data is worthless):**
- A ghost's legs must be **PRE-REGISTERED** — they appear in the match file's
  Pre-match read (locked before kickoff) and are settled **BLIND**. Constructing a
  "build that would've won" after seeing the result is curve-fitting, the exact
  self-deception docs/community-findings.md warns about. Don't do it.
- Retrospective ghosts may only use selections present in that game's pre-match
  read. Any leg-choice influenced by knowing the result, or any odds that are
  estimated (no board price), gets FLAGGED in the note. Flagged ghosts don't count
  toward headline edge stats.
- Settle ghost legs from the same verified match data used for real settlement.

**Going forward:** when analysing a game, log every tier generated (Safer /
Balanced / Aggressive + the placed build) to the ghost ledger as pre-registered
ghosts. The placed one is also a real bet; the rest stay ghosts. This is the gold
standard — zero hindsight — and it's how the ledger should mainly grow.

**First backfill (14 Jun) — retro-method A/B on the 8 settled games:** the
new-method 3-leg soft-spine build (pre-registered legs, blind-settled) went **5–3
(~+£43 paper at estimated odds) vs the actual 1–7 (−£22.29)**. It rescued 4 of 7
real losses (Korea, Canada, Brazil via dropped-lottery + double-chance; USA with a
flagged hindsight leg) but still LOST 3 (Qatar — no winning soft 3rd leg; Haiti —
McTominay 0 SOT; Australia — fav lost outright so even DC fails). Honest signal:
the method change has real teeth but is NOT a silver bullet. Odds estimated, n=8,
USA mildly hindsight-tainted — treat as suggestive, not proof.

**Dashboard panel is LIVE** ("Ghost ledger — unplaced builds"). Tier A/B across
all 24 backfilled ghosts: **new-method soft spine 5/8, base-3-leg 2/4, Safer 1/4,
Balanced-Best 0/4, Aggressive 0/4** — the new spine beats every old tier, and the
builds we actually placed (Balanced-Best) went 0/4. The ledger now grows
automatically: log each game's tiers at analysis (Pick step 8), settle them blind
when results land (Settle step).

## Reference docs

- `docs/paddy-rules.md` — Paddy Power settlement rules: void vs lose for
  player legs, Super Sub exact mechanics, Opta gotchas (woodwork ≠ SOT,
  corners taken not awarded, own goals don't count), promos incl. Bet
  Builder Insurance. Consult BEFORE settling and when constructing legs.
- `docs/improvements.md` — research-driven backlog and the honest economics
  of bet builders (15–30% hold; humility required).
- `docs/readiness.md` — graded go-live checklist (P0 blockers → P3 monitors).
  Check it at the start of an autonomous/maintenance session; tick items as done.
- `docs/community-findings.md` — Reddit/forum lived experience (soft markets:
  corners, early props; PP quirks; tilt rules) and the tracked-LLM-betting
  evidence that motivates the de-vig prior, devil's-advocate pass, and
  calibration logging in the pick process.

## Don'ts

- Don't ask permission for steps that are part of the lifecycle — just do
  them and report.
- Don't edit a Pre-match read after kickoff.
- Don't credit a Super Sub without match-data verification.
- Don't auto-settle REAL bets from web data ahead of the user's settled-bets
  screenshot — settlement is screenshot-driven by preference (decided 14 Jun).
  Web data is for verification and for settling GHOSTS (which have no screenshot).
- Don't include a dead-weight leg (a short pure-vig leg), and don't dress up a
  coverage bet as +EV — state the honest landing % and EV read (#value-not-floor).
- Don't construct a ghost bet from legs that weren't in the pre-match read —
  hindsight makes the data worthless. Settle ghosts blind from match data.
- Don't log a free bet with a cash stake — `stake = 0.00`, winnings-only return.
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
