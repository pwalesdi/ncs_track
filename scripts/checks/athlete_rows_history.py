"""Check every blob in all history for the athlete-level MOC-place tables (and their JSON
embedded in old dashboards). Exit 1 if any is found.

    .venv/bin/python scripts/checks/athlete_rows_history.py
"""

import subprocess
import sys

from ncs_track import paths

# Signatures of the removed tables: their CSV headers and their dashboard JSON keys.
SIGNATURES = [
    b"season,gender,event_code,area,route,top_finish,moc_overall_place",      # core_places.csv
    b"season,gender,event_code,area,route,moc_overall_place,top_finish,count",  # core_place_counts.csv
    b'"core_places":[{', b'"core_place_counts":[{',                         # data arrays in dashboards
    b"season,gender,event_code,area,rank_among_non_qualifiers,area_place,area_mark",  # left_out.csv
    b"season,gender,event_code,area,qualifier_type,rollup,competed,top_finish",       # unsuppressed moc_performance.csv
]
REMOVED_PATHS = ["data/summary/core_places.csv", "data/summary/core_place_counts.csv", "data/summary/left_out.csv"]


def git(*a, **kw) -> bytes:
    return subprocess.run(["git", *a], cwd=paths.ROOT, capture_output=True, check=True, **kw).stdout


def main() -> int:
    hits = []
    for path in REMOVED_PATHS:
        if git("log", "--all", "--oneline", "--", path).strip():
            hits.append(f"path still in history: {path}")
    objs = {}
    for line in git("rev-list", "--all", "--objects").decode().splitlines():
        sha, _, path = line.partition(" ")
        objs.setdefault(sha, path)
    batch = git("cat-file", "--batch-check=%(objectname) %(objecttype)",
                input="\n".join(objs).encode()).decode().split("\n")
    blobs = [l.split()[0] for l in batch if l.endswith(" blob")]
    for sha in blobs:
        if objs[sha] == "scripts/checks/athlete_rows_history.py":      # its own signature strings
            continue
        data = git("cat-file", "-p", sha)
        for sig in SIGNATURES:
            if sig in data:
                hits.append(f"{objs[sha]} ({sha[:8]}): contains {sig.decode()}")
    commits = len(git("rev-list", "--all").split())
    print(f"scanned {len(blobs)} blobs in {commits} commits")
    for h in hits:
        print("FOUND", h)
    print("no athlete-level MOC-place tables in history" if not hits else f"{len(hits)} problem(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
