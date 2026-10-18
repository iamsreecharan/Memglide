import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-1/ts-daily-editor-literal-replace-all/domain/src/literal_replace_all.ts";
import * as api from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-1/ts-daily-editor-literal-replace-all/domain/src/literal_replace_all_api.ts";
test("all literal occurrences and replacement metacharacters",()=>{
  assert.equal(core.replaceLiteral("a.a.a",".","$&"),"a$&a$&a");
  assert.equal(core.replaceLiteral("aaaaa","aa","x"),"xxa");
  assert.equal(api.applyReplacement("a a a"," ","_"),"a_a_a");
  assert.equal(api.applyReplacement(".x.x",".x","$1"),"$1$1");
});
test("empty needle whitespace and unchanged strings",()=>{
  assert.throws(()=>core.replaceLiteral("abc","","x"));
  assert.throws(()=>api.applyReplacement("abc","","x"));
  assert.equal(api.applyReplacement(" a  "," ",""),"a");
  assert.equal(core.replaceLiteral("😀ab😀","😀","é"),"éabé");
  assert.equal(api.applyReplacement("abc","z","x"),"abc");
});
