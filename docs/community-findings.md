# Community & LLM-betting research (12 Jun 2026)

Reddit/forum lived experience + tracked LLM-betting experiments. Source links in
the original agent reports; the durable conclusions live here.

## What the community knows that the docs don't

- **Corners are the softest builder market** (tiny max stakes, books defend them
  by limiting winners, not sharpening prices). Player shots are soft AT ODDS
  RELEASE and sharpen fast — early placement is the edge there, in tension with
  our wait-for-lineups rule; resolve per-leg (shots legs early only when the
  player is nailed). International tournaments make props extra lazy early
  (books lack national-team data).
- **Paddy Power consensus**: Super Sub genuinely saves bets BUT its value is
  partly priced into PP's relatively poor builder odds. Bet365 rated deepest
  for builders. Single-book loyalty costs real money (same builder 8/1 vs 11/1
  across books).
- **Opta is final** — settlement disputes about shots/fouls always lose unless
  Opta agrees. Screenshot slips; argue only with Opta-backed evidence.
- **Free bet builders convert at ~60% of face value** (matched-betting
  community number) — Bet Builder Insurance refunds are worth ~£6 per £10, not £10.
- **The one defensible pro-builder thesis**: short builders (2–4 legs) of
  independently researched +EV props. The evidence it can work: books stake-limit
  the people doing it.
- **Tracking culture**: manual logging beats auto-sync (friction reduces bet
  count — a feature); the breakdown that matters after months is by market
  type and leg count. Elaborate tags/confidence fields tend to go unused.

## Tilt rules worth encoding (from the graveyard threads)

1. A big win is the dangerous event, not a big loss — wins trigger withdrawal,
   never stake escalation.
2. Flat staking; no stake changes within 24h of a loss. (Flat £5 = compliant.)
3. "One leg away" is engineered hope — near-misses are losses, full stop. Our
   near-miss table exists to find leg-construction errors, not to feel close.
4. Review builder ROI by leg count monthly.

## The LLM-betting evidence — about this project itself

- **Every tracked experiment of meaningful size shows LLM picks losing at
  roughly the vig** (best sample: OLBG's 380-match PL season — ChatGPT -11%
  ROI). LLMs predict likely winners, not value vs the price, and verbalized
  confidence is poorly calibrated (one test: 1-3 on its highest-confidence picks).
- Academic picture: retrieval-grounded, ensembled LLMs reach generic-crowd
  forecasting quality; nothing credible beats the de-vigged closing line.
  Pinnacle's football close is near-fully efficient over ~398k matches.
- **Calibration beats accuracy** (Walsh & Joshi 2023): selecting on calibration
  flipped -35% to +35% returns in their setup. Implication: grade this
  project's probability estimates (Brier score), not just W/L.
- Practitioner-converged mitigations, now adopted as house rules:
  anchor on de-vigged market priors and justify deviations; force explicit
  probabilities per leg; run a devil's-advocate pass before finalising; never
  state the user's lean before the model's estimate; the LLM's strongest
  contribution is research synthesis + building the tooling, with CLV as the
  external judge of whether the judgment layer adds anything.

## Honest project framing

This is an experiment in whether disciplined process + research synthesis can
survive a 15–30% builder hold, instrumented well enough to know the answer.
The prior, per all available evidence, is NO on raw picking — the upside lives
in discipline, promo capture (insurance/free builders at ~60% conversion),
soft-market awareness (corners, early props), and honest measurement. If CLV
and calibration data eventually say the picks add nothing, believe the data.

---

## Four-model deep-research synthesis (19 Jun 2026)

Commissioned exhaustive reports from Copilot, Gemini, Perplexity and ChatGPT on
optimal bet-builder/SGP strategy, cross-checked against our 33-bet dataset. The
convergence was strong; this is the evidence base for the REFINED METHODOLOGY block
in CLAUDE.md.

**Unanimous consensus (all 4):**
- **Hold compounds per leg.** ~4-5% single → ~8-10% (2 legs) → ~15-19% (4 legs),
  plus a same-game correlation tax (often pushing real hold to 20-30%+). Leg count
  is THE biggest EV lever. Our 4-leg 0/21 is the math, not variance. Default 2,
  max 3, 4+ banned.
