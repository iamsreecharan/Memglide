import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern35/repo/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern35/repo/src/strict_pointer_lookup.ts";

test("falsy values escapes and root",()=>{
  const document={"a/b":{"~x":[false,0,"",null]}};
  for(const [index,expected] of [[0,false],[1,0],[2,""],[3,null]])assert.equal(api.lookup(document,`/a~1b/~0x/${index}`),expected);
  assert.deepEqual(core.lookup(document,""),document); assert.equal(api.lookup({"":7},"/"),7);
});
test("strict arrays own keys and copy isolation",()=>{
  for(const pointer of ["/arr/01","/arr/-","/arr/2","/arr/-1","/arr/0.0","/missing","/~2","not-pointer"])assert.throws(()=>api.lookup({arr:[1,2]},pointer));
  assert.throws(()=>api.lookup({},"/constructor"));const document={a:{items:[1]}};const result=api.lookup(document,"/a");result.items.push(2);assert.deepEqual(document,{a:{items:[1]}});
  assert.throws(()=>api.lookup({x:null},"/x/a"));
});
