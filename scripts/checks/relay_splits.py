"""Check that no Athletic.net file has relay-split legs mislabelled as individual 400/800 rows.

Three checks (results recorded in docs/checks/relay_splits.md):

1. Row counts per meet, gender, event and round for 400/800, their "(Relay Split)" rows
   and the 4x400/4x800 relays.
2. Row-level signs of a mislabelled split in the individual 400/800: repeated athlete_id
   in one event+round, blank athlete_id, relay columns filled.
3. Independent sources: every Athletic.net 400/800 row must match an athlete in the Hy-Tek
   results for that meet and round (name-token match), and MOC prelim counts must equal
   the MOC program entry counts. Unmatched rows with a mark must pair one-for-one with
   unmatched Hy-Tek rows (spelling variants); the rest must be DNS/DQ rows, which Hy-Tek
   omits.

Run from the repo root: .venv/bin/python scripts/checks/relay_splits.py [--names]
--names also prints the unmatched athlete names (local use only; never commit them).
"""

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

from ncs_track import paths

SHOW_NAMES = "--names" in sys.argv
INDIVIDUAL = ["400 Meters", "800 Meters"]


def load_athleticnet() -> dict[str, pd.DataFrame]:
    meets = pd.read_csv(paths.MEETS, dtype=str, keep_default_na=False)
    key = dict(zip(meets["athleticnet_meet_id"], meets["meet_key"]))
    out = {}
    for f in sorted(paths.RAW_ATHLETICNET.glob("*.csv")):
        d = pd.read_csv(f, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        ids = set(d["meet_id"]) - {""}
        if len(ids) != 1:
            raise SystemExit(f"{f.name}: meet_id column has {sorted(ids)}")
        out[key[ids.pop()]] = d[d["division"] != "Unified"]
    return out


def counts(an: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for mk, d in an.items():
        x = d[d["event_raw"].str.contains("400|800")]
        for (g, ev, rd), y in x.groupby(["gender", "event_raw", "round_raw"]):
            rows.append({"meet": mk, "gender": g, "round": rd, "event": ev, "n": len(y)})
    return pd.DataFrame(rows).pivot_table(index=["meet", "gender", "round"], columns="event",
                                          values="n", aggfunc="sum").fillna(0).astype(int)


def row_signals(an: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for mk, d in an.items():
        for (g, ev, rd), x in d[d["event_raw"].isin(INDIVIDUAL)].groupby(["gender", "event_raw", "round_raw"]):
            ids = x["athlete_id"][x["athlete_id"] != ""]
            rows.append({"meet": mk, "gender": g, "event": ev[:3], "round": rd, "n": len(x),
                         "repeated_id": int(ids.duplicated().sum()),
                         "blank_id": int((x["athlete_id"] == "").sum()),
                         "relay_cols": int(((x["relay_team_label"] != "") | (x["relay_leg_names"] != "")).sum())})
    return pd.DataFrame(rows)


def _toks(name: str) -> frozenset:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower().replace("'", "")
    s = re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", " ", s)
    return frozenset(re.findall(r"[a-z]+", s))


_TITLE = re.compile(r"^(?:Event\s+\d+\s+)?(Girls|Boys)\s+(400|800) Meter (?:Dash|Run) Varsity\s*$")
_ROW = re.compile(r"^\s*(\d+|--)\s+(.+?,\s*\S.*?)\s{2,}")


def hytek_400_800(path: Path) -> pd.DataFrame:
    """Minimal reader: athlete names in the 400/800 blocks of a Hy-Tek results page."""
    out, cur, rd = [], None, None
    for line in open(path, encoding="latin-1"):
        line = line.rstrip("\n")
        m = _TITLE.match(line)
        if m:
            cur, rd = ({"Girls": "F", "Boys": "M"}[m.group(1)], m.group(2)), None
            continue
        if cur is None:
            continue
        if re.match(r"^\S", line) and line.strip() not in ("Preliminaries", "Finals") and not line.startswith("="):
            cur = None
            continue
        if line.strip() in ("Preliminaries", "Finals"):
            rd = line.strip()[:4]
            continue
        if re.search(r"\bName\b.*\bSchool\b", line):
            rd = "Prel" if "Prelims" in line else "Fina"
            continue
        m = _ROW.match(line)
        if m and rd:
            out.append((cur[0], cur[1], rd, re.sub(r"\s+\d{1,2}$", "", m.group(2).strip())))
    return pd.DataFrame(out, columns=["gender", "event", "round", "name"])


def against_hytek(an: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, detail = [], []
    for mk, d in an.items():
        h = paths.RAW_HYTEK / f"{mk}.htm"
        if not h.exists():
            continue
        ht = hytek_400_800(h)
        for (g, ev, rd), x in d[d["event_raw"].isin(INDIVIDUAL)].groupby(["gender", "event_raw", "round_raw"]):
            y = ht[(ht["gender"] == g) & (ht["event"] == ev[:3]) & (ht["round"] == rd[:4])]
            A, H = [_toks(n) for n in x["athlete_name"]], [_toks(n) for n in y["name"]]
            an_only = [(n, s) for n, s, t in zip(x["athlete_name"], x["status"], A) if t not in H]
            ht_only = [n for n, t in zip(y["name"], H) if t not in A]
            marked = sum(1 for _, s in an_only if not s)
            rows.append({"meet": mk, "gender": g, "event": ev[:3], "round": rd, "athleticnet": len(x),
                         "hytek": len(y), "an_only_with_mark": marked, "an_only_dns_dq": len(an_only) - marked,
                         "hytek_only": len(ht_only), "paired": marked == len(ht_only)})
            detail += [(mk, g, ev[:3], rd, "Athletic.net only", n, s) for n, s in an_only]
            detail += [(mk, g, ev[:3], rd, "Hy-Tek only", n, "") for n in ht_only]
    return pd.DataFrame(rows), pd.DataFrame(detail, columns=["meet", "gender", "event", "round", "side", "name", "status"])


def against_programs(an: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pe = pd.read_csv(paths.PROCESSED / "moc_entries.csv")
    pe = pe[pe["event_code"].isin(["400", "800"]) & ~pe["is_adaptive"]]
    prog = pe.groupby(["season", "gender", "event_code"]).size().rename("program")
    rows = []
    for mk, d in an.items():
        if not mk.endswith("-moc"):
            continue
        x = d[d["event_raw"].isin(INDIVIDUAL) & (d["round_raw"] == "Prelims")]
        for (g, ev), y in x.groupby(["gender", "event_raw"]):
            rows.append({"season": int(mk[:4]), "gender": {"F": "girls", "M": "boys"}[g],
                         "event_code": ev[:3], "athleticnet_prelims": len(y)})
    out = pd.DataFrame(rows).set_index(["season", "gender", "event_code"]).join(prog)
    out["diff"] = out["athleticnet_prelims"] - out["program"]
    return out


def main() -> int:
    pd.set_option("display.width", 250)
    pd.set_option("display.max_rows", 500)
    an = load_athleticnet()
    print(f"{len(an)} Athletic.net files\n\n1. Row counts\n{counts(an).to_string()}")
    sig = row_signals(an)
    print(f"\n2. Row-level signals: repeated ids {sig['repeated_id'].sum()}, blank ids {sig['blank_id'].sum()}, "
          f"relay columns filled {sig['relay_cols'].sum()} (all should be 0)")
    t, detail = against_hytek(an)
    print(f"\n3a. Against Hy-Tek ({t['meet'].nunique()} meets)\n{t.to_string(index=False)}")
    print(f"\nrows checked {t['athleticnet'].sum()} (Hy-Tek {t['hytek'].sum()}); "
          f"Athletic.net-only with mark {t['an_only_with_mark'].sum()}, DNS/DQ {t['an_only_dns_dq'].sum()}, "
          f"Hy-Tek-only {t['hytek_only'].sum()}; groups not pairing one-for-one: {(~t['paired']).sum()}")
    if SHOW_NAMES:
        print(detail.to_string(index=False))
    p = against_programs(an)
    print(f"\n3b. MOC prelims vs program entries\n{p.to_string()}")
    bad = sig[["repeated_id", "blank_id", "relay_cols"]].values.sum() + (~t["paired"]).sum() + (p["diff"] != 0).sum()
    print("\nPASS" if bad == 0 else f"\nFAIL ({bad} problems)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
