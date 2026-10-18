import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-bounded-run-length-decode-r2-A/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-bounded-run-length-decode-r2-A/src/bounded_run_length_decode.ts";

test("copies and zero runs",()=>{
  const value={items:[1]}; const result=api.decodeRuns([{value,count:2},{value:"x",count:0}],2);
  result[0].items.push(2); assert.deepEqual(result[1],{items:[1]}); assert.deepEqual(value,{items:[1]});
  assert.deepEqual(core.decodeRuns([],0),[]); assert.deepEqual(api.decodeRuns([{value:false,count:1},{value:null,count:1}],2),[false,null]);
});
test("strict counts cap and overflow",()=>{
  for(const count of [-1,1.5,NaN,Infinity,Number.MAX_SAFE_INTEGER+1]) assert.throws(()=>api.decodeRuns([{value:0,count}],10));
  for(const cap of [-1,1.5,NaN]) assert.throws(()=>api.decodeRuns([],cap));
  assert.throws(()=>api.decodeRuns([{value:1,count:2},{value:2,count:2}],3));
  assert.throws(()=>api.decodeRuns([{value:1,count:Number.MAX_SAFE_INTEGER},{value:2,count:1}],Number.MAX_SAFE_INTEGER));
});
