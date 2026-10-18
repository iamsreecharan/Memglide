import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cost-v1/corpus-validation-workspaces/test_baseline_fails_behavior_r5/repo/src/signed_cents.ts";
test("small fractions and signs",()=>{
  for(const [value,expected] of [[0,"0.00"],[5,"0.05"],[-5,"-0.05"],[105,"1.05"],[-100,"-1.00"],[100,"1.00"]])assert.equal(core.formatCents(value),expected);
});
test("safe-integer validation and boundary",()=>{
  for(const value of [0.1,NaN,Infinity,Number.MAX_SAFE_INTEGER+1])assert.throws(()=>core.formatCents(value),RangeError);
  assert.equal(core.formatCents(Number.MAX_SAFE_INTEGER),"90071992547409.91");
});
