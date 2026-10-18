import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/corpus-validation-final/ts-cache-forms-required-whitespace/reference/src/required_whitespace.ts";
test("empty Unicode and ASCII whitespace",()=>{
  for(const value of [""," ","\t\r\n","\u00a0\u2003"])assert.equal(core.isRequiredBlank(value),true);
});
test("visible text zero and nontrimmed format character",()=>{
  for(const value of ["0"," false "," a ","😀","\u200b"])assert.equal(core.isRequiredBlank(value),false);
});
