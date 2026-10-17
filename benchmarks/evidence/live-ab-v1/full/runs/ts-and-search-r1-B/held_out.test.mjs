import test from "node:test";
import assert from "node:assert/strict";
import { TTLCache } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-and-search-r1-B/src/cache.ts";
import { DocumentService } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-and-search-r1-B/src/service.ts";
import { page } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-and-search-r1-B/src/pagination.ts";
import { Repository, ConflictError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-and-search-r1-B/src/repository.ts";
import { canAccess, resolveUnder } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-and-search-r1-B/src/security.ts";
import { dependencies } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-and-search-r1-B/src/graph.ts";
import { runWithRetry, TemporaryError } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-and-search-r1-B/src/retry.ts";
import { parseFlag } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-and-search-r1-B/src/config.ts";
import { search } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-and-search-r1-B/src/search.ts";
import { proratedCents } from "file:///workspace/Memglide/.local/benchmarks/device-auth-ab-full-v1/worktrees/ts-and-search-r1-B/src/billing.ts";

test("all tokens and no mutation", () => {
  const records = [{ id: "b", title: "Cloud", body: "CACHE docs" }, { id: "a", title: "cache cloud", body: "guide" }, { id: "c", title: "Cloud", body: "unrelated" }, { id: "d", title: "cloudy", body: "cache" }];
  const original = structuredClone(records);
  assert.deepEqual(new DocumentService().searchDocuments(records, "CLOUD cache").map(item => item.id), ["a", "b"]);
  assert.deepEqual(records, original);
});
test("empty repeated and punctuation", () => {
  const records = [{ id: "a", title: "alpha beta", body: "" }, { id: "b", title: "alpha", body: "" }];
  assert.deepEqual(search(records, "!!!"), []);
  assert.deepEqual(search(records, "alpha ALPHA,beta").map(item => item.id), ["a"]);
});
