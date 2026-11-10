#!/usr/bin/env python3
"""Startup valuation — cost mode: 6 h per calendar day with an eligible commit.

See ../references/cost.md. Stdlib only. Company/project agnostic.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from calendar import month_abbr
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Defaults: senior monthly pay 7000 / 140 h → 50 per hour
DEFAULT_CURRENCY = "USD"
DEFAULT_HOURLY_RATE = 50
DEFAULT_HOURS_PER_ACTIVE_DAY = 6
DEFAULT_TIMEZONE = "UTC"
DEFAULT_LOCALE = "en"

BOT_PATTERNS = (
    "dependabot",
    "renovate",
    "[bot]",
    "github-actions",
    "gitlab-bot",
    "semantic-release",
)

LABOR_START = "<!-- valuation:labor:start -->"
LABOR_END = "<!-- valuation:labor:end -->"

MONTH_ABBR_PT = {
    1: "jan",
    2: "fev",
    3: "mar",
    4: "abr",
    5: "mai",
    6: "jun",
    7: "jul",
    8: "ago",
    9: "set",
    10: "out",
    11: "nov",
    12: "dez",
}


def month_label(yyyy_mm: str, locale: str) -> str:
    year, month = yyyy_mm.split("-")
    m = int(month)
    if locale.lower().startswith("pt"):
        abbr = MONTH_ABBR_PT[m]
    else:
        abbr = month_abbr[m].lower()
    return f"{abbr}/{year[2:]}"


def load_config(path: Path | None) -> dict:
    if path is None or not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"config {path} must be a JSON object")
    return data


def resolve_settings(args: argparse.Namespace, config: dict) -> dict:
    """CLI overrides config overrides defaults."""
    base = getattr(args, "base", None) or config.get("base") or "."
    repos = getattr(args, "repos", None)
    if repos is None:
        repos = config.get("repos")
    if not repos:
        repos = ["."]
    if isinstance(repos, str):
        repos = [r.strip() for r in repos.split(",") if r.strip()]

    currency = getattr(args, "currency", None) or config.get("currency") or DEFAULT_CURRENCY
    hourly_rate = getattr(args, "hourly_rate", None)
    if hourly_rate is None:
        hourly_rate = config.get("hourly_rate", DEFAULT_HOURLY_RATE)
    hours = getattr(args, "hours_per_active_day", None)
    if hours is None:
        hours = config.get("hours_per_active_day", DEFAULT_HOURS_PER_ACTIVE_DAY)
    timezone = getattr(args, "timezone", None) or config.get("timezone") or DEFAULT_TIMEZONE
    locale = getattr(args, "locale", None) or config.get("locale") or DEFAULT_LOCALE
    exclude_hashes = list(config.get("exclude_hashes") or [])
    extra = getattr(args, "exclude_hashes", None)
    if extra:
        exclude_hashes.extend(h.strip() for h in extra.split(",") if h.strip())
    authors = config.get("authors")
    series_start = config.get("series_start")

    return {
        "base": str(Path(base).expanduser().resolve()),
        "repos": repos,
        "currency": str(currency).upper(),
        "hourly_rate": float(hourly_rate),
        "hours_per_active_day": float(hours),
        "timezone": timezone,
        "locale": locale,
        "exclude_hashes": exclude_hashes,
        "authors": authors,
        "series_start": series_start,
    }


def parse_cutoff(cutoff: str, tz: ZoneInfo) -> float:
    dt = datetime.strptime(cutoff, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59, tzinfo=tz
    )
    return dt.timestamp()


def is_bot(author_name: str, author_email: str) -> bool:
    blob = f"{author_name} {author_email}".lower()
    return any(p in blob for p in BOT_PATTERNS)


def author_allowed(author_name: str, author_email: str, authors: list | None) -> bool:
    if not authors:
        return True
    name = author_name.lower()
    email = author_email.lower()
    for a in authors:
        token = str(a).lower()
        if token and (token in email or token in name):
            return True
    return False


def hash_excluded(short_hash: str, exclude: list[str]) -> bool:
    for t in exclude:
        if short_hash.startswith(t) or t.startswith(short_hash):
            return True
    return False


def repo_path(base: str, repo: str) -> Path:
    if repo in (".", ""):
        return Path(base)
    p = Path(repo)
    if p.is_absolute():
        return p
    return Path(base) / repo


def load_commits(
    settings: dict,
    cutoff_ts: float,
) -> list[tuple[int, str, str]]:
    tz = ZoneInfo(settings["timezone"])
    series_start_ts: float | None = None
    if settings.get("series_start"):
        series_start_ts = parse_cutoff(settings["series_start"], tz)
        # series_start is start-of-day inclusive: use 00:00 that day
        series_start_ts = datetime.strptime(settings["series_start"], "%Y-%m-%d").replace(
            tzinfo=tz
        ).timestamp()

    commits: list[tuple[int, str, str]] = []
    missing: list[str] = []
    for repo in settings["repos"]:
        path = repo_path(settings["base"], repo)
        git_dir = path / ".git"
        if not path.is_dir() or not (git_dir.exists() or git_dir.is_file()):
            # .git can be a file in worktrees
            if not path.is_dir() or not (path / ".git").exists():
                missing.append(str(path))
                continue
        out = subprocess.check_output(
            [
                "git",
                "-C",
                str(path),
                "log",
                "--no-merges",
                "--format=%at|%h|%an|%ae",
            ],
            text=True,
        )
        label = repo if repo not in (".", "") else path.name
        for line in out.splitlines():
            if not line.strip():
                continue
            parts = line.split("|", 3)
            if len(parts) < 4:
                continue
            ts_s, h, an, ae = parts
            ts = int(ts_s)
            if hash_excluded(h, settings["exclude_hashes"]):
                continue
            if is_bot(an, ae):
                continue
            if not author_allowed(an, ae, settings.get("authors")):
                continue
            if series_start_ts is not None and ts < series_start_ts:
                continue
            if ts <= cutoff_ts:
                commits.append((ts, label, h))
    if missing:
        print(
            f"warning: missing repos (skipped): {', '.join(missing)}",
            file=sys.stderr,
        )
    commits.sort(key=lambda x: x[0])
    return commits


def money_value(hours: float, rate: float) -> float | int:
    raw = hours * rate
    if float(rate).is_integer() and float(hours).is_integer():
        return int(raw)
    return round(raw, 2)


def compute_months(
    commits: list[tuple[int, str, str]],
    settings: dict,
) -> tuple[list[dict], float, float | int]:
    tz = ZoneInfo(settings["timezone"])
    hours_day = settings["hours_per_active_day"]
    rate = settings["hourly_rate"]
    locale = settings["locale"]

    active: dict[str, set[str]] = defaultdict(set)
    month_commits: dict[str, int] = defaultdict(int)
    for ts, *_ in commits:
        dt = datetime.fromtimestamp(ts, tz)
        ym = dt.strftime("%Y-%m")
        active[ym].add(dt.strftime("%Y-%m-%d"))
        month_commits[ym] += 1

    months: list[dict] = []
    running: float | int = 0
    total_hours = 0.0
    for m in sorted(active):
        days = len(active[m])
        hours = days * hours_day
        value = money_value(hours, rate)
        if isinstance(value, int) and (isinstance(running, int) or float(running).is_integer()):
            running = int(running) + int(value)
        else:
            running = round(float(running) + float(value), 2)
        total_hours += hours
        months.append(
            {
                "month": m,
                "label": month_label(m, locale),
                "commits": month_commits.get(m, 0),
                "days": days,
                "hours": float(hours),
                "value": value,
                "cumulative": running,
            }
        )
    return months, float(total_hours), running if months else 0


def normalize_since(since: str) -> str:
    if len(since) == 7 and since[4] == "-":
        datetime.strptime(since + "-01", "%Y-%m-%d")
        return since
    if len(since) == 10:
        datetime.strptime(since, "%Y-%m-%d")
        return since[:7]
    raise ValueError(f"invalid --since {since!r}; use YYYY-MM or YYYY-MM-DD")


def build_result(
    cutoff: str,
    settings: dict,
    since: str | None = None,
) -> dict:
    tz = ZoneInfo(settings["timezone"])
    cutoff_ts = parse_cutoff(cutoff, tz)
    commits = load_commits(settings, cutoff_ts)
    primary_months, primary_hours, series_value = compute_months(commits, settings)

    period = "full"
    since_norm: str | None = None
    total_value: float | int = series_value
    total_hours = primary_hours
    months = primary_months
    if since:
        since_norm = normalize_since(since)
        filtered = [m for m in primary_months if m["month"] >= since_norm]
        period = "partial"
        months = filtered
        total_hours = round(sum(m["hours"] for m in filtered), 1)
        if filtered and all(isinstance(m["value"], int) for m in filtered):
            total_value = sum(int(m["value"]) for m in filtered)
        else:
            total_value = round(sum(float(m["value"]) for m in filtered), 2)

    return {
        "cutoff": cutoff,
        "since": since_norm,
        "period": period,
        "currency": settings["currency"],
        "hourly_rate": settings["hourly_rate"],
        "hours_per_active_day": settings["hours_per_active_day"],
        "timezone": settings["timezone"],
        "locale": settings["locale"],
        "base": settings["base"],
        "repos": settings["repos"],
        "commit_count": len(commits),
        "total_hours": total_hours,
        "total_value": total_value,
        "series_total_value": series_value,
        "months": months,
    }


def format_text(result: dict) -> str:
    lines = [
        f"cutoff={result['cutoff']} since={result.get('since')} "
        f"period={result.get('period')} currency={result['currency']} "
        f"rate={result['hourly_rate']}",
        f"commits={result['commit_count']} hours={result['total_hours']} "
        f"value={result['total_value']} series_total={result.get('series_total_value')}",
        "",
        f"{'month':<8} {'label':<8} {'commits':>7} {'days':>5} "
        f"{'hours':>7} {'value':>12} {'cum':>12}",
    ]
    for m in result["months"]:
        lines.append(
            f"{m['month']:<8} {m['label']:<8} {m['commits']:>7} {m['days']:>5} "
            f"{m['hours']:>7.1f} {m['value']:>12} {m['cumulative']:>12}"
        )
    return "\n".join(lines)


def render_labor_markdown(result: dict) -> str:
    currency = result["currency"]
    lines = [
        f"| Month | Cumulative ({currency}) | Monthly increment ({currency}) |",
        "|-------|--------------------------|--------------------------------|",
    ]
    for m in result["months"]:
        lines.append(
            f"| {m['label']} | {m['cumulative']} | {m['value']} |"
        )
    if not result["months"]:
        lines.append("| — | — | — |")
    return "\n".join(lines) + "\n"


def apply_labor_region(content: str, labor_md: str) -> str:
    block = f"{LABOR_START}\n\n{labor_md}\n{LABOR_END}"
    pattern = re.compile(
        re.escape(LABOR_START) + r".*?" + re.escape(LABOR_END),
        re.DOTALL,
    )
    if pattern.search(content):
        return pattern.sub(block, content, count=1)
    # Append section if markers missing
    return content.rstrip() + "\n\n## Labor / development — cumulative series\n\n" + block + "\n"


def seed_cash_flow(template_path: Path, cash_flow: Path, settings: dict) -> None:
    text = template_path.read_text(encoding="utf-8")
    text = text.replace("[CURRENCY]", settings["currency"])
    text = text.replace("[ISO code, e.g. USD]", settings["currency"])
    cash_flow.parent.mkdir(parents=True, exist_ok=True)
    cash_flow.write_text(text, encoding="utf-8")


def add_common_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--cutoff", default=None, help="YYYY-MM-DD end of day in project TZ")
    parser.add_argument("--since", default=None, help="YYYY-MM or YYYY-MM-DD filter for months[]")
    parser.add_argument("--config", default=None, help="Path to business/valuation.json")
    parser.add_argument("--currency", default=None)
    parser.add_argument("--hourly-rate", type=float, default=None)
    parser.add_argument("--hours-per-active-day", type=float, default=None)
    parser.add_argument("--timezone", default=None)
    parser.add_argument("--locale", default=None)
    parser.add_argument("--base", default=None)
    parser.add_argument("--repos", default=None, help="Comma-separated paths under --base")
    parser.add_argument("--exclude-hashes", default=None, help="Comma-separated short hashes")
    parser.add_argument("--format", choices=["json", "text"], default="json")


def prepare(args: argparse.Namespace) -> tuple[dict, str]:
    config_path = Path(args.config).expanduser() if args.config else None
    if config_path is None:
        candidate = Path.cwd() / "business" / "valuation.json"
        if candidate.is_file():
            config_path = candidate
    config = load_config(config_path)
    settings = resolve_settings(args, config)
    tz = ZoneInfo(settings["timezone"])
    cutoff = args.cutoff or datetime.now(tz).strftime("%Y-%m-%d")
    datetime.strptime(cutoff, "%Y-%m-%d")
    if args.since:
        normalize_since(args.since)
    return settings, cutoff


def cmd_calculate(args: argparse.Namespace) -> int:
    try:
        settings, cutoff = prepare(args)
    except (ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    result = build_result(cutoff, settings, since=args.since)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text(result))
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    try:
        settings, cutoff = prepare(args)
    except (ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    result = build_result(cutoff, settings, since=args.since)
    # Full series for cash-flow labor region unless --since given for partial refresh
    cash_flow = Path(args.cash_flow).expanduser()
    skill_root = Path(__file__).resolve().parent.parent
    template = skill_root / "templates" / "cash-flow.md"
    if not cash_flow.is_file():
        if not template.is_file():
            print(f"error: missing cash-flow and template {template}", file=sys.stderr)
            return 1
        seed_cash_flow(template, cash_flow, settings)
    content = cash_flow.read_text(encoding="utf-8")
    labor_md = render_labor_markdown(result)
    updated = apply_labor_region(content, labor_md)
    cash_flow.write_text(updated, encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote": str(cash_flow),
                "months": len(result["months"]),
                "series_total_value": result["series_total_value"],
                "currency": result["currency"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Startup valuation cost mode: 6 h per calendar day with an eligible commit"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_calc = sub.add_parser("calculate", help="Compute labor valuation JSON/text")
    add_common_flags(p_calc)
    p_calc.set_defaults(func=cmd_calculate)

    p_render = sub.add_parser("render", help="Update labor region in business/CASH_FLOW.md")
    add_common_flags(p_render)
    p_render.add_argument(
        "--cash-flow",
        default="business/CASH_FLOW.md",
        help="Path to CASH_FLOW.md",
    )
    p_render.set_defaults(func=cmd_render)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
