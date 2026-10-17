import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern33/repo/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern33/repo/src/quoted_env_values.ts";

test("quotes embedded hashes escaped values and duplicates",()=>{
  const text="export A=plain # comment\nB=\" x#y \" # outside\nC='a#b'\nD=\"one\\ntwo\\t\\\"q\\\"\"\nA=last\n";
  assert.deepEqual({...api.parseEnv(text)},{A:"last",B:" x#y ",C:"a#b",D:'one\ntwo\t"q"'});
  assert.deepEqual({...core.parseEnv("#comment\r\n EMPTY=\r\n")},{EMPTY:""});
  assert.equal(api.parseEnv("X='a\\nb'").X,"a\\nb");
});
test("malformed lines and ordinary special keys",()=>{
  for(const text of ["bad-line","1KEY=x","X=\"unclosed","X='a'junk",String.raw`X="bad\q"`])assert.throws(()=>api.parseEnv(text));
  const result=api.parseEnv("__proto__=safe\nconstructor=value"); assert.equal(Object.hasOwn(result,"__proto__"),true); assert.equal(result.__proto__,"safe");
  assert.deepEqual({...api.parseEnv("")},{});
});
