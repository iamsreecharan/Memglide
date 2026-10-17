import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern24/repo/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/pytest-corpus-v2-final/test_all_baselines_fail_extern24/repo/src/keyed_upsert_order.ts";

test("last values first positions and special keys",()=>{
  const rows=[{key:"b",payload:1},{key:"a",payload:2},{key:"b",payload:0},{key:"__proto__",payload:false},{key:"constructor",payload:null}];
  assert.deepEqual(api.upsertRows(rows),[{key:"b",payload:0},{key:"a",payload:2},{key:"__proto__",payload:false},{key:"constructor",payload:null}]);
  assert.deepEqual(core.upsertRows([]),[]);
  assert.deepEqual(api.upsertRows([{key:"",payload:1},{key:"",payload:2}]),[{key:"",payload:2}]);
});
test("deep copy isolation",()=>{
  const rows=[{key:"a",payload:{items:[1]}}]; const result=api.upsertRows(rows); result[0].payload.items.push(2);
  assert.deepEqual(rows[0].payload,{items:[1]}); rows[0].payload.items.push(3); assert.deepEqual(result[0].payload,{items:[1,2]});
  assert.equal(rows.length,1);
});
