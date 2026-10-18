import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/formal-formats-20-v1/worktrees/fmt-ts-cache-collections-last-value-fallback-r1-B/src/last_value_fallback.ts";
test("final position and falsy final values",()=>{
  assert.equal(core.lastOrDefault([1,2,3],9),3);
  for(const value of [undefined,null,false,0,""])assert.equal(core.lastOrDefault(["first",value],"fallback"),value);
});
test("empty fallback and unchanged input",()=>{
  const fallback={id:1};assert.equal(core.lastOrDefault([],fallback),fallback);
  const items=[1,2];assert.equal(core.lastOrDefault(items,0),2);assert.deepEqual(items,[1,2]);
});
