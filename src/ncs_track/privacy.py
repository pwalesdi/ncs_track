"""Keep athlete names out of tracked files.

The results name minors, so athlete-level data stays out of git (see .gitignore and the
README "Data" section). This module finds real athlete names in text so a test and the
pre-push check can fail when one leaks into a tracked file.

A name is matched as a whole-word token sequence, in both "First Last" and "Last, First"
order, after folding case, accents and punctuation. Only names with at least two tokens
are used; a lone surname would match ordinary words.

Allowed: school names and a few generic phrases. An athlete whose name reads like a
school (there is a real "Logan, James" and a James Logan High School) is therefore not
caught; that is the price of not flagging every school name.
"""

from __future__ import annotations

import re
import subprocess
import unicodedata
from pathlib import Path

import pandas as pd

MAX_TOKENS = 6
GENERIC_PHRASES = {"relay team", "team relay"}      # Athletic.net placeholder for missing relay legs
_SUFFIX = re.compile(r"\b(jr|sr|ii|iii|iv)\b\.?", re.I)


def _tokens(text: str) -> list[str]:
    s = unicodedata.normalize("NFKD", text)
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = s.replace("'", "").replace("’", "")
    return re.findall(r"[a-z]+", s)


def name_forms(raw: str) -> set[str]:
    """Normalised token strings for one name, in both orders."""
    raw = re.sub(r"\([^)]*\)", " ", raw or "")          # drop "(Nick)"
    raw = _SUFFIX.sub(" ", raw)
    if "," in raw:
        last, first = raw.split(",", 1)
        last_t, first_t = _tokens(last), _tokens(first)
    else:
        t = _tokens(raw)
        last_t, first_t = t[-1:], t[:-1]
    if not last_t or not first_t:
        return set()
    forms = {" ".join(first_t + last_t), " ".join(last_t + first_t)}
    return {f for f in forms if 2 <= len(f.split()) <= MAX_TOKENS}


def forms_for(names) -> set[str]:
    out: set[str] = set()
    for n in names:
        if isinstance(n, str) and n.strip():
            out |= name_forms(n)
    return out


_LEG_GRADE = re.compile(r"\s+\d{1,2}$")


def names_from_processed(processed: Path) -> set[str]:
    """Every athlete name in data/processed/*.csv (athletes and relay legs)."""
    names: set[str] = set()
    for f in sorted(processed.glob("*.csv")):
        df = pd.read_csv(f, dtype=str, keep_default_na=False)
        for col in ("athlete_name", "athlete_name_raw"):
            if col in df:
                is_relay = df["is_relay"].str.lower().eq("true") if "is_relay" in df else False
                names |= set(df.loc[~is_relay, col] if is_relay is not False else df[col])
        if "relay_legs" in df:
            for legs in df["relay_legs"]:
                names |= {_LEG_GRADE.sub("", leg.strip()) for leg in legs.split(";") if leg.strip()}
    names.discard("")
    return names


def find(text: str, forms: set[str]) -> list[str]:
    """Name forms that occur in `text` as whole-word sequences."""
    toks = _tokens(text)
    hits = set()
    for n in range(2, MAX_TOKENS + 1):
        for i in range(len(toks) - n + 1):
            g = " ".join(toks[i:i + n])
            if g in forms:
                hits.add(g)
    return sorted(hits)


def allowed_forms(reference: Path) -> set[str]:
    """School names (both token orders) and generic phrases that are not athletes."""
    schools: set[str] = set()
    lists = reference / "ncs_source_of_truth_lists.csv"
    if lists.exists():
        schools |= set(pd.read_csv(lists, dtype=str)["School"])
    for f, col in (("school_aliases.csv", "canonical_name"), ("school_alias_spellings.csv", "raw")):
        if (reference / f).exists():
            schools |= set(pd.read_csv(reference / f, dtype=str, keep_default_na=False)[col])
    out = set(GENERIC_PHRASES)
    for s in schools:
        t = _tokens(re.sub(r"\([^)]*\)", " ", s))
        if len(t) >= 2:
            out |= {" ".join(t), " ".join(t[1:] + t[:1]), " ".join(t[-1:] + t[:-1])}
    return out


def tracked_files(root: Path, include_untracked: bool = True) -> list[Path]:
    """Tracked files, plus untracked ones that .gitignore would let into the next commit."""
    cmd = ["git", "ls-files", "-z", "--cached"] + (["--others", "--exclude-standard"] if include_untracked else [])
    out = subprocess.run(cmd, cwd=root, capture_output=True, check=True).stdout
    return [root / p for p in out.decode().split("\0") if p]


def read_text(path: Path) -> str | None:
    """File text, or None for binary files (PDFs etc.)."""
    data = path.read_bytes()
    if b"\0" in data[:8192] or path.suffix.lower() in {".pdf", ".png", ".jpg", ".xlsx"}:
        return None
    return data.decode("utf-8", errors="replace")


def scan(files: list[Path], forms: set[str], root: Path) -> dict[str, list[str]]:
    """{relative path: [name forms found]} for files containing a real name."""
    out = {}
    for f in files:
        if not f.is_file():
            continue
        text = read_text(f)
        if text is None:
            continue
        hits = find(text, forms)
        if hits:
            out[str(f.relative_to(root))] = hits
    return out
