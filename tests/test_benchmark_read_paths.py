"""Shell-text regressions for read-command proxies; no command text is executed."""

from __future__ import annotations

import importlib.util
import json
import shlex
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "memglide_benchmark_read_paths", Path(__file__).resolve().parents[1] / "benchmarks/telemetry.py"
)
assert SPEC and SPEC.loader
telemetry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(telemetry)


@pytest.mark.parametrize("separator", ["\n", "\r\n", ";", "&&", "\n\n"])
def test_diff_operands_are_not_misattributed_to_preceding_cat(separator):
    command = "cat tests/test_parser.py" + separator + "git diff -- src/parser.py"
    assert telemetry.observed_read_paths(command) == ["tests/test_parser.py"]


def test_multiline_reads_and_cd_have_separate_literal_scope():
    command = (
        "cd src\ncat parser.py\ngit diff -- renderer.py\ncd ../tests\nsed -n '1,12p' test_parser.py"
    )
    assert telemetry.observed_read_paths(command) == [
        "src/parser.py",
        "src/../tests/test_parser.py",
    ]


@pytest.mark.parametrize("shell", ["bash", "/bin/bash", "sh", "/bin/sh", "zsh"])
@pytest.mark.parametrize("option", ["-c", "-lc"])
def test_native_shell_wrapper_preserves_inner_newline_boundaries(shell, option):
    command = (
        shell + " " + option + " " + shlex.quote("cd src\ncat parser.py\ngit diff -- renderer.py")
    )
    assert telemetry.observed_read_paths(command) == ["src/parser.py"]


@pytest.mark.parametrize("quote", ["'", '"'])
def test_quoted_newlines_remain_argument_data_and_cannot_create_fake_commands(quote):
    quoted = quote + "not-a-path.py\ncat invented.py" + quote
    assert telemetry.observed_read_paths("printf " + quoted + "\ncat real.py") == ["real.py"]
    assert telemetry.observed_read_paths("cat " + quoted + " safe.py\ngit diff -- changed.py") == [
        "safe.py"
    ]


@pytest.mark.parametrize(
    "command",
    [
        "cat src/pa\\\nrser.py\ngit diff -- other.py",
        'cat "src/pa\\\nrser.py"\ngit diff -- other.py',
    ],
)
def test_shell_line_continuation_does_not_create_a_command_boundary(command):
    assert telemetry.observed_read_paths(command) == ["src/parser.py"]


def test_multifile_line_continuation_keeps_literal_cat_operands():
    assert telemetry.observed_read_paths("cat first.py \\\n second.py\ngit diff -- third.py") == [
        "first.py",
        "second.py",
    ]


def test_shell_comment_ends_at_newline_without_joining_next_command():
    assert telemetry.observed_read_paths("cat first.py # ignored.py\ncat second.py") == [
        "first.py",
        "second.py",
    ]
    assert telemetry.observed_read_paths("cat first.py # ignored \\\ncat second.py") == [
        "first.py",
        "second.py",
    ]


def test_nested_standalone_shell_wrappers_remain_lexical_only():
    inner = "cat first.py\ngit diff -- second.py"
    command = "bash -lc " + shlex.quote("sh -c " + shlex.quote(inner))
    assert telemetry.observed_read_paths(command) == ["first.py"]


def test_inner_cd_cannot_escape_shell_wrapper_into_outer_command_scope():
    command = "bash -lc 'cd src; cat inner.py'\ncat outer.py"
    # Mixed outer/shell compound commands are conservatively not flattened.
    assert telemetry.observed_read_paths(command) == ["outer.py"]


@pytest.mark.parametrize(
    "command",
    [
        "cat source.py > output.py",
        "cat source.py >> output.py",
        "cat <<< source.py",
        "cat source.py >& output.py",
        "cat source.py <> other.py",
        "cat source.py |& head",
        "cat < source.py",
        "cat source.py | head",
        "cat source.py || cat fallback.py",
        "cat source.py & cat second.py",
        "cat <<'EOF'\ncat invented.py\nEOF\ncat actual.py",
        "cat <<EOF\n$(cat invented.py)\nEOF",
    ],
)
def test_redirections_heredocs_and_unsafe_operators_stay_excluded(command):
    assert telemetry.observed_read_paths(command) == []


def test_quoted_operator_characters_do_not_exclude_unrelated_literal_file():
    assert telemetry.observed_read_paths("printf '| << > &&'\ncat file.py") == ["file.py"]


def test_multiline_proxy_change_does_not_turn_observation_into_actual_io():
    def item(identifier, command):
        return {
            "type": "item.completed",
            "item": {
                "id": identifier,
                "type": "command_execution",
                "status": "completed",
                "exit_code": 0,
                "command": command,
            },
        }

    events = [
        item("one", "cat test_parser.py\ngit diff -- parser.py"),
        item("two", "git diff -- test_parser.py\ncat parser.py"),
        {
            "type": "turn.completed",
            "usage": {"input_tokens": 10, "cached_input_tokens": 5, "output_tokens": 1},
        },
    ]
    result = telemetry.parse_codex_jsonl("\n".join(json.dumps(event) for event in events))
    assert result["observed_file_read_commands"] == 2
    assert result["observed_repeated_read_commands"] == 0
    assert result["observed_read_command_paths"] == ["test_parser.py", "parser.py"]
    assert result["repeated_file_reads"] is None
    assert result["file_reads_complete"] is False


def test_here_doc_payload_never_executes_even_when_it_contains_shell_commands(tmp_path):
    marker = tmp_path / "must-not-exist"
    command = "cat <<'EOF'\ntouch " + str(marker) + "\ncat fake.py\nEOF"
    assert telemetry.observed_read_paths(command) == []
    assert not marker.exists()


def test_new_diagnostic_cli_refuses_to_replace_existing_output_before_reading_inputs(tmp_path):
    import subprocess
    import sys

    prefix = tmp_path / "retained-diagnostic"
    retained = prefix.with_suffix(".json")
    retained.write_text('{"preserved":true}\n')
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "benchmarks.read_path_diagnostics",
            "--experiment",
            str(tmp_path / "does-not-exist"),
            "--output-prefix",
            str(prefix),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2 and "already exist" in result.stderr
    assert retained.read_text() == '{"preserved":true}\n'
    assert not prefix.with_suffix(".md").exists()
