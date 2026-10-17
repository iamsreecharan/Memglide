import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-ttl-boundary-r1-B/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-ttl-boundary-r1-B/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-ttl-boundary-r1-B/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-ttl-boundary-r1-B/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-ttl-boundary-r1-B/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-ttl-boundary-r1-B/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-ttl-boundary-r1-B/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-ttl-boundary-r1-B/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-ttl-boundary-r1-B/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-ttl-boundary-r1-B/src/billing.ts";

test("deadline and service", () => {
  const service = new DocumentService();
  service.cache.put("a", "old", { now: 100, ttl: 10 });
  assert.equal(service.cachedDocument("a", 109.999), "old");
  assert.equal(service.cachedDocument("a", 110), undefined);
  assert.equal(service.cache.entries.has("a"), false);
});
test("overwrite and zero TTL", () => {
  const cache = new TTLCache();
  cache.put("a", 1, { now: 0, ttl: 2 });
  cache.put("a", 2, { now: 1, ttl: 10 });
  assert.equal(cache.get("a", { now: 3 }), 2);
  assert.equal(cache.get("a", { now: 11 }), undefined);
  cache.put("zero", 1, { now: 0, ttl: 0 });
  assert.equal(cache.get("zero", { now: 0 }), undefined);
});
