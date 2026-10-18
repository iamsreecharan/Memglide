import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/formal-20-v1/worktrees/ts-daily-inventory-numeric-median-r2-B/src/numeric_median.ts";
test("numeric ordering even lengths and fractions",()=>{
  assert.equal(core.median([2,10,3]),3);assert.equal(core.median([4,1,3,2]),2.5);
  assert.equal(core.median([-5,-1,-3,-2]),-2.5);assert.equal(core.median([1.25]),1.25);
  assert.equal(core.median([Number.MAX_VALUE,Number.MAX_VALUE]),Number.MAX_VALUE);
  assert.equal(core.median([Number.MIN_VALUE,Number.MIN_VALUE]),Number.MIN_VALUE);
  assert.equal(core.median([Number.MIN_VALUE,Number.MIN_VALUE*2]),Number.MIN_VALUE*2);
});
test("immutable input and validation",()=>{
  const values=[10,2,1];const before=[...values];assert.equal(core.median(values),2);assert.deepEqual(values,before);
  for(const values of [[],[NaN],[1,Infinity],[-Infinity,1]])assert.throws(()=>core.median(values));
});
