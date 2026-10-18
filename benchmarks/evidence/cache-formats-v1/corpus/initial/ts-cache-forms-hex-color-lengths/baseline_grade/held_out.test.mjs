import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/corpus-validation/ts-cache-forms-hex-color-lengths/baseline/src/hex_color_lengths.ts";
test("only supported lengths and ASCII hexadecimal",()=>{
  for(const value of ["#abc","#ABCD","#a1b2c3","#12345678"])assert.equal(core.isHexColor(value),true);
  for(const value of ["#ab","#abcde","#abcdefg","#1234567","#123456789","#ggg","abc"])assert.equal(core.isHexColor(value),false);
});
test("strict complete input and empty text",()=>{
  for(const value of [""," #abc","#abc ","#abc\n","#abc\r\n","#１２３"])assert.equal(core.isHexColor(value),false);
});
