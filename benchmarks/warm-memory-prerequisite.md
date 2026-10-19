# Warm-memory prerequisite check

A real temporary Git repository and Service passed all nine checks. This check made **zero model requests**. A fresh Python preparation process reproduced the same prepared prompt from the original active Memglide session. This tests the preparation prerequisite; native Codex effectiveness requires the separate benchmark.

| Check | Observation |
|---|---|
| Source-backed active memory | One current claim prepared |
| Fresh preparation process | Identical prepared prompt SHA-256 |
| Preparation lifetime behavior | Session row unchanged; no TTL refresh |
| Service restart | Same active session remains usable |
| New Memglide session | No recalled old memories; original ID rejected |
| Changed cited source | Entire addition declined |
| Ended session | Addition declined; engine recall rejects with 410 |
| Past expiration deadline | Addition declined without deleting or renewing state |
| Ordinary expiration cleanup | Session and memory deleted |

Defaults remain 60 minutes of inactivity and an eight-hour absolute lifetime. Expiration was tested by setting the fixture deadline into the past, not by extending retention or waiting an hour.

The supported warm benchmark reuses one bounded active Memglide session across fresh native Codex processes. It must not be described as persistent memory across new Memglide sessions. All cited sources must remain eligible and current, and source freshness alone does not verify a claim's meaning.

The JSON receipt includes actual observations, boolean checks, timestamp and the preparation module SHA-256.
