"""Checksum manifest for source files: proves they are untouched.

Covers data/raw/ (results) and data/reference/entries/ (meet programs / entry lists).
`build` recomputes sha256/bytes for every file in those directories and keeps the
hand-entered provenance columns from the existing manifest. `check` fails if any
file changed, disappeared, or is not listed.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from . import paths

COLUMNS = ["path", "source", "meet_key", "bytes", "sha256", "original_name", "source_url",
           "fetched_at", "verified", "notes"]
PROVENANCE = ["original_name", "source_url", "fetched_at", "verified", "notes"]
SKIP = {".gitkeep", ".DS_Store", "MANIFEST.csv"}
DIRS = ("data/raw", "data/reference/entries")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _files(root: Path, dirs: tuple[str, ...]) -> list[Path]:
    out = []
    for d in dirs:
        base = root / d
        if base.exists():
            out += [p for p in base.rglob("*") if p.is_file() and p.name not in SKIP]
    return sorted(out)


def _source(rel: Path) -> str:
    return "entries" if rel.parts[:3] == ("data", "reference", "entries") else rel.parent.name


def _athleticnet_keys(meets: Path = paths.MEETS) -> dict[str, str]:
    """Athletic.net file name -> meet_key, from meets.csv `file_name`."""
    if not meets.exists():
        return {}
    df = pd.read_csv(meets, dtype=str, keep_default_na=False)
    return {f: k for f, k in zip(df.get("file_name", []), df["meet_key"]) if f}


def _meet_key(p: Path, athleticnet_keys: dict[str, str] | None = None) -> str:
    if p.parent.name == "athleticnet":
        return (athleticnet_keys or {}).get(p.name, "")
    return p.name.split(".")[0]


def read(manifest: Path = paths.MANIFEST) -> pd.DataFrame:
    if not manifest.exists():
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(manifest, dtype=str, keep_default_na=False)


def build(root: Path = paths.ROOT, manifest: Path = paths.MANIFEST,
          dirs: tuple[str, ...] = DIRS) -> pd.DataFrame:
    old = read(manifest).set_index("path")
    an_keys = _athleticnet_keys()
    rows = []
    for p in _files(root, dirs):
        rel = p.relative_to(root)
        key = rel.as_posix()
        row = {"path": key, "source": _source(rel), "meet_key": _meet_key(p, an_keys),
               "bytes": str(p.stat().st_size), "sha256": sha256(p)}
        for col in PROVENANCE:
            row[col] = old.at[key, col] if key in old.index else ""
        rows.append(row)
    df = pd.DataFrame(rows, columns=COLUMNS)
    df.to_csv(manifest, index=False)
    return df


def check(root: Path = paths.ROOT, manifest: Path = paths.MANIFEST,
          dirs: tuple[str, ...] = DIRS) -> list[str]:
    """Return a list of problems; empty means every file matches the manifest."""
    listed = read(manifest).set_index("path")
    problems = []
    seen = set()
    for p in _files(root, dirs):
        key = p.relative_to(root).as_posix()
        seen.add(key)
        if key not in listed.index:
            problems.append(f"not in manifest: {key}")
        elif sha256(p) != listed.at[key, "sha256"]:
            problems.append(f"CHANGED: {key}")
    for key in listed.index:
        if key not in seen:
            problems.append(f"missing from disk: {key}")
    return problems
