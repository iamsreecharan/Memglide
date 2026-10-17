import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern36/repo/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern36/repo/src/utf8_feature_cohorts.ts";

test("UTF8 reference vectors and strict threshold",()=>{
  function expectedBucket(user,salt){let hash=2166136261;for(const byte of Buffer.from(salt+":"+user,"utf8"))hash=Number((BigInt(hash^byte)*16777619n)&0xffffffffn)>>>0;return hash%10000;}
  for(const [user,salt] of [["é","v1"],["😀","salt"],["東京","β"],["alice","v1"],["",""]]){
    const bucket=expectedBucket(user,salt);assert.equal(api.inCohort(user,salt,bucket),false);assert.equal(core.inCohort(user,salt,bucket+1),true);
  }
});
test("rate extremes determinism and validation",()=>{
  assert.equal(api.inCohort("user","salt",0),false);assert.equal(api.inCohort("user","salt",10000),true);
  assert.equal(api.inCohort("user","salt",5000),api.inCohort("user","salt",5000));
  for(const rate of [-1,10001,1.5,NaN,Infinity])assert.throws(()=>api.inCohort("a","b",rate));
});
