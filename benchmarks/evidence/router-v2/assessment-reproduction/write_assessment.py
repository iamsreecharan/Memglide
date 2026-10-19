from __future__ import annotations

import datetime
import hashlib
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path

root = Path('/workspace/Memglide')
evidence = root / 'benchmarks/evidence/router-v2'
offline = json.loads((evidence / 'offline/report.json').read_text())
plan = json.loads((evidence / 'plan/preregistration.json').read_text())
native = json.loads((evidence / 'native-not-started/report.json').read_text())
profile = json.loads((evidence / 'profile/report.json').read_text())
validation = json.loads((root / 'benchmarks/router-v2-final-validation.json').read_text())
rows = offline['rows']
assert len(rows) == 72 and offline['technical_eligibility']['passed'] is False
assert len(native['runs']) == 72 and not any(r['attempted'] for r in native['runs'])

grouped = defaultdict(list)
for row in rows:
    grouped[row['task_id']].append(row)
tasks = []
for task_id, members in sorted(grouped.items()):
    c = sorted((r for r in members if r['configuration'] == 'C'), key=lambda r: r['repeat'])
    expected = c[0]['expected_paths_evaluator_only']
    ranks = [next((n for n, item in enumerate(r['context_preparation']['automatic_selection']['ranked_candidates'], 1) if item['path'] in expected), None) for r in c]
    tasks.append({'task_id': task_id, 'language': c[0]['language'], 'expected_paths_evaluator_only': expected,
                  'c_target_ranks_posthoc': ranks, 'c_reasons': [r['context_preparation']['reason'] for r in c],
                  'c_selected_paths': [r['selected_paths'] for r in c],
                  'b_complete_scope_repetitions': sum(r['declared_scope_complete_proxy'] for r in members if r['configuration'] == 'B'),
                  'c_complete_scope_repetitions': sum(r['declared_scope_complete_proxy'] for r in c)})

