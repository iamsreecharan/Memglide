import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-lru-eviction-r1-B/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-lru-eviction-r1-B/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-lru-eviction-r1-B/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-lru-eviction-r1-B/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-lru-eviction-r1-B/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-lru-eviction-r1-B/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-lru-eviction-r1-B/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-lru-eviction-r1-B/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-lru-eviction-r1-B/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-lru-eviction-r1-B/src/billing.ts";

test("successful read refreshes recency", () => {
  const cache = new TTLCache(2);
  cache.put("a", 1, { now: 0, ttl: 100 });
  cache.put("b", 2, { now: 0, ttl: 100 });
  assert.equal(cache.get("a", { now: 1 }), 1);
  cache.put("c", 3, { now: 2, ttl: 100 });
  assert.equal(cache.get("b", { now: 2 }), undefined);
  assert.equal(cache.get("a", { now: 2 }), 1);
  assert.equal(cache.entries.size, 2);
});
test("updates misses and expiration", () => {
  const cache = new TTLCache(2);
  cache.put("a", 1, { now: 0, ttl: 10 });
  cache.put("b", 2, { now: 0, ttl: 100 });
  assert.equal(cache.get("missing", { now: 1 }), undefined);
  cache.put("a", 9, { now: 1, ttl: 10 });
  cache.put("c", 3, { now: 2, ttl: 100 });
  assert.equal(cache.get("b", { now: 2 }), undefined);
  assert.equal(cache.get("a", { now: 5 }), 9);
  assert.equal(cache.get("a", { now: 12 }), undefined);
});
