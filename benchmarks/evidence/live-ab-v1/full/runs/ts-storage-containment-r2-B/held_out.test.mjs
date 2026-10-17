import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-storage-containment-r2-B/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-storage-containment-r2-B/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-storage-containment-r2-B/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-storage-containment-r2-B/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-storage-containment-r2-B/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-storage-containment-r2-B/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-storage-containment-r2-B/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-storage-containment-r2-B/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-storage-containment-r2-B/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-storage-containment-r2-B/src/billing.ts";

test("sibling prefix and absolute denied", () => {
  for (const key of ["../database/secret", "../data-backup/key", "../../etc/passwd", "/srv/data/absolute"]) {
    assert.throws(() => resolveUnder("/srv/data", key), undefined, key);
  }
});
test("normalization and service", () => {
  const service = new DocumentService();
  for (const [key, expected] of [["", "/srv/data"], [".", "/srv/data"], ["docs/../a/./b", "/srv/data/a/b"], ["docs..txt", "/srv/data/docs..txt"]]) {
    assert.equal(service.storageKey("/srv/data", key), expected);
  }
  assert.equal(service.storageKey("/srv/data/", "a"), "/srv/data/a");
});