- **1+ SOT on the primary nailed focal forward** is the core soft prop. Secondary
  strikers/subs/weak-team outlets blank — matches our data exactly. Never two SOT.
- **Dead markets:** anytime scorer, team-goals-over, total-cards-over, low-line
  corners (high vig + variance). Confirmed.
- **1.20-1.70 value band = variance/longshot-bias heuristic, NOT an edge.** Never
  stack sub-1.20 dead-weight (compounds vig for ~no payout).
- **Promos are the only realistic route to break-even.** Power Ups on 2-leg cash;
  free bets are stake-not-returned so EV-max on LONG odds (~4.5-5.0+); don't pad
  legs for acca insurance.
- **Flat stake; Kelly = 0 on -EV bets; "bet every game" is the biggest leak.**
- **Honest ceiling −2% to −15%; break-even only via promos.** CLV is the only real
  edge proof — track it at the LEG level (builder CLV is unmeasurable).

**Where the research corrected/extended our beliefs:**
- **Double Chance is variance reduction, NOT value.** Our 7-0 DC is small-sample
  variance; all 4 agree it doesn't make money, it lowers ruin. Keep it for variance
  on two-way games; straight win only for genuinely strong/underpriced favs.
  (ChatGPT nuance: Asian DNB / Asian 0 are academically better-priced than 1X2-derived
  DC, and English football shows a mild draw bias — worth testing if PP offers them.)
- **🆕 Player FOULS / TACKLES = softest untapped market** (2 of 4). Referee + tactical
  matchup driven, thinly modelled. We've never used them — flagged to test as the
  3rd-leg market with WC referee foul/card data.
- **Correlation: prefer VOLUME over NARRATIVE.** Books over-tax obvious positive
  stacks (fav win + scorer + over); softer shape is protected-result + volume prop
  (SOT/corners from a dominant side) = already our spine. Gemini pushed counter-
  narrative NEGATIVE correlation (fav wins while their juiced striker BLANKS) as an
  inflated-price niche — speculative, untested.
- **Super Sub: CONFLICT.** Gemini claims a +10-27% unpriced edge (inherit the sub's
  minutes); our data is 0-rescues-in-19. Resolution: mild tiebreaker only, do NOT
  chase. Believe our data over the theory until it shows up.
- **4-leg hold honest number:** ~15-19% before extras, not auto 25-35% (that's the
  correlated/exotic top end). Our "4-5% per leg" intuition was right.

Caveat the reports themselves stressed: most edges they cite are model-dependent and
single-book-unprovable without leg-level CLV. Treat the project as "minimise the
bleed + capture promos + measure honestly," not a profit engine.

---

## Match-stats dataset ingested (21 Jun) — data/match_stats.csv

The user maintains a full per-game stats table (shots, SoT, possession, fouls, cards,
corners) for every WC game. Now committed as `data/match_stats.csv` and is the CANONICAL
source for settling corners / cards / team-SoT legs and for analysis — STOP web-guessing
these. First use already corrected two conservatively-flagged ghost legs (GCANQAT-AGG:
Qatar 3 cards; GSCOMAR-AGG: Morocco 5 corners) from Lost -> Won.

What the dataset reveals across 36 group games:
- **#parked-bus-goals-trap is MASSIVE, not occasional: 10 of 36 games (~28%) had a side
  take 15+ shots and score <=1 goal** (Spain 23sh/0, Ecuador 26sh/0, Turkey 33sh/0 & 28sh/0,
  Uruguay 27sh/1, Switzerland 27sh/1, Belgium 15sh/1, Ivory Coast 16sh/1, S.Africa 17sh/1,
  Sweden 20sh/1). Several were OUR losses. Hard rule: vs a deep block, a favourite-WIN or
  goals-OVER leg carries ~1-in-4 shutout/low-block risk REGARDLESS of shot dominance. The
  favourite's own SOT volume is the only thing the bus reliably can't stop (team median 4
  SoT/game; only 3 of 72 team-games registered 0 SoT). This is the strongest single argument
  for: SOT spine yes; favourite-win/Over legs are the swing, especially vs minnows.
- Team SoT: median 4/game, mean 4.6 — so a primary shooter hitting 1+ SOT is well-supported
  (matches our ~71% 1+SOT hit rate); the risk is player-specific blanks, not team drought.
