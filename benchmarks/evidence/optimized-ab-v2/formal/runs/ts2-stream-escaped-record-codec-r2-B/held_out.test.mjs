import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-escaped-record-codec-r2-B/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-escaped-record-codec-r2-B/src/escaped_record_codec.ts";

test("escaped delimiters backslashes and empty fields",()=>{
  assert.deepEqual(api.decodeRecord(String.raw`a\|b|c`),["a|b","c"]);
  assert.deepEqual(core.decodeRecord(String.raw`a\\|b`),["a\\","b"]);
  assert.deepEqual(api.decodeRecord("|a||"),["","a","",""]);
  assert.deepEqual(api.decodeRecord(""),[""]);
  assert.deepEqual(api.decodeRecord("é|😀"),["é","😀"]);
});
test("invalid escapes and repeated escaped separators",()=>{
  assert.throws(()=>api.decodeRecord("a\\")); assert.throws(()=>api.decodeRecord(String.raw`a\q`));
  assert.deepEqual(api.decodeRecord(String.raw`\|\|`),["||"]);
  assert.deepEqual(api.decodeRecord(String.raw`\\\\`),["\\\\"]);
});