findings = [
    {'area':'Known-path complete-source delivery', 'status':'preserved', 'evidence':'24/24 fresh preparations delivered the declared scope; all source hashes and complete bodies verified.'},
    {'area':'Source safety and exact fallback', 'status':'preserved within checked scope', 'evidence':'All 72 offline treatments passed independent source/passthrough fidelity reconstruction; application/security regressions and installed transports passed. Native task correctness remains unmeasured.'},
    {'area':'Source-controlled identifier normalization', 'status':'resource defect fixed', 'evidence':'Fixed-width boundaries replace quadratic suffix rescanning; compatibility cases and a bounded 500,000-character subprocess regression pass. No model speedup is claimed.'},
    {'area':'Automatic target delivery', 'status':'failed; not improved', 'evidence':'C delivered source on one of 12 tasks in both repeats, but delivered the wrong type-only file; declared target scope was complete on zero tasks. V1 also delivered zero target scopes.'},
    {'area':'Local preparation time', 'status':'regressed in this cohort', 'evidence':'C mean 2.098610s versus B 1.216337s and V1 1.357629s. These are cold local components, not full coding-task times.'},
    {'area':'Local CPU', 'status':'more observed work', 'evidence':'Mean parent CPU C 1.193451s vs B 0.720920s; separate waited-child CPU C 0.759263s vs B 0.340620s. Counters have different scopes and are not an exact total.'},
    {'area':'Synthetic memory and latency profile', 'status':'no consistent improvement', 'evidence':'18/18 synthetic Python selections/fidelity passed. C preparation medians exceeded V1 at both sizes; whole-process SELF RSS was similar/slightly higher. No real-repository or TS-worker peak-memory result exists.'},
    {'area':'Model tokens, cache, cost per success and full task time', 'status':'unproven; no native attempts', 'evidence':'Offline eligibility failed, so all 72 planned native assignments remain unrun. No invented token or dollar measurements.'},
    {'area':'Automatic warm memory', 'status':'disabled and unchanged', 'evidence':'No new memory injection; existing explicit memory features and installed memory smoke remain available.'},
]
limitations = [
    'Twelve controlled mutation tasks across four complete small upstream snapshots, six Python/six TypeScript; not a random sample or proof about larger repositories. Two repeats are not 24 independent tasks.',
    'Expected paths are an independent author-declared repair-scope proxy. Scope coverage is not semantic dependency completeness, native correctness, or an assessment that an agent cannot solve the original task after fallback.',
    'Known-path B is an oracle baseline: manual source discovery effort is unmeasured and excluded. No invented avoided work is credited to C.',
    'Caches and shared-host scheduling are uncontrolled. Balanced execution order does not establish equivalent provider or OS cache state. Cold setup/preparation excludes fixture/worktree creation, imports, independent reconstruction and grading.',
    'The local profile uses synthetic Python only. SELF RSS includes interpreter, imports, fixture/index/setup/preparation; child peak is a separate maximum, not simultaneous total or incremental preparation allocation. TS parser peak RSS was not measured.',
    'The offline runner seals its source manifest before dispatch but has no per-observation/end-of-offline source guard. Operator sequencing and the frozen Git snapshot support this run; they are not an independently timestamped proof of runtime immutability.',
    'Posthoc ranks and cause analyses were inspected only after the fixed gate failed. These tasks are now exposed and must not be reused as independent confirmation for a changed policy.',
    'Actual billing, native model telemetry, cost per successful coding task and end-to-end coding latency are unavailable because native execution was not initiated. Historical API-equivalent savings are not transferred to this policy.',
]
next_experiments = [
    {'priority':1,'proposal':'Local runtime/helper-aware ranking using already indexed AST roles, parameter/alias evidence and bounded caller/callee relationships; distinguish runtime definitions from type-only declarations without excluding types needed by type tasks.', 'test':'Develop on exposed/development cases, then freeze and evaluate NEW issue-only tasks; compare target ranking, bundle delivery, abstention, false inclusions and all local overhead before model spend.'},
    {'priority':2,'proposal':'Clean signature evidence at actual declaration boundaries, and expose safe typed phase-budget/failure diagnostics. Current inherited signature slices can contain comments; generic discovery_unavailable hides the exact exception.', 'test':'Independent comment-mutation and phase-timeout tests before fresh heldout work. Do not call a likely SQLite deadline cause proven without an observed error counter.'},
    {'priority':3,'proposal':'Plan bounded complete source bundles around the relevant helper rather than indiscriminate broad callers/import closures; keep all-or-nothing safety where complete bodies exceed caps.', 'test':'Fresh multi-file/large-file tasks with independent dependency grading; no threshold retuning to rescue this cohort, no silent truncation.'},
    {'priority':4,'proposal':'Evaluate trusted reusable index generations and explicit phase budgets to reduce duplicate cold scan/parse work, preserving authoritative source/policy checks and fallback under uncertainty.', 'test':'Separate cold, warm unchanged, edited, renamed, deleted, ignore-changed, symlink and race cohorts. Measure setup, retrieval, parser/Git child CPU and RSS separately.'},
    {'priority':5,'proposal':'After a new policy passes fresh offline coverage, run a newly frozen all-task A/B/C comparison with cost per strict success, full time, task-cluster uncertainty and byte-identical controls.', 'test':'New task corpus, matched model/settings, isolated environments, balanced repeats and a separately recorded planning allowance; preserve failed attempts and unknown usage.'},
]
report = {
    'version':'router-v2-assessment-1', 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'conclusion':'Rejected for promotion: automatic v2 failed fresh offline technical eligibility, did not improve target delivery and added local overhead. Native comparison was not initiated.',
    'frozen_study_revision':offline['frozen_manifest']['git_head'],
    'frozen_preregistration_sha256':offline['frozen_preregistration_sha256'],
    'final_behavior':{'automatic_discovery_opt_in':True,'discovery_default':'v1','v2_requires_explicit_selection':True,'known_path_source_preload':'preserved','automatic_memory_injection':False,'v2_promoted':False,'post_study_changes':'Compatibility default/help/docstring rollback and explicit v2 test fixtures only; no v2 evidence-policy tuning or heldout rerun.'},
    'configurations':{'A':'Bare Codex; native planned only','B':'Existing complete source using independent author-known paths','C':'Explicit v2 automatic selection with no target paths','V1':'Explicit original automatic policy, offline comparator only'},
    'study_design':{'tasks':12,'languages':{'python':6,'typescript':6},'repositories':4,'repeats':2,'offline_observations':72,'planned_native_assignments':72,'native_assignments_attempted':0,'native_assignments_unrun':72,'selection_auxiliary_model_calls':0,'hidden_grades_outside_agent_and_indexed_roots':True,'corpus_controls':'12 baseline failures, 12 reference passes and 12 partial/wrong-fix failures','cache_conditions':'Balanced order; provider/OS state uncontrolled','paid_dispatches':0},
    'technical_eligibility':offline['technical_eligibility'], 'offline_summary':offline['summary'],
    'paired_local_preparation_effects':offline['paired_local_preparation_effects'],
    'per_task_diagnostics_posthoc':tasks,'individual_offline_runs':rows,
    'native_status':'not started because preregistered offline eligibility failed; unrun is not coding failure',
    'individual_native_planned_assignments':native['runs'],
    'model_measurements':{key:None for key in ['total_input_tokens','cached_input_tokens','cached_write_tokens','uncached_input_tokens','output_tokens','provider_model_calls','repeated_file_reads','strict_completion_rate','full_task_seconds','estimated_api_equivalent_cost_per_strict_success_usd','actual_billed_cost_usd']},
    'local_synthetic_profile':profile,'engineering_validation':validation,
    'findings':findings,'limitations':limitations,'next_experiments':next_experiments,
    'historical_evidence':'Previous incomplete warm study descriptive source-only differences (9.055% lower API-equivalent cost; 6.892% shorter mean time) remain in their original reports and are neither pooled nor attributed to automatic v2.',
    'research':'router-v2-research.md; original primary-source reading scopes and fetch failures retained',
    'evidence_directory':'evidence/router-v2','artifact_ledger':'evidence/router-v2/artifact-ledger.json',
}
Path(root/'benchmarks/router-v2-assessment.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')

