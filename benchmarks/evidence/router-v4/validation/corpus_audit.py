"""Independent static held-out corpus audit; never import or run a selector."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(path: Path) -> str:
    assert path.is_file() and not path.is_symlink(), str(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    seal_path = ROOT / '.local/router-v4/corpus-spec-freeze.json'
    assert sha(seal_path) == 'a8d985ba502ecaf6c69d50083c2c8120c302cc92f98909080ccba5c088ffd9b7'
    seal = json.loads(seal_path.read_text())
    for path, expected in seal['files'].items():
        assert sha(ROOT / path) == expected, path
    fixtures = ROOT / 'benchmarks/automatic-v4-fixtures'
    actual = {p.relative_to(fixtures).as_posix(): sha(p)
              for root in sorted(fixtures.glob('r*')) for p in sorted(root.rglob('*')) if p.is_file()}
    assert actual == seal['fixture_hashes']
    tasks = json.loads((ROOT / 'benchmarks/tasks_automatic_v4.json').read_text())
    controls = json.loads((ROOT / 'benchmarks/controls_automatic_v4.json').read_text())
    labels = json.loads((ROOT / 'benchmarks/automatic-v4-grading.json').read_text())
    native = json.loads((ROOT / '.local/router-v4/native-tasks.json').read_text())
    provenance = json.loads((ROOT / 'benchmarks/automatic-v4-provenance.json').read_text())
    assert len(tasks) == len(native) == 12 and len(controls) == 4
    assert {t['language'] for t in tasks} == {'python', 'typescript'}
    assert all(sum(t['language'] == lang for t in group) == 6
               for group in (tasks, native) for lang in ('python', 'typescript'))
    assert len({t['repository'] for t in tasks}) == len(provenance) == 6
    assert {t['prompt'] for t in tasks}.isdisjoint({t['prompt'] for t in native})
    tracked = subprocess.check_output(['git', 'ls-files', 'benchmarks'], cwd=ROOT, text=True).splitlines()
    historical_urls = set()
    for relative in tracked:
        p = ROOT / relative
        if p.suffix == '.json':
            historical_urls.update(re.findall(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', p.read_text(errors='replace')))
    rows = []
    for key, record in sorted(provenance.items()):
        assert record['repository_url'] not in historical_urls, key
        assert re.fullmatch(r'[0-9a-f]{40}', record['commit'])
        assert record['commit'] in record['archive_url']
        archive = ROOT / record['archive_artifact']
        assert sha(archive) == record['archive_sha256']
        retained = record['retained_file_sha256']
        prefix = record['archive_prefix'] + '/'
        verified = set()
        with tarfile.open(archive, 'r:gz') as handle:
            regular = [m for m in handle.getmembers() if m.isfile()]
            assert len(regular) == record['archive_regular_file_count']
            for member in regular:
                assert member.name.startswith(prefix)
                relative = member.name[len(prefix):]
                if relative not in retained:
                    continue
                assert relative not in verified
                stream = handle.extractfile(member)
                assert stream is not None
                content = stream.read()
                content.decode('utf-8')
                assert hashlib.sha256(content).hexdigest() == retained[relative]
                assert sha(fixtures / key / relative) == retained[relative]
                verified.add(relative)
        assert verified == set(retained)
        assert len(retained) == record['retained_regular_file_count']
        assert record['excluded_archive_regular_file_count'] == len(regular) - len(retained)
        assert all(sha(fixtures / key / p) == record['license_file_sha256'][p]
                   for p in record['license_paths'])
        rows.append({'repository': key, 'repository_url': record['repository_url'],
                     'commit': record['commit'], 'archive_sha256': record['archive_sha256'],
                     'retained_files': len(retained), 'archive_regular_files': len(regular),
                     'excluded_regular_files': len(regular)-len(retained),
                     'retained_bytes': sum((fixtures/key/p).stat().st_size for p in retained),
                     'coverage': record['tracked_tree_status'], 'licenses_verified': record['license_paths']})
    for task in tasks + controls:
        assert set(task) == {'id', 'repository', 'language', 'prompt'}
        grade = labels[task['id']]
        if task in tasks:
            assert grade['kind'] == 'positive' and grade['required_paths']
            for relative in grade['required_paths']:
                assert sha(fixtures/task['repository']/relative) == provenance[task['repository']]['retained_file_sha256'][relative]
                assert relative not in task['prompt']
        else:
            assert grade['kind'] == 'abstention_control' and grade['required_paths'] == []
    output = ROOT / '.local/router-v4/corpus-static-audit.json'
    assert not output.exists()
    output.write_text(json.dumps({'version':1, 'observed_at':datetime.now(timezone.utc).isoformat(),
        'spec_freeze_sha256':sha(seal_path), 'fixture_files_verified':len(actual),
        'upstream_bytes_and_licenses_verified':True,'new_unrelated_urls_vs_tracked_history':True,
        'public_task_shapes_verified':True, 'native_prompts_distinct_from_offline':True,
        'scope_labels_existing_and_not_in_public_prompt':True,
        'controls':'Four easy normative non-code tasks; these do not establish hard semantic abstention.',
        'limitations':['Author-selected retained subsets; not whole upstream repositories.',
                       'Required source paths are inclusion proxies, not coding correctness or semantic completeness.',
                       'Native behavior graders still require independent audit and frozen control receipts.'],
        'repositories':rows, 'selector_calls':0, 'model_calls':0, 'upstream_code_executions':0}, indent=2)+'\n')
    print(json.dumps({'verified':True,'files':len(actual),'roots':len(rows),'audit':str(output)}))


if __name__ == '__main__':
    main()
