import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-scope-authorization-r2-B/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-scope-authorization-r2-B/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-scope-authorization-r2-B/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-scope-authorization-r2-B/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-scope-authorization-r2-B/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-scope-authorization-r2-B/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-scope-authorization-r2-B/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-scope-authorization-r2-B/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-scope-authorization-r2-B/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-scope-authorization-r2-B/src/billing.ts";

test("exact and resource wildcard", () => {
  const service = new DocumentService();
  for (const scopes of [["docs:read"], ["docs:*"], ["other:write", "docs:read"]]) {
    assert.equal(service.authorized(scopes, "docs", "read"), true);
  }
});
test("partial and unrelated scopes denied", () => {
  for (const scope of ["", "read", "docs", "doc", "docs:rea", "*", "*:read", "doc:*", "docs:write", "archive:read"]) {
    assert.equal(canAccess([scope], "docs", "read"), false, scope);
  }
  assert.equal(canAccess([], "docs", "read"), false);
});
