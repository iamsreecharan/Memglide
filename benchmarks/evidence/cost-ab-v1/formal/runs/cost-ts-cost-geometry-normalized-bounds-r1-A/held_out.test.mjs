import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cost-v1/formal-10-v1/worktrees/cost-ts-cost-geometry-normalized-bounds-r1-A/src/normalized_bounds.ts";
import * as api from "file:///workspace/Memglide/.local/cost-v1/formal-10-v1/worktrees/cost-ts-cost-geometry-normalized-bounds-r1-A/src/normalized_bounds_api.ts";
test("independent ordering and exact public fractions",()=>{
  assert.deepEqual(core.normalizeBounds(3,1,1,5),{left:1,top:1,right:3,bottom:5});
  assert.deepEqual(api.rectangleBounds({x1:2.75,y1:4.5,x2:-1.25,y2:0.5}),{left:-1.25,top:0.5,right:2.75,bottom:4.5});
});
test("finite validation and unchanged input",()=>{
  for(const bad of [NaN,Infinity,-Infinity])assert.throws(()=>core.normalizeBounds(0,1,bad,3),RangeError);
  const input=Object.freeze({x1:4.25,y1:-3.5,x2:2.5,y2:-2.25});
  assert.deepEqual(api.rectangleBounds(input),{left:2.5,top:-3.5,right:4.25,bottom:-2.25});
});
