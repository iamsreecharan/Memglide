import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cache-v2/corpus-validation-final/ts-cache-forms-strict-calendar-date/baseline/src/strict_calendar_date.ts";
test("month lengths leap centuries and small years",()=>{
  for(const parts of [[2025,2,29],[2024,2,30],[2025,4,31],[1900,2,29]])assert.equal(core.validDateParts(...parts),false);
  for(const parts of [[2024,2,29],[2000,2,29],[4,2,29],[99,1,1],[9999,12,31]])assert.equal(core.validDateParts(...parts),true);
});
test("integer bounds and nonfinite inputs",()=>{
  for(const parts of [[0,1,1],[10000,1,1],[2025,0,1],[2025,13,1],[2025,1,0],[2025,1,32],[2025,1,1.5],[NaN,1,1],[2025,Infinity,1]])assert.equal(core.validDateParts(...parts),false);
});
