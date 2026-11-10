# Cost approach — Git labor valuation

Replacement cost of development effort inferred from Git history.
**Not** a round pre-money.

## Constants (defaults)

| Constant | Default | Notes |
|----------|---------|-------|
| Hourly rate | **50** (currency units per hour) | From senior monthly pay 7000 / 140 hours |
| Currency | **USD** | Override with project config; rate must already be in that currency |
| Active day | **6 hours** | Calendar day (project timezone) with ≥1 eligible commit |
| Timezone | **UTC** | Override per project |
| Locale | **en** | Month labels for human tables |
| Series start | First eligible commit | Or explicit `series_start` in config |

Changing formula, default rate, or hours-per-day requires a **skill version bump**
and a note that historical series are not comparable.

## Eligible commits

- `git log --no-merges`
- Skip bot authors matching: Dependabot, Renovate, `[bot]`, `github-actions`,
  `gitlab-bot`, `semantic-release` (case-insensitive on author name/email)
- Skip short hashes listed in config `exclude_hashes` (template/bootstrap commits)
- Optional `authors` allow-list: if set, only those emails/names count

## Formula

`D(m)` = unique calendar days in month `m` (project TZ) with ≥1 eligible commit
across the union of configured repositories.

```text
H(m) = D(m) × hours_per_active_day
V(m) = H(m) × hourly_rate
V_cum(m) = sum(V(k) for k ≤ m)
```

Days without an eligible commit = 0 hours. Multiple commits on the same day do
not increase the 6 hours.

## Config file — `business/valuation.json`

Example (currency-agnostic keys):

```json
{
  "currency": "USD",
  "hourly_rate": 50,
  "hours_per_active_day": 6,
  "timezone": "UTC",
  "locale": "en",
  "base": ".",
  "repos": ["."],
  "exclude_hashes": [],
  "series_start": null
}
```

- `base`: directory that contains the listed `repos` (or `.` for cwd)
- `repos`: relative paths under `base`. Omit or `["."]` → current Git root
- Sibling discovery under a parent path is **never** automatic

## CLI

```bash
python3 scripts/calculate.py calculate \
  --cutoff YYYY-MM-DD \
  [--since YYYY-MM] \
  [--config business/valuation.json] \
  [--currency CODE] [--hourly-rate N] \
  [--timezone IANA] [--locale LOCALE] \
  [--base PATH] [--repos r1,r2] \
  [--format json|text]
```

`--since` filters which months appear in `months[]`. Day counting always uses
the full timeline through cutoff.

```bash
python3 scripts/calculate.py render \
  --cutoff YYYY-MM-DD \
  --cash-flow business/CASH_FLOW.md \
  [--config business/valuation.json] \
  [same overrides as calculate]
```

`render` replaces only the region between
`<!-- valuation:labor:start -->` and `<!-- valuation:labor:end -->`.
If the file is missing, seed from [`../templates/cash-flow.md`](../templates/cash-flow.md).

## Rejected methods

| Method | Verdict |
|--------|---------|
| Commits × fixed hours | Rejected — squash-sensitive |
| LOC / churn | Rejected — inflated by AI, templates, lockfiles |
| Sessionization (gap clock) | Not used — under-counts days with long pauses |
| 6 h per active day | **Primary** |

AI assistance is already in observed productivity — **no hour multiplier**.

## Presentation

| Field | Rule |
|-------|------|
| Monthly hours | `days × hours_per_active_day` |
| Money | Integer when rate is integer; otherwise round half-up to 2 decimals |
| Headline | Sum of monthly `value` (or `series_total_value` when partial) |
