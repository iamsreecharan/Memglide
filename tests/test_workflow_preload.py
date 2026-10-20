"""Real approved-index and rendering controls; no native model calls."""
from __future__ import annotations

import hashlib
import subprocess
import sys
from copy import deepcopy

import pytest

from memglide.core.indexer import Indexer
from memglide.integrations import command_provider as providers
from memglide.integrations import public_check
from memglide.integrations import workflow_policy as policy
from memglide.integrations import workflow_preload as workflow
from memglide.integrations.auto_preload import prepare_task_prompt
from memglide.storage.database import Database


@pytest.fixture
def prepared(tmp_path):
    root = tmp_path / 'arbitrary-checkout'
    root.mkdir()
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    (root / 'cooling.py').write_text('def cooling_window(flow_rate, capacity):\n    return flow_rate / capacity\n')
    (root / 'tests').mkdir()
    (root / 'tests/test_cooling.py').write_text('from cooling import cooling_window\n' + '# public background context\n' * 650 + '\ndef test_cooling_zero():\n    assert cooling_window(0, 4) == 0\n\ndef test_cooling_positive():\n    assert cooling_window(4, 2) == 2\n')
    database = Database(tmp_path / 'isolated-state.db')
    project = Indexer(database).add_project(str(root))['id']
    task = 'Cooling window must account for flow rate and capacity.'
    base = prepare_task_prompt(task, task_query=task, enabled=True, selection_policy='v4', db_path=database.path, project_id=project)
    assert base['mode'] == 'preloaded', base
    return (root, database, project, task, base)

def augment(prepared, config, provider=None, **kwargs):
    _, database, project, task, base = prepared
    return workflow.augment_preparation(base, task, project_id=project, db_path=database.path, config=config, provider=provider, task_query=task, **kwargs)

def validate(prepared, value, config, provider=None):
    _, database, project, task, base = prepared
    return workflow.validate_workflow_preparation(value, base, task, project_id=project, db_path=database.path, config=config, provider=provider, task_query=task)

def provider(prepared, tmp_path, commands=None):
    _, database, project, _, _ = prepared
    return providers.verify_public_commands(commands or [{'name': 'public tests', 'kind': 'tests', 'argv': [sys.executable, '-c', "print('2 passed')"]}], project_id=project, db_path=database.path, receipt_path=tmp_path / 'explicit-provider.json')

def test_default_is_same_object_and_validated_v4_identity(prepared):
    base = prepared[-1]
    before = deepcopy(base)
    assert augment(prepared, None) is base
    prompt, metadata = validate(prepared, base, None)
    assert prompt == before['prompt'] and base == before
    assert 'workflow' not in metadata

def test_missing_verified_provider_preserves_base_and_does_not_claim_readiness(prepared):
    config = {**policy.selected_policy(), 'command_card': 'commands_counts'}
    value = augment(prepared, config)
    assert value['prompt'] == prepared[-1]['prompt']
    assert value['workflow']['reason'] == 'verified_public_command_provider_required'
    assert validate(prepared, value, config)[0] == prepared[-1]['prompt']

