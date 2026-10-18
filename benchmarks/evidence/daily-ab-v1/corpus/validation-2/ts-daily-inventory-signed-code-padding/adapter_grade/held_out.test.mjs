import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-2/ts-daily-inventory-signed-code-padding/adapter/src/signed_code_padding.ts";
import * as api from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-2/ts-daily-inventory-signed-code-padding/adapter/src/signed_code_padding_api.ts";
test("sign position zero and short widths",()=>{
  assert.equal(core.padCode(-7,4),"-007");assert.equal(api.labelCode(0,3),"000");
  assert.equal(api.labelCode(-12,5),"-0012");assert.equal(core.padCode(-123,2),"-123");
  assert.equal(api.labelCode(123,0),"123");assert.equal(core.padCode(0,0),"0");
});
test("validation and normal values",()=>{
  assert.equal(api.labelCode(42,4),"0042");assert.equal(core.padCode(Number.MAX_SAFE_INTEGER,1),String(Number.MAX_SAFE_INTEGER));
  for(const args of [[1.2,3],[1,-1],[1,0.5],[Infinity,2],[Number.MAX_SAFE_INTEGER+1,2]]) {
    assert.throws(()=>core.padCode(...args));assert.throws(()=>api.labelCode(...args));
  }
});
