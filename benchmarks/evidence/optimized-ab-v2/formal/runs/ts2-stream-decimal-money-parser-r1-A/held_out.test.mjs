import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-decimal-money-parser-r1-A/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-stream-decimal-money-parser-r1-A/src/decimal_money_parser.ts";

test("decimal precision signs and safe bounds", () => {
  for (const [text, expected] of [["0.29",29],["1.13",113],["-0.29",-29],["+1.2",120],["90071992547409.91",9007199254740991],["-90071992547409.91",-9007199254740991]]) assert.equal(api.parseCents(text),expected);
  assert.equal(Object.is(core.parseCents("-0.00"),-0),false);
});
test("strict grammar and overflow", () => {
  for (const text of [" 1","1 ","1\n","1\r\n","1e2",".5","1.","1.001","NaN","90071992547409.92","-90071992547409.92",""]) assert.throws(() => api.parseCents(text));
  assert.equal(api.parseCents("0002"),200);
});
