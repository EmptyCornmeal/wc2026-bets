# Go-live readiness checklist (graded)

Pre-flight + while-it-runs list for the autonomous phase. Created 14 Jun 2026.
Tick boxes as done; re-grade as priorities shift. Grades:

- **P0 — blocker**: correctness or public-repo safety; do at go-live.
- **P1 — core**: the measurement that gives the project its point; do this week.
- **P2 — decision/build**: needs a user call or a build; not blocking.
- **P3 — monitor**: ongoing risk — watch, don't build.
- **U — user/recurring**: only the user can do it; happens every cycle.

---

## P0 — do at go-live (blockers)
- [x] **Log the 4 current games' tiers as Open ghosts** (Germany / Netherlands /
      Ivory Coast / Sweden). Done 14 Jun — 8 Open ghosts added (Safer/Balanced/
      Aggressive per file); settle blind when results land.
- [x] **Verify `matches/TEMPLATE.md` reflects the new method** — done 14 Jun:
      template now bakes in 3-leg soft spine, double-chance result leg, banned
      lottery legs, value-not-floor, and the ghost-logging step.
- [x] **PII sweep of the public repo** — done 14 Jun: clean. Only hit was the
      standard GitHub Actions bot email in `odds-snapshot.yml`. `.gitignore`
      covers `*.local.*` + scratch files.
- [ ] **Settle the 4 open bets + their ghosts** when results land — first live
      test of the new method. *(recurring every matchday)*

## P1 — core measurement (this week)
- [ ] **Brier calibration panel** — grade `est_win_prob` vs outcomes. ~3 bets
      from the 15-bet threshold. THE metric: calibration > accuracy (per
      community-findings.md). Also in improvements.md backlog.
- [ ] **CLV panel** from `odds_snapshots.csv` (~9.5k rows, currently unused) —
      per-leg de-vigged closing-line value for anchor legs (match odds / totals
      / BTTS). The one honest edge metric. Also in improvements.md backlog.
- [ ] **Confirm Bet Builder Insurance opt-in in-app** (U) — the Germany free bet
      and every future one-leg loss depend on it.

## P2 — decisions + non-blocking builds
- [ ] **DECISION C8 — settlement autonomy**: settle from web match-data
      provisionally (marked "unconfirmed"), then reconcile when the screenshot is
      pasted — or keep waiting for the screenshot? The biggest "let it run" call.
      *(Ghosts already settle from web data; only real bets wait.)*
- [ ] **DECISION C9 — schedule a cloud agent**: if C8 = web-settle, set up a
      `/schedule` routine to detect finished games → settle + settle ghosts →
      regenerate → push overnight. Depends on C8.
- [ ] **DECISION C10 — knockout fixtures**: 25 placeholder rows (1A, W73, "3rd
      A/B"). Auto-resolve from web as the bracket fills, or manual on your word?
- [ ] Ghost per-tier strike-rate trend chart (needs a few more days of data).
- [ ] Odds-band breakdown + rolling-10 window stats (improvements.md, needs n).

## P3 — monitor (ongoing, no build)
- [ ] **Odds API quota** — cron burns ~240/mo (2 credits × 4×/day) of 500 free;
      460 left now. If tight mid-month, drop cron to 8–12h or snapshots stop and
      CLV gets gaps.
- [ ] **Git conflicts with the 6-hourly cron bot** — always `git pull --rebase`
      before push; append-only CSVs (snapshots, bets, legs) conflict otherwise.
- [ ] **Bankroll runway** — £12.71 balance + £15 in flight; ~£520 lifetime stake
      at £5/game; needs steady top-ups. Flat-staking discipline already encoded.
- [ ] **Sample-size discipline** — 0 bets settled under the new method. Review
      weekly; do NOT rewrite rules on n=1–2.

## U — user / recurring (can't automate)
- [ ] Paste open + settled screenshots each matchday (required for real settle).
- [ ] Deposit as the bankroll draws down.
- [ ] Confirm in-app promo opt-ins (insurance, Super Sub, any new tokens).
