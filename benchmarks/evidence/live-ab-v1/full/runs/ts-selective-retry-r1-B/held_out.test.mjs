import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-selective-retry-r1-B/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-selective-retry-r1-B/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-selective-retry-r1-B/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-selective-retry-r1-B/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-selective-retry-r1-B/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-selective-retry-r1-B/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-selective-retry-r1-B/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-selective-retry-r1-B/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-selective-retry-r1-B/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-selective-retry-r1-B/src/billing.ts";

test("permanent error not retried", () => {
  let calls = 0; const error = new TypeError("permanent");
  assert.throws(() => runWithRetry(() => { calls++; throw error; }, 5), value => value === error);
  assert.equal(calls, 1);
});
test("temporary success exhaustion validation", () => {
  let calls = 0; const error = new TemporaryError("later");
  const operation = () => { calls++; if (calls < 3) throw error; return { ok: true }; };
  assert.deepEqual(runWithRetry(operation, 3), { ok: true });
  assert.equal(calls, 3); calls = 0;
  assert.throws(() => runWithRetry(operation, 2), value => value === error);
  assert.equal(calls, 2);
  assert.throws(() => runWithRetry(() => null, 0));
});
