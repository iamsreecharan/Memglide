import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-abort-aware-delay-plan-r2-B/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-abort-aware-delay-plan-r2-B/src/abort_aware_delay_plan.ts";

test("prefix deadline boundaries and zero work",()=>{
  assert.deepEqual(api.delayPlan([2,10,1],4),[0]); assert.deepEqual(core.delayPlan([10,1],2),[]);
  assert.deepEqual(api.delayPlan([0,0,1],0),[0,1]); assert.deepEqual(api.delayPlan([1,2,0],3),[0,1,2]); assert.deepEqual(api.delayPlan([],0),[]);
});
test("validation fractions and input preservation",()=>{
  const delays=[0.5,0.25,1]; assert.deepEqual(api.delayPlan(delays,0.75),[0,1]); assert.deepEqual(delays,[0.5,0.25,1]);
  for(const delays of [[-1],[NaN],[Infinity]])assert.throws(()=>api.delayPlan(delays,2));
  for(const deadline of [-1,NaN,Infinity])assert.throws(()=>api.delayPlan([],deadline));
  assert.throws(()=>api.delayPlan([Number.MAX_VALUE,Number.MAX_VALUE],Number.MAX_VALUE));
});
