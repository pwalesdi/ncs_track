"""Repository paths. Everything is resolved from the repo root, never the CWD."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
RAW = DATA / "raw"
RAW_HYTEK = RAW / "hytek"
RAW_ATHLETICNET = RAW / "athleticnet"
MANIFEST = RAW / "MANIFEST.csv"

REFERENCE = DATA / "reference"
MEETS = REFERENCE / "meets.csv"
SCHOOLS = REFERENCE / "schools.csv"
SCHOOL_ALIASES = REFERENCE / "school_aliases.csv"
AREA_LISTS = REFERENCE / "ncs_source_of_truth_lists.csv"
RULES = REFERENCE / "rules"

PROCESSED = DATA / "processed"
REVIEW = DATA / "review"
OUTPUTS = ROOT / "outputs"


def rules_path(season: int) -> Path:
    return RULES / f"{season}.yaml"
