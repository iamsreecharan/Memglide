import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/efficiency-v1/corpus-v2-controls/ts-workflow2-coordinates-bounded-cardinal-neighbors/reference/src/bounded_cardinal_neighbors.ts";
import * as api from "file:///workspace/Memglide/.local/efficiency-v1/corpus-v2-controls/ts-workflow2-coordinates-bounded-cardinal-neighbors/reference/src/bounded_cardinal_neighbors_api.ts";
test("grid edges and singleton dimensions",()=>{
  assert.deepEqual(core.gridNeighbors(0,0,2,2),[[1,0],[0,1]]);
  assert.deepEqual(core.gridNeighbors(0,0,1,1),[]);
  assert.deepEqual(core.gridNeighbors(0,1,1,3),[[0,0],[0,2]]);
});
test("blocked neighbors order and set preservation",()=>{
  const blocked=new Set(["0,1","1,0"]);const before=[...blocked];
  assert.deepEqual(api.reachableNeighbors(1,1,3,3,blocked),[[2,1],[1,2]]);
  assert.deepEqual([...blocked],before);assert.deepEqual(api.reachableNeighbors(0,0,2,2,new Set(["1,0"])),[[0,1]]);
});
