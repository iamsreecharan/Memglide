import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/efficiency-v1/corpus-v2-controls-final/ts-workflow2-contracts-unicode-common-prefix/reference/src/unicode_common_prefix.ts";
test("longest prefix across every string",()=>{
  assert.equal(core.commonPrefix(["flower","flow","flight"]),"fl");
  assert.equal(core.commonPrefix(["abc","abc",""]),"");
  assert.equal(core.commonPrefix(["Alpha","alpha"]),"");
});
test("complete code points and unchanged input",()=>{
  const values=["🙂alpha","🙂beta"];const before=[...values];
  assert.equal(core.commonPrefix(values),"🙂");assert.deepEqual(values,before);
  assert.equal(core.commonPrefix(["😀a","😁b"]),"");
});
