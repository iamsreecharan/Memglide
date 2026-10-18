import test from "node:test";
import assert from "node:assert/strict";
import * as api from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-complete-form-errors-r1-B/src/api.ts";
import * as core from "file:///workspace/Memglide/.local/optimization-v2/formal-40-v1/worktrees/ts2-config-complete-form-errors-r1-B/src/complete_form_errors.ts";

test("all errors stable order and no coercion",()=>{
  assert.deepEqual(api.validateSignup({email:"bad",password:"short",confirmation:"other",age:17}),["email","password","confirmation","age"]);
  assert.deepEqual(core.validateSignup({email:null,password:12345678,confirmation:12345678,age:"18"}),["email","password","confirmation","age"]);
  assert.deepEqual(api.validateSignup({email:"a@b.co",password:"short",confirmation:"short",age:120}),["password"]);
});
test("boundaries whitespace and immutability",()=>{
  const good={email:"a@b.co",password:"abcdefgh",confirmation:"abcdefgh",age:18};const before=structuredClone(good);assert.deepEqual(api.validateSignup(good),[]);assert.deepEqual(good,before);
  for(const age of [17,121,18.5,NaN])assert.deepEqual(api.validateSignup({...good,age}),["age"]);
  assert.deepEqual(api.validateSignup({...good,email:" a@b.co"}),["email"]);assert.deepEqual(api.validateSignup({...good,age:120}),[]);
});
