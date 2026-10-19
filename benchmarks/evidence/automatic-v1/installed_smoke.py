"""Exercise the built wheel from an isolated installed Python environment.

Run with that environment's Python and ``-I``. This script never contacts a
model: its one Codex handoff uses a controlled local fake installed executable.
The receipt is created exclusively so an earlier failed attempt is preserved.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

import memglide
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from memglide.integrations.auto_preload import prepare_task_prompt
from memglide.integrations.memory_preload import prepare_memory_prompt
from memglide.integrations.preload import TASK_SEPARATOR
from memglide.service import Service


async def smoke(receipt: dict[str, Any]) -> None:
    checks = receipt["checks"]
    module = Path(memglide.__file__).resolve()
    assert "site-packages" in module.parts, "use Python from a clean wheel installation"
    receipt["installed_module"] = str(module)
    checks["installed_wheel_import"] = True
    executable = sys.executable
    with tempfile.TemporaryDirectory(prefix="memglide-auto-installed-smoke-") as temporary:
        base = Path(temporary)
        repository = base / "repo"
        repository.mkdir()
        subprocess.run(["git", "init", "-q", str(repository)], check=True, timeout=10)
        source = "def total(values):\n    return sum(values)\n"
        (repository / "calc.py").write_text(source, encoding="utf-8")
        service = Service(base / "state" / "db.sqlite")
        environment = {**os.environ, "MEMGLIDE_HOME": str(base / "state")}
        try:
            project_id = service.indexer.add_project(str(repository))["id"]
            task = "Fix `total` summation and preserve its public interface."
            automatic = prepare_task_prompt(
                task,
                db_path=service.db.path,
                project_id=project_id,
                enabled=True,
                context_format="compact-prefix",
            )
            selection = automatic["automatic_selection"]
            digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
            assert automatic["mode"] == "preloaded", automatic["reason"]
            assert selection["decision"] == "FOCUSED_SOURCE"
            assert selection["auxiliary_model_calls"] == 0
            assert selection["selected_paths"] == ["calc.py"]
            assert selection["source_versions"] == {"calc.py": digest}
            envelope = json.loads(automatic["prompt"].removesuffix(TASK_SEPARATOR + task))
            assert envelope["memglide_sources"] == [{"path": "calc.py", "content": source}]
            assert automatic["files"] == [{
                "path": "calc.py", "sha256": digest,
                "start_line": 1, "end_line": len(source.splitlines()),
            }]
            assert service.db.one("SELECT count(*) AS n FROM sessions")["n"] == 0
            assert service.db.one("SELECT count(*) AS n FROM memories")["n"] == 0
            receipt["automatic_preparation"] = {
                "decision": selection["decision"],
                "selected_paths": selection["selected_paths"],
                "source_versions": selection["source_versions"],
                "context_bytes": automatic["context_bytes"],
                "estimated_added_tokens": selection["estimated_added_tokens"],
                "estimate_is_measured_usage": False,
            }
            checks["installed_automatic_complete_source_without_memory"] = True

            launcher_help = subprocess.run(
                [executable, "-I", "-m", "memglide.integrations.codex_preload", "--help"],
                capture_output=True, text=True, check=True, env=environment, timeout=15,
            )
            assert "--discover" in launcher_help.stdout
            assert "--max-added-tokens" in launcher_help.stdout
            checks["installed_automatic_cli_help"] = True

            fake_directory = base / "installed-bin"
            fake_directory.mkdir()
            fake = fake_directory / "codex"
            capture = base / "native-capture.jsonl"
            preparation_report = base / "preparation.json"
            fake.write_text(
                f"#!{executable}\n"
                "import json,os,sys\n"
                "with open(os.environ['MEMGLIDE_SMOKE_NATIVE_CAPTURE'],'a') as stream:\n"
                " stream.write(json.dumps({'argv':sys.argv,"
                "'stdin':sys.stdin.buffer.read().decode('utf-8')})+'\\n')\n"
                "raise SystemExit(23)\n",
                encoding="utf-8",
            )
            fake.chmod(0o700)
            fake_result = subprocess.run(
                [
                    executable, "-I", "-m", "memglide.integrations.codex_preload",
                    "--discover", "--db", str(service.db.path), "--project", project_id,
                    "--codex-executable", str(fake),
                    "--preparation-report", str(preparation_report), task,
                    "--", "--json", "--model", "synthetic-no-model-request",
                ],
                cwd=repository,
                env={**environment, "MEMGLIDE_SMOKE_NATIVE_CAPTURE": str(capture)},
                capture_output=True, text=True, timeout=20,
            )
            assert fake_result.returncode == 23, fake_result.stderr
            captures = capture.read_text(encoding="utf-8").splitlines()
            assert len(captures) == 1
            native = json.loads(captures[0])
            assert native["argv"] == [
                str(fake), "exec", "--json", "--model", "synthetic-no-model-request", "--", "-",
            ]
            native_envelope = json.loads(native["stdin"].removesuffix(TASK_SEPARATOR + task))
            assert native_envelope["memglide_sources"] == [{"path": "calc.py", "content": source}]
            private_report = json.loads(preparation_report.read_text(encoding="utf-8"))
            assert private_report["version"] == 4
            assert private_report["preparation"]["automatic_selection"]["decision"] == "FOCUSED_SOURCE"
            assert private_report["preparation"]["automatic_selection"]["auxiliary_model_calls"] == 0
            assert private_report["native_stdin"]["sha256"] == hashlib.sha256(
                native["stdin"].encode("utf-8")
            ).hexdigest()
            assert source not in preparation_report.read_text(encoding="utf-8")
            assert preparation_report.stat().st_mode & 0o777 == 0o600
            checks["installed_automatic_fake_native_handoff"] = True

            session_id = service.memory.start_session(project_id, "Verify total")["id"]
            claim = service.memory.save_memory(
                session_id, "observation", "return sum(values)", "source quote",
                sources=[{"path": "calc.py"}],
            )
            memory = prepare_memory_prompt(
                "Inspect total", db_path=service.db.path, project_id=project_id,
                session_id=session_id, memory_ids=[claim["id"]],
            )
            assert memory["mode"] == "preloaded"
            checks["installed_optional_memory_preparation"] = True

            for profile, expected_count in (("default", 14), ("agent", 2)):
                arguments = ["-I", "-m", "memglide.cli", "--db", str(service.db.path), "mcp"]
                if profile == "agent":
                    arguments += ["--profile", "agent", "--project", project_id]
                parameters = StdioServerParameters(
                    command=executable, args=arguments, env=environment,
                )
                async with asyncio.timeout(45):
                    async with stdio_client(parameters) as (read, write):
                        async with ClientSession(read, write) as client:
                            await client.initialize()
                            assert len((await client.list_tools()).tools) == expected_count
                            if profile == "default":
                                result = await client.call_tool("get_context", {
                                    "session_id": session_id, "query": "total",
                                    "level": 2, "budget": 4000,
                                })
                                assert not result.is_error and result.structured_content["items"]
                            else:
                                result = await client.call_tool(
                                    "fetch_context", {"query": "Inspect total", "budget": 4000},
                                )
                                assert not result.is_error
                                assert json.loads(result.content[0].text)["items"]
                                result = await client.call_tool("verify_context", {})
                                assert not result.is_error
                                assert json.loads(result.content[0].text)["source_freshness"] == "Current"
                checks[f"installed_{profile}_mcp"] = True

            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with (base / "server.log").open("w", encoding="utf-8") as log:
                server = subprocess.Popen(
                    [executable, "-I", "-m", "memglide.cli", "--db", str(service.db.path),
                     "serve", "--port", str(port)],
                    stdout=log, stderr=log, env=environment,
                )
                try:
                    url = f"http://127.0.0.1:{port}"
                    deadline = time.monotonic() + 15
                    while time.monotonic() < deadline:
                        try:
                            with opener.open(url + "/api/health", timeout=1) as response:
                                assert json.load(response)["status"] == "ok"
                            break
                        except OSError:
                            if server.poll() is not None:
                                raise AssertionError("installed API server exited before readiness")
                            time.sleep(0.05)
                    else:
                        raise AssertionError("installed API server readiness failed")
                    with opener.open(url + "/api/overview", timeout=10) as response:
                        overview = json.load(response)
                        assert overview["counts"]["projects"] == 1
                        assert overview["counts"]["sessions"] >= 1
                    with opener.open(url + "/", timeout=2) as response:
                        assert b"<html" in response.read().lower()
                    checks["installed_loopback_api_and_spa"] = True
                finally:
                    server.terminate()
                    try:
                        server.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        server.kill()
                        server.wait(timeout=5)
                        raise

            doctor = subprocess.run(
                [executable, "-I", "-m", "memglide.cli", "--db", str(service.db.path), "doctor"],
                capture_output=True, text=True, check=True, env=environment, timeout=15,
            )
            assert json.loads(doctor.stdout)["database_integrity"] == "ok"
            checks["installed_cli_doctor"] = True
        finally:
            service.close()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: installed-python -I installed_smoke.py NEW_RECEIPT.json")
    destination = Path(sys.argv[1]).absolute()
    # Reserve the receipt before work, preserving every original attempt.
    with destination.open("x", encoding="utf-8") as output:
        receipt: dict[str, Any] = {"checks": {}, "all_passed": False, "model_requests": 0}
        try:
            asyncio.run(smoke(receipt))
            receipt["all_passed"] = bool(receipt["checks"]) and all(receipt["checks"].values())
        except BaseException as error:
            receipt["error_type"] = type(error).__name__
            receipt["error"] = str(error)
            raise
        finally:
            json.dump(receipt, output, indent=2, allow_nan=False)
            output.write("\n")
            output.flush()
        print(json.dumps(receipt, allow_nan=False))


if __name__ == "__main__":
    main()
