import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/efficiency-v1/corpus-final-validation/ts-workflow-text-utf8-byte-length/baseline/src/utf8_byte_length.ts";
test("Unicode byte sizes",()=>{
  assert.equal(core.utf8Size("é"),2);assert.equal(core.utf8Size("東京"),6);
  assert.equal(core.utf8Size("😀"),4);assert.equal(core.utf8Size("a😀é"),7);
});
test("replacement semantics and controls",()=>{
  assert.equal(core.utf8Size("\uD800"),3);assert.equal(core.utf8Size("\uDC00x"),4);
  assert.equal(core.utf8Size("\0"),1);assert.equal(core.utf8Size(""),0);
});
