---
match: Saudi Arabia v Uruguay
kickoff: 2026-06-15 23:00
stage: Group H
archetype: favourite control
confidence: 6/10
predicted_weakest_leg: Saudi over 1.5 cards (swing) / Uruguay win (draw risk)
est_win_prob: 0.28
min_odds_floor: 3.20
bet_id: O/7913296/0000310
status: lost
---

# Saudi Arabia v Uruguay

## Pre-match read
Hard Rock Miami, open pitch, high heat + humidity → slower tempo, supports a
controlled low-scoring game. Uruguay 1.44 (de-vig ~67%) away, Saudi 7.50: Bielsa's
side strong favourites vs the worst WC win-rate nation (Saudi lost 68% of 19). The
control/unders read fits Uruguay's profile (clean sheets in 6 of 9; only 5 of last
23 over 2.5) AND Saudi's poverty up front (BTTS failed in 8 of 13). **BUT the named
crack: Araújo + Giménez (both CBs) likely OUT injured** — Uruguay's makeshift
defence is exactly why books flag BTTS Yes 2.10, so BTTS-No/unders is a LEAN, not a
lock. **Núñez is the unambiguous shot monopolist** (led qualifying for shots + SOT)
— 1+ SOT is the clean attacking leg. Ref Mariani ~4.1 YC/g (strict); Saudi the
better team-cards side — **Abdulhamid is a card magnet** (5Y+1R in 20 Ligue 1
starts, carded 27/10). TEAM-1.5 cards only (#cards-over-trap), never total-over.

## The bet
**PLACED** (O/7913296/0000310) · Power Up 25% (2.32 → **2.65**) · £5 → **£13.27**:
- Uruguay — Match Odds
- Darwin Núñez — 1+ Shots On Target Incl Woodwork (Super Sub, Win More)
- Over — Home Team Total Cards 1.5 (Saudi 2+)

Recommended Balanced-Best exactly, with the 25% boost applied. Original below.

**Recommended (Balanced-Best) — target 3.5–4.0:**
- Uruguay to win (1.44) — strong sub-1.6 favourite vs a toothless side
- Darwin Núñez 1+ shot on target (~1.45, the monopolist)
- Saudi Arabia over 1.5 team cards (~1.75–1.95 board — Abdulhamid magnet + strict ref)
Combined ~3.7. £5 cash. ~28% land. Confidence 6/10.

Safer (~2.5): Uruguay double chance + Núñez 1+ SOT + Under 2.5 goals.
Aggressive (~7, 1u): Uruguay win + Núñez over 1.5 SOT + Saudi over 1.5 cards + Under 2.5.
Avoid: BTTS No stacked as "safe" (makeshift Uruguay D — books flag BTTS Yes);
total-cards-over; Núñez anytime as the anchor (#goalscorer-lottery — use 1+ SOT).
**Weakest leg: Saudi over 1.5 cards** (tonight proved card legs swing). **Fallback:
Under 2.5 goals** in its place if cards prices poorly. Uruguay-win draw risk (25%)
is the other soft spot → double chance if you want the Safer shape.

## Result
**LOST · £5 → £0.00 (−£5).** Saudi Arabia 1-1 Uruguay (Al-Amri 43'; Maxi Araújo 90'
equaliser). Uruguay had 67% possession — their highest on WC record — but a 1.44
favourite couldn't beat the group's weakest side. All three legs lost:
- Uruguay Match Odds — **LOST** (1-1 draw, Uruguay did not win).
- Darwin Núñez 1+ SOT — **LOST** (headed wide from a promising position pre-half; 0
  shots on target. Super Sub Canobbio display cosmetic — no rescue).
- Saudi over 1.5 cards — **LOST** (Saudi only 1 card, Al-Amri 43').

## Learnings
Predicted weakest leg called **two of the three killers**: "Saudi over 1.5 cards
(swing) / Uruguay win (draw risk)" — both lost. But the slip didn't even need them:
the supposedly clean attacking anchor, **Núñez 1+ SOT, also blanked** — a 1.44
favourite contained to a draw drags its shot-monopolist's prop down with it (the
legs were more correlated than priced).

The avoidable error is a **process violation**: `est_win_prob` was logged at **0.28**
(≤ 0.30) — under #result-leg-can-kill the result leg should have defaulted to
**double chance**, but we placed straight Uruguay win. The Safer ghost (Uruguay DC +
Núñez SOT + Under 2.5) had its DC and Under legs WIN; only Núñez sank it. DC wouldn't
have rescued this exact slip (Núñez was the common killer), but stacking a straight-win
leg we'd already flagged below our own gate is undisciplined.

**#est-prob-gate-violated** — if `est_win_prob ≤ 0.30`, the result leg MUST be double
chance. Quoting a 1.44 favourite's straight win in the placed build when our own
estimate said 28% is exactly the trap #result-leg-can-kill warns against.
