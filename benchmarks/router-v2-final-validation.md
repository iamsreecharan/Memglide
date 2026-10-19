# Final router verification

The frozen full Python run passed **2033 cases**. A later 43-case runner run added six distinct cases. After offline rejection, the discovery default was restored to v1; **324 affected cases passed**, including one new default-compatibility guard. The receipt union contains **2040 distinct Python cases**, all passing. This is not one enlarged full-suite run.

Frontend unit **24/24** and production browser **3/3** passed. The frontend was unchanged after those checks. A final rebuilt wheel installed into another clean environment passed **14 separate smoke checks**, including both real MCP profiles, API/SPA, CLI and explicit v1/v2 TypeScript parser delivery. Ruff and mypy (33 files) passed. No model requests were made by these checks.

The [original verification](router-v2-validation.md) preserves initial failures, including the non-reproduced frontend initial-load wait failure and unchanged successful reruns. Protected existing tests and timeouts were not weakened. The [JSON receipt](router-v2-final-validation.json) and `evidence/router-v2/post-evaluation/` retain final default hashes, exact regression XML, installed smoke and wheel hash.
