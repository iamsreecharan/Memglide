import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern23/repo/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern23/repo/src/event_time_rolling_counts.ts";

test("out of order duplicates and open lower boundary",()=>{
  const events=[{id:"late",at:10},{id:"early",at:5},{id:"same",at:10},{id:"edge",at:0}];
  assert.deepEqual(api.rollingCounts(events,5),[{id:"late",count:2},{id:"early",count:1},{id:"same",count:2},{id:"edge",count:1}]);
  assert.deepEqual(core.rollingCounts([{id:"a",at:1},{id:"b",at:1}],2),[{id:"a",count:2},{id:"b",count:2}]);
  assert.deepEqual(api.rollingCounts([],1),[]);
});
test("validation negatives and no mutation",()=>{
  const events=[{id:"a",at:-2},{id:"b",at:-1}]; const before=structuredClone(events);
  assert.deepEqual(api.rollingCounts(events,2),[{id:"a",count:1},{id:"b",count:2}]); assert.deepEqual(events,before);
  for(const width of [0,-1,Infinity,NaN]) assert.throws(()=>api.rollingCounts(events,width));
  assert.throws(()=>api.rollingCounts([{id:"a",at:NaN}],1));
});
