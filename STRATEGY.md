# WC 2026 Betting Doctrine — House Rules v2

The binding strategy for the tracker. Every pick is graded against the **pre-flight
gate** below *before* a slip is handed over. This file is the single source of truth;
`CLAUDE.md` points the bet-maker process here.

_Last revised: 2026-06-13, after the first 4 settled bets._

---

## Where we stand

| Metric | Value |
|---|---|
| Settled bets | 4 (1 W / 3 L) |
| Settled stake | £20.00 |
| Returns | £17.71 |
| **P/L** | **−£2.29** |
| **ROI** | **−11.5%** |
| Open bets | 4 (Qatar-Swiss, Brazil-Morocco, Haiti-Scot, Aus-Türkiye) |
| Balance | £17.71 |

**This is not a leak — it's variance plus self-inflicted leg errors.** Down £2.29 over
four bets is essentially flat. The fixable part is that all three losses came from the
*same two mistakes*, repeated.

---

## The core finding — leg tier list

Across the 16 settled legs, sorted by what actually happened:

### Tier A — the edge (back these freely)
| Leg type | Record | Notes |
|---|---|---|
| Favourite Match Odds | 3W / 1L | Reliable, but the 1L (Canada draw) shows it's still two-way |
| Total Goals **Under** | 2W / 1L | The 1L (USA) contradicted our own "low-event" script — see #read-vs-slip-mismatch |
| **BTTS No** | 1W / 0L | Clean suppression |
| **Cards Over** (team/match) | 1W / 0L | Referee card-avg edge is real (Paraguay o1.5) |
| **Corners Over** | 1W / 0L | Lands early when a fav sieges |
| Home Team Over 1.5 | 1W / 0L | When the fav is genuinely on top |

**Suppression legs — unders, BTTS No, cards over, corners over — are where our money
comes from.** They cash even when the result leg fails (Canada: corners + unders won
while the match died).

### Tier C — the leak (restrict or ban)
| Leg type | Record | Verdict |
|---|---|---|
| Anytime Goalscorer | 1W / 1L | Needs *one specific* goal — high variance. Never load-bearing. |
| Player Shots / SOT | 1W / 1L | OK for a nailed-on volume shooter (Son); the 1L was Pulisic, subbed at HT |
| Team-scores-zero / clean-sheet-against | 0W / 1L | Adds a whole new failure mode. Banned as a bolt-on (#clean-sheet-legs) |
| "Optional" bolt-on 4th leg | 0W / 2L | **Converted two winning bases into losers** (Korea, USA). Banned. |

> Small sample (16 legs, one tournament, just started) — but the *direction* is
> consistent with construction logic: fewer specific-event dependencies = higher hit
> rate. Revisit these tallies every ~10 settled bets.

---

## House Rules v2

1. **Three legs, not four.** Every loss had a killer 4th leg. Use a 4th leg *only* when
   all four share one tight script and none of them is a player prop.
2. **Suppression-first.** Build the spine from corners / unders / cards / BTTS-No.
   Favourite Match Odds is *one* leg, not the thesis.
3. **No optional bolt-ons.** 0-for-2. Bet the base you believe in. The old "qualifies if
   combined odds ≥ X" rule is dead — it's a *price* test, never a *risk* test.
4. **One player prop max**, and only: a confirmed starter, shots/SOT (not anytime-
   goalscorer), no fitness/rotation/early-sub risk. Prefer team-level shots over a lone
   star who can be withdrawn (#single-player-prop-risk).
5. **No redundant legs.** If two legs fail on the *same* single event (e.g. Match Odds +
   team-2+ + BTTS-No all need "fav wins, dog scores zero"), cut to one (#leg-redundancy,
   #favourite-control-trap).
6. **Self-consistency check.** No leg whose kill condition already appears in this match's
   own "what kills it" notes (#clean-sheet-legs), and no leg that contradicts the written
   script (#read-vs-slip-mismatch).
7. **Floor enforced at the till.** Below the stated min-odds floor = no bet. No exceptions
   (#min-odds-discipline).
8. **One game script per slip** — correlated legs only (unchanged from v1).

---

## Pre-flight gate (run before handing over any slip)

```
[ ] ≤ 3 legs?  (4 only if one tight script AND no player prop)
[ ] Suppression spine present? (≥1 of corners / unders / cards / BTTS-No)
[ ] Zero "optional / bolt-on" legs?
[ ] ≤ 1 player prop, confirmed starter, shots/SOT, no sub-risk?
[ ] No two legs failing on the same single event? (redundancy)
[ ] No leg whose kill is in this match's own "what kills it"?
[ ] No leg contradicting the written pre-match script?
[ ] Combined odds ≥ min-odds floor?
[ ] One game script, correlated legs only?
```

Any unchecked box → fix the slip or drop the leg before it's recommended. If the only way
to clear the gate is "no bet", that's a valid output even with the bet-every-game goal —
take a tighter 2-leg suppression slip at shorter odds instead of reaching.

---

## Staking & bankroll

- Flat **£5 per game**, £5 deposited per game (existing convention). No chasing, no
  variable stakes.
- **Bet all 104 games, but scale ambition to confidence**, not the other way round:
  - High confidence → the full 3-leg suppression-led build.
  - Low confidence → a 2-leg suppression slip at shorter odds. Don't manufacture a
    4-leg 7/1 longshot just to make a low-read game "interesting".
- Breakeven hit rate at ~3.5 avg decimal odds is ~29%. Disciplined suppression-led
  builds should clear that comfortably; the goal is green over the group stage, not a
  weekly win.
- Track ROI on **settled** stake (not total staked) per the analysis conventions.

---

## Tag glossary (the vault's accumulated rules)

| Tag | Rule |
|---|---|
| `#suppression-legs` | Unders/BTTS-No/cards/corners are the edge — build around them |
| `#favourite-control-trap` | Don't pair Match Odds + anytime-scorer (both need the fav to win *and* score) |
| `#optional-legs` | Bolt-on 4th legs convert winners to losers — banned |
| `#leg-redundancy` | Don't stack legs that fail on the same single event |
| `#clean-sheet-legs` | Never add a team-scores-zero leg as a bolt-on, esp. if it's the dog's one strength |
| `#single-player-prop-risk` | A lone star can be subbed/injured — prefer team-level props |
| `#read-vs-slip-mismatch` | Cut any leg that contradicts the written pre-match script |
| `#min-odds-discipline` | Below the floor = no bet, enforced at the till |
| `#super-sub` | The Super Sub badge is cosmetic — verify the actual scorer/shot on settle |
| `#live-entry` | Live entry after an early goal can find value in suppression legs (Mexico) |
| `#weakest-leg-confirmed` | Logged when the predicted weakest leg was indeed a killer |

---

## Review cadence

- Re-tally the leg tier list every **~10 settled bets**; promote/demote leg types on
  evidence, not vibes.
- When a knockout bracket fills in, update `fixtures.csv` placeholders.
- This doctrine is living — every settled match adds a #tagged learning, and rules here
  get revised when the data says so.
