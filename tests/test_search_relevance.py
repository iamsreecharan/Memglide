"""Retrieval regressions with independent, domain-varied examples, not task oracles."""

from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path

import pytest

from memglide.core.indexer import Indexer
from memglide.core.query import explicit_identifier, explicit_path, tokens
from memglide.storage.database import Database


def indexed(tmp_path: Path, sources: dict[str, str]) -> tuple[Indexer, Database, str]:
    root = tmp_path / "source"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for relative, content in sources.items():
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)
    db = Database(tmp_path / "state" / "index.db")
    indexer = Indexer(db)
    return indexer, db, indexer.add_project(str(root))["id"]


def test_shared_tokenizer_handles_acronyms_identifiers_and_regular_plurals() -> None:
    assert tokens("HTTPServer policyNames user_profiles") == [
        "http",
        "server",
        "policy",
        "name",
        "user",
        "profile",
    ]
    assert tokens("policies classes caches status series") == [
        "policy",
        "class",
        "cache",
        "status",
        "series",
    ]
    assert tokens("IDs APIKeys URLs") == ["id", "api", "key", "url"]
    assert tokens("indexes boxes buses batches brushes caches statuses sizes prizes") == [
        "index",
        "box",
        "bus",
        "batch",
        "brush",
        "cache",
        "status",
        "size",
        "prize",
    ]
    assert tokens("Which files have changes?", normalize=False, remove_stopwords=False) == [
        "which",
        "files",
        "have",
        "changes",
    ]


@pytest.mark.parametrize("name", ["Workspace", "Envelope", "Ledger"])
def test_plain_prose_nouns_are_not_explicit_identifiers(name: str) -> None:
    assert not explicit_identifier(f"Fix {name} validation rules", name, name)
    assert explicit_identifier(f"Inspect `{name}` validation rules", name, name)
    assert explicit_identifier(f"Inspect {name}() validation rules", name, name)


@pytest.mark.parametrize("name", ["parse_ticket", "parseTicket", "HTTPParser", "Ledger.total"])
def test_code_shaped_identifiers_remain_explicit(name: str) -> None:
    assert explicit_identifier(f"Inspect {name} validation rules", name, name)
    assert not explicit_identifier(f"Inspect {name}Suffix validation", name, name)


def test_query_noun_does_not_outrank_specific_shipping_evidence(tmp_path: Path) -> None:
    indexer, _, project = indexed(
        tmp_path,
        {
            "workspace.py": "class Workspace:\n    pass\n",
            "deliveries.py": (
                "def validate_postcode(value):\n"
                "    '''Shipping addresses reject invalid postcodes.'''\n"
                "    return value.isalnum()\n"
            ),
            "colors.py": "def palette():\n    return ['blue']\n",
        },
    )
    result = indexer.search(project, "Fix workspace shipping addresses rejecting invalid postcodes")
    assert result[0]["path"] == "deliveries.py"
    workspace = next(row for row in result if row.get("name") == "Workspace")
    assert "explicit symbol" not in workspace["reason"]
    assert indexer.search(project, "Workspace")[0]["name"] == "Workspace"
    assert indexer.search(project, "Inspect `Workspace` validation")[0]["name"] == "Workspace"


def test_rare_term_beats_ubiquitous_class_noun(tmp_path: Path) -> None:
    sources = {
        "model.py": "class Entry:\n    pass\n",
        "geometry.py": "def contains(point):\n    '''Entry geofence boundaries.'''\n    return point\n",
        **{f"other_{number}.py": "# Entry activity\n" for number in range(5)},
    }
    indexer, _, project = indexed(tmp_path, sources)
    result = indexer.search(project, "entry geofence")
    assert result[0]["path"] == "geometry.py"
    assert result[0]["score"] > next(row["score"] for row in result if row.get("name") == "Entry")


def test_plural_camel_and_snake_forms_retrieve_same_declaration(tmp_path: Path) -> None:
    indexer, _, project = indexed(
        tmp_path,
        {
            "rules.ts": "export function inspectPolicyNames(value: string) { return value; }\n",
            "themes.py": "def change_color(value):\n    return value\n",
        },
    )
    for query in ("policy names", "policy_name", "policies name"):
        assert indexer.search(project, query)[0]["name"] == "inspectPolicyNames"


