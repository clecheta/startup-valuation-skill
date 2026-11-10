#!/usr/bin/env python3
"""Unit tests for cost-mode calculate.py — synthetic git repos only."""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from calculate import (
    DEFAULT_HOURLY_RATE,
    apply_labor_region,
    build_result,
    money_value,
    render_labor_markdown,
)


def _git(cwd: Path, *args: str, env: dict | None = None) -> None:
    subprocess.check_call(["git", "-C", str(cwd), *args], env=env)


def _init_repo(path: Path) -> None:
    path.mkdir(parents=True)
    _git(path, "init")
    _git(path, "config", "user.email", "dev@example.com")
    _git(path, "config", "user.name", "Dev Example")


def _commit_at(path: Path, when: str, message: str, author: str = "Dev Example <dev@example.com>") -> None:
    """Create a commit with author/committer date = when (ISO-like for git)."""
    file = path / "f.txt"
    file.write_text(message + "\n", encoding="utf-8")
    _git(path, "add", "f.txt")
    env = {
        **os.environ,
        "GIT_AUTHOR_DATE": when,
        "GIT_COMMITTER_DATE": when,
    }
    _git(path, "commit", "--author", author, "-m", message, env=env)


class MoneyTests(unittest.TestCase):
    def test_integer_rate(self) -> None:
        self.assertEqual(money_value(6.0, 50), 300)

    def test_float_rate(self) -> None:
        self.assertEqual(money_value(6.0, 50.5), 303.0)


class CalculateRepoTests(unittest.TestCase):
    def test_days_times_six_times_rate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "app"
            _init_repo(repo)
            # Two commits same day → 1 active day
            _commit_at(repo, "2024-01-10T12:00:00+00:00", "a")
            _commit_at(repo, "2024-01-10T18:00:00+00:00", "b")
            # Second day
            _commit_at(repo, "2024-01-11T09:00:00+00:00", "c")
            settings = {
                "base": str(root),
                "repos": ["app"],
                "currency": "USD",
                "hourly_rate": 50,
                "hours_per_active_day": 6,
                "timezone": "UTC",
                "locale": "en",
                "exclude_hashes": [],
                "authors": None,
                "series_start": None,
            }
            result = build_result("2024-01-31", settings)
            self.assertEqual(result["hours_per_active_day"], 6)
            self.assertEqual(result["total_hours"], 12.0)  # 2 days × 6
            self.assertEqual(result["total_value"], 600)  # 12 × 50
            self.assertEqual(result["currency"], "USD")
            self.assertEqual(result["hourly_rate"], DEFAULT_HOURLY_RATE)
            self.assertEqual(len(result["months"]), 1)
            self.assertEqual(result["months"][0]["days"], 2)
            self.assertEqual(result["months"][0]["label"], "jan/24")

    def test_merge_and_bot_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "app"
            _init_repo(repo)
            _commit_at(repo, "2024-02-01T10:00:00+00:00", "human")
            _commit_at(
                repo,
                "2024-02-02T10:00:00+00:00",
                "deps",
                author="dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>",
            )
            primary = subprocess.check_output(
                ["git", "-C", str(repo), "branch", "--show-current"], text=True
            ).strip()
            _git(repo, "checkout", "-b", "feature")
            _commit_at(repo, "2024-02-03T10:00:00+00:00", "feat")
            _git(repo, "checkout", primary)
            env = {
                **os.environ,
                "GIT_AUTHOR_DATE": "2024-02-04T10:00:00+00:00",
                "GIT_COMMITTER_DATE": "2024-02-04T10:00:00+00:00",
            }
            _git(repo, "merge", "--no-ff", "feature", "-m", "merge feature", env=env)

            settings = {
                "base": str(root),
                "repos": ["app"],
                "currency": "EUR",
                "hourly_rate": 40,
                "hours_per_active_day": 6,
                "timezone": "UTC",
                "locale": "en",
                "exclude_hashes": [],
                "authors": None,
                "series_start": None,
            }
            result = build_result("2024-02-28", settings)
            # human day + feature day = 2; bot and merge excluded
            self.assertEqual(result["months"][0]["days"], 2)
            self.assertEqual(result["currency"], "EUR")
            self.assertEqual(result["total_value"], 2 * 6 * 40)

    def test_since_filters_months_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "app"
            _init_repo(repo)
            _commit_at(repo, "2024-01-05T10:00:00+00:00", "jan")
            _commit_at(repo, "2024-02-05T10:00:00+00:00", "feb")
            settings = {
                "base": str(root),
                "repos": ["app"],
                "currency": "USD",
                "hourly_rate": 50,
                "hours_per_active_day": 6,
                "timezone": "UTC",
                "locale": "en",
                "exclude_hashes": [],
                "authors": None,
                "series_start": None,
            }
            full = build_result("2024-02-28", settings)
            self.assertEqual(full["period"], "full")
            self.assertEqual(full["series_total_value"], 600)
            partial = build_result("2024-02-28", settings, since="2024-02")
            self.assertEqual(partial["period"], "partial")
            self.assertEqual(len(partial["months"]), 1)
            self.assertEqual(partial["months"][0]["month"], "2024-02")
            self.assertEqual(partial["total_value"], 300)
            self.assertEqual(partial["series_total_value"], 600)

    def test_exclude_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "app"
            _init_repo(repo)
            _commit_at(repo, "2024-03-01T10:00:00+00:00", "template")
            h = subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], text=True
            ).strip()
            _commit_at(repo, "2024-03-02T10:00:00+00:00", "real")
            settings = {
                "base": str(root),
                "repos": ["app"],
                "currency": "USD",
                "hourly_rate": 50,
                "hours_per_active_day": 6,
                "timezone": "UTC",
                "locale": "pt-BR",
                "exclude_hashes": [h],
                "authors": None,
                "series_start": None,
            }
            result = build_result("2024-03-31", settings)
            self.assertEqual(result["months"][0]["days"], 1)
            self.assertEqual(result["months"][0]["label"], "mar/24")

    def test_render_markers(self) -> None:
        result = {
            "currency": "USD",
            "months": [
                {
                    "label": "jan/24",
                    "value": 300,
                    "cumulative": 300,
                }
            ],
        }
        labor = render_labor_markdown(result)
        content = "Header\n\n<!-- valuation:labor:start -->\nold\n<!-- valuation:labor:end -->\n\nFooter\n"
        updated = apply_labor_region(content, labor)
        self.assertIn("jan/24", updated)
        self.assertIn("<!-- valuation:labor:start -->", updated)
        self.assertIn("Footer", updated)
        self.assertNotIn("old", updated)


if __name__ == "__main__":
    unittest.main()