lines=['# Task-aware router v2: final assessment','',
       '**The new automatic policy did not improve Memglide on its fresh test. It failed the fixed offline gate and is not promoted. No live Codex A/B/C requests were made.**','',
       'The existing known-path source path is preserved. Automatic discovery remains opt-in with its original v1 default; experimental v2 requires `--selection-policy v2` or `selection_policy="v2"`. V1 is retained for compatibility, not claimed efficient. Memory remains explicit. A fixed-width identifier-normalization fix addresses a separate resource defect.','',
       '## What was implemented and tested','',
       'V2 inspects bounded current identifier evidence, combines project/candidate term frequencies, compares distinct evidence rather than saturated-score ratios, and uses the existing pinned Tree-sitter grammars in one isolated local worker for JavaScript/TypeScript. It adds no selection LLM call and preserves complete-source safety, ignores, approvals, source hashes and exact fallback. [Implementation guide](../docs/task-aware-router.md), [research and resolved security/resource findings](router-v2-research.md).','',
       f'The policy, corpus, protocol, graders, pricing, toolchain and assignments were frozen at `{report["frozen_study_revision"]}` before the first fresh selection. Twelve independent issue-only tasks cover four complete unfamiliar upstream snapshots: blinker, cachetools, defu and hookable. These are small controlled mutation tasks, six Python/six TypeScript. There are two repeats and all six arm permutations are balanced. No hidden answer, repair path or descriptive task identifier enters C\'s query or agent-visible worktree name.','',
       'Independent grading controls passed for all 12 defective baselines, reference restorations and partial/wrong fixes (36 expected outcomes). The fixed offline gate required C to preload on at least 50% of unique tasks and cover at least 75% of B-preparable scopes, with both repeats qualifying. It filters no individual formal task. [Frozen protocol](automatic-v2-protocol.md) and [preregistration](evidence/router-v2/plan/preregistration.json).','',
       '## Fresh offline outcomes','',
       '| Arm | Observations | Source delivered | Complete declared scope | Mean cold setup + prep (s) | Median (s) | Mean added bytes |',
       '|---|---:|---:|---:|---:|---:|---:|']
