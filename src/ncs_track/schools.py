"""School alias table: every raw school spelling -> one canonical school.

Canonical schools are the rows of data/reference/ncs_source_of_truth_lists.csv. Raw
spellings come from the Hy-Tek results (data/raw/hytek/) and the MOC programs
(data/processed/moc_entries.csv).

Matching never guesses. A spelling is assigned only when exactly one canonical school
fits by one of these rules, tried in order:

  exact      normalised spelling == normalised canonical name
  nospace    same, ignoring spaces ("DeLaSalle" -> "De La Salle")
  base       == canonical name without its qualifier ("Foothill (Pleasanton)" -> "foothill",
             "Liberty - Brentwood" -> "liberty"), when that base belongs to one school only
  prefix     spelling looks truncated (Hy-Tek cuts school names to 12 characters) and is
             the start of exactly one canonical name or base; a one-letter truncated
             tail ("California S") is too little evidence and goes to review
  generic    canonical name = spelling + generic words only ("St. Mary's" -> "St Mary's
             College", "Salesian" -> "Salesian College Preparatory")

If a rule finds several candidates, the areas of the Area meets where the spelling was
seen are used to narrow them ("California" at Tri-Valley -> "California (San Ramon)");
that is recorded as `+area`. Anything else goes to the review queue with its candidates.
Renames (e.g. Analy / West County) are never merged automatically.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

LIST_AREAS = {"Tri-Valley": "tri-valley", "Bayshore": "bay-shore", "Bay Shore": "bay-shore",
              "Redwood Empire": "redwood-empire", "Class A": "class-a"}
SEASONS = (2019, 2022, 2023, 2024, 2025, 2026)
HYTEK_WIDTH = 12
GENERIC = {"college", "preparatory", "prep", "high", "school", "hs", "academy"}

# Notes for the review queue only; never used to match. From docs/audit.md §2.1 and common
# knowledge, all unconfirmed (renames question is open).
RENAME_HINTS = {
    "west county": "possible rename of Analy (unconfirmed)",
    "university sf": "possibly San Francisco University (unconfirmed)",
    "sir francis drake": "possibly former name of Archie Williams (unconfirmed)",
    "sir francis": "possibly former name of Archie Williams (unconfirmed)",
}

_NC_SUFFIX = re.compile(r"\s*\((?:nc?|ncs)?\)?\s*$", re.I)      # "(Nc)", "(N", "(" from truncation
_QUALIFIER = re.compile(r"\s*(?:\([^)]*\)|\s-\s.*)$")          # "(Pleasanton)", " - Brentwood"
_RELAY_LABEL = re.compile(r"\s+'[A-F]'$")                    # only quoted: "California C" is a school


def norm(s: str) -> str:
    """Case-, accent- and punctuation-insensitive form used for comparison only."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = s.replace("&", " and ").replace("’", "'")
    s = re.sub(r"'s\b", "", s)                 # possessive: St. Bernard's -> st bernard
    s = s.replace("'", "")
    s = re.sub(r"\bsaint\b", "st", s)
    s = re.sub(r"\bprep\b", "preparatory", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def slug(s: str) -> str:
    return norm(s).replace(" ", "-")


def clean_raw(raw: str) -> str:
    """Drop the "(Nc)" marker (full or truncated) and relay labels; keep everything else."""
    s = _RELAY_LABEL.sub("", raw.strip())
    return _NC_SUFFIX.sub("", s).strip()


def looks_truncated(raw: str) -> bool:
    # Hy-Tek pads/cuts to 12; a cut at a space leaves 11 visible characters.
    return len(raw.strip()) in (HYTEK_WIDTH - 1, HYTEK_WIDTH)


# ---------------------------------------------------------------------------
# Canonical list
# ---------------------------------------------------------------------------
def load_canonical(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df["area"] = df["List"].map(LIST_AREAS)
    if df["area"].isna().any():
        raise ValueError(f"unknown list names: {sorted(df.loc[df['area'].isna(), 'List'].unique())}")
    df["school_key"] = df["School"].map(slug)
    if df["school_key"].duplicated().any():
        raise ValueError(f"duplicate canonical schools: {df.loc[df['school_key'].duplicated(), 'School'].tolist()}")
    df["name_norm"] = df["School"].map(norm)
    df["base_norm"] = df["School"].map(lambda s: norm(_QUALIFIER.sub("", s)))
    return df[["school_key", "School", "area", "name_norm", "base_norm"]].rename(columns={"School": "canonical_name"})


# ---------------------------------------------------------------------------
# Raw spellings
# ---------------------------------------------------------------------------
_PLACE_LINE = re.compile(r"^\s*(?:\d+|--)\s+\S")
_LEG_LINE = re.compile(r"^\s*\d\)")
# The school cell ends where the mark or status begins (marks are right-aligned, so the
# next header's position is not reliable, especially in relay blocks).
_CELL_END = re.compile(r"\s+(?=(?:[JjXx]?\d|DQ\b|DNF\b|DNS\b|NH\b|NM\b|ND\b|NT\b|FOUL\b|FS\b|SCR\b|--|X\b))")


def hytek_school_strings(text: str) -> list[str]:
    """School strings from a Hy-Tek results <pre> text, located by each block's header."""
    out = []
    start = None
    for line in text.splitlines():
        if re.search(r"\bSchool\b", line) and not _PLACE_LINE.match(line):
            start = line.index("School")
            continue
        if start is None or not _PLACE_LINE.match(line) or _LEG_LINE.match(line):
            continue
        # A cell that starts mid-word is misaligned; skip it rather than keep half a name.
        if len(line) <= start or not line[start - 1].isspace() or line[start].isspace():
            continue
        cell = _CELL_END.split(line[start:], maxsplit=1)[0].strip()
        if cell:
            out.append(cell)
    return out


def collect_spellings(hytek_files: list[Path], moc_entries: pd.DataFrame | None,
                      meets: pd.DataFrame, root: Path) -> pd.DataFrame:
    """One row per (raw spelling, source file) with the meet's area (blank for MOC)."""
    area_of = dict(zip(meets["meet_key"], meets["area"].fillna("")))
    rows = []
    for f in hytek_files:
        meet_key = f.name.split(".")[0]
        text = f.read_text(encoding="latin-1")
        for s in hytek_school_strings(text):
            rows.append((s, "hytek", str(f.relative_to(root)), meet_key, area_of.get(meet_key, "")))
    if moc_entries is not None:
        for (s, src, mk), _ in moc_entries.groupby(["school_name", "source_file", "meet_key"]):
            rows.append((s, "moc_program", src, mk, ""))
    df = pd.DataFrame(rows, columns=["raw", "source", "source_file", "meet_key", "meet_area"])
    df["raw"] = df["raw"].str.strip()
    return df[df["raw"] != ""].drop_duplicates().reset_index(drop=True)


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------
def _candidates(raw: str, canon: pd.DataFrame) -> tuple[str | None, list[str]]:
    """(rule, candidate school_keys) for the first rule that finds any candidate."""
    c = norm(clean_raw(raw))
    if not c:
        return None, []
    c0 = c.replace(" ", "")
    for rule, mask in (
        ("exact", canon["name_norm"] == c),
        ("nospace", canon["name_norm"].str.replace(" ", "") == c0),
        ("base", canon["base_norm"] == c),
    ):
        if mask.any():
            return rule, canon.loc[mask, "school_key"].tolist()
    truncated = looks_truncated(raw) or bool(_NC_SUFFIX.search(raw.strip()) and "(" in raw
                                              and not raw.strip().endswith(")"))
    if truncated and len(c.split()[-1]) == 1:
        return "prefix-weak", []
    if truncated:
        mask = canon["name_norm"].str.startswith(c) | canon["base_norm"].str.startswith(c)
        if mask.any():
            return "prefix", canon.loc[mask, "school_key"].tolist()
    ctoks = c.split()

    def generic_extension(name: str) -> bool:
        toks = name.split()
        return toks[: len(ctoks)] == ctoks and len(toks) > len(ctoks) and set(toks[len(ctoks):]) <= GENERIC
    mask = canon["name_norm"].map(generic_extension)
    if mask.any():
        return "generic", canon.loc[mask, "school_key"].tolist()
    return None, []


def match_spellings(spellings: pd.DataFrame, canon: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(matched long table, review queue)."""
    area_of = dict(zip(canon["school_key"], canon["area"]))
    name_of = dict(zip(canon["school_key"], canon["canonical_name"]))
    seen = spellings.groupby("raw").agg(
        sources=("source", lambda s: "|".join(sorted(set(s)))),
        meet_keys=("meet_key", lambda s: "|".join(sorted(set(s)))),
        meet_areas=("meet_area", lambda s: sorted(set(a for a in s if a))),
    ).reset_index()

    matched, review = [], []
    for _, r in seen.iterrows():
        rule, cands = _candidates(r["raw"], canon)
        method = rule
        if len(cands) > 1 and r["meet_areas"]:
            narrowed = [k for k in cands if area_of[k] in r["meet_areas"]]
            if len(narrowed) == 1:
                cands, method = narrowed, f"{rule}+area"
        base = {"raw": r["raw"], "sources": r["sources"], "meet_keys": r["meet_keys"],
                "seen_at_areas": "|".join(r["meet_areas"])}
        if len(cands) == 1:
            k = cands[0]
            if r["meet_areas"] and area_of[k] not in r["meet_areas"]:
                review.append({**base, "reason": f"matched {name_of[k]} ({area_of[k]}) by {method}, "
                               f"but seen at a different Area meet",
                               "candidates": name_of[k], "hint": ""})
                continue
            matched.append({**base, "school_key": k, "method": method})
        else:
            if rule == "prefix-weak":
                reason = "truncated to a one-letter tail; prefix too weak to match"
            elif not cands:
                reason = "no canonical school fits"
            else:
                reason = f"ambiguous ({rule}): {len(cands)} candidates"
            review.append({**base, "reason": reason, "candidates": "|".join(name_of[k] for k in cands),
                           "hint": RENAME_HINTS.get(norm(clean_raw(r["raw"])), "")})
    m_cols = ["raw", "school_key", "method", "sources", "meet_keys", "seen_at_areas"]
    r_cols = ["raw", "reason", "candidates", "hint", "sources", "meet_keys", "seen_at_areas",
              "school_key_decision", "notes"]
    rv = pd.DataFrame(review, columns=r_cols[:-2])
    rv["school_key_decision"] = ""
    rv["notes"] = ""
    return pd.DataFrame(matched, columns=m_cols), rv[r_cols]


def alias_table(canon: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    """One row per canonical school with every matched spelling and a per-season area."""
    spell = matched.groupby("school_key")["raw"].apply(lambda s: "|".join(sorted(set(s))))
    out = canon[["school_key", "canonical_name", "area"]].copy()
    out["spellings"] = out["school_key"].map(spell).fillna("")
    for season in SEASONS:
        out[f"area_{season}"] = out["area"]
    out["area_source"] = "ncs_source_of_truth_lists.csv (undated list; same area applied to every season)"
    out["athleticnet_school_id"] = ""
    return out.drop(columns="area")


def build(root: Path, canon_path: Path, hytek_files: list[Path], moc_entries: pd.DataFrame | None,
          meets: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    canon = load_canonical(canon_path)
    spellings = collect_spellings(hytek_files, moc_entries, meets, root)
    matched, review = match_spellings(spellings, canon)
    return alias_table(canon, matched), matched, review


def lookup(matched: pd.DataFrame) -> dict[str, str]:
    """raw spelling -> school_key, for joins."""
    return dict(zip(matched["raw"], matched["school_key"]))

