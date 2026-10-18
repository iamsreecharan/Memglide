import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-casefold-header-collection-r1-B/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-casefold-header-collection-r1-B/src/casefold_header_collection.ts";

test("duplicate names cookie order and trimmed values",()=>{
  const headers=[["X-A","1"],["Set-Cookie","a=1"],["x-a"," 2 "],["set-cookie","b=2"],["X-Z",""]];
  const result=api.collectHeaders(headers);assert.deepEqual({...result},{"x-a":["1","2"],"set-cookie":["a=1","b=2"],"x-z":[""]});
  assert.deepEqual(Object.keys(result),["x-a","set-cookie","x-z"]);assert.deepEqual({...core.collectHeaders([])},{});
  assert.equal(headers[2][1]," 2 ");
});
test("injection names and own special keys",()=>{
  for(const header of [["Bad Name","x"],["X\r\nInjected","x"],["X","a\nb"],["X","a\rb"],["","x"]])assert.throws(()=>api.collectHeaders([header]));
  const result=api.collectHeaders([["__proto__","safe"],["Constructor","value"]]);assert.equal(Object.hasOwn(result,"__proto__"),true);assert.deepEqual(result.__proto__,["safe"]);assert.deepEqual(result.constructor,["value"]);
});
