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
- [~] Cross-book comparison — **RULED OUT by user preference (16 Jun): Paddy Power
      only, and staying that way.** Removes the one externally-proven price lever, so
      all edge must come from pick quality, promo capture, correlation exploitation,
      and timing WITHIN Paddy. The ideas below are scoped to that constraint.

## Make-it-work plan (16 Jun audit — built to WIN, not just diagnose)

Context: 2-14 real / -57% yield over 16 settled. Calibration n=12: predicted 30%
win rate, delivered 8% (variance-low; true talent ~20-25%). The killer insight —
**our own est_win_prob (~30%) on 3-leg builds at ~2.7 already implies -EV; we place
anyway because the charter says "bet every game."** Fixing structure > fixing picks.
Decisions to make WITH the user at the keyboard (do not auto-apply while away).

### P0 — prove or disprove edge (do these first)
- [ ] **CLV tracker (the truth-detector).** Per-leg de-vigged CLV for anchor legs
      (match-odds/totals/BTTS) = our placement price vs last pre-KO snapshot from
      odds_snapshots.csv. Headline metric, above P/L. Tells us in ~20 bets what P/L
      needs 104 to say. If CLV +, keep betting; if -, pivot to paper-tracker.
- [ ] **Per-bet EV at placement** = Σ(true% per leg) → combined true% × decimal odds.
      Log it. Auto-flag any slip with EV < 1.0 as a COVERAGE bet (smaller stake) vs
      a VALUE bet. Stop dressing -EV coverage as +EV.
- [ ] **Leg-type edge table by CLV/strike** — we already know 1+ SOT 73%, match-odds
      54% coinflip, goalscorer/team-goals ~25%. Formalise into an allowed-leg
      whitelist; demote anything below break-even strike.

### P1 — structural changes that stop the bleed
- [ ] **Relax "bet every game."** Bet only games with (a) a soft-market angle, or
      (b) a Power Up / promo. Paper-trade the rest. Coverage-for-coverage = donation.
- [ ] **Soft-spine as the PLACED default** (not Balanced-Best). Drop/DC the result
      leg unless fav sub-1.4. Ledger: soft-spine 5-3 +£43.50 vs result-leg builds
      1-11 -£45.65.
- [ ] **Variable staking — actually use the 1-10 unit scale** (currently flat £5,
      ignored). £2 coverage / £5-8 value+PP. Flat-staking -EV just sets bleed rate.
- [ ] **Two-SOT-monopolist builds** — replace the result leg with a second nailed
      1+ SOT (our 73% leg) where two genuine shot-monopolists exist.

### P2 — capture free value + de-noise
- [ ] **Power Up on every eligible slip** (only 4 of 20 used — free EV left on table).
- [ ] **De-weight Super Sub in SELECTION** — 19 SS legs, 0 ever rescued, 8 cosmetic.
      Pick the best leg, ignore the badge (it stays a settlement red-herring too).
- [ ] **Never prop a fitness-doubt player** — always the nailed monopolist
      (Lautaro-over-Messi, 16 Jun, was correct; formalise it).
- [ ] **Calibration + CLV panels live on the dashboard** so over-confidence and
      edge show up in real time, not in a post-mortem.

### P3 — the honest pivot option (if CLV stays negative after the groups)
- [ ] Shrink real stakes toward zero, expand ghost/paper coverage to all 104, and
      run this as a CALIBRATION + PREDICTION engine. Bet real money ONLY on
      leg-types/games where CLV is demonstrably positive. "Win" = provable edge,
      not a smaller monthly tax.

## Edge-generation ideas within the Paddy-only constraint (16 Jun)

Paddy Power is the only book (user preference, locked). No line-shopping. Edge must
come from FOUR sources only. All are backlog/spitball — agree with user before acting.

### 1. Exploit Paddy's own lazy correlation pricing (the main offensive lever)
- [ ] Build our own correlation read: when legs genuinely rise together in one game
      script (fav win + that fav's monopolist 1+ SOT + that fav's team corners), PP
      often prices them near-independent and OVERPAYS. Hunt builders where our
      true-correlation > PP's implied discount. This is the closest thing to +EV we
      have without cross-book.
- [ ] Conversely flag NEGATIVELY-correlated stacks PP underprices against us
      (e.g. Over 2.5 + a clean-sheet leg) and never place them (#leg-redundancy).
- [ ] Track per-build: our combined true% vs PP combined implied% — if the gap is
      consistently positive on a build TYPE, that's a repeatable angle.

### 2. Promo capture (free/boosted value — pure, no model risk)
- [ ] **Power Up on every eligible slip** (only 4 of 20 used). Quantify the boost
      captured (£ boosted) as a dashboard KPI — it's guaranteed +EV.
- [ ] **Bet Builder Insurance**: opt in; track 4+ leg builders where exactly one leg
      loses (free bet back). NOTE this pulls AGAINST the 3-leg soft-spine default —
      decide per-slip whether the insurance shape is worth the extra failure-mode leg.
- [ ] Systematically log every PP promo seen (Money Back tokens, free builders,
      acca boosts) and a rule for deploying each (free bets → longest-priced slip).

### 3. Live entry within Paddy (untapped — we only do live ADJUSTMENT)
- [ ] Live in-play soft markets on PP: 0-0 at 60' between cagey sides → unders/
      corners juiced; early fav goal → opponent-suppression legs mispriced. Define
      2-3 pre-set live triggers + the leg to take when each fires. React fast.
- [ ] Use the PP "Cash Out" figure as a live fair-value signal even when not cashing
      out (it reveals PP's live model).

### 4. Pick-quality compounding (the slow, real one)
- [ ] Whitelist allowed leg-types by historical strike: 1+ SOT (73%) = spine;
      match-odds (54%) = demote to DC/drop; goalscorer & team-goals (~25%) = banned.
- [ ] Systematic WC referee card-rate table — bet the gap where PP prices cards off
      stale season averages (cards must be TEAM-1.5, never totals — #cards-over-trap).
- [ ] Venue/condition log (altitude, heat, roof) feeding tempo→totals/corners reads.
- [ ] Never prop a fitness-doubt player — always the nailed monopolist (formalise).

### Cheap experiments to run now (Paddy-only safe)
- [ ] A/B placement method live: place soft-spine, ghost the result-leg version
      (we currently do the inverse). Let real money follow whichever wins on paper.
- [ ] Build the CLV tracker off odds_snapshots.csv for PP anchor legs only — works
      single-book (our PP placement price vs PP closing price). The keystone metric.
