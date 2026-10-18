import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-specific-route-matching-r2-B/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-specific-route-matching-r2-B/src/specific_route_matching.ts";

test("specificity stable ties and decoded values",()=>{
  const routes=[{id:"parameter",pattern:"/users/:id"},{id:"literal",pattern:"/users/new"},{id:"tie",pattern:"/users/:name"}];
  assert.equal(api.matchRoute(routes,"/users/new").id,"literal");const value=core.matchRoute(routes,"/users/a%20b");assert.equal(value.id,"parameter");assert.deepEqual({...value.params},{id:"a b"});
  assert.equal(api.matchRoute(routes,"/users/a/extra"),null);assert.equal(api.matchRoute(routes,"/missing/a"),null);assert.equal(routes[0].id,"parameter");
});
test("unsafe escapes literal decoding and own params",()=>{
  for(const path of ["/users/%2F","/users/%5c","/users/%GG","/users/%C0%AF"])assert.throws(()=>api.matchRoute([{id:"x",pattern:"/users/:id"}],path));
  assert.equal(api.matchRoute([{id:"x",pattern:"/café"}],"/caf%C3%A9").id,"x");
  const value=api.matchRoute([{id:"x",pattern:"/:__proto__"}],"/safe");assert.equal(Object.hasOwn(value.params,"__proto__"),true);assert.equal(value.params.__proto__,"safe");
});
