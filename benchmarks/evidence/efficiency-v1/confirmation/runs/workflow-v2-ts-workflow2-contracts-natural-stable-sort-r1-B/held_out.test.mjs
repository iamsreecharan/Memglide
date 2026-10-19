import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/efficiency-v1/formal-workflow-confirmation-v2/worktrees/workflow-v2-ts-workflow2-contracts-natural-stable-sort-r1-B/src/natural_stable_sort.ts";
import * as api from "file:///workspace/Memglide/.local/efficiency-v1/formal-workflow-confirmation-v2/worktrees/workflow-v2-ts-workflow2-contracts-natural-stable-sort-r1-B/src/natural_stable_sort_api.ts";
test("numeric runs use exact integer values",()=>{
  assert.equal(core.compareNatural("item2","item10"),-1);
  assert.equal(core.compareNatural("x0002","x2"),0);
  assert.equal(core.compareNatural("x9007199254740993","x9007199254740992"),1);
});
test("sorting is stable and does not mutate",()=>{
  const values=["x10","x2","x02","x1"];const before=[...values];
  assert.deepEqual(api.sortedNatural(values),["x1","x2","x02","x10"]);
  assert.deepEqual(values,before);assert.equal(core.compareNatural("a","a1"),-1);
});
