import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/efficiency-v1/corpus-initial-validation/ts-workflow-text-path-segment-roundtrip/baseline/src/path_segment_roundtrip.ts";
import * as api from "file:///workspace/Memglide/.local/efficiency-v1/corpus-initial-validation/ts-workflow-text-path-segment-roundtrip/baseline/src/path_segment_roundtrip_api.ts";
test("reserved characters remain data",()=>{
  assert.equal(core.encodeSegment("a/b?c#d"),"a%2Fb%3Fc%23d");
  assert.equal(api.buildPath(["a/b","?q"]),"/a%2Fb/%3Fq");
});
test("empty segments order unicode and unchanged input",()=>{
  const parts=["A","","é",""];const before=[...parts];
  assert.equal(api.buildPath(parts),"/A//%C3%A9/");assert.deepEqual(parts,before);
  assert.equal(api.buildPath([""]),"/");
});
