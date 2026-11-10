# Cash flow — [Company / project]

Operational cost and revenue log. Currency: **[CURRENCY]**.

**Documented horizon:** `[start month/year]` – `[end month/year]`  
**Last update:** `YYYY-MM-DD`  
**Scenario:** base (recorded costs)

---

## Premises

| Item | Value |
|------|-------|
| Scope | [software development + cloud ops / other] |
| Currency | [ISO code, e.g. USD] |
| Data type | Outflows (costs); inflows when available |
| Labor / development cost | 6 h per calendar day with an eligible commit (skill `startup-valuation`); rate from `business/valuation.json` |
| Domains | Sporadic — only on payment events |
| Cloud | One row per charge when known |
| Legal / IP | Sporadic |

### Cost categories

| Category | Description |
|----------|-------------|
| **Labor / development** | Via skill `startup-valuation` (6 h per active commit day) |
| **Development tools** | IDE, CI, subscriptions |
| **Cloud** | Cloud provider charges |
| **Domains** | Sporadic registration / renewal |
| **Legal / IP** | Marks, counsel, IP filings |
| **Other** | Anything else recorded |

### Revenue categories (when informed)

| Category | Description |
|----------|-------------|
| **Subscriptions / SaaS** | Recurring plan revenue |
| **Payments / take rate** | Payment-related revenue |
| **Other inflows** | Services, capital inflows, other |

---

## History by category

### Domains

| Month | Amount | Note |
|-------|--------|------|
| — | — | — |

### Legal / IP

| Month | Amount | Note |
|-------|--------|------|
| — | — | — |

### Cloud

| Month | Amount | Label | Note |
|-------|--------|-------|------|
| — | — | — | — |

### Development tools

| Month | Amount |
|-------|--------|
| — | — |

---

## Labor / development — cumulative series

Source: skill `startup-valuation`. Increment = monthly value; cumulative from JSON.

<!-- valuation:labor:start -->

| Month | Cumulative | Monthly increment |
|-------|------------|-------------------|
| — | — | — |

<!-- valuation:labor:end -->

---

## Monthly consolidation (recorded outflows)

| Month | Labor | Tools | Cloud | Domains | Legal / IP | Other | **Partial total** |
|-------|-------|-------|-------|---------|------------|-------|-------------------|
| — | — | — | — | — | — | — | — |

---

## Derived indicators

| Indicator | Value / note |
|-----------|--------------|
| **Labor cumulative (latest)** | *from labor series* |
| **Recorded revenue** | *RESEARCH NEEDED* |
| **Runway** | *RESEARCH NEEDED* (needs cash balance + revenue) |
| **Break-even** | *RESEARCH NEEDED* |

---

## Gaps and next steps

| Gap | Suggested action |
|-----|------------------|
| Revenue / MRR | Record subscriptions and other inflows |
| Opening cash / current balance | Needed for runway |
| Forward 12-month plan | Model base / optimistic / pessimistic |

---

## Notes for agents

- Always recalculate labor via skill `startup-valuation` (do not paste a manual series).
- Domains and Legal / IP are sporadic — `—` in a month is expected.
- Do not invent revenue or runway without explicit data.
- Preserve history outside the labor markers; only refresh `<!-- valuation:labor:* -->`.
