import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cost-v1/formal-10-v1/worktrees/cost-ts-cost-ledger-memo-empty-only-r1-A/src/memo_empty_only.ts";
test("nonempty memos are exact",()=>{
  for(const value of [" ","  paid  ","0","\t","東京"])assert.equal(core.memoLabel(value,"none"),value);
});
test("only empty uses exact fallback",()=>{
  assert.equal(core.memoLabel("","  pending  "),"  pending  ");assert.equal(core.memoLabel("",""),"");assert.equal(core.memoLabel("x","other"),"x");
});