for arm in ['B','V1','C']:
    value=offline['summary'][arm]
    delivered=sum(r['context_preparation']['mode']=='preloaded' for r in rows if r['configuration']==arm)
    lines.append(f'| {arm} | {value["observations"]} | {delivered} | {value["complete_declared_scope_count"]} | {value["cold_setup_and_preparation_seconds"]["mean"]:.6f} | {value["cold_setup_and_preparation_seconds"]["median"]:.6f} | {value["added_bytes"]["mean"]:.2f} |')
lines += ['',
    'B delivered the declared source on **12/12 tasks in both repeats**. C preloaded on **1/12**, but both preloads selected `src/types.ts` instead of the required runtime implementation `src/defu.ts`: complete target delivery was **0/12**. C skipped 22/24 observations. V1 skipped 24/24. The fixed eligibility result is **false**. This is source-selection failure, not 24 measured native coding failures.','',
    'All **72/72 source or exact-passthrough fidelity checks passed**. A current, faithfully quoted file can still be irrelevant. The original task and ordinary agent tools remain available after fallback.','',
    '| C reason | Observations |','|---|---:|']
for reason,count in offline['summary']['C']['reasons'].items(): lines.append(f'| `{reason}` | {count} |')
lines += ['', '## Time, CPU and uncertainty','',
    'C mean local preparation was **72.54% longer than B** and **54.58% longer than V1** in this cohort. No native task time was measured. The paired effects below subtract baseline time from C time; positive is slower. Bootstrap intervals resample 12 task clusters, keeping both repeats together (2,000 seeded draws). They describe this small corpus, not all repositories.','',
    '| Comparison | Mean paired difference (s) | Median paired difference (s) | 95% task-cluster interval for mean (s) |',
    '|---|---:|---:|---|']
for key,value in offline['paired_local_preparation_effects'].items():
    interval=value['mean_difference_task_cluster_bootstrap_95_percent_interval']
    lines.append(f'| {key} | {value["mean_paired_difference"]:+.6f} | {value["median_paired_difference"]:+.6f} | [{interval[0]:+.6f}, {interval[1]:+.6f}] |')
lines += ['', '| Arm | Mean parent CPU (s) | Mean waited preparation child CPU (s), separate |', '|---|---:|---:|']
for arm in ['B','V1','C']:
    v=offline['summary'][arm]
    lines.append(f'| {arm} | {v["parent_cpu_seconds"]["mean"]:.6f} | {v["observed_waited_prep_child_cpu_seconds"]["mean"]:.6f} |')
