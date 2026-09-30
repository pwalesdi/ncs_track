"""School alias table: every raw school spelling -> one canonical school.

Canonical schools are the rows of data/reference/ncs_source_of_truth_lists.csv, plus any
school that competed at an Area meet in the Athletic.net results but is not on the list
(`in_source_list` = False). Raw spellings come from the Hy-Tek results, the MOC programs
and Athletic.net.

Athletic.net school IDs: each Athletic.net (school_id, name) is matched to the list by the
exact / nospace / base / confirmed rules only (its names are full, never truncated). An ID
is recorded only when it maps to exactly one school and that school gets exactly one ID;
anything else goes to review.

Area per season = the Area meet the school actually competed at in that season's
Athletic.net results ("area from meet participation"). The source-of-truth list is kept
as `list_area` and checked against 2026 participation. 2019 has no Athletic.net data, so
area_2019 is blank.

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

  athlete    (programs only) the spelling's MOC entrants, matched by name to the same
             season's Athletic.net MOC results, all belong to one Athletic.net school, and
             at least ATHLETE_LINK_MIN different athletes agree; used only when the name
             rules fail ("Urban-SF (Nc)" -> Urban of San Francisco)

If a rule finds several candidates, the areas of the Area meets where the spelling was
seen are used to narrow them ("California" at Tri-Valley -> "California (San Ramon)");
that is recorded as `+area`. Anything else goes to the review queue with its candidates.
Renames are merged only when confirmed (CONFIRMED_ALIASES); unconfirmed ones (Analy /
West County / El Molino) go to review with a hint.
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

ATHLETICNET_SEASONS = (2022, 2023, 2024, 2025, 2026)
AREA_SOURCE = ("area_2022..area_2026: area from meet participation (Athletic.net Area meets); "
               "area_2019: blank (no Athletic.net data)")

# Renames/aliases confirmed by Patrick 2026-09-29. Keys are norm(clean_raw(spelling)).
CONFIRMED_ALIASES = {
    "sir francis drake": "archie-williams",       # renamed 2020
    "sir francis": "archie-williams",             # truncated form of the same
    "university sf": "san-francisco-university",
    "sf university": "san-francisco-university",
    "san francisco university": "san-francisco-university",
}

# Notes for the review queue only; never used to match. Unconfirmed.
RENAME_HINTS = {
    "west county": "possible rename of Analy (unconfirmed)",
    "el molino": "possibly merged into Analy / West County (unconfirmed)",
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
def _canon_frame(names: list[str], areas: list[str | None], in_list: bool) -> pd.DataFrame:
    df = pd.DataFrame({"canonical_name": names, "area": areas})
    df["school_key"] = df["canonical_name"].map(slug)
    df["in_source_list"] = in_list
    df["name_norm"] = df["canonical_name"].map(norm)
    df["base_norm"] = df["canonical_name"].map(lambda s: norm(_QUALIFIER.sub("", s)))
    return df[["school_key", "canonical_name", "area", "in_source_list", "name_norm", "base_norm"]]


def load_canonical(path: Path) -> pd.DataFrame:
    """The source-of-truth list. `area` is the list's area (later kept as `list_area`)."""
    df = pd.read_csv(path, dtype=str)
    areas = df["List"].map(LIST_AREAS)
    if areas.isna().any():
        raise ValueError(f"unknown list names: {sorted(df.loc[areas.isna(), 'List'].unique())}")
    out = _canon_frame(list(df["School"]), list(areas), True)
    if out["school_key"].duplicated().any():
        raise ValueError(f"duplicate canonical schools: {out.loc[out['school_key'].duplicated(), 'canonical_name'].tolist()}")
    return out


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
    if c in CONFIRMED_ALIASES and CONFIRMED_ALIASES[c] in set(canon["school_key"]):
        return "confirmed", [CONFIRMED_ALIASES[c]]
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


