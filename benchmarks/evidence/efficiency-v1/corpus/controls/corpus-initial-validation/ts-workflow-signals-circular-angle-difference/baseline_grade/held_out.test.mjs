import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/efficiency-v1/corpus-initial-validation/ts-workflow-signals-circular-angle-difference/baseline/src/circular_angle_difference.ts";
test("wraparound and half-open ties",()=>{
  assert.equal(core.angleDifference(350,10),20);assert.equal(core.angleDifference(10,350),-20);
  assert.equal(core.angleDifference(0,180),-180);assert.equal(core.angleDifference(180,0),-180);
});
test("multiple turns fractions and validation",()=>{
  assert.equal(core.angleDifference(720.25,-359.25),0.5);
  assert.equal(core.angleDifference(-1080,1080),0);
  for(const value of [Infinity,-Infinity,NaN])assert.throws(()=>core.angleDifference(value,0),RangeError);
});
