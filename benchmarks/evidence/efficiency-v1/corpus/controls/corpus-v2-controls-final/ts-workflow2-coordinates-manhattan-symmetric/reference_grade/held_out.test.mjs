import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/efficiency-v1/corpus-v2-controls-final/ts-workflow2-coordinates-manhattan-symmetric/reference/src/manhattan_symmetric.ts";
test("symmetric absolute differences",()=>{
  assert.equal(core.manhattanDistance([3,4],[1,2]),4);
  assert.equal(core.manhattanDistance([5,-2],[-1,3]),11);
});
test("fractions and unchanged tuples",()=>{
  const a=[-1.5,2.25],b=[0.5,-0.75];
  assert.equal(core.manhattanDistance(a,b),5);assert.equal(core.manhattanDistance(b,a),5);
  assert.deepEqual(a,[-1.5,2.25]);assert.deepEqual(b,[0.5,-0.75]);
});
