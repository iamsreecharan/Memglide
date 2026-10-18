import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-1/ts-daily-inventory-equal-length-zip/reference/src/equal_length_zip.ts";
import * as api from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-1/ts-daily-inventory-equal-length-zip/reference/src/equal_length_zip_api.ts";
test("both mismatch directions and empty arrays",()=>{
  for(const [left,right] of [[[1],[2,3]],[[1,2],[3]],[[],[1]],[[1],[]]]) {
    assert.throws(()=>core.zipEqual(left,right));assert.throws(()=>api.pairColumns(left,right));
  }
  assert.deepEqual(api.pairColumns([],[]),[]);
});
test("values order and fresh tuple containers",()=>{
  const left=[0,false,""],right=[null,2,3];const result=api.pairColumns(left,right);
  assert.deepEqual(result,[[0,null],[false,2],["",3]]);result[0][0]="changed";
  assert.deepEqual(left,[0,false,""]);assert.deepEqual(right,[null,2,3]);
  assert.deepEqual(core.zipEqual(["x"],[false]),[["x",false]]);
});
