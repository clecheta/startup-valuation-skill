# Market sizing — TAM, SAM, SOM

Nested annual spend figures in **one currency** and **one horizon**. Required
before closing a **market-mode** round price. Teach these definitions in the
user’s language, then compute from their inputs.

## Definitions

| Layer | Meaning |
|-------|---------|
| **TAM** (Total Addressable Market) | Annual spend on the whole problem, no reach filter |
| **SAM** (Serviceable Addressable Market) | Share of TAM this business model, geography, and segment can serve |
| **SOM** (Serviceable Obtainable Market) | Share of SAM the company can capture in the declared horizon (often 3–7 years for a VC exit year) |

Must hold: `SOM ≤ SAM ≤ TAM`. Same unit (customer annual spend × count).

## How to build each layer

### Top-down

1. Start with a population × annual spend (with a **source**).
2. Apply an **explicit exclusion list** (who is out and why) to reach SAM.
3. Apply a second exclusion / capacity list to reach SOM.
4. Never jump layers with a bare percentage and no rationale.

### Bottom-up (preferred early-stage)

1. Reachable accounts × annual spend per account = SOM candidate.
2. Widen filters (segment, geography) → SAM.
3. Drop model/geo filters → TAM.
4. Filters remain named exclusions with sources.

## Questions (stop at each gap)

1. Who is the customer?
2. How many exist (source)?
3. Annual spend per customer (source)?
4. What does this model **not** serve (SAM filter)?
5. Capture horizon (years) and capacity / channel limits (SOM)?
6. Currency and year of the spend figures?

Population, ticket, or capture rate **without a source** stays blank. This
skill does **not** ship a sector TAM.

## Complementary checks

- Fill TAM, SAM, SOM; **reject** the series if nesting breaks.
- **VC method:** exit-year revenue must fit inside SOM for that year. Overflow
  → gap, not a silently capped pre-money.
- **Scorecard:** the “opportunity size” factor gets a score only when SOM (and
  the chain to TAM) is filled.
- User-pasted comps without a funnel → draft labeled **“comps without funnel”**.
  Headline market price waits for a complete funnel.

## Trap

Tables that back into “required monthly revenue” from a post-money × assumed
multiple are **not** TAM/SAM/SOM. Refuse to treat them as market sizing.
