import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/efficiency-v1/corpus-v2-tests-final-tmp/test_new_regression_file_allow1/repo/src/luhn_checksum.ts";
test("alternating doubling and reduction",()=>{
  assert.equal(core.luhnCheck("4111111111111111"),true);
  assert.equal(core.luhnCheck("4111111111111112"),false);
  assert.equal(core.luhnCheck("18"),true);
});
test("leading zeros parity and strict syntax",()=>{
  assert.equal(core.luhnCheck("0018"),true);assert.equal(core.luhnCheck("00018"),true);
  assert.equal(core.luhnCheck("79927398713"),true);assert.equal(core.luhnCheck("18x"),false);
  assert.equal(core.luhnCheck("１８"),false);
});
