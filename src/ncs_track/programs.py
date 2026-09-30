"""Parse Hy-Tek "Meet Program" PDFs (heat sheets) into entry rows.

The programs are two-column pages. Each page is cropped into a left and right half and
read top to bottom, left then right; the parser is a line state machine, so an event that
continues into the next column or page ("Flight 2 of 3 Finals" with no event header, or
"Heat 3 of 3 Prelims...(Event 1 ...)") keeps its event.

Tolerant by design: a line that looks like an entry but can't be split cleanly is kept
with `parse_issues` set rather than dropped, and lines that aren't recognised at all are
returned separately so validation can report them.

A program lists every round. An athlete's *entry* is their row in the first round of the
event (prelims when the event has them, otherwise finals); later rounds list advancers
and are dropped by `entry_rows`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from pathlib import Path

import pandas as pd

from .events import parse_event, parse_gender
from .marks import MarkParseError, parse_mark

GRADES = {"7", "8", "9", "10", "11", "12", "FR", "SO", "JR", "SR"}
_GRADE_WORDS = {"FR": 9, "SO": 10, "JR": 11, "SR": 12}

ENTRY_COLUMNS = [
    "season", "meet_key", "gender", "event_code", "event_raw", "is_relay", "is_adaptive",
    "event_modifier", "round", "unit_type", "heat", "heats_total", "position",
    "athlete_name", "grade", "school_name", "relay_legs", "seed_mark_raw",
    "seed_mark_value", "seed_status", "seed_flags", "parse_issues", "source_file",
    "page", "column", "line",
]

_EVENT = re.compile(r"^Event\s+(\d+)\s+(Girls|Boys|Women|Men|Mixed)\s+(.+?)\s*$", re.I)
_UNIT = re.compile(r"^(Heat|Flight|Section)\s+(\d+)\s+of\s+(\d+)\s+(Prelims|Finals|Semis|Trials)\b(.*)$", re.I)
_CONT_EVENT = re.compile(r"\(Event\s+\d+\s+(Girls|Boys|Women|Men|Mixed)\s+(.+?)\)?\s*$", re.I)

# Lines that are never entries: page furniture, event metadata, column headers.
_NOISE = [re.compile(p, re.I) for p in (
    r"^Diablo Timing", r"Hy-Tek'?s MEET MANAGER", r"^NCS Meet of Champions", r"Meet Program",
    r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
    r"^\S*\s*-\s*\d{1,2}/\d{1,2}/\d{4}\s+to\s+", r"\bSchool\s*$", r"^(Pos|Lane)\s+(Name|Team)\b",
    r"^MOC:", r"At[- ]Large\s*$", r"Advance:", r"^am\s+-", r"^m\s+-", r"^-\s", r"^\S{0,12}$",
    r"^Dublin Hi", r"^Meet Progr", r"^r?a?m\s+-\s", r"attempts", r"^Opening Height",
    r"Unified competitor unit", r"added together", r"^Meet of Champions",
    # relay record holders: "M Drew, A Savage Brooks, M Terdiman, V Donohoe"
    r"^[A-Z]\.? [A-Z][\w'-]+(?: [\w'-]+)*, [A-Z]\.? [A-Z]",
)]

# Seed tokens: a mark (time or distance), or a no-mark word.
_SEED_TOKEN = r"(?:\d{1,3}(?::\d{2})*\.\d{1,3}|\d{1,3}-\d{1,2}(?:\.\d{1,2})?|NT|NM|ND|NH|SCR)"
_FLAG_TOKENS = r"(?:CIF|NCS|[*#@&xX]|q|Q|R)"
_TAIL = rf"(?P<seed>{_SEED_TOKEN})?(?P<flags>(?:\s+{_FLAG_TOKENS})*)\s*$"

# "12 Harrowgate II, Leopold 11 Heritage 42-09.00 CIF"
_INDIV = re.compile(
    rf"^(?P<pos>\d{{1,3}})\s+(?P<name>[^\d,][^\d]*?,[^\d]*?)\s+(?P<grade>{'|'.join(sorted(GRADES, key=len, reverse=True))})\s+"
    rf"(?P<school>.+?)\s+{_TAIL}"
)
# Grade missing (or printed "--"): name and school run together; resolved against known
# school strings.
_INDIV_NOGRADE = re.compile(rf"^(?P<pos>\d{{1,3}})\s+(?P<rest>[^\d,][^\d]*?,[^\d]+?)\s+{_TAIL}")
# "4 St. Mary's 46.98 CIF" / "8 Santa Rosa ( 52.10" / "3 Foothill (Nc) 'A' 8:06.08".
# Only a quoted letter is a relay label: "California C" is a school name.
_RELAY = re.compile(rf"^(?P<pos>\d{{1,3}})\s+(?P<school>[^,\d][^,]*?)(?:\s+'(?P<label>[A-F])')?\s+{_TAIL}")
_TRUNCATED_ADAPTIVE = re.compile(r"\b(Unif|Ambul|Divisio)", re.I)
_LEG = re.compile(r"(\d)\)\s*(.*?)(?=\s+\d\)|$)")
_LEG_GRADE = re.compile(r"^(.*?)(?:\s+(\d{1,2}|FR|SO|JR|SR))?$")


@dataclass
class _State:
    gender: str | None = None
    event_raw: str | None = None
    round: str | None = None
    unit_type: str | None = None
    heat: int | None = None
    heats_total: int | None = None
    seed_header: str | None = None
    last_row: dict | None = None


@dataclass
class ParseResult:
    rows: list[dict] = field(default_factory=list)
    unparsed: list[dict] = field(default_factory=list)


def extract_lines(pdf_path: Path) -> list[tuple[int, str, str]]:
    """(page, column, line) for every text line, left column before right."""
    import pdfplumber

    out = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            w, h = page.width, page.height
            for col, box in (("L", (0, 0, w / 2, h)), ("R", (w / 2, 0, w, h))):
                text = page.crop(box).extract_text() or ""
                out += [(i, col, ln.strip()) for ln in text.splitlines() if ln.strip()]
    return out


def _is_noise(line: str) -> bool:
    return any(p.search(line) for p in _NOISE)


def _round(word: str) -> str:
    return {"prelims": "prelim", "trials": "prelim", "semis": "semi"}.get(word.lower(), "final")


def _grade(tok: str | None) -> int | None:
    if not tok:
        return None
    return _GRADE_WORDS.get(tok.upper(), int(tok) if tok.isdigit() else None)


def _seed(raw: str | None, measure: str | None) -> tuple[float | None, str, list[str]]:
    """(value, status, issues) for a seed string."""
    if not raw:
        return None, "missing", ["seed missing"]
    if measure is None:
        return None, "unparsed", ["event not recognised; seed not parsed"]
    try:
        m = parse_mark(raw, measure)
    except MarkParseError as e:
        return None, "unparsed", [f"seed: {e}"]
    return m.value, m.status, []


def _split_school(rest: str, known_schools: set[str]) -> tuple[str, str | None]:
    """Split "Ormsby, Caspian El Cerrito" into name and school using known school strings."""
    words = rest.split()
    for k in range(1, len(words)):
        school = " ".join(words[k:])
        if school in known_schools and "," in " ".join(words[:k]):
            return " ".join(words[:k]), school
    return rest, None


def parse_lines(lines: list[tuple[int, str, str]], *, season: int, meet_key: str,
                source_file: str, known_schools: set[str] | None = None) -> ParseResult:
    known = known_schools or set()
    st = _State()
    res = ParseResult()

    def event_info():
        info = parse_event(st.event_raw or "")
        # Column cropping truncates long titles ("100 Meter Dash Boys Divisio Unif").
        if not info.is_adaptive and _TRUNCATED_ADAPTIVE.search(st.event_raw or ""):
            info = replace(info, is_adaptive=True)
        return info

    for page, col, line in lines:
        m = _EVENT.match(line)
        if m:
            st = _State(gender=parse_gender(m.group(2)) or m.group(2).lower(), event_raw=m.group(3))
            continue
        m = _UNIT.match(line)
        if m:
            unit = (m.group(1).lower(), int(m.group(2)), int(m.group(3)), _round(m.group(4)))
            # A page break repeats the current unit's header; the relay above keeps its legs.
            if unit != (st.unit_type, st.heat, st.heats_total, st.round):
                st.last_row = None
            st.unit_type, st.heat, st.heats_total, st.round = unit
            cont = _CONT_EVENT.search(m.group(5) or "")
            if cont:
                st.gender = parse_gender(cont.group(1)) or cont.group(1).lower()
                st.event_raw = cont.group(2)
            continue
        if re.match(r"^(Pos|Lane)\s+(Name|Team)", line, re.I):
            st.seed_header = "Prelims" if line.endswith("Prelims") else "Seed"
            continue
        if _LEG.match(line) and st.last_row is not None and st.last_row["is_relay"]:
            legs = []
            for _, leg in _LEG.findall(line):
                gm = _LEG_GRADE.match(leg.strip())
                legs.append(f"{gm.group(1)} {gm.group(2)}".strip() if gm.group(2) else gm.group(1))
            prev = st.last_row["relay_legs"]
            st.last_row["relay_legs"] = "; ".join(filter(None, [prev, *legs]))
            continue
        if _is_noise(line):
            continue

        info = event_info()
        base = {
            "season": season, "meet_key": meet_key, "gender": st.gender,
            "event_code": info.code, "event_raw": st.event_raw, "is_relay": info.is_relay,
            "is_adaptive": info.is_adaptive, "event_modifier": info.modifier,
            "round": st.round, "unit_type": st.unit_type, "heat": st.heat,
            "heats_total": st.heats_total, "relay_legs": None, "source_file": source_file,
            "page": page, "column": col, "line": line,
        }
        row = None
        if st.event_raw is None or st.round is None:
            pass
        elif info.is_relay:
            m = _RELAY.match(line)
            if m:
                row = {**base, "position": int(m.group("pos")), "athlete_name": None, "grade": None,
                       "school_name": m.group("school").strip() + (f" {m.group('label')}" if m.group("label") else ""),
                       "seed_mark_raw": m.group("seed"), "seed_flags": m.group("flags").split()}
        else:
            m = _INDIV.match(line)
            if m:
                row = {**base, "position": int(m.group("pos")), "athlete_name": m.group("name").strip(),
                       "grade": _grade(m.group("grade")), "school_name": m.group("school").strip(),
                       "seed_mark_raw": m.group("seed"), "seed_flags": m.group("flags").split(),
                       "_issues": []}
            else:
                m = _INDIV_NOGRADE.match(line)
                if m:
                    rest = m.group("rest")
                    if " -- " in rest:
                        name, school = (p.strip() for p in rest.split(" -- ", 1))
                    else:
                        name, school = _split_school(rest, known)
                    issues = ["grade missing"]
                    if school is None:
                        issues.append("name/school split unknown (no grade; school not recognised)")
                    row = {**base, "position": int(m.group("pos")), "athlete_name": name, "grade": None,
                           "school_name": school, "seed_mark_raw": m.group("seed"),
                           "seed_flags": m.group("flags").split(), "_issues": issues}
        if row is None:
            res.unparsed.append({"meet_key": meet_key, "source_file": source_file, "page": page,
                                 "column": col, "event_raw": st.event_raw,
                                 "in_scope": not info.is_adaptive, "line": line})
            continue
        issues = row.pop("_issues", [])
        value, status, seed_issues = _seed(row["seed_mark_raw"], info.measure)
        # A final listed with a "Prelims" column is an advancement round, not an entry list;
        # a blank seed there is normal.
        if st.seed_header == "Prelims" and status == "missing":
            seed_issues = []
        row.update(seed_mark_value=value, seed_status=status,
                   seed_flags=" ".join(row["seed_flags"]) or None,
                   parse_issues="; ".join(issues + seed_issues) or None)
        res.rows.append(row)
        st.last_row = row
    return res


def to_frame(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=ENTRY_COLUMNS)
    return df.astype({"season": "Int64", "heat": "Int64", "heats_total": "Int64",
                      "position": "Int64", "grade": "Int64", "page": "Int64",
                      "seed_mark_value": "Float64"})


def _event_key(df: pd.DataFrame) -> pd.Series:
    return (df["event_code"].fillna(df["event_raw"]) + "|" + df["is_adaptive"].astype(str)
            + "|" + df["event_modifier"].fillna(""))


def entry_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only each event's first round (prelim if it has one), i.e. the entry list."""
    order = {"prelim": 0, "semi": 1, "final": 2}
    r = df["round"].map(order)
    key = [df["season"], df["gender"], _event_key(df)]
    first = r.groupby(key, dropna=False).transform("min")
    return df[r == first].reset_index(drop=True)


