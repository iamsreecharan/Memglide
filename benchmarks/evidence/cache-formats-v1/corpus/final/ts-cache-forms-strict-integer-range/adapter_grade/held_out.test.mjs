import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/corpus-validation-final/ts-cache-forms-strict-integer-range/adapter/src/strict_integer_range.ts";
import * as api from "file:///workspace/Memglide/.local/cache-v2/corpus-validation-final/ts-cache-forms-strict-integer-range/adapter/src/strict_integer_range_api.ts";
test("signed complete integer syntax",()=>{
  assert.deepEqual(core.parseIntegerRange("-3..+05"),{start:-3,end:5});assert.deepEqual(api.rangeField("0..0"),{start:0,end:0});
  for(const text of ["1 ..3","1.. 3","1.5..3","1e2..300","..3","1..","1..2..3"])assert.throws(()=>core.parseIntegerRange(text));
  for(const text of [" 1..3","1..3 ","1..3\n"])assert.throws(()=>api.rangeField(text));
});
test("safe endpoints ordering and ordinary bounds",()=>{
  for(const text of ["3..1","9007199254740992..9007199254740993","Infinity..Infinity","a..b"])assert.throws(()=>api.rangeField(text));
  assert.deepEqual(api.rangeField("-9007199254740991..9007199254740991"),{start:-9007199254740991,end:9007199254740991});
});
