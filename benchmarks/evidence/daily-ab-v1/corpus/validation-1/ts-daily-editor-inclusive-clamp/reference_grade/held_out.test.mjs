import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-1/ts-daily-editor-inclusive-clamp/reference/src/inclusive_clamp.ts";
test("inclusive ends fractional and equal bounds",()=>{
  assert.equal(core.clamp(10,0,10),10);assert.equal(core.clamp(11,0,10),10);
  assert.equal(core.clamp(-1,0,10),0);assert.equal(core.clamp(2.5,0,10),2.5);
  assert.equal(core.clamp(1,3,3),3);assert.equal(core.clamp(8,3,3),3);
});
test("negative ranges and invalid numbers",()=>{
  assert.equal(core.clamp(0,-10,-2),-2);assert.equal(core.clamp(-20,-10,-2),-10);
  for(const args of [[NaN,0,1],[0,1,0],[0,-Infinity,1],[0,0,Infinity]]) assert.throws(()=>core.clamp(...args));
});
