import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-transactional-accumulator-r1-B/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-transactional-accumulator-r1-B/src/transactional_accumulator.ts";

test("rollback entire batch and snapshot",()=>{
  const state={a:2,b:1}; assert.throws(()=>api.accumulate(state,[{key:"a",amount:1},{key:"b",amount:-2}])); assert.deepEqual(state,{a:2,b:1});
  const result=core.accumulate(state,[{key:"a",amount:-2},{key:"new",amount:3}]); assert.deepEqual(state,{a:0,b:1,new:3}); result.a=999; assert.equal(state.a,0);
  assert.deepEqual(api.accumulate({},[]),{});
});
test("special keys and invalid amounts",()=>{
  const state={}; const result=api.accumulate(state,[{key:"__proto__",amount:2},{key:"constructor",amount:1}]);
  assert.equal(Object.hasOwn(state,"__proto__"),true); assert.equal(result.__proto__,2); assert.equal(result.constructor,1);
  for(const amount of [1.5,NaN,Infinity,Number.MAX_SAFE_INTEGER+1]) assert.throws(()=>api.accumulate({},[{key:"x",amount}]));
  const full={x:Number.MAX_SAFE_INTEGER}; assert.throws(()=>api.accumulate(full,[{key:"x",amount:1}])); assert.equal(full.x,Number.MAX_SAFE_INTEGER);
});
