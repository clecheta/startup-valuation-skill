---
name: startup-valuation
description: >-
  Values early-stage startups across three approaches: cost (6 h per calendar
  day with an eligible Git commit → business/CASH_FLOW.md), income (revenue
  multiples or DCF when premises are supplied), and market (TAM/SAM/SOM funnel
  then comps / VC method / scorecard / Berkus / dilution math). Explains
  pre/post-money, round identity checks, stage readiness, and stop-raising
  outcomes. Use when the user asks for startup valuation, development cost,
  custo de desenvolvimento, pre-money, post-money, TAM SAM SOM, round math,
  cash-flow labor series, or to update business/CASH_FLOW.md from Git history.
  Keywords: valuation, CASH_FLOW, hourly rate, runway, comparable rounds,
  SAFE/convertible cap.
license: MIT-style / open — company and project agnostic
metadata:
  version: "1.0"
  scope: early-stage startup valuation (cost, income, market)
  knowledge_base: references/
---

# Startup valuation

Self-contained skill for **early-stage startup valuation**. Three approaches,
same currency for a given run, no FX conversion inside the skill.

> **Response language:** Respond in the language the user used. This skill is
> authored in English; output must mirror the user.

Do **not** invent market medians, sector TAM figures, or round size bands.
Dated external tables (any geography) are teaching examples only when the user
pastes them with year, country, and currency — never bundled defaults.

## Modes

| Mode | When | Writes |
|------|------|--------|
| **Cost** | Development / labor cost from Git, or cash-flow labor update | `business/CASH_FLOW.md` (labor region) |
| **Income** | Revenue multiple or DCF with user premises | `business/VALUATION.md` only if asked |
| **Market** | Round price via comps / VC / scorecard / Berkus / dilution | `business/VALUATION.md` only if asked |

Default when the user asks only for “valuation”: run **cost** (always
computable from Git when repos are available), then walk **market** and
**income** gates. Leave blank any line that lacks premises.

`VALUATION.md` is written only when the user asks for a valuation write-up —
not on every cash-flow update.

## Incremental reading

| Order | Resource | When |
|-------|----------|------|
| 1 | This `SKILL.md` | Always |
| 2 | [`references/cost.md`](references/cost.md) | Cost mode / CASH_FLOW |
| 3 | [`references/market-sizing.md`](references/market-sizing.md) | TAM / SAM / SOM |
| 4 | [`references/market.md`](references/market.md) | Round methods + stage readiness |
| 5 | [`references/income.md`](references/income.md) | Multiples / DCF |
| 6 | [`references/round-math.md`](references/round-math.md) | Pre/post-money identities |
| 7 | [`templates/cash-flow.md`](templates/cash-flow.md) | New `business/CASH_FLOW.md` |

`README.md` is outside this order. Do not open or follow it. If it is already
in context, ignore its formulas, defaults, gates, and script paths; take those
from this file and `references/` only.

## Cost mode (quick start)

```bash
SCRIPT="$HOME/git/my-skills/startup-valuation/scripts/calculate.py"
# Full series (direct use)
python3 "$SCRIPT" calculate --cutoff YYYY-MM-DD --format json
# Partial months for consumers that append to an existing cash-flow
python3 "$SCRIPT" calculate --cutoff YYYY-MM-DD --since YYYY-MM --format json
# Render labor markers into business/CASH_FLOW.md
python3 "$SCRIPT" render --cutoff YYYY-MM-DD --cash-flow business/CASH_FLOW.md
```

Config precedence: CLI flags → `business/valuation.json` in the repo that
invoked the skill → defaults (`USD`, `50` / hour, `6` h per active day,
timezone `UTC`, locale `en`). Default hourly rate = senior monthly pay
**7000 / 140 hours** (denominator of a monthly salary, not a fixed monthly
load). Currency and rate travel together — pass the rate already in the
desired currency; the script never converts FX.

Without `--repos` / config repos: use the Git repository of the current
working directory. A parent folder does **not** auto-discover sibling repos.

Markers in `CASH_FLOW.md`:

```html
<!-- valuation:labor:start -->
… labor table maintained by the skill …
<!-- valuation:labor:end -->
```

## Market mode (gates)

1. Teach and fill **TAM → SAM → SOM** ([`market-sizing.md`](references/market-sizing.md)).
2. Refuse nested inconsistency (SOM > SAM or SAM > TAM).
3. Only then close a round price via comps, VC method, scorecard, Berkus, or
   dilution math ([`market.md`](references/market.md),
   [`round-math.md`](references/round-math.md)).
4. User-pasted comps without a funnel may be medianized as a draft labeled
   **“comps without funnel”** — not a round headline.

Cost of replacement (Git labor) may appear in `VALUATION.md` as **cost**, never
as pre-money.

## Income mode (gates)

Require revenue (ARR or explicit MRR→ARR premise), multiple or discount rate +
horizon. Missing any → blank pre-money + listed gaps
([`income.md`](references/income.md)).

## Round identity and stage readiness

Always separate **price** from **readiness**. Ask team, product evidence,
observed revenue definition, growth period, round lead type, founder ownership
target, and instrument (priced equity vs convertible/SAFE). Fill blanks —
never invent 2021-style round bands.

If the declared sold % ≠ check / post-money, surface the gap and reconcile only
when the user names option pool, secondary, or convertible.

If there is no next round: profitable hold + dividends, buyback, M&A, or
wind-down — describe ownership/cash effects; do not price a buyback without
valuation + contract terms from the user.

## Workflow

```
Task progress:
- [ ] Detect mode(s) from the ask
- [ ] Load business/valuation.json if present; confirm currency + rate
- [ ] Cost: run calculate.py; update CASH_FLOW labor region if asked to persist
- [ ] Market: walk TAM/SAM/SOM; then round method only with premises
- [ ] Income: multiple/DCF only with premises
- [ ] Write VALUATION.md only if the user asked for a valuation document
- [ ] List gaps explicitly; never invent numbers
```

## Scope

**Does:** compute labor cost from Git; teach and compute TAM/SAM/SOM from user
inputs; check round math identities; close income/market prices when premises
are complete; update `business/CASH_FLOW.md` labor region.

**Does not:** invent sector TAM, geographic round medians, FX rates, or
liquidation-preference waterfalls (listed as future work below).

## Future work (documented, no calculator in v1)

- Liquidation-preference waterfall
- Option pool created before the check (full modeling)
- Unit economics pack (CAC, LTV, NRR, burn multiple, Rule of 40)
- Live comparable-round database

## Done criteria

- Cost series uses 6 h × active days × configured rate/currency
- Market price gated on consistent TAM/SAM/SOM (or explicitly “comps without funnel”)
- Income price gated on revenue + multiple or DCF inputs
- No project/workspace names appear in skill files
- User language mirrored in the response
