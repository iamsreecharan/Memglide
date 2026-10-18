import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cost-v1/formal-10-v1/worktrees/cost-ts-cost-geometry-edge-touch-r1-A/src/edge_touch.ts";
test("edges corners and degenerate area",()=>{
  const a={left:0,top:0,right:2,bottom:2};
  for(const b of [{left:2,top:0,right:4,bottom:2},{left:2,top:2,right:3,bottom:3},{left:1,top:1,right:1,bottom:2},{left:1,top:1,right:2,bottom:1}])assert.equal(core.overlaps(a,b),false);
});
test("fractional negative coordinates and preservation",()=>{
  const a=Object.freeze({left:-2,top:-1,right:0.5,bottom:1}),b=Object.freeze({left:0,top:0,right:1,bottom:2});
  assert.equal(core.overlaps(a,b),true);assert.equal(core.overlaps(b,a),true);assert.equal(core.overlaps(a,{left:3,top:3,right:4,bottom:4}),false);
});
