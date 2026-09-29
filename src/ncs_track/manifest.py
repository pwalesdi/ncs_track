"""Checksum manifest for data/raw/: proves raw files are untouched.

`build` recomputes sha256/bytes for every file under data/raw/ and keeps the
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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _raw_files(raw: Path) -> list[Path]:
    return sorted(p for p in raw.rglob("*") if p.is_file() and p.name not in SKIP)


def _meet_key(p: Path) -> str:
    name = p.name.split(".")[0]
    return name if not name.startswith("athleticnet_") else ""


def read(manifest: Path = paths.MANIFEST) -> pd.DataFrame:
    if not manifest.exists():
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(manifest, dtype=str, keep_default_na=False)


def build(raw: Path = paths.RAW, manifest: Path = paths.MANIFEST) -> pd.DataFrame:
    old = read(manifest).set_index("path") if manifest.exists() else None
    rows = []
    for p in _raw_files(raw):
        rel = p.relative_to(raw.parent.parent).as_posix()   # data/raw/...
        row = {"path": rel, "source": p.parent.name, "meet_key": _meet_key(p),
               "bytes": str(p.stat().st_size), "sha256": sha256(p)}
        for col in PROVENANCE:
            row[col] = old.at[rel, col] if old is not None and rel in old.index else ""
        rows.append(row)
    df = pd.DataFrame(rows, columns=COLUMNS)
    df.to_csv(manifest, index=False)
    return df


def check(raw: Path = paths.RAW, manifest: Path = paths.MANIFEST) -> list[str]:
    """Return a list of problems; empty means every raw file matches the manifest."""
    listed = read(manifest).set_index("path")
    problems = []
    seen = set()
    for p in _raw_files(raw):
        rel = p.relative_to(raw.parent.parent).as_posix()
        seen.add(rel)
        if rel not in listed.index:
            problems.append(f"not in manifest: {rel}")
        elif sha256(p) != listed.at[rel, "sha256"]:
            problems.append(f"CHANGED: {rel}")
    for rel in listed.index:
        if rel not in seen:
            problems.append(f"missing from disk: {rel}")
    return problems
