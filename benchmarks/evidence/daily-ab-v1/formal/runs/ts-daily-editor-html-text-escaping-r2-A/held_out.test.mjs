import test from "node:test";
import assert from "node:assert/strict";
import * as core from "file:///workspace/Memglide/.local/daily-v1/formal-20-v1/worktrees/ts-daily-editor-html-text-escaping-r2-A/src/html_text_escaping.ts";
test("all five special characters escaped exactly once",()=>{
  assert.equal(core.escapeHtml(`<a title="x&y">'`),"&lt;a title=&quot;x&amp;y&quot;&gt;&#39;");
  assert.equal(core.escapeHtml("&&<<"),"&amp;&amp;&lt;&lt;");
  assert.equal(core.escapeHtml("&lt; &#39;"),"&amp;lt; &amp;#39;");
});
test("empty Unicode and plain punctuation",()=>{
  assert.equal(core.escapeHtml(""),"");assert.equal(core.escapeHtml("café 😀 / ="),"café 😀 / =");
  assert.equal(core.escapeHtml("\n\t"),"\n\t");
});
