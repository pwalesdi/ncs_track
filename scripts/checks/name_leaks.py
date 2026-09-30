"""Pre-push check: no real athlete name in any blob of any commit, on any ref.

Names are taken from every local source: data/processed/, the Athletic.net CSVs, the
Hy-Tek result rows and relay legs. Run from the repo root:

    .venv/bin/python scripts/checks/name_leaks.py

Exit status 1 if a name is found.
"""

import glob
import re
import subprocess
import sys

import pandas as pd

from ncs_track import paths, privacy

ROW = re.compile(r"^\s*(?:\d+|--)\s+([^\d,]+?,\s*[^\d]+?)\s+(?:\d{1,2}\s)")
LEG = re.compile(r"\d\)\s+([^\d,]+?,\s*[^\d]+?)\s+\d{1,2}\b")


def all_names() -> set[str]:
    names = privacy.names_from_processed(paths.PROCESSED) if paths.PROCESSED.exists() else set()
    for f in glob.glob(str(paths.RAW_ATHLETICNET / "*.csv")):
        d = pd.read_csv(f, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        names |= set(d["athlete_name"])
        for legs in d["relay_leg_names"]:
            names |= {x for x in legs.split("|") if x}
    for f in glob.glob(str(paths.RAW_HYTEK / "*.htm")):
        for line in open(f, encoding="latin-1"):
            m = ROW.match(line)
            if m:
                names.add(m.group(1).strip())
            names |= {x.strip() for x in LEG.findall(line)}
    names.discard("")
    return names


def git(*args) -> bytes:
    return subprocess.run(["git", *args], cwd=paths.ROOT, capture_output=True, check=True).stdout


def main() -> int:
    forms = privacy.forms_for(all_names()) - privacy.allowed_forms(paths.REFERENCE)
    blobs = {}
    for line in git("rev-list", "--all", "--objects").decode().splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            blobs.setdefault(parts[0], parts[1])
    leaks = {}
    for sha, path in blobs.items():
        if git("cat-file", "-t", sha).strip() != b"blob":
            continue
        data = git("cat-file", "-p", sha)
        if b"\0" in data[:8192] or path.lower().endswith(".pdf"):
            continue
        hits = privacy.find(data.decode("utf-8", errors="replace"), forms)
        if hits:
            leaks[f"{path} ({sha[:8]})"] = hits
    print(f"{len(forms)} name forms checked against {len(blobs)} objects in all history")
    for k, v in leaks.items():
        print(f"LEAK {k}: {len(v)} names, e.g. {v[:3]}")
    print("no athlete names in history" if not leaks else f"{len(leaks)} blob(s) contain athlete names")
    return 1 if leaks else 0


if __name__ == "__main__":
    sys.exit(main())
