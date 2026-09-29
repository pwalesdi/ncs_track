import re

from ncs_track import manifest, paths
from ncs_track.schema import ATHLETICNET_COLUMNS, PERFORMANCES, RELAY_LEGS

SPEC = paths.ROOT / "docs" / "ingest_spec_athleticnet.md"


def test_repo_raw_files_untouched():
    assert manifest.check() == []


def test_manifest_detects_changes(tmp_path):
    raw = tmp_path / "data" / "raw"
    (raw / "hytek").mkdir(parents=True)
    f = raw / "hytek" / "x.htm"
    f.write_text("original")
    man = raw / "MANIFEST.csv"
    manifest.build(raw, man)
    assert manifest.check(raw, man) == []
    f.write_text("edited")
    (raw / "hytek" / "new.htm").write_text("new")
    problems = manifest.check(raw, man)
    assert any(p.startswith("CHANGED") for p in problems)
    assert any(p.startswith("not in manifest") for p in problems)


def test_manifest_keeps_provenance(tmp_path):
    raw = tmp_path / "data" / "raw"
    (raw / "hytek").mkdir(parents=True)
    (raw / "hytek" / "x.htm").write_text("a")
    man = raw / "MANIFEST.csv"
    df = manifest.build(raw, man)
    df.loc[0, "source_url"] = "https://example.test/x"
    df.to_csv(man, index=False)
    assert manifest.build(raw, man).loc[0, "source_url"] == "https://example.test/x"


def test_spec_documents_every_column_and_check():
    spec = SPEC.read_text()
    for col in (*ATHLETICNET_COLUMNS, *PERFORMANCES, *RELAY_LEGS):
        assert f"`{col}`" in spec, f"{col} missing from {SPEC.name}"
    for n in range(1, 16):
        assert re.search(rf"\bV{n:02d}\b", spec), f"V{n:02d} missing from spec"
