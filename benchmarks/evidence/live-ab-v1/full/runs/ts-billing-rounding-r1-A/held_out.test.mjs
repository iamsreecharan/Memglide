import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-billing-rounding-r1-A/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-billing-rounding-r1-A/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-billing-rounding-r1-A/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-billing-rounding-r1-A/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-billing-rounding-r1-A/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-billing-rounding-r1-A/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-billing-rounding-r1-A/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-billing-rounding-r1-A/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-billing-rounding-r1-A/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-billing-rounding-r1-A/src/billing.ts";

test("half up and exact integer arithmetic", () => {
  for (const [monthly, active, days] of [[101, 1, 2], [100, 1, 3], [100, 2, 3], [99, 30, 30], [0, 0, 31], [9007199254740991, 6, 7], [9007199254740991, 999, 1000]]) {
    const numerator = BigInt(monthly) * BigInt(active), denominator = BigInt(days);
    const expected = Number(numerator / denominator + (2n * (numerator % denominator) >= denominator ? 1n : 0n));
    assert.equal(proratedCents(monthly, active, days), expected);
  }
});
test("validation and zero", () => {
  assert.equal(proratedCents(100, 0, 31), 0);
  for (const args of [[-1, 1, 2], [10, 3, 2], [10, 0, 0], [1.2, 1, 2], [true, 1, 2]]) assert.throws(() => proratedCents(...args));
});
