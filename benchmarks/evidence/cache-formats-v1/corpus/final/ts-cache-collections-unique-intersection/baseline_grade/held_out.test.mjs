import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/corpus-validation-final/ts-cache-collections-unique-intersection/baseline/src/unique_intersection.ts";
test("deduplication left order and Set equality",()=>{
  assert.deepEqual(core.intersection([3,1,3,2,1],[1,2,3]),[3,1,2]);assert.deepEqual(core.intersection([NaN,NaN,0,-0],[NaN,0]),[NaN,0]);
  const item={id:1};assert.deepEqual(core.intersection([item,item,{id:1}],[item]),[item]);
});
test("empty inputs and no mutation",()=>{
  const left=[2,1,2],right=[2];assert.deepEqual(core.intersection(left,right),[2]);assert.deepEqual(left,[2,1,2]);assert.deepEqual(right,[2]);
  assert.deepEqual(core.intersection([],right),[]);assert.deepEqual(core.intersection([1],[]),[]);
});
