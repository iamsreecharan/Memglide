# Optional verified command context

The selected workflow adds a public test-command card and observed baseline
counts to complete v4 source context. It keeps full command output and the
existing 12,000-byte / 4,000-estimated-token context caps. Existing launcher
defaults stay unchanged; enable this feature explicitly for an approved,
indexed project.

First verify the commands you want the card to show. This separate action runs
project code, so use your normal execution isolation and installed tools.
Preparation itself never runs the checks. The check runner bounds time/output
and preserves failures and raw logs; it is not an operating-system sandbox.

Save a JSON list outside the project, using its actual atomic test command:

```json
[
  {
    "name": "public tests",
    "kind": "tests",
    "argv": ["python", "-m", "pytest", "-q", "{root}/tests"]
  }
]
```

Use `kind: "typecheck"` for a compiler check. Do not combine commands into a
shell string. `{root}` expands to the approved project root. Optional
`expected_tests` supplies a minimum behavioral count; verification otherwise
records the positive observed count. A zero-test result does not qualify as a
passing behavioral baseline.

Run from the environment where Memglide is installed:

```sh
python -m memglide.integrations.command_provider verify \
  --project "$PROJECT_ID" --db "$MEMGLIDE_DB" \
  --commands-json "$CHECK_SPEC" --receipt "$CHECK_RECEIPT"
```

Keep the new receipt outside the project and retain the returned
`trusted_sha256`. That pin must come from your verification action, rather than
an automatically trusted file supplied by a repository. Then opt in:

```sh
memglide-codex --discover --selection-policy v4 \
  --context-format compact-prefix --workflow-policy selected \
  --project "$PROJECT_ID" --db "$MEMGLIDE_DB" \
  --public-check-receipt "$CHECK_RECEIPT" \
  --public-check-sha256 "$TRUSTED_CHECK_SHA256" \
  --preparation-report "$PREPARATION_REPORT" \
  "Your task"
```

Append native Codex exec options after `--` when needed.

The report records `PREPARED` when command context is added, or `SKIP` when
optional evidence is unavailable/stale or the additional context will not fit.
A skip retains ordinary v4 source preparation. Invalid explicit receipt/pin
input fails before native execution. `--mode off`, `--context-supplied`, and
ordinary source abstentions bypass optional command context.

Reverify after eligible source, tests, configuration, approval policy, or
declared tool inputs change. Counts describe the verified baseline, not the
result of the requested code change. The receipt binds a bounded eligible
public-text tree and declared tools; it does not capture the entire dependency,
binary-fixture, environment, or external-resource state. Preparation rechecks
these local bindings and complete selected source without executing checks.

The installed-system comparison measured this path, including fresh command
verification and provider/freshness validation. Its observed cost difference
did not establish reliable savings or a speed advantage; see the
[research overview](../research/README.md) for the results and uncertainty.
