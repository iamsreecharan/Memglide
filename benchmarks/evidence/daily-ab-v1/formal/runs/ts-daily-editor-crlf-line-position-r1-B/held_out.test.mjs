import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/formal-20-v1/worktrees/ts-daily-editor-crlf-line-position-r1-B/src/crlf_line_position.ts";
test("mixed newlines and offsets inside CRLF",()=>{
  const text="a\r\nb\rc\nd";
  const expected=[[0,0],[0,1],[1,0],[1,0],[1,1],[2,0],[2,1],[3,0],[3,1]];
  for(let offset=0;offset<=text.length;offset++) assert.deepEqual(core.lineColumn(text,offset),{line:expected[offset][0],column:expected[offset][1]});
  assert.deepEqual(core.lineColumn("\r\n\r\n",4),{line:2,column:0});
});
test("UTF16 offsets empty input and invalid offsets",()=>{
  assert.deepEqual(core.lineColumn("😀x",2),{line:0,column:2});
  assert.deepEqual(core.lineColumn("",0),{line:0,column:0});
  for(const offset of [-1,2,0.5,NaN,Infinity])assert.throws(()=>core.lineColumn("a",offset));
});
