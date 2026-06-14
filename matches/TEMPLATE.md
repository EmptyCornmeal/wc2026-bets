---
match: Home v Away
kickoff: YYYY-MM-DD HH:MM
stage: Group X
bet_id:
archetype: # favourite control | cagey unders | cards & fouls | corners pressure | siege script
confidence: # n/10 at placement
predicted_weakest_leg: # the leg most likely to kill the slip
est_win_prob: # explicit probability the whole builder wins, for Brier grading
min_odds_floor: # LEGACY — optional guidance target only, not a hard gate (#value-not-floor)
status: analysed | placed | won | lost
---

# Home v Away

## Pre-match read
<!-- Bet-maker analysis: team news, form, tactical script, referee card avg, venue,
     and the DE-VIGGED market price as the prior. Written BEFORE kickoff, never edited
     after — the honest record. -->

## The bet
<!-- DEFAULT = 3-leg SOFT-MARKET spine (cards / 1+ SOT / corners / unders / BTTS).
     Result leg demoted to DOUBLE CHANCE (or dropped) unless a genuinely strong
     sub-1.6 favourite. NO anytime-scorer / 2+-shots / team-to-score-2+ lottery legs
     (#process-over-outcome, #goalscorer-lottery).
     Tier the builders Safer / Balanced-Best (the one placed) / Aggressive — each with
     legs, est odds, realistic landing % + EV read (true% vs implied price), stake,
     what kills it, fallback, and an Avoid list. No hard floor — gate on dead-weight
     legs + value (#value-not-floor). Free bet → longest-priced slip.
     THEN log every tier to the ghost ledger as Open pre-registered ghosts (Pick step 8). -->

## Result
<!-- Final score, per-leg outcomes, returns. Settle the ghost-ledger rows for this
     game too (blind, from match data). -->

## Learnings
<!-- What the read got right/wrong. Was predicted_weakest_leg the actual killer?
     End with one transferable #tagged lesson; add new rules to CLAUDE.md's vault list. -->