def test_explicit_verification_produces_pinned_counts_without_executing_during_prepare(prepared, tmp_path, monkeypatch):
    verified = provider(prepared, tmp_path)
    raw = (tmp_path / 'explicit-provider.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == verified.trusted_sha256
    loaded = providers.load_verified_provider(tmp_path / 'explicit-provider.json', verified.trusted_sha256)

    def forbidden(*args, **kwargs):
        pytest.fail('preparation must never execute public checks')
    monkeypatch.setattr(public_check, 'run_check', forbidden)
    config = {**policy.selected_policy(), 'command_card': 'commands_counts'}
    value = augment(prepared, config, loaded)
    assert 'Public baseline: {"exit_code":0,"tests":2}' in value['prompt']
    assert validate(prepared, value, config, loaded)[0] == value['prompt']

def test_stale_public_test_binding_declines_command_card(prepared, tmp_path):
    verified = provider(prepared, tmp_path)
    (prepared[0] / 'tests/test_cooling.py').write_text('# changed public tests\n')
    config = {**policy.selected_policy(), 'command_card': 'commands_counts'}
    value = augment(prepared, config, verified)
    assert value['workflow']['reason'] == 'verified_public_command_provider_stale_or_unavailable'
    assert value['prompt'] == prepared[-1]['prompt']

def test_selected_source_mutation_is_fatal_even_with_missing_optional_provider(prepared):
    (prepared[0] / 'cooling.py').write_text('def cooling_window(flow_rate, capacity):\n    return 42\n')
    with pytest.raises(ValueError, match='production changed'):
        augment(prepared, {**policy.selected_policy(), 'command_card': 'commands_counts'})

def test_optional_budget_overflow_skips_without_truncation(prepared, tmp_path):
    base = prepared[-1]
    config = policy.selected_policy()
    verified = provider(prepared, tmp_path)
    value = augment(prepared, config, verified, max_context_bytes=base['context_bytes'])
    assert value['prompt'] == base['prompt']
    assert value['workflow']['reason'] == 'workflow_context_budget'

def test_roundtrip_rejects_prompt_and_complete_body_tampering(prepared, tmp_path):
    config = policy.selected_policy()
    verified = provider(prepared, tmp_path)
    value = augment(prepared, config, verified)
    tampered = deepcopy(value)
    tampered['prompt'] += '\nextra instruction'
    with pytest.raises(ValueError, match='roundtrip'):
        validate(prepared, tampered, config, verified)
    tampered = deepcopy(value)
    tampered['_workflow_payload']['production'][0]['content'] += '# changed\n'
    with pytest.raises(ValueError, match='hash'):
        validate(prepared, tampered, config, verified)

def test_new_competing_source_forces_full_v4_revalidation(prepared, tmp_path):
    config = policy.selected_policy()
    verified = provider(prepared, tmp_path)
    value = augment(prepared, config, verified)
    (prepared[0] / 'cooling_window.py').write_text('def cooling_window(flow_rate, capacity):\n    return flow_rate / capacity\n')
    with pytest.raises(ValueError, match='Full v4 source-selection'):
        validate(prepared, value, config, verified)

def test_unknown_policy_and_weakened_caps_rejected(prepared):
    with pytest.raises(ValueError):
        augment(prepared, {**policy.selected_policy(), 'freshness': 'off'})
    with pytest.raises(ValueError, match='caps'):
        augment(prepared, policy.selected_policy(), max_context_bytes=12001)

@pytest.mark.parametrize('skip', [{'mode': 'off'}, {'context_supplied': True}])
def test_original_passthrough_gates_never_reopen_state_or_reenable_source(tmp_path, monkeypatch, skip):
    from memglide.integrations import auto_preload
    config = {**policy.selected_policy(), 'command_card': 'commands_counts'}
    task = 'Cooling window must account for flow rate and capacity.'
    absent = tmp_path / 'never-created.db'
    base = prepare_task_prompt(task, project_id='not-opened', db_path=absent, enabled=True, selection_policy='v4', context_format='compact-prefix', **skip)
    assert base['mode'] == 'passthrough'
    value = workflow.augment_preparation(base, task, project_id='not-opened', db_path=absent, config=config)
    assert value is base
    monkeypatch.setattr(auto_preload, 'prepare_task_prompt', lambda *args, **kwargs: pytest.fail('skip gate reopened state'))
    prompt, metadata = workflow.validate_workflow_preparation(value, base, task, project_id='not-opened', db_path=absent, config=config)
    assert prompt == task and metadata['mode'] == 'passthrough'
    assert not absent.exists()


def test_deleted_verified_executable_declines_to_original_v4(prepared, tmp_path, monkeypatch):
    executable = tmp_path / 'explicit-public-check'
    executable.write_text('#!' + sys.executable + "\nprint('2 passed')\n")
    executable.chmod(0o700)
    verified = provider(prepared, tmp_path, [{'name': 'public tests', 'kind': 'tests',
        'argv': [str(executable)]}])
    executable.unlink()
    monkeypatch.setattr(public_check, 'run_check', lambda *args, **kwargs: pytest.fail('preparation executed a missing check'))
    config = policy.selected_policy()
    value = augment(prepared, config, verified)
    assert value['workflow']['decision'] == 'SKIP'
    assert value['workflow']['reason'] == 'verified_public_command_provider_stale_or_unavailable'
    assert value['prompt'] == prepared[-1]['prompt']
    assert validate(prepared, value, config, verified)[0] == prepared[-1]['prompt']


def test_missing_optional_tool_cannot_mask_revoked_source_policy(prepared, tmp_path):
    executable = tmp_path / 'explicit-public-check'
    executable.write_text('#!' + sys.executable + "\nprint('2 passed')\n")
    executable.chmod(0o700)
    verified = provider(prepared, tmp_path, [{'name': 'public tests', 'kind': 'tests',
        'argv': [str(executable)]}])
    executable.unlink()
    (prepared[0] / '.gitignore').write_text('cooling.py\n')
    with pytest.raises(ValueError, match='source_excluded'):
        augment(prepared, policy.selected_policy(), verified)
