import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-idempotent-events-r2-B/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-idempotent-events-r2-B/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-idempotent-events-r2-B/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-idempotent-events-r2-B/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-idempotent-events-r2-B/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-idempotent-events-r2-B/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-idempotent-events-r2-B/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-idempotent-events-r2-B/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-idempotent-events-r2-B/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-idempotent-events-r2-B/src/billing.ts";

test("first payload and sequence win", () => {
  const repository = new Repository();
  const first = repository.putEvent("a", { value: 1 });
  assert.deepEqual(repository.putEvent("a", { value: 999 }), first);
  assert.deepEqual(repository.events.get("a"), first);
  assert.equal(repository.putEvent("b", {}).sequence, 2);
  assert.equal(repository.putEvent("a", {}).sequence, 1);
});
test("nested defensive copies", () => {
  const repository = new Repository(), payload = { items: [1] };
  const event = repository.putEvent("a", payload);
  payload.items.push(2); event.payload.items.push(3);
  const duplicate = repository.putEvent("a", {});
  assert.deepEqual(duplicate.payload, { items: [1] });
  duplicate.payload.items.push(4);
  assert.deepEqual(repository.events.get("a").payload, { items: [1] });
});
