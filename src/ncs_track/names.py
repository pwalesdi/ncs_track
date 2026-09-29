"""Name normalisation for the no-ID fallback match (Hy-Tek rows).

Normalised names are a *matching aid*, never an identity. Anything that doesn't
match exactly on (gender, name_key, school_id, grad_year) goes to review; there
are no automatic fuzzy merges.
"""

from __future__ import annotations

import re
import unicodedata


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower().replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def split_name(raw: str) -> tuple[str, str, str | None]:
    """Return (last, first, nickname) from "Last, First (Nick)" or "First Last"."""
    text = (raw or "").strip()
    nick = None
    m = re.search(r"\(([^)]*)\)", text)
    if m:
        nick = m.group(1).strip() or None
        text = (text[: m.start()] + text[m.end():]).strip()
    if "," in text:
        last, first = (p.strip() for p in text.split(",", 1))
    else:
        parts = text.split()
        last, first = (parts[-1], " ".join(parts[:-1])) if parts else ("", "")
    return last, first, nick


def name_key(raw: str) -> str:
    """Canonical "last|first" key: accents, punctuation and case removed."""
    last, first, _ = split_name(raw)
    return f"{_fold(last)}|{_fold(first)}"


def grad_year(season: int, grade: int | None) -> int | None:
    """Graduation year from season and grade (a 12th grader in 2024 graduates 2024)."""
    if grade is None:
        return None
    return season + (12 - grade)
