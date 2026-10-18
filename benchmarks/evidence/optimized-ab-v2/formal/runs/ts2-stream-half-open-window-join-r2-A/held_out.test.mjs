import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-half-open-window-join-r2-A/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-half-open-window-join-r2-A/src/half_open_window_join.ts";

test("half-open boundaries empty windows and pair order", () => {
  const left=[{id:"a",start:0,end:2},{id:"b",start:1,end:4},{id:"empty",start:1,end:1}];
  const right=[{id:"x",start:2,end:3},{id:"y",start:0,end:1}];
  assert.deepEqual(api.joinWindows(left,right),[{left:"a",right:"y",start:0,end:1},{left:"b",right:"x",start:2,end:3}]);
  assert.deepEqual(core.joinWindows([{id:"a",start:0,end:1}],[{id:"b",start:1,end:2}]),[]);
  assert.deepEqual(api.joinWindows([],right),[]);
});
test("nested intervals negatives validation and mutation", () => {
  const left=[{id:"a",start:-5,end:5}], right=[{id:"b",start:-1,end:1}]; const before=structuredClone([left,right]);
  assert.deepEqual(api.joinWindows(left,right),[{left:"a",right:"b",start:-1,end:1}]); assert.deepEqual([left,right],before);
  assert.throws(()=>api.joinWindows([{id:"bad",start:2,end:1}],[]));
  assert.throws(()=>api.joinWindows([],[{id:"bad",start:2,end:1}]));
});
