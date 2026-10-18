import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-fragmented-ndjson-r1-A/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-fragmented-ndjson-r1-A/src/fragmented_ndjson.ts";

test("fragments CRLF empty lines and falsy values",()=>{
  const chunks=['{"id":','1}\r','\n\nfa','lse\n0\nnull\n"','hello"'];
  assert.deepEqual(api.parseNdjson(chunks),[{id:1},false,0,null,"hello"]);
  assert.deepEqual(core.parseNdjson([" ","\n","\t"]),[]);
  assert.deepEqual(api.parseNdjson([]),[]);
  assert.deepEqual(api.parseNdjson(["[1,2]\n"]),[[1,2]]);
});
test("strict malformed records and no mutation",()=>{
  for(const chunks of [['{"x":'],['{}\nnot-json\n'],['{"x":1,}\n']]) assert.throws(()=>api.parseNdjson(chunks));
  const chunks=['{"x":','1}\n']; const before=[...chunks]; assert.deepEqual(api.parseNdjson(chunks),[{x:1}]); assert.deepEqual(chunks,before);
  assert.deepEqual(api.parseNdjson(["true"]),[true]);
});
