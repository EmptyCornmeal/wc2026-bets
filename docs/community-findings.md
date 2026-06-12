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
