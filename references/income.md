# Income approach — multiples and DCF

Value from expected cash generation. Early-stage companies often lack the
inputs; then leave pre-money blank and list gaps.

## Revenue multiple

Inputs (all required for a closed number):

| Input | Notes |
|-------|-------|
| Revenue | ARR, or MRR with an explicit “× 12 = ARR” premise written down |
| Multiple | User-supplied (sector/stage comps). Skill never invents the multiple |
| Definition | Net revenue vs GMV — must match how the multiple was defined |

```text
Equity value ≈ Revenue × Multiple
```

State whether the result is treated as pre- or post-money for the round
context. Usually this is an enterprise / equity indication, not a term sheet
by itself.

## DCF (discounted cash flow)

Inputs: projected free cash flows by period, discount rate, terminal value
method (exit multiple or perpetuity) with its premises, horizon.

```text
PV = sum( CF_t / (1+r)^t ) + PV(terminal)
```

Without rate, horizon, and cash-flow series → blank.

## Gates

- No revenue figure → no income-mode price
- No multiple (and no full DCF set) → no income-mode price
- Do not borrow “required monthly revenue” from inverted post-money tables as
  if it were observed ARR

## Relation to other modes

- Cost (Git labor) is a floor / diligence signal, not a substitute for income
- Market funnel (SOM) should bound aggressive exit-year revenue in a VC or
  DCF narrative when both modes are used together
