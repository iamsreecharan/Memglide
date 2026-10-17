import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern31/repo/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern31/repo/src/safe_local_redirects.ts";

test("origin includes scheme and port",()=>{
  for(const target of ["http://app.example/a","https://app.example:444/a","//evil.example/a","https://user:pass@app.example/a","javascript:alert(1)"]) assert.throws(()=>api.localRedirect("https://app.example/base",target));
  assert.equal(core.localRedirect("https://APP.example:443/a","https://app.example/b?x=1#top"),"/b?x=1#top");
  assert.equal(api.localRedirect("http://app.example:8080/a","http://app.example:8080/b"),"/b");
});
test("relative normalization malformed URL and encoding",()=>{
  assert.equal(api.localRedirect("https://app.example/a/b","../c%20d?q=%2F#x"),"/c%20d?q=%2F#x");
  assert.equal(api.localRedirect("https://app.example/a","?q=1"),"/a?q=1");
  assert.throws(()=>api.localRedirect("https://user@app.example/a","https://app.example/b")); assert.throws(()=>api.localRedirect("file:///tmp/a","b")); assert.throws(()=>api.localRedirect("https://app.example/a","http://[broken"));
});
