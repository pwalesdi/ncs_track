#!/usr/bin/env bash
# Run every privacy check; push only if all pass. Usage: scripts/checks/pre_push.sh [git push args]
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=.venv/bin/python

echo "1/5 leak test (tracked files vs data/processed names)"
$PY -m pytest -q tests/test_no_athlete_names.py

echo "2/5 name scan of every commit"
$PY scripts/checks/name_leaks.py

echo "3/5 commit emails"
emails=$(git log --all --format='%ae' | sort -u)
if [ "$emails" != "50930764+pwalesdi@users.noreply.github.com" ]; then
  echo "FAIL: unexpected commit emails: $emails"; exit 1
fi

echo "4/5 no athlete-data paths tracked"
if git ls-files | grep -E '^data/(raw/(athleticnet|hytek)|processed|reference/entries)/'; then
  echo "FAIL: athlete-data paths are tracked"; exit 1
fi
if git ls-files data/review | grep -v '^data/review/school_aliases_review\.csv$'; then
  echo "FAIL: data/review file other than school_aliases_review.csv is tracked"; exit 1
fi

echo "5/5 no athlete-level MOC-place tables anywhere in history"
$PY scripts/checks/athlete_rows_history.py

echo "all checks passed; pushing"
git push "$@"