lines += ['',
    'Parent CPU excludes child work. Waited-child CPU uses the OS counter around approval/index/preparation and includes synchronous Git/parser workers, excluding later audit/native/grading and un-waited children. These are not an exact combined resource total. Local preparation includes cold approval/index, secure refresh and retrieval even on SKIP. Cache state and shared-host scheduling remain uncontrolled.','',
    '## Why selection failed — posthoc diagnosis','',
    'The target appeared somewhere in every recorded C candidate list; only **4/24 observations (2/12 tasks)** ranked it first, and 18/24 ranked it within three. Candidate recall did not translate to a correct bundle. These diagnostic cutoffs were inspected after rejection and are not a newly validated policy.','',
    '- Broad callers and public API/type vocabulary outranked the actual small helpers. TypeScript type aliases and Python stubs can receive ordinary identifier weight. Both positive selections were type-only source, showing that token rarity and channel agreement do not establish runtime usefulness.',
    '- Six `source_unavailable` observations chose blinker\'s 19,132-byte broad implementation, above the 12,000-byte complete-file cap, instead of the 1,628–1,668-byte required helper. Current-source/hash checks were valid; this was not evidence of stale files.',
    '- Four budget declines combined hookable\'s caller, types and helper into 13,822–13,827 raw bytes before JSON overhead. That exceeded the complete-source budget. Removing safety caps or truncating the bundle would conceal the failure.',
    '- Inherited Python signature slices can contain leading body comments, contaminating the supposed declaration channel. Code-body comment exclusion alone does not clean this metadata. `args`/`kwargs`/compound-name vocabulary also poorly matches natural-language requirements.',
    '- Two second-repeat observations returned generic `discovery_unavailable` after ranking but before dependency counters. The aged global two-second metadata-reader budget is a plausible cause when it resumes after parsing; the exact exception was not retained and is **not proven**. Typed phase/error diagnostics remain needed.','',
    'These limitations are not presented as fixed by lowering thresholds. The v2 evidence policy was not tuned or rerun on these exposed tasks. After rejection, only compatibility defaults/help/docstrings and explicit-v2 test fixtures were changed. The frozen study remains reproducible at its original revision.','',
    '## Local memory and synthetic profile','',
    'A separate 18-observation Python-only development profile used fresh workers, 8/100 files, 2,048 bytes per file and three repeats per arm. All 18 expected target deliveries and full-source fidelity checks passed; all arms added 2,229 bytes. These easier fixtures did not predict held-out usefulness.','',
    '| Files | Arm | Mean API preparation (s) | Median (s) | Median whole-process Python SELF peak (MiB) |',
    '|---:|---|---:|---:|---:|']
for s in profile['summary']:
    lines.append(f'| {s["files"]} | {s["arm"]} | {s["preparation_wall_seconds"]["mean"]:.6f} | {s["preparation_wall_seconds"]["median"]:.6f} | {s["peak_python_self_rss_bytes"]["median"]/1048576:.3f} |')
lines += ['',
    'C\'s median preparation was slower than V1 at both sizes. The eight-file mean favored C because of V1 variability; it is not a consistent speed improvement. Whole-process RSS includes imports, fixture, index and preparation, not incremental router memory. Child peaks are separate maxima and must not be added to SELF peaks. This Python profile does not measure the TypeScript worker\'s peak memory. OS/cache/shared-host activity was uncontrolled, including possible overlap with a local analyzer unit check. [All 18 raw observations and worker logs](evidence/router-v2/profile/report.json).','',
    '## Native A/B/C, tokens and money','',
    'The user authorized the proposed 72 native assignments after disclosure of an **$18.59 estimated API-equivalent planning allowance** (not a billed maximum or hard cap). The preregistered technical gate failed, so **zero were dispatched**. All 72 planned assignments are retained as unrun, 24 per A/B/C. There were no live failures, retries, replacements or selectively dropped tasks. No new backend authentication claim is made.','',
    '| Requested metric | New-study observation |','|---|---|',
    '| Strict native completion rate and full task time | Unavailable: no attempted native tasks |',
    '| Input, cache read/write, uncached input, output | Unavailable: no native usage events |',
    '| Model and MCP invocations | Zero native assignments; zero auxiliary selection-model calls; live MCP intentionally outside source-preload treatment |',
    '| Repeated file reads / avoided investigation | Unavailable; not inferred from source size |',
    '| API-equivalent cost per successful task | Unavailable: no strict successes or observed model usage |',
    '| Actual billed charges / savings | Unavailable; no invoice telemetry |',
    '| Context freshness and target-scope proxy | 72/72 treatment fidelity; B 24/24 scope, C 0/24 scope |','',
    'Byte/3 added-token estimates remain planning proxies, not model input measurements. Pricing was rechecked against official sources and is preserved with reading scopes, but no dollar saving is calculated from those byte proxies. Cached input economics and cache-write sensitivity matter only when actual usage exists. The administrative [all-unrun record](evidence/router-v2/native-not-started/report.json) and [analysis](router-v2-formal-analysis.md) retain null metrics, missing pairs and zero attempts. They are **not a completed 72-run model benchmark**.','',
    'Historical incomplete source-only results (9.055% lower API-equivalent cost, 6.892% shorter mean time in a matched subset) remain in their original reports. They neither prove billed savings nor validate this automatic router.','',
    '## Engineering verification and promotion','',
    'The frozen full Python run passed **2,033** cases. The later 43-case runner run added six distinct cases; the post-study default rollback passed **324** affected cases with one new compatibility case. The union is **2,040 distinct Python cases**, not one enlarged full-suite run. **24 frontend, three production browser, and 14 separate final clean-wheel smoke checks** passed. Ruff and mypy passed. The smoke includes actual default/agent MCP clients, API/SPA, CLI, optional memory, both explicit policies and the installed native parser from an import-shadowed directory.','',
    'Initial development failures and a frontend initial-load timing failure are retained. That frontend case and the complete 24-case suite passed unchanged on rerun; no concrete frontend bug was proven. Existing protected tests/timeouts were not weakened. [Frozen validation](router-v2-validation.md) and [final default-rollback verification](router-v2-final-validation.md).','',
    '| Area | Outcome | Evidence / limit |','|---|---|---|']
