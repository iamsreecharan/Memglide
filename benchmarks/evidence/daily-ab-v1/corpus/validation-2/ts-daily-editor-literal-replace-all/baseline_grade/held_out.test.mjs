import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-2/ts-daily-editor-literal-replace-all/baseline/src/literal_replace_all.ts";
import * as api from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-2/ts-daily-editor-literal-replace-all/baseline/src/literal_replace_all_api.ts";
test("all literal occurrences and replacement metacharacters",()=>{
  assert.equal(core.replaceLiteral("a.a.a",".","$&"),"a$&a$&a");
  assert.equal(core.replaceLiteral("aaaaa","aa","x"),"xxa");
  assert.equal(api.applyReplacement("a a a"," ","_"),"a_a_a");
  assert.equal(api.applyReplacement(".x.x",".x","$1"),"$1$1");
  assert.deepEqual(api.replaceBatch([{text:"a a a",needle:" ",replacement:"$&"},{text:".x.x",needle:".x",replacement:"$1"}]),[{before:"a a a",after:"a$&a$&a",changed:true},{before:".x.x",after:"$1$1",changed:true}]);
});
test("empty needle whitespace and unchanged strings",()=>{
  assert.throws(()=>core.replaceLiteral("abc","","x"));
  assert.throws(()=>api.applyReplacement("abc","","x"));
  assert.equal(api.applyReplacement(" a  "," ",""),"a");
  assert.equal(core.replaceLiteral("😀ab😀","😀","é"),"éabé");
  assert.equal(api.applyReplacement("abc","z","x"),"abc");
  const request={text:"a a",needle:" ",replacement:"_"};const before=structuredClone(request);
  assert.deepEqual(api.previewReplacement(request),{before:"a a",after:"a_a",changed:true});assert.deepEqual(request,before);
  assert.deepEqual(api.previewReplacement({text:"abc",needle:"z",replacement:"x"}),{before:"abc",after:"abc",changed:false});
  assert.throws(()=>api.replaceBatch([{text:"a",needle:"",replacement:"x"}]));assert.deepEqual(api.replaceBatch([]),[]);
});
