import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-semantic-version-precedence-r2-B/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-semantic-version-precedence-r2-B/src/semantic_version_precedence.ts";

test("numeric core and prerelease ordering",()=>{
  const ordered=["1.0.0-alpha","1.0.0-alpha.1","1.0.0-alpha.2","1.0.0-alpha.10","1.0.0-beta","1.0.0","1.10.0","2.0.0"];
  for(let i=1;i<ordered.length;i++){assert.equal(api.compareVersions(ordered[i-1],ordered[i]),-1);assert.equal(core.compareVersions(ordered[i],ordered[i-1]),1);}
  assert.equal(api.compareVersions("1.0.0+build.1","1.0.0+different"),0);
  assert.equal(api.compareVersions("99999999999999999999.0.0","100000000000000000000.0.0"),-1);
});
test("strict syntax and numeric identifier rules",()=>{
  for(const value of ["1.0","01.0.0","1.0.0-01","1.0.0-","1.0.0+","v1.0.0","1.0.0-a..b","1.0.0\n","1.0.0\r\n"])assert.throws(()=>api.compareVersions(value,"1.0.0"));
  assert.equal(api.compareVersions("0.0.0-0","0.0.0-a"),-1);assert.equal(api.compareVersions("1.0.0-a","1.0.0-a"),0);
});
