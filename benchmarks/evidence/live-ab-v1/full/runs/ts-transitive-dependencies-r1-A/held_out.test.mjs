import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-transitive-dependencies-r1-A/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-transitive-dependencies-r1-A/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-transitive-dependencies-r1-A/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-transitive-dependencies-r1-A/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-transitive-dependencies-r1-A/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-transitive-dependencies-r1-A/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-transitive-dependencies-r1-A/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-transitive-dependencies-r1-A/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-transitive-dependencies-r1-A/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-transitive-dependencies-r1-A/src/billing.ts";

test("cycles diamonds and input", () => {
  const graph = { a: ["c", "b", "a"], b: ["d"], c: ["d", "e"], d: ["a"], e: ["leaf"] };
  const original = structuredClone(graph);
  assert.deepEqual(new DocumentService().dependenciesFor(graph, "a"), ["b", "c", "d", "e", "leaf"]);
  assert.deepEqual(graph, original);
});
test("missing and long chain", () => {
  assert.deepEqual(dependencies({}, "missing"), []);
  const graph = Object.fromEntries(Array.from({ length: 300 }, (_, i) => [String(i), [String(i + 1)]]));
  assert.deepEqual(dependencies(graph, "0"), Array.from({ length: 300 }, (_, i) => String(i + 1)).sort());
});