def match_spellings(spellings: pd.DataFrame, canon: pd.DataFrame,
                    areas_of: dict[str, set[str]] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(matched long table, review queue).

    `areas_of`: school_key -> every area it is known to belong to (list area and meet
    participation); defaults to the list area.
    """
    if areas_of is None:
        areas_of = {k: {a} for k, a in zip(canon["school_key"], canon["area"]) if a}
    area_of = {k: "|".join(sorted(v)) for k, v in areas_of.items()}
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
            narrowed = [k for k in cands if areas_of.get(k, set()) & set(r["meet_areas"])]
            if len(narrowed) == 1:
                cands, method = narrowed, f"{rule}+area"
        base = {"raw": r["raw"], "sources": r["sources"], "meet_keys": r["meet_keys"],
                "seen_at_areas": "|".join(r["meet_areas"])}
        if len(cands) == 1:
            k = cands[0]
            if r["meet_areas"] and areas_of.get(k) and not areas_of[k] & set(r["meet_areas"]):
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


# ---------------------------------------------------------------------------
# Athletic.net: school IDs and meet participation
# ---------------------------------------------------------------------------
_ID_RULES = {"exact", "nospace", "base", "confirmed"}


def athleticnet_ids(perf: pd.DataFrame, canon: pd.DataFrame) -> tuple[dict[str, str], pd.DataFrame, list[dict]]:
    """(school_id -> school_key, new schools not on the list, review rows).

    `canon` is the source-of-truth list. Schools that don't match it become new canonical
    schools named as Athletic.net names them.
    """
    pairs = (perf[["school_id", "school_name_raw"]].dropna().astype(str)
             .drop_duplicates().sort_values(["school_id", "school_name_raw"]))
    review, id_map, new = [], {}, {}
    blank = perf[perf["school_id"].isna() | perf["school_id"].astype(str).isin(["0", ""])]
    for meet, g in blank.groupby("meet_key"):
        review.append({"raw": f"school_id 0 / blank ({meet})", "reason": f"{len(g)} rows with no Athletic.net school",
                       "candidates": "", "hint": "", "sources": "athleticnet", "meet_keys": meet, "seen_at_areas": ""})
    pairs = pairs[pairs["school_id"] != "0"]
    for sid, g in pairs.groupby("school_id"):
        if g["school_name_raw"].nunique() > 1:
            review.append({"raw": " | ".join(g["school_name_raw"]), "reason": f"Athletic.net school_id {sid} has several names",
                           "candidates": "", "hint": "", "sources": "athleticnet", "meet_keys": "", "seen_at_areas": ""})
            continue
        name = g["school_name_raw"].iloc[0]
        rule, cands = _candidates(name, canon)
        if rule in _ID_RULES and len(cands) == 1:
            id_map[sid] = cands[0]
        elif not cands or rule not in _ID_RULES:
            id_map[sid] = slug(name)
            new[slug(name)] = name
        else:
            review.append({"raw": name, "reason": f"Athletic.net school_id {sid}: ambiguous ({rule})",
                           "candidates": "|".join(cands), "hint": "", "sources": "athleticnet",
                           "meet_keys": "", "seen_at_areas": ""})
    # One school, one ID: a school claimed by several IDs is not confident.
    by_key: dict[str, list[str]] = {}
    for sid, k in id_map.items():
        by_key.setdefault(k, []).append(sid)
    for k, sids in by_key.items():
        if len(sids) > 1:
            for sid in sids:
                id_map.pop(sid)
            review.append({"raw": k, "reason": f"several Athletic.net school_ids {sids} map to one school",
                           "candidates": "", "hint": "", "sources": "athleticnet", "meet_keys": "", "seen_at_areas": ""})
    new_canon = _canon_frame(list(new.values()), [None] * len(new), False)
    new_canon = new_canon[new_canon["school_key"].isin(set(id_map.values()))]
    return id_map, new_canon, review


ATHLETE_LINK_MIN = 2


def _name_tokens(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower().replace("'", "")
    s = re.sub(r"\([^)]*\)|\b(jr|sr|ii|iii|iv)\b\.?", " ", s)
    return " ".join(sorted(re.findall(r"[a-z]+", s)))


def athlete_links(review: pd.DataFrame, moc_entries: pd.DataFrame, perf: pd.DataFrame,
                  id_map: dict[str, str]) -> pd.DataFrame:
    """Review spellings resolved through their athletes: raw, school_key, method, evidence."""
    ind = moc_entries[~moc_entries["is_relay"].astype(bool) & moc_entries["athlete_name"].notna()].copy()
    ind["tok"] = ind["athlete_name"].map(_name_tokens)
    an = perf[(perf["level"] == "moc") & perf["athlete_name_raw"].notna() & perf["school_id"].notna()].copy()
    an["tok"] = an["athlete_name_raw"].map(_name_tokens)
    an["school_key"] = an["school_id"].astype(str).map(id_map)
    an = an[["season", "gender", "event_code", "tok", "school_key"]].drop_duplicates()
    out = []
    for raw in review["raw"]:
        e = ind[ind["school_name"] == raw][["season", "gender", "event_code", "tok"]].drop_duplicates()
        hits = e.merge(an, on=["season", "gender", "event_code", "tok"])
        keys = set(hits["school_key"].dropna())
        athletes = hits["tok"].nunique()
        if len(keys) == 1 and athletes >= ATHLETE_LINK_MIN:
            out.append({"raw": raw, "school_key": keys.pop(), "method": f"athlete ({athletes} athletes)"})
    return pd.DataFrame(out, columns=["raw", "school_key", "method"])


def _is_unconfirmed_rename(raw: str) -> bool:
    return norm(clean_raw(raw)) in RENAME_HINTS


def participation(perf: pd.DataFrame, id_map: dict[str, str]) -> pd.DataFrame:
    """school_key, season, areas (sorted list) from Area-meet rows."""
    area = perf[(perf["level"] == "area") & perf["school_id"].notna()].copy()
    area["school_key"] = area["school_id"].astype(str).map(id_map)
    area = area.dropna(subset=["school_key", "meet_area"])
    return (area.groupby(["school_key", "season"])["meet_area"]
            .agg(lambda s: sorted(set(s))).rename("areas").reset_index())


def alias_table(canon: pd.DataFrame, matched: pd.DataFrame, id_map: dict[str, str] | None = None,
                part: pd.DataFrame | None = None) -> tuple[pd.DataFrame, list[dict]]:
    """One row per canonical school: spellings, Athletic.net ID, area per season. Also
    returns review rows for schools seen at two Area meets in one season."""
    spell = matched.groupby("school_key")["raw"].apply(lambda s: "|".join(sorted(set(s))))
    out = canon[["school_key", "canonical_name", "in_source_list", "area"]].rename(columns={"area": "list_area"}).copy()
    out["spellings"] = out["school_key"].map(spell).fillna("")
    ids = {k: sid for sid, k in (id_map or {}).items()}
    out["athleticnet_school_id"] = out["school_key"].map(ids).fillna("")
    review = []
    part = part if part is not None else pd.DataFrame(columns=["school_key", "season", "areas"])
    for season in SEASONS:
        p = part[part["season"] == season].set_index("school_key")["areas"]
        col = []
        for k in out["school_key"]:
            areas = p.get(k, [])
            if len(areas) > 1:
                review.append({"raw": dict(zip(out["school_key"], out["canonical_name"]))[k],
                               "reason": f"competed at {len(areas)} Area meets in {season}: {areas}",
                               "candidates": "", "hint": "", "sources": "athleticnet", "meet_keys": "",
                               "seen_at_areas": "|".join(areas)})
            col.append(areas[0] if len(areas) == 1 else "")
        out[f"area_{season}"] = col
    out["area_source"] = AREA_SOURCE
    return out, review


def area_vs_list(aliases: pd.DataFrame, season: int = 2026) -> pd.DataFrame:
    """Schools whose participation area differs from the source-of-truth list."""
    a = aliases[aliases["in_source_list"]]
    diff = a[a[f"area_{season}"] != a["list_area"]]
    return diff[["school_key", "canonical_name", "list_area", f"area_{season}"]].rename(
        columns={f"area_{season}": f"participation_area_{season}"})


def build(root: Path, canon_path: Path, hytek_files: list[Path], moc_entries: pd.DataFrame | None,
          meets: pd.DataFrame, perf: pd.DataFrame | None = None):
    """(aliases, matched spellings, review queue, 2026 area-vs-list report)."""
    canon = load_canonical(canon_path)
    spellings = collect_spellings(hytek_files, moc_entries, meets, root)
    id_map, part, review_an = {}, None, []
    if perf is not None:
        id_map, new_canon, review_an = athleticnet_ids(perf, canon)
        canon = pd.concat([canon, new_canon], ignore_index=True)
        part = participation(perf, id_map)
    areas_of: dict[str, set[str]] = {k: {a} for k, a in zip(canon["school_key"], canon["area"]) if a}
    if part is not None:
        for k, areas in zip(part["school_key"], part["areas"]):
            areas_of.setdefault(k, set()).update(areas)
    an_names = set()
    if perf is not None:
        names = perf[["school_id", "school_name_raw"]].dropna().astype(str).drop_duplicates()
        names = names[names["school_id"].isin(id_map)]
        an_names = set(names["school_name_raw"])
        spellings = spellings[~spellings["raw"].isin(an_names)]
    matched, review = match_spellings(spellings, canon, areas_of)
    if perf is not None and moc_entries is not None:
        links = athlete_links(review, moc_entries, perf, id_map)
        # Unconfirmed renames stay in review; the athlete evidence goes into the hint.
        held = links[links["raw"].map(_is_unconfirmed_rename)]
        for _, h in held.iterrows():
            i = review.index[review["raw"] == h["raw"]]
            review.loc[i, "hint"] = review.loc[i, "hint"] + f"; athlete link: {h['method']} -> {h['school_key']} in Athletic.net"
        links = links[~links["raw"].isin(held["raw"])]
        if len(links):
            info = review.set_index("raw").loc[links["raw"], ["sources", "meet_keys", "seen_at_areas"]].reset_index()
            matched = pd.concat([matched, links.merge(info, on="raw")], ignore_index=True)
            review = review[~review["raw"].isin(links["raw"])]
    if perf is not None:
        an = pd.DataFrame({"raw": names["school_name_raw"], "school_key": names["school_id"].map(id_map),
                           "method": "athleticnet_id", "sources": "athleticnet", "meet_keys": "", "seen_at_areas": ""})
        matched = pd.concat([matched, an], ignore_index=True).drop_duplicates("raw").sort_values("raw")
    aliases, review_area = alias_table(canon, matched, id_map, part)
    extra = pd.DataFrame(review_an + review_area, columns=review.columns[:-2])
    extra["school_key_decision"] = ""
    extra["notes"] = ""
    review = pd.concat([review, extra], ignore_index=True)
    return aliases, matched.reset_index(drop=True), review, area_vs_list(aliases)


def lookup(matched: pd.DataFrame) -> dict[str, str]:
    """raw spelling -> school_key, for joins."""
    return dict(zip(matched["raw"], matched["school_key"]))