@pytest.mark.parametrize(
    "plural,singular", [("indexes", "index"), ("boxes", "box"), ("buses", "bus")]
)
def test_regular_plural_query_finds_singular_source_identifier(
    tmp_path: Path, plural: str, singular: str
) -> None:
    indexer, _, project = indexed(
        tmp_path,
        {
            "tools.py": f"def {singular}(value):\n    return value\n",
            "unrelated.py": "def shade():\n    return 'green'\n",
        },
    )
    matches = indexer.search(project, plural)
    assert matches[0]["name"] == singular
    assert matches[0]["path"] == "tools.py"


def test_path_references_are_strong_without_arbitrary_prefix_matching(tmp_path: Path) -> None:
    indexer, _, project = indexed(
        tmp_path,
        {"services/catalog.py": "def expand_catalog(value):\n    return value\n"},
    )
    assert not indexer.search(project, "cat")
    assert explicit_path("Update services/catalog.py to validate input", "services/catalog.py")
    assert explicit_path("catalog", "services/catalog.py")
    assert not explicit_path("cat", "services/catalog.py")
    result = indexer.search(project, "Update services/catalog.py to validate input")
    assert result[0]["kind"] == "file"
    assert "matching file path" in result[0]["reason"]


def test_zero_exact_weight_does_not_invent_requested_callees(tmp_path: Path) -> None:
    indexer, db, project = indexed(
        tmp_path,
        {
            "addresses.py": "def format_address(value):\n    return str(value)\n",
            "checkout.py": (
                "from addresses import format_address\n"
                "def summarize(value):\n    return format_address(value)\n"
            ),
        },
    )
    weights = db.settings()["retrieval_weights"]
    weights["exact_symbol"] = 0
    db.execute("UPDATE settings SET value=? WHERE key='retrieval_weights'", (json.dumps(weights),))
    result = indexer.search(project, "Which functions call address formatting?")
    assert not any("resolved caller" in row["reason"] for row in result)
    requested = indexer.search(project, "Which functions call format_address?")
    assert any(
        row["name"] == "summarize" and "resolved caller" in row["reason"] for row in requested
    )
    disabled = {key: 0 for key in weights}
    db.execute("UPDATE settings SET value=? WHERE key='retrieval_weights'", (json.dumps(disabled),))
    assert not indexer.search(project, "Which functions call format_address?")


def test_configured_field_weights_still_control_ranking(tmp_path: Path) -> None:
    indexer, db, project = indexed(
        tmp_path, {"shipping.py": "def validate_postcode(value):\n    return value\n"}
    )
    assert indexer.search(project, "validate_postcode")[0]["kind"] == "function"
    weights = db.settings()["retrieval_weights"]
    weights["full_text"] = 1000
    db.execute("UPDATE settings SET value=? WHERE key='retrieval_weights'", (json.dumps(weights),))
    assert indexer.search(project, "validate_postcode")[0]["kind"] == "file"


def test_existing_fts_index_upgrades_without_reparsing_or_changing_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    indexer, db, project = indexed(
        tmp_path,
        {"transport.py": "class HTTPServer:\n    pass\n"},
    )
    original_file = db.one("SELECT * FROM files WHERE project_id=?", (project,))
    original_symbol = db.one("SELECT * FROM symbols WHERE project_id=?", (project,))
    db.execute(
        "UPDATE file_search SET identifiers='HTTPServer HTTPServer httpserver' WHERE project_id=?",
        (project,),
    )
    db.execute("UPDATE projects SET index_stats='{}' WHERE id=?", (project,))

    def no_parsing(sources: dict[str, str]) -> dict[str, object]:
        assert not sources
        return {}

    monkeypatch.setattr("memglide.core.indexer.parse_sources", no_parsing)
    stats = indexer.reindex(project)
    assert stats["indexed"] == 0 and stats["search_index_refreshed"] == 1
    assert db.one("SELECT * FROM files WHERE project_id=?", (project,)) == original_file
    assert db.one("SELECT * FROM symbols WHERE project_id=?", (project,)) == original_symbol
    result = indexer.search(project, "http server", refresh=False)
    assert result[0]["name"] == "HTTPServer"
    assert indexer.reindex(project)["search_index_refreshed"] == 0


