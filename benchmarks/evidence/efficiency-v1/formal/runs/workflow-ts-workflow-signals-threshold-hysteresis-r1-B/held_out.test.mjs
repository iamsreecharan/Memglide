import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/efficiency-v1/formal-workflow-v1/worktrees/workflow-ts-workflow-signals-threshold-hysteresis-r1-B/src/threshold_hysteresis.ts";
import * as api from "file:///workspace/Memglide/.local/efficiency-v1/formal-workflow-v1/worktrees/workflow-ts-workflow-signals-threshold-hysteresis-r1-B/src/threshold_hysteresis_api.ts";
test("hysteresis middle and exact thresholds",()=>{
  assert.equal(core.nextState(true,3,2,5),true);assert.equal(core.nextState(true,2,2,5),false);
  assert.equal(core.nextState(false,5,2,5),true);assert.equal(core.nextState(false,3,2,5),false);
});
test("initial state propagation and unchanged inputs",()=>{
  const values=[3,4,2,5,3];const before=[...values];
  assert.deepEqual(api.traceStates(values,2,5,true),[true,true,false,true,true]);
  assert.deepEqual(values,before);assert.deepEqual(api.traceStates([3],2,5,false),[false]);
});
