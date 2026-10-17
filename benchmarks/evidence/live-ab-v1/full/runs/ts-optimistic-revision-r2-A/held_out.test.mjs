import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-optimistic-revision-r2-A/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-optimistic-revision-r2-A/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-optimistic-revision-r2-A/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-optimistic-revision-r2-A/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-optimistic-revision-r2-A/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-optimistic-revision-r2-A/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-optimistic-revision-r2-A/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-optimistic-revision-r2-A/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-optimistic-revision-r2-A/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-optimistic-revision-r2-A/src/billing.ts";

test("conflicts are atomic", () => {
  const repository = new Repository();
  repository.create("a", { value: 1 });
  repository.update("a", { value: 2 }, { expected_revision: 1 });
  for (const revision of [1, 0, 99]) {
    assert.throws(() => repository.update("a", { value: 99 }, { expected_revision: revision }), ConflictError);
    assert.deepEqual(repository.records.get("a"), { id: "a", body: { value: 2 }, revision: 2 });
  }
});
test("success and defensive copy", () => {
  const repository = new Repository();
  repository.create("a", {});
  const body = { items: [1] };
  const result = repository.update("a", body, { expected_revision: 1 });
  body.items.push(2); result.body.items.push(3);
  assert.deepEqual(repository.records.get("a").body, { items: [1] });
  assert.equal(result.revision, 2);
});