def parse_program(pdf_path: Path, *, season: int, meet_key: str, source_file: str,
                  known_schools: set[str] | None = None) -> ParseResult:
    return parse_lines(extract_lines(pdf_path), season=season, meet_key=meet_key,
                       source_file=source_file, known_schools=known_schools)


# ---------------------------------------------------------------------------
# Build + validate data/processed/moc_entries.csv
# ---------------------------------------------------------------------------
FIELD_MIN, FIELD_MAX = 24, 32
RELAY_4X800_MAX = 16            # rules.relay_4x800.area_to_moc.field_max


def program_files(entries_dir: Path, level: str = "moc") -> list[Path]:
    return sorted(p for p in entries_dir.glob(f"*-{level}.*_program.pdf"))


def _file_season(path: Path) -> tuple[int, str]:
    meet_key = path.name.split(".")[0]
    return int(meet_key[:4]), meet_key


def build_moc_entries(files: list[Path], root: Path,
                      extra_schools: set[str] = frozenset()) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parse MOC programs. Returns (entries, unparsed lines).

    Two passes: the first collects school strings from rows that have a grade, the second
    uses them (plus `extra_schools`, e.g. canonical names) to split grade-less rows
    ("Ormsby, Caspian El Cerrito 130-07").
    """
    lines = {f: extract_lines(f) for f in files}

    def run(known):
        rows, unparsed = [], []
        for f, ls in lines.items():
            season, meet_key = _file_season(f)
            r = parse_lines(ls, season=season, meet_key=meet_key,
                            source_file=str(f.relative_to(root)), known_schools=known)
            rows += r.rows
            unparsed += r.unparsed
        return to_frame(rows), pd.DataFrame(unparsed)

    first, _ = run(set())
    known = set(first.loc[first["grade"].notna() | first["is_relay"], "school_name"].dropna()) | set(extra_schools)
    df, unparsed = run(known)
    return entry_rows(df), unparsed


def validate_entries(entries: pd.DataFrame, unparsed: pd.DataFrame,
                     main_events: dict[str, list[str]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(counts per season/gender/event with a flag column, issues list)."""
    scope = entries[~entries["is_adaptive"] & entries["event_modifier"].isna()]
    counts = (scope.groupby(["season", "gender", "event_code"], dropna=False)
              .size().rename("entries").reset_index())
    # Events the rules expect but the program lacks count as zero.
    expected = pd.DataFrame([(s, g, e) for s in sorted(entries["season"].unique())
                             for g, evs in main_events.items() for e in evs],
                            columns=["season", "gender", "event_code"])
    counts = expected.merge(counts, how="outer").fillna({"entries": 0})
    counts["entries"] = counts["entries"].astype(int)

    def flag(r):
        if r["event_code"] == "4x800":
            return "over 16 (4x800 field max)" if r["entries"] > RELAY_4X800_MAX else None
        if r["entries"] < FIELD_MIN:
            return f"under {FIELD_MIN}"
        if r["entries"] > FIELD_MAX:
            return f"over {FIELD_MAX}"
        return None
    counts["flag"] = counts.apply(flag, axis=1)

    issues = []
    for _, r in counts[counts["flag"].notna()].iterrows():
        issues.append({"kind": "count", "season": r["season"], "gender": r["gender"],
                       "event": r["event_code"], "detail": f"{r['entries']} entries ({r['flag']})",
                       "source_file": None, "page": None, "line": None})
    for _, r in entries[entries["parse_issues"].notna()].iterrows():
        issues.append({"kind": "field_adaptive" if r["is_adaptive"] else "field", "season": r["season"], "gender": r["gender"],
                       "event": r["event_code"] or r["event_raw"], "detail": r["parse_issues"],
                       "source_file": r["source_file"], "page": r["page"], "line": r["line"]})
    for _, r in entries[entries["seed_status"].isin(["NT", "NM", "NH", "SCR"])].iterrows():
        issues.append({"kind": "seed_no_mark", "season": r["season"], "gender": r["gender"],
                       "event": r["event_code"], "detail": f"seed {r['seed_status']}",
                       "source_file": r["source_file"], "page": r["page"], "line": r["line"]})
    dup_key = ["season", "gender", "event_code", "athlete_name", "school_name"]
    ind = scope[~scope["is_relay"]]
    for _, r in ind[ind.duplicated(dup_key, keep=False)].iterrows():
        issues.append({"kind": "duplicate_entry", "season": r["season"], "gender": r["gender"],
                       "event": r["event_code"], "detail": "athlete listed twice in entry round",
                       "source_file": r["source_file"], "page": r["page"], "line": r["line"]})
    for _, r in unparsed.iterrows():
        issues.append({"kind": "unparsed_line" if r["in_scope"] else "unparsed_line_adaptive",
                       "season": int(r["meet_key"][:4]), "gender": None, "event": r["event_raw"],
                       "detail": "line not recognised", "source_file": r["source_file"],
                       "page": r["page"], "line": r["line"]})
    cols = ["kind", "season", "gender", "event", "detail", "source_file", "page", "line"]
    return counts, pd.DataFrame(issues, columns=cols)
