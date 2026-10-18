import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/formal-formats-20-v1/worktrees/fmt-ts-cache-collections-signed-left-rotation-r1-A/src/signed_left_rotation.ts";
test("signed modulo and empty arrays",()=>{
  assert.deepEqual(core.rotateLeft([1,2,3],-1),[3,1,2]);assert.deepEqual(core.rotateLeft([1,2,3],-4),[3,1,2]);
  assert.deepEqual(core.rotateLeft([1,2,3],4),[2,3,1]);assert.deepEqual(core.rotateLeft([],4),[]);
});
test("fresh arrays values and validation",()=>{
  const items=[0,false,""];const result=core.rotateLeft(items,0);assert.deepEqual(result,items);assert.notEqual(result,items);result[0]=1;assert.deepEqual(items,[0,false,""]);
  for(const steps of [1.5,NaN,Infinity])assert.throws(()=>core.rotateLeft([1],steps));
});
