import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-2/ts-daily-inventory-equal-length-zip/baseline/src/equal_length_zip.ts";
import * as api from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-2/ts-daily-inventory-equal-length-zip/baseline/src/equal_length_zip_api.ts";
test("both mismatch directions and empty arrays",()=>{
  for(const [left,right] of [[[1],[2,3]],[[1,2],[3]],[[],[1]],[[1],[]]]) {
    assert.throws(()=>core.zipEqual(left,right));assert.throws(()=>api.pairColumns(left,right));
    assert.throws(()=>api.pairTable({name:"left",values:left},{name:"right",values:right}));
  }
  assert.deepEqual(api.pairColumns([],[]),[]);
  assert.deepEqual(api.pairTable({name:"left",values:[]},{name:"right",values:[]}),{headers:["left","right"],rows:[]});
});
test("values order and fresh tuple containers",()=>{
  const left=[0,false,""],right=[null,2,3];const result=api.pairColumns(left,right);
  assert.deepEqual(result,[[0,null],[false,2],["",3]]);result[0][0]="changed";
  assert.deepEqual(left,[0,false,""]);assert.deepEqual(right,[null,2,3]);
  assert.deepEqual(core.zipEqual(["x"],[false]),[["x",false]]);
  const a={name:"left",values:[0,false,""]},b={name:"right",values:[null,2,3]};const before=structuredClone([a,b]);
  const table=api.pairTable(a,b);assert.deepEqual(table,{headers:["left","right"],rows:[[0,null],[false,2],["",3]]});
  table.headers[0]="changed";table.rows[0][0]="changed";assert.deepEqual([a,b],before);
  for(const [leftName,rightName] of [["","right"],["left",""],["same","same"]])assert.throws(()=>api.pairTable({name:leftName,values:[]},{name:rightName,values:[]}));
});
