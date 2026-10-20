"""Finalize existing standard-control receipts; never dispatch code or models."""
import datetime
import hashlib
import json
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmarks import run_router_coding as native


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = ROOT / '.local/router-v4'
    review = base / 'native-corpus-review'
    seals = {v: json.loads((base / f'native-corpus-freeze{s}.json').read_text())
             for v, s in (('v1', ''), ('v2', '-v2'))}
    for version, seal in seals.items():
        assert native.offline.tree_hashes(Path(seal['grader_root'])) == seal['private_file_hashes'], version
    private_root = Path(seals['v2']['grader_root'])
    tasks = json.loads((base / 'native-tasks-v2.json').read_text())
    grades = json.loads((private_root / 'grading.json').read_text())
    native.validate_tasks(tasks, grades)
    native.validate_grader_bindings(grades, private_root)
    native.validate_control_receipts(tasks, grades, ROOT / 'benchmarks/automatic-v4-fixtures')
    replays = {}
    for version, directory in (('v1', review / 'external-controls'),
                               ('v2', base / 'native-corpus-review-v2/external-controls')):
        summary = json.loads((directory / 'control-summary.json').read_text())
        assert summary['success'] is True and summary['tasks'] == 12 and summary['controls'] == 24
        counts = {}
        for task in tasks:
            task_id = task['id']
            counts[task_id] = {}
            for mode, expected in (('baseline', False), ('reference', True)):
                path = directory / f'{task_id}-{mode}.json'
                row = json.loads(path.read_text())
                assert row['success'] is expected and row['executed'] is True and row['checks'] > 0
                assert row['source_and_git_unchanged_by_grader'] is True
                if version == 'v2':
                    assert row['task_digest'] == grades[task_id]['task_digest']
                counts[task_id][mode] = {'checks': row['checks'], 'success': row['success'],
                                        'receipt_sha256': digest(path)}
        replays[version] = {'standard_control_runs': 24, 'baseline_expected_failures': 12,
                            'reference_expected_passes': 12,
                            'check_counts_include_integrity_checks': True,
                            'controls': counts, 'summary_sha256': digest(directory / 'control-summary.json')}
    notice = private_root / 'vendor/TYPESCRIPT-THIRD-PARTY-NOTICES.txt'
    with tarfile.open(base / 'compiler-runtime/typescript-5.9.3.tgz', 'r:gz') as archive:
        data = archive.extractfile('package/ThirdPartyNoticeText.txt').read()
        assert notice.read_bytes() == data
    report = {
        'version': 1, 'finalized_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Independent standard-control replays and static limits. Plan-only clearance; never native execution.',
        'v1_and_v2_frozen_authorities_unchanged': True, 'replays': replays,
        'source_and_git_unchanged_by_replays': True,
        'six_author_integrity_controls': 'Original historical receipt retained, not independently rerun or rerun for v2.',
        'compiler_review_sha256': digest(review / 'compiler-review.json'),
        'final_notice_verified_against_archive': {'path': notice.relative_to(private_root).as_posix(), 'sha256': digest(notice)},
        'python_static_review_sha256': digest(review / 'python-review.json'),
        'known_limits': [
            'Python candidate code shares its process with assertions/result emission. Static review flagged possible result interference; no dynamic reproduction completed.',
            'Compression-level preservation is not directly distinguished for n02; invoking several levels is incomplete coverage.',
            'Protected original-file scopes can reject valid broader helper/documentation refactors not prohibited in the public request.',
            'Private authority is procedurally omitted from model/indexed inputs; adversarial host filesystem isolation is unproven.',
            'Compiler blobs are locally hash-verified; independent authenticated registry provenance and universal compiler API closure are unproven.',
            'Full TypeScript semantic oracle review did not complete. Reference controls are limited checks, not complete correctness proofs.'
        ],
        'unrun_security_check': {'kind': 'proposed synthetic grader-tampering control',
                                'status': 'automatic review rejected for possible cybersecurity risk; unrun',
                                'source': 'Independent reviewer agent ended with automatic safety-review error; no bypass or repeated attempt.'},
        'native_manifest_repair': {'v1_validation': 'Slash-separated prose key/reverse/nonempty rejected as an apparent source path before any plan.',
                                   'v2_validation': 'All three frozen validators pass.',
                                   'change': 'Only equivalent n06 punctuation, authority path rebinding and actually refreshed receipts.',
                                   'deviation_sha256': digest(base / 'native-v2-protocol-deviation.json'),
                                   'timing': 'After offline comparison; before any native plan or dispatch.',
                                   'pre_offline_prompt_bytes_untouched': False,
                                   'author_blind_to_selection_results': True},
        'initial_audit_invocation_errors': 'First finalizer used a case-sensitive Notice glob for an uppercase NOTICES filename; assertion stopped before writing. Exact filename fixed in audit helper only.',
        'formal_native_eligibility': False, 'plan_only_clearance': True,
        'model_calls': 0, 'selector_calls': 0, 'new_adversarial_source_execution': False
    }
    output = review / 'audit.json'
    assert not output.exists()
    output.write_text(json.dumps(report, indent=2) + '\n')
    old = base / 'native-admission.json'
    admission = json.loads(old.read_text())
    admission.update(earlier_admission_sha256=digest(old), independent_grader_review_sha256=digest(output),
                     grader_review_complete=False, grader_execution_eligibility=False,
                     blocker=admission['blocker'] + ' Native graders retain documented coverage/isolation gaps and an unrun security control; standard baseline/reference replays do not clear formal native execution.')
    final = base / 'native-admission-final.json'
    assert not final.exists()
    final.write_text(json.dumps(admission, indent=2) + '\n')
    print(json.dumps({'audit_sha256': digest(output), 'final_admission_sha256': digest(final),
                      'standard_replays_per_version': 24, 'native_execution_eligible': False}))


if __name__ == '__main__':
    main()
