import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/efficiency-v1/corpus-final-validation-v2/ts-workflow-text-negative-array-offset/reference/src/negative_array_offset.ts";
test("negative offsets and bounds",()=>{
  assert.equal(core.atPosition(["a","b","c"],-1),"c");
  assert.equal(core.atPosition(["a","b","c"],-3),"a");
  assert.equal(core.atPosition(["a"],-2),undefined);assert.equal(core.atPosition([],-1),undefined);
});
test("validation and unchanged generic values",()=>{
  for(const index of [0.5,NaN,Infinity])assert.throws(()=>core.atPosition([1],index),RangeError);
  const token={v:1};const values=[token];assert.equal(core.atPosition(values,-1),token);
  assert.deepEqual(values,[token]);
});
