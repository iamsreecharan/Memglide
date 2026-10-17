import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern26/repo/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern26/repo/src/simultaneous_text_edits.ts";

test("original coordinates unsorted and adjacent edits",()=>{
  const edits=[{start:4,end:6,text:"Z"},{start:0,end:1,text:"LONG"}];
  assert.equal(api.applyEdits("abcdef",edits),"LONGbcdZ"); assert.equal(edits[0].start,4);
  assert.equal(core.applyEdits("abcd",[{start:0,end:2,text:""},{start:2,end:4,text:"X"}]),"X");
  assert.equal(api.applyEdits("ab",[{start:2,end:2,text:"!"}]),"ab!"); assert.equal(api.applyEdits("",[]),"");
});
test("overlaps same starts and invalid offsets",()=>{
  for(const edits of [[{start:0,end:3,text:"x"},{start:2,end:4,text:"y"}],[{start:1,end:1,text:"x"},{start:1,end:2,text:"y"}],[{start:-1,end:1,text:"x"}],[{start:1,end:5,text:"x"}],[{start:1.5,end:2,text:"x"}]]) assert.throws(()=>api.applyEdits("abcd",edits));
  assert.equal(api.applyEdits("😀x",[{start:2,end:3,text:"!"}]),"😀!");
});
