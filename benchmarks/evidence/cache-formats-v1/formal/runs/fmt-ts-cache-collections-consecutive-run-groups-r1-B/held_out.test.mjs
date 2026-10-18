import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/formal-formats-20-v1/worktrees/fmt-ts-cache-collections-consecutive-run-groups-r1-B/src/consecutive_run_groups.ts";
import * as api from "file:///workspace/Memglide/.local/cache-v2/formal-formats-20-v1/worktrees/fmt-ts-cache-collections-consecutive-run-groups-r1-B/src/consecutive_run_groups_api.ts";
test("nonadjacent groups and single item visibility",()=>{
  const items=[{kind:"a",value:1},{kind:"a",value:2},{kind:"b",value:3},{kind:"a",value:4}];
  const expected=[{kind:"a",items:items.slice(0,2)},{kind:"b",items:[items[2]]},{kind:"a",items:[items[3]]}];
  assert.deepEqual(core.groupRuns(items),expected);assert.deepEqual(api.visibleRuns(items),expected);
});
test("detached records empty input and ordinary string keys",()=>{
  const items=[{kind:"__proto__",value:0}];const result=api.visibleRuns(items);assert.equal(result.length,1);result[0].items[0].value=9;assert.equal(items[0].value,0);
  assert.deepEqual(core.groupRuns([]),[]);assert.deepEqual(api.visibleRuns([]),[]);assert.equal(api.visibleRuns([{kind:"",value:1}])[0].kind,"");
});