def test_long_queries_retain_terms_past_sqlite_batch_boundaries(tmp_path: Path) -> None:
    indexer, _, project = indexed(
        tmp_path, {"rare.py": "def spectrometer():\n    return 'wavelength'\n"}
    )
    query = " ".join(f"absent{number}" for number in range(400)) + " wavelength"
    assert len(query) <= 4000
    assert indexer.search(project, query)[0]["path"] == "rare.py"


def test_rare_late_term_survives_many_matching_common_query_terms(tmp_path: Path) -> None:
    common = " ".join(f"shared{number}" for number in range(80))
    sources = {
        **{f"bulk{number}.py": f"# {common}\n" for number in range(5)},
        "rare.py": f"# {common}\ndef spectrometer():\n    return 'wavelength'\n",
    }
    indexer, _, project = indexed(tmp_path, sources)
    # Every early term matches all files. Candidate generation must use corpus
    # specificity, rather than taking an arbitrary prefix of the prompt.
    assert indexer.search(project, common + " wavelength")[0]["path"] == "rare.py"


def test_vocabulary_frequencies_preserve_plural_unions_unicode_and_project_scope(
    tmp_path: Path,
) -> None:
    indexer, db, project = indexed(
        tmp_path, {"policy.py": "# policy policies café box\n", "other.py": "# unrelated\n"}
    )
    expressions = {
        "policy": '("policy" OR "policies")',
        "café": '("café")',
        "box": '("box" OR "boxes")',
        "absent": '("absent")',
    }
    with db.connect() as conn:
        frequencies = indexer._document_frequencies(conn, project, expressions)
    assert frequencies == {"policy": 1, "café": 1, "box": 1, "absent": 0}
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    subprocess.run(["git", "init", "-q", str(foreign)], check=True)
    (foreign / "policy.py").write_text("# policy policies café box absent\n")
    indexer.add_project(str(foreign))
    with db.connect() as conn:
        # Vocabulary counts are global; another project's documents must never
        # change the frequencies used to rank this project's source.
        assert indexer._document_frequencies(conn, project, expressions) == frequencies


def test_document_frequencies_fall_back_when_vocabulary_module_is_unavailable(
    tmp_path: Path,
) -> None:
    indexer, db, project = indexed(
        tmp_path,
        {"policy.py": "# policy policies café box\n", "other.py": "# policies\n"},
    )
    expressions = {
        "policy": '("policy" OR "policies")',
        "café": '("café")',
        "box": '("box" OR "boxes")',
        "absent": '("absent")',
    }
    with db.connect() as conn:

        class WithoutVocabulary:
            attempted_vocabulary = False

            def execute(self, sql: str, parameters: tuple[str, ...] = ()) -> sqlite3.Cursor:
                if "USING fts5vocab" in sql:
                    self.attempted_vocabulary = True
                    raise sqlite3.OperationalError("no such module: fts5vocab")
                return conn.execute(sql, parameters)

        restricted = WithoutVocabulary()
        assert indexer._document_frequencies(restricted, project, expressions) == {
            "policy": 2,
            "café": 1,
            "box": 1,
            "absent": 0,
        }
        assert restricted.attempted_vocabulary


def test_project_frequency_scope_resets_when_reusing_a_connection(tmp_path: Path) -> None:
    indexer, db, project = indexed(
        tmp_path, {"policy.py": "# policy policies box\n", "other.py": "# unrelated\n"}
    )
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    subprocess.run(["git", "init", "-q", str(foreign)], check=True)
    (foreign / "first.py").write_text("# policy policies absent\n")
    (foreign / "second.py").write_text("# policies\n")
    foreign_project = indexer.add_project(str(foreign))["id"]
    expressions = {
        "policy": '("policy" OR "policies")',
        "box": '("box" OR "boxes")',
        "absent": '("absent")',
    }
    first_expected = {"policy": 1, "box": 1, "absent": 0}
    foreign_expected = {"policy": 2, "box": 0, "absent": 1}
    with db.connect() as conn:
        assert indexer._document_frequencies(conn, project, expressions) == first_expected
        assert indexer._document_frequencies(conn, foreign_project, expressions) == foreign_expected
        assert indexer._document_frequencies(conn, project, expressions) == first_expected
