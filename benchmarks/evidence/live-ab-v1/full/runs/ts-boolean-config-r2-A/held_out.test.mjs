import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-boolean-config-r2-A/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-boolean-config-r2-A/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-boolean-config-r2-A/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-boolean-config-r2-A/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-boolean-config-r2-A/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-boolean-config-r2-A/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-boolean-config-r2-A/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-boolean-config-r2-A/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-boolean-config-r2-A/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-boolean-config-r2-A/src/billing.ts";

test("supported values and service", () => {
  const service = new DocumentService();
  for (const value of [true, "true", "  TRUE ", "1", "Yes", "ON"]) assert.equal(service.featureEnabled(value), true);
  for (const value of [false, "false", "  FALSE ", "0", "No", "OFF"]) assert.equal(service.featureEnabled(value), false);
  assert.equal(parseFlag(null, true), true);
  assert.equal(parseFlag(undefined), false);
});
test("invalid values rejected", () => {
  for (const value of [0, 1, 1.0, "", "truthy", [], {}, ["true"]]) assert.throws(() => parseFlag(value));
});
