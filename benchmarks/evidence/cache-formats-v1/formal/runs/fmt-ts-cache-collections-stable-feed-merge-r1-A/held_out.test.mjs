import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/formal-formats-20-v1/worktrees/fmt-ts-cache-collections-stable-feed-merge-r1-A/src/stable_feed_merge.ts";
import * as api from "file:///workspace/Memglide/.local/cache-v2/formal-formats-20-v1/worktrees/fmt-ts-cache-collections-stable-feed-merge-r1-A/src/stable_feed_merge_api.ts";
test("stable left ties and frozen public inputs",()=>{
  const left=[{key:1,id:"l1"},{key:1,id:"l2"},{key:3,id:"l3"}],right=[{key:1,id:"r1"},{key:2,id:"r2"}];
  assert.deepEqual(core.mergeSorted(left,right).map(row=>row.id),["l1","l2","r1","r2","l3"]);
  Object.freeze(left);Object.freeze(right);assert.deepEqual(api.mergeFeeds(left,right).map(row=>row.id),["l1","l2","r1","r2","l3"]);
});
test("identity empty feeds and unchanged arrays",()=>{
  const entry={key:1,id:"a"},left=[entry],right=[];const result=api.mergeFeeds(left,right);assert.notEqual(result,left);assert.equal(result[0],entry);
  assert.deepEqual(left,[entry]);assert.deepEqual(right,[]);assert.deepEqual(api.mergeFeeds([],[]),[]);
});
