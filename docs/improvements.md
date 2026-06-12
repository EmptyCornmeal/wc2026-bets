# Research-driven roadmap (12 Jun 2026)

From a three-agent sweep: SGP/bet-builder economics, tracking best practice,
Paddy Power mechanics (see paddy-rules.md). Checkboxes = backlog.

## Honest framing from the economics research

- Bet builders carry **15–30% effective bookmaker hold** (vs ~5% on singles);
  margin compounds per leg and the correlation adjustment is a second, opaque
  layer of vig. Raw +EV builder betting is considered near-impossible without
  the book's correlation model. This project's edge claims should stay humble —
  the realistic wins are discipline, promo capture (insurance/free builders),
  and avoiding the known leaks.
- **Correlation tax nuance**: tightly positively correlated stacks (win + team
  total + star prop) attract the LARGEST correlation discount (10–50%). "One
  game script per slip" remains right for avoiding uncorrelated lottery legs,
  but we are not being paid full freight for the story — another reason the
  minimum-odds floor matters more than the narrative.
- Leg-count guidance from the analysis community: 2–4 legs, never short-price
  filler legs (a 1.2 leg adds margin but barely moves payout).
- At builder odds (~5–6 decimal), proving real edge needs **thousands of
  bets** — p-values won't be meaningful this tournament. The Monte Carlo
  no-edge band is the right tool at our sample size.

## Dashboard backlog

- [x] Rename ROI → Yield (profit ÷ turnover is yield; that's what we compute)
- [x] Max drawdown + longest losing streak KPI (realized)
- [ ] Calendar heatmap of daily P/L
- [ ] Odds-band breakdown (performance by price bracket)
- [ ] Rolling 10-bet window stats once n permits
- [ ] CLV panel once closing snapshots accumulate: per-leg de-vigged CLV for
      anchor legs (match odds / totals / BTTS from odds_snapshots.csv);
      builder-level CLV via the "re-quote the identical builder at kickoff"
      method — manual, screenshot the same slip pre-KO when practical
- [ ] Cumulative expected-vs-actual P/L overlay once per-bet EV is logged
- [ ] Discipline metrics: % of bets placed below min-odds floor, unplanned-bet
      share (bets with no pre-match analysis file), stake creep (flat £5 makes
      this trivial for now)
- [ ] Builder ROI by leg count (monthly review — community tilt rule #4)
- [ ] Calibration panel: Brier score of `est_win_prob` vs outcomes once ~15
      bets carry the frontmatter field (added to pick process 12 Jun)

## Process backlog

- [ ] CHECK Bet Builder Insurance opt-in (free bet back if exactly one leg of
      a 4+ leg builder loses — the Korea loss was exactly this shape)
- [ ] Log per-bet EV estimate at placement (estimated true % per leg vs price)
- [ ] When practical, screenshot the same builder's price just before kickoff
      (manual closing line for the builder itself)
- [ ] Cross-book comparison is the one real price lever the community endorses
      (same builder varies 8/1 vs 11/1 across books) — out of scope while
      single-book on Paddy, revisit if edge looks real after the groups
