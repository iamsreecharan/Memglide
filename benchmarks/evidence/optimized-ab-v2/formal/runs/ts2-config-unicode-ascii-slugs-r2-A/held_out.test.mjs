import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-unicode-ascii-slugs-r2-A/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-unicode-ascii-slugs-r2-A/src/unicode_ascii_slugs.ts";

test("accents compatibility marks and punctuation",()=>{
  assert.equal(api.slugify("Crème brûlée"),"creme-brulee"); assert.equal(core.slugify("Ｆｕｌｌ １２"),"full-12");
  assert.equal(api.slugify("Cafe\u0301"),"cafe"); assert.equal(api.slugify("---a__b!!!"),"a-b"); assert.equal(api.slugify("ﬃ ①"),"ffi-1");
});
test("empty non Latin digits and stable output",()=>{
  for(const value of ["","   ","😀","東京"]) assert.equal(api.slugify(value),"");
  assert.equal(api.slugify(" A1 B2 "),"a1-b2"); assert.equal(api.slugify(api.slugify("Ångström")),"angstrom");
});
