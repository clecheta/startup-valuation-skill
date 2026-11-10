# Round math — identities

Currency-agnostic. Primary new cash into the company.

## Single round

```text
post_money = pre_money + primary_check
sold_fraction = primary_check / post_money
founder_fraction_after = 1 - sold_fraction   # if no other dilution that round
```

Equivalently: `pre_money = post_money - primary_check`.

If the user states a sold % that disagrees with `check / post_money`, surface
the delta. Reconcile only when they name one of:

- option pool increase
- secondary sale (cash to sellers, not to the company)
- convertible / SAFE converting on different terms

## Multi-round path

Founder ownership after n rounds (ignoring pool/secondary for the product):

```text
remaining = product over i of (1 - dilution_i)
```

A single round does **not** answer “how much does the founder still own?” after
a path of raises.

## Labels

| Label | Meaning |
|-------|---------|
| Pre-money | Value before the new primary check |
| Post-money | Pre-money + primary check (cash on the balance sheet) |
| Fully diluted | Ownership after options / convertibles as defined by the user |

Headline figures must name which label they use.

## Convertible / SAFE

No firm pre-money unless priced. A **cap** appears only when the user states
the cap. Discount and MFN terms are described, not invented.

## Trap — inverted revenue columns

Some teaching tables list “estimated monthly revenue” that algebraically
satisfies `post_money ≈ 3× to 5× annual revenue`. That is a **multiple
scenario**, not observed revenue and not SOM. Refuse to use it as market
sizing or as income-mode ARR.
