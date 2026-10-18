import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-repeated-query-values-r2-B/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-repeated-query-values-r2-B/src/repeated_query_values.ts";

test("duplicates decoding flags and equals signs",()=>{
  assert.deepEqual({...api.parseQuery("?q=a+b&q=c%2Bd&flag&x=a=b&&")},{q:["a b","c+d"],flag:[""],x:["a=b"]});
  assert.deepEqual({...core.parseQuery("a%20b=%E2%9C%93&=empty")},{"a b":["✓"],"":["empty"]});
  assert.deepEqual({...api.parseQuery("")},{});
});
test("own special keys and malformed escapes",()=>{
  const result=api.parseQuery("__proto__=a&__proto__=b&constructor=x");
  assert.equal(Object.hasOwn(result,"__proto__"),true); assert.deepEqual(result.__proto__,["a","b"]); assert.deepEqual(result.constructor,["x"]);
  for(const query of ["x=%","x=%GG","%E2=x","x=%C0%AF"]) assert.throws(()=>api.parseQuery(query));
});
