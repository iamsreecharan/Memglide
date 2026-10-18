import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/cost-v1/formal-10-v1/worktrees/cost-ts-cost-ledger-receipt-quantity-r1-B/src/receipt_quantity.ts";
import * as api from "file:///workspace/Memglide/.local/cost-v1/formal-10-v1/worktrees/cost-ts-cost-ledger-receipt-quantity-r1-B/src/receipt_quantity_api.ts";
test("multiplication and duplicate receipt lines",()=>{
  assert.equal(core.lineTotal({unitCents:125,quantity:3}),375);
  const line={unitCents:50,quantity:2};assert.equal(api.receiptTotal([line,line]),200);
  assert.equal(api.receiptTotal([{unitCents:25,quantity:0}]),0);
});
test("invalid arithmetic and unchanged records",()=>{
  for(const line of [{unitCents:-1,quantity:2},{unitCents:1,quantity:0.5},{unitCents:Number.MAX_SAFE_INTEGER,quantity:2}])assert.throws(()=>api.receiptTotal([line]),RangeError);
  assert.throws(()=>api.receiptTotal([{unitCents:Number.MAX_SAFE_INTEGER,quantity:1},{unitCents:1,quantity:1}]),RangeError);
  const lines=Object.freeze([Object.freeze({unitCents:10,quantity:2})]);assert.equal(api.receiptTotal(lines),20);
});
