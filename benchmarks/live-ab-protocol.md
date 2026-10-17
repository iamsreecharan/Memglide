# Live Codex A/B protocol: MCP authorization

Successful device authorization restored real Codex requests in this cloud
environment. Authentication is distinct from permission to invoke MCP tools.
The first authenticated two-run smoke experiment is retained unchanged at
`.local/benchmarks/device-auth-smoke-v1/`. Its two external task grades passed,
but B made no MCP calls and was correctly marked `invalid_treatment`. It is not
a verified A/B comparison and must not support a Memglide benefit claim.

A subsequent explicit, nonediting MCP diagnostic attempted
`memglide.list_projects`. Codex rejected it with:

> MCP tool call requires approval, but approval policy is never

The server was exposed and started in that diagnostic. The rejected invocation
identified a permission problem; it did not establish that every request saw
the server's tools. Memglide's tools
do not claim that operations which create sessions, refresh retrieval records,
or change memory are read-only. Missing MCP annotations caused Codex's automatic
tool policy to require an interactive approval unavailable to `codex exec`.

## Scoped authorization for the isolated benchmark

The benchmark user authorized Memglide operations on synthetic repositories and
fresh, isolated databases. B now supplies that authorization using Codex's
supported per-tool configuration. Its server entry contains an `enabled_tools`
allowlist and `tools.<name>.approval_mode = "approve"` for exactly these tools:

- `list_projects`, `start_session`, `get_session_status`, `end_session`
- `search_code`, `get_symbol`, `get_dependencies`
- `get_context`, `expand_context`, `get_context_passport`
- `save_memory`, `recall_memory`, `update_memory`, `invalidate_memory`

The list includes all 14 current Memglide tools, preserving access to search and
memory functionality. A newly added tool is excluded until the list and its
authorization test are deliberately updated. No server-wide default approval,
global approval-policy change, sandbox bypass, or artificial MCP safety hint is
introduced. A still has an empty MCP server map; both arms retain the existing
`workspace-write` sandbox, model, effort, prompt, output schema and other flags.
The policy is an invocation override, not a modification of the user's Codex
configuration.

The second smoke, `.local/benchmarks/device-auth-smoke-v2/`, used the scoped
authorization but B again made no MCP calls. Both independent task grades passed;
B remained an invalid treatment. A second explicit diagnostic with the exact
same prompt found only native resource discovery tools. Neither observation
proves that scoped MCP calls succeeded. These two invalid pilots stay separate
from any later experiment.

Codex also distinguishes optional MCP startup from required startup. An optional
server can still be initializing when the model receives its tool catalog. This
is a hypothesis for the inconsistent tool visibility, not an established cause
of the two pilots. B now specifies `required = true` and
`startup_readiness = "connection"`: Codex must await the live server connection
before continuing, and initialization failure must not silently become an
ordinary coding run. Its 30-second startup timeout and all other settings are
unchanged. Every fresh database and connection initialization remains inside
the measured treatment setup/process time. A live retest must still verify
successful tool invocation; accepted configuration alone is insufficient.

The third pilot, `.local/benchmarks/device-auth-smoke-v3/`, verified one actual
A/B pair with the required-connection setting. A made zero MCP calls. B completed
six error-free Memglide calls: `list_projects`, `start_session`, two
`get_context` calls and two `get_context_passport` calls. Both external grades
passed eight tests, original protected files were unchanged, and both terminal
JSONL streams exposed complete token usage. Their starting commits and prompt
hashes matched within the pair. The prompt also matched both earlier pilots;
Memglide's runtime source hash remained
`20cc181bc45cecacc6e96f40e4a470112dd1581212eac7acece46c44f7270454`.
This verifies a working treatment under the new startup policy; a single retest
does not establish the sole cause of the earlier visibility failures. A used
48,343 input tokens (43,392 cached) and 892 output tokens; B used 172,380 input
tokens (138,752 cached) and 1,341 output tokens. This one-task pilot shows higher
observed usage for B and supports no savings claim. Provider invoiced cost and
underlying model-call counts remain unavailable. Keep pilot observations
separate from the full, newly frozen experiment.

The installed CLI is `codex-cli 0.159.2`. Official sources for that exact version
confirm the configuration and its semantics:

- [Configuration schema](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/core/config.schema.json):
  `RawMcpServerConfig.enabled_tools`, `RawMcpServerConfig.tools`,
  `RawMcpServerConfig.required`, `RawMcpServerConfig.startup_readiness`,
  `McpServerToolConfig.approval_mode`, and the `AppToolApproval` enum.
  Downloaded schema SHA-256:
  `eda7251b7e46e0b9d0f3d8eef5dab451e11a55d723e2b802e152b7208045836a`.
- [MCP call policy](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/core/src/mcp_tool_call.rs#L2476):
  `requires_mcp_tool_approval_for_mode` maps `Approve` to no additional tool
  approval prompt; `Auto` consults the tool annotations.
- [Required MCP startup](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/codex-mcp/src/connection_manager/required.rs):
  `validate_required_servers` awaits the connection for required servers whose
  readiness policy does not accept a cached catalog. The schema's supported
  readiness values are `connection` and `catalog`.

An offline test decodes the generated TOML and compares its authorization list
with the server's actual public tool declarations. A native CLI test runs
`codex mcp get memglide --json` with an empty, isolated `CODEX_HOME`; it checks
that the installed CLI accepts the configuration and exposes the exact tool
allowlist. That command makes no model request and does not prove invocation.
The supported CLI's `mcp get` response omits per-tool approval policies, so the
configuration schema, runtime source, decoded TOML test, and live tool result
serve different verification purposes.

## Evidence and interpretation

Retain the first invalid smoke, the failed explicit diagnostic, and any later
smoke in separate output directories. Do not merge diagnostic usage into coding
task aggregates. Start a fresh full experiment only after a new smoke verifies
completed, error-free `get_context` invocation. No task prompt or application
source needs to change for this permission correction. Each experiment records
the runner hash and before/after Memglide source hashes.

All original safeguards remain: identical starting commits and prompt hashes,
counterbalanced repeats, independent external grades, preserved failures,
complete-stream usage checks, and successful retrieval evidence for B. Provider
invoiced cost, underlying model-call count, and actual filesystem-read counts
remain unavailable unless their respective telemetry is supplied. Successful
login and scoped tool approval alone establish no token or cost savings.
