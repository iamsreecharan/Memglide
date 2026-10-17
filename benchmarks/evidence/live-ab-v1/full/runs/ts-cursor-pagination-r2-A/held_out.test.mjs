import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-cursor-pagination-r2-A/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-cursor-pagination-r2-A/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-cursor-pagination-r2-A/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-cursor-pagination-r2-A/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-cursor-pagination-r2-A/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-cursor-pagination-r2-A/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-cursor-pagination-r2-A/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-cursor-pagination-r2-A/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-cursor-pagination-r2-A/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-cursor-pagination-r2-A/src/billing.ts";

test("walk and no mutation", () => {
  const records = ["d", "a", "c", "b", "e"].map(id => ({ id }));
  const original = structuredClone(records), seen = [];
  let cursor;
  for (let i = 0; i < 10; i++) {
    const current = page(records, { cursor, limit: 2 });
    seen.push(...current.items.map(item => item.id));
    cursor = current.next_cursor;
    if (cursor === null) break;
  }
  assert.deepEqual(seen, ["a", "b", "c", "d", "e"]);
  assert.equal(cursor, null);
  assert.deepEqual(records, original);
});
test("deleted cursor and service", () => {
  assert.deepEqual(page([{ id: "a" }, { id: "d" }], { cursor: "b", limit: 1 }).items, [{ id: "d" }]);
  const service = new DocumentService();
  for (const key of ["b", "a", "c"]) service.repository.create(key, {});
  assert.deepEqual(service.listDocuments("b").items.map(item => item.id), ["c"]);
  for (const limit of [0, -1, 101]) assert.throws(() => page([], { limit }));
});
