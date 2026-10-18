import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-1/ts-daily-inventory-zero-count-plural/reference/src/zero_count_plural.ts";
test("zero one many and supplied words",()=>{
  assert.equal(core.pluralize(0,"item","items"),"items");assert.equal(core.pluralize(1,"child","children"),"child");
  assert.equal(core.pluralize(9,"child","children"),"children");assert.equal(core.pluralize(0,"x",""),"");
});
test("invalid counts",()=>{
  for(const count of [-1,0.5,NaN,Infinity]) assert.throws(()=>core.pluralize(count,"item","items"));
  assert.equal(core.pluralize(1000000,"one","many"),"many");
});
