import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-1/ts-daily-editor-whitespace-word-spans/baseline/src/whitespace_word_spans.ts";
import * as api from "file:///workspace/Memglide/.local/daily-v1/corpus-validation-1/ts-daily-editor-whitespace-word-spans/baseline/src/whitespace_word_spans_api.ts";
test("Unicode punctuation single characters and precise spans",()=>{
  const text=" a 😀 café!\tb-c\nZ ";
  const spans=[{text:"a",start:1,end:2},{text:"😀",start:3,end:5},{text:"café!",start:6,end:11},{text:"b-c",start:12,end:15},{text:"Z",start:16,end:17}];
  assert.deepEqual(core.wordSpans(text),spans);assert.deepEqual(api.wordsForSelection(text),spans);
  for(const span of core.wordSpans(text))assert.equal(text.slice(span.start,span.end),span.text);
});
test("empty whitespace and detached output arrays",()=>{
  assert.deepEqual(api.wordsForSelection(""),[]);assert.deepEqual(core.wordSpans(" \t\n\u00a0"),[]);
  assert.deepEqual(api.wordsForSelection("x"),[{text:"x",start:0,end:1}]);
  const first=core.wordSpans("ab");first[0].text="changed";assert.equal(core.wordSpans("ab")[0].text,"ab");
});
