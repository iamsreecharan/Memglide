import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/formal-20-v1/worktrees/ts-daily-inventory-chunk-without-empty-tail-r2-B/src/chunk_without_empty_tail.ts";
test("empty exact multiples and oversize chunks",()=>{
  assert.deepEqual(core.chunk([],2),[]);assert.deepEqual(core.chunk([1,2,3,4],2),[[1,2],[3,4]]);
  assert.deepEqual(core.chunk([1,2],1),[[1],[2]]);assert.deepEqual(core.chunk([1],5),[[1]]);
});
test("new containers order and invalid sizes",()=>{
  const input=["a","b","c"];const output=core.chunk(input,2);output[0].push("new");assert.deepEqual(input,["a","b","c"]);
  assert.deepEqual(core.chunk([false,null,0,""],3),[[false,null,0],[""]]);
  for(const size of [0,-1,1.5,NaN,Infinity])assert.throws(()=>core.chunk([1],size));
});
