# Local efficiency and warm-memory engineering validation

The complete collected Python regression run passed **1,626 tests** with no failures,
errors or skips (514.89 seconds). Two subsequently added benchmark recovery cases
also passed, for **1,628 distinct verified Python cases**. The 1,628-case enlarged
suite is not claimed as one full run; application source stayed unchanged.

**24 frontend tests and three production Chromium tests passed.** A clean installed
wheel passed real CLI, loopback API/SPA, default MCP and compact agent MCP checks,
plus memory preparation. All 44 packaged Python/source asset files matched current
source bytes. These functional checks are separate from pytest case counts.

Ruff and mypy passed. All 36 canonical warm-study stages successfully used the
production source preloader with exact complete source hashes. The bounded memory
adapter passed 43 cases and nine real prerequisite checks. The corpus passed 73
cases; the finalized runner passed all 47 cases (45 overlap the full suite).
Those targeted counts overlap the complete suite and are not added again.

An initial full attempt was interrupted after 390 passes and one fixture failure:
a comparison test assumed temporary artifacts were inside the checkout. The test
now declares its temporary artifact root explicitly; out-of-root and symlink
pointers still fail. All 16 comparison tests pass. The failure receipt hash and
final XML hash remain in the adjacent JSON. Two upstream Click deprecation warnings
remain. These checks made zero model requests.

Native warm-memory outcomes belong to the separately frozen study, not this
engineering validation. Component measurements do not establish model savings.
