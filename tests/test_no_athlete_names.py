"""Fail if a real athlete name appears in any file git tracks (or would add).

Names come from data/processed/, which only exists on a machine that has rebuilt the
data; a public clone skips this test.
"""

import pytest

from ncs_track import paths, privacy


def test_no_athlete_names_in_tracked_files():
    names = privacy.names_from_processed(paths.PROCESSED) if paths.PROCESSED.exists() else set()
    if not names:
        pytest.skip("no data/processed/*.csv to take names from")
    forms = privacy.forms_for(names) - privacy.allowed_forms(paths.REFERENCE)
    leaks = privacy.scan(privacy.tracked_files(paths.ROOT), forms, paths.ROOT)
    assert leaks == {}, f"real athlete names in tracked files: {leaks}"


def test_scanner_finds_both_name_orders():
    forms = privacy.forms_for(["Quenby, Rosalind Mae", "Barnaby Quill"])
    assert privacy.find("see QUENBY, Rosalind Mae (heat 2)", forms) == ["quenby rosalind mae"]
    assert privacy.find("Quill, Barnaby 12 Albany", forms) == ["quill barnaby"]
    assert privacy.find("Barnaby Quillfeather", forms) == []
