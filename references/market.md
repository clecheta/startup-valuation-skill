# Market approach — round price methods

Close a round price only after a consistent **TAM / SAM / SOM** funnel
([`market-sizing.md`](market-sizing.md)), unless the user explicitly accepts a
draft labeled **“comps without funnel”**.

Do **not** embed geographic round-size or post-money bands as defaults. If the
user pastes a dated table, keep year, country, and currency on the citation.

## Methods (each with a closed input list)

### Comparable rounds

Inputs: list of rounds (stage, geography, year, pre- or post-money, currency).
Output: median / range as draft. Adjust only with user-stated traction deltas.

### VC method

Inputs: exit-year revenue (or exit value), exit multiple, required fund return,
ownership target at exit, dilution path to exit.
Check: exit revenue ≤ SOM in that year.
Output: implied post-money today; pre-money = post − primary check (see
[`round-math.md`](round-math.md)).

### Scorecard (Payne-style)

Inputs: baseline pre-money **supplied by the user**, factor weights and scores
for team, opportunity size (needs SOM), product, competition, channels, need
for capital.
Output: weighted adjustment of the baseline. Opportunity-size score stays blank
without SOM.

### Berkus

Inputs: caps per factor **supplied by the user** (idea, prototype, team,
relationships, rollout).
Output: sum of awarded caps. No silent dollar ceilings from the skill.

### Dilution math alone

Inputs: check size + max dilution the founder accepts (or target post-money).
Output: implied post- and pre-money. Useful at the table; still label the method.

## Stage readiness (separate from price)

Ask and leave blank when unanswered — do **not** fill from any 2021-style chart:

| Theme | Ask |
|-------|-----|
| Team | Complementarity, first key hires, functional leadership |
| Product evidence | Thesis only / early PMF signals / product that already needs a company around it |
| Observed revenue | Definition written (net revenue; GMV only if the multiple is on GMV) |
| Growth | Rate **and** period (MoM early; YoY later) — form of the question from stage maps; rate from the user |
| Round lead | Angel / local fund / foreign fund (changes comps set) |
| Founder ownership target | Post-round goal; blank without premise |
| Instrument | Priced equity → pre-money; convertible / SAFE → cap only if user states the cap |

## If there is no next round

Describe ownership and cash effects; do not invent prices:

1. Stay profitable and distribute (if the agreement allows)
2. Buyback (needs valuation + contract terms from the user)
3. Sale (M&A) — investors take their share
4. Wind-down — assets / convertible claims per contract

## Headline labels

Every headline number in `VALUATION.md` must say whether it is **pre-money**,
**post-money**, or **fully diluted**. Cost of Git labor is never the headline
round price.