for finding in findings: lines.append(f'| {finding["area"]} | {finding["status"]} | {finding["evidence"]} |')
lines += ['',
    'No automatic promotion. Known-path complete source remains the practical existing option when paths are known. Bare Codex remains appropriate when the router lacks reliable task evidence. No reduction in native correctness, time or cost has been demonstrated by this new study.','',
    '## Next experiments, in order','']
for item in next_experiments: lines += [f'{item["priority"]}. {item["proposal"]} {item["test"]}']
lines += ['', '## Every offline observation','',
    'Times include cold approval/index and preparation. “Scope” is the declared-path proxy. Full source versions, ranking evidence, phase timing, CPU counters and exact fidelity receipts are retained in the accompanying JSON and per-run records.','',
    '| Order | Task / repeat | Arm | Decision | Scope complete | Cold prep (s) | Added bytes | Reason |',
    '|---:|---|---|---|---|---:|---:|---|']
for row in sorted(rows,key=lambda r:r['order']):
    p=row['context_preparation']; decision=(p.get('automatic_selection') or {}).get('decision',p['mode'])
    lines.append(f'| {row["order"]} | {row["task_id"]} / {row["repeat"]} | {row["configuration"]} | {decision} | {row["declared_scope_complete_proxy"]} | {row["cold_setup_and_preparation_seconds"]:.6f} | {p["context_bytes"]} | {p["reason"]} |')
lines += ['', '## Reproduction and limits','',
    'Use the frozen source revision and locked toolchain recorded in `evidence/router-v2/plan/preregistration.json`; regenerate into fresh plan/output directories. The final documentation/default-rollback commit intentionally differs from that frozen HEAD, so the archived plan is a historical record, not a dispatchable plan for an arbitrary later checkout. No model command should be used to bypass the failed eligibility gate. The original corpus controls and complete Git-blob byte checks remain archived.','',
    *['- '+item for item in limitations],'',
    '[Machine-readable detailed report](router-v2-assessment.json) includes every offline and planned native row, all profile observations and metric summaries. [Evidence ledger](evidence/router-v2/artifact-ledger.json) hashes allowlisted artifacts; no auth, Codex state, runtime databases, dependencies or indexed worktrees are included. Historical reports and raw outcomes are preserved unchanged.','']
(root/'benchmarks/router-v2-assessment.md').write_text('\n'.join(lines))
print(json.dumps({'offline_observations':len(rows),'native_attempted':0,'native_unrun':len(native['runs']),'promoted':False}))
