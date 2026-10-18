import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/formal-formats-20-v1/worktrees/fmt-ts-cache-forms-hex-color-lengths-r1-A/src/hex_color_lengths.ts";
test("only supported lengths and ASCII hexadecimal",()=>{
  for(const value of ["#abc","#ABCD","#a1b2c3","#12345678"])assert.equal(core.isHexColor(value),true);
  for(const value of ["#ab","#abcde","#abcdefg","#1234567","#123456789","#ggg","abc"])assert.equal(core.isHexColor(value),false);
});
test("strict complete input and empty text",()=>{
  for(const value of [""," #abc","#abc ","#abc\n","#abc\r\n","#abc\u2028","#abc\u2029","#abc\u00a0","#１２３"])assert.equal(core.isHexColor(value),false);
});
