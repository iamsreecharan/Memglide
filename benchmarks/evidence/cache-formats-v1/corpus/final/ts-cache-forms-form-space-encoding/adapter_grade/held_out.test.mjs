import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/corpus-validation-final/ts-cache-forms-form-space-encoding/adapter/src/form_space_encoding.ts";
import * as api from "file:///workspace/Memglide/.local/cache-v2/corpus-validation-final/ts-cache-forms-form-space-encoding/adapter/src/form_space_encoding_api.ts";
test("space plus Unicode and original key case",()=>{
  assert.equal(core.encodeFormComponent("a b+c"),"a+b%2Bc");
  assert.equal(api.toFormPair("User Name","a b+c"),"User+Name=a+b%2Bc");
  assert.equal(api.toFormPair("É","東京"),"%C3%89=%E6%9D%B1%E4%BA%AC");
});
test("empty values separators and repeated spaces",()=>{
  assert.equal(api.toFormPair("X",""),"X=");assert.equal(api.toFormPair("",""),"=");
  assert.equal(core.encodeFormComponent("  &="),"++%26%3D");
  assert.equal(api.toFormPair("A+B","x=y&z"),"A%2BB=x%3Dy%26z");
});
