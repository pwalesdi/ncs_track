"""Validation issue record shared by ingest and validate."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

SEVERITIES = ("error", "warning", "info")


@dataclass(frozen=True)
class Issue:
    check: str          # V01..V15, see docs/ingest_spec_athleticnet.md
    severity: str       # error | warning | info
    meet_key: str
    message: str
    performance_id: str | None = None


def to_frame(issues: list[Issue]) -> pd.DataFrame:
    cols = ["check", "severity", "meet_key", "message", "performance_id"]
    return pd.DataFrame([asdict(i) for i in issues], columns=cols)


def errors(issues: list[Issue]) -> list[Issue]:
    return [i for i in issues if i.severity == "error"]
