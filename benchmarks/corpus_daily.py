"""Fresh ordinary coding tasks and independent, external behavioral oracles.

All task source scopes are disclosed in the common prompts. Four tasks also
include their complete relevant source. Reference fixes and hidden assertions
never enter an agent worktree; that separation is procedural, not a sandbox.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Any

from benchmarks.corpus import _command

CORPUS_VERSION = "daily-1.0.0"
REPOSITORIES = {
    "desk-python-daily": ("python", "desk"),
    "catalog-python-daily": ("python", "catalog"),
    "editor-typescript-daily": ("typescript", "editor"),
    "inventory-typescript-daily": ("typescript", "inventory"),
}
SPECS: list[dict[str, Any]] = []


def _clean(source: str) -> str:
    return textwrap.dedent(source).strip("\n") + "\n"


def _add(
    repository: str,
    slug: str,
    function: str,
    request: str,
    source: str,
    replacements: dict[str, str],
    smoke: str,
    cases: str,
    *,
    adapter: str | None = None,
    adapter_replacements: dict[str, str] | None = None,
    supplied: bool = False,
) -> None:
    baseline = _clean(source)
    reference = baseline
    for old, new in replacements.items():
        if reference.count(old) != 1:
            raise ValueError(f"nonunique domain reference edit: {slug}: {old!r}")
        reference = reference.replace(old, new)
    adapter_baseline = _clean(adapter) if adapter is not None else None
    adapter_reference = adapter_baseline
    for old, new in (adapter_replacements or {}).items():
        if adapter_reference is None or adapter_reference.count(old) != 1:
            raise ValueError(f"nonunique adapter reference edit: {slug}: {old!r}")
        adapter_reference = adapter_reference.replace(old, new)
    SPECS.append(
        {
            "repository": repository,
            "slug": slug,
            "function": function,
            "request": request,
            "baseline": baseline,
            "reference": reference,
            "adapter_baseline": adapter_baseline,
            "adapter_reference": adapter_reference,
            "supplied": supplied,
            "smoke": smoke,
            "cases": _clean(cases),
        }
    )


_add(
    "desk-python-daily",
    "elapsed-clock",
    "format_elapsed",
    "Fix format_elapsed(seconds) so elapsed hours do not wrap at 24. Return H:MM:SS, with unpadded hours and exactly two minute/second digits. Continue rejecting negative values, bools and non-integers with ValueError.",
    '''
    def format_elapsed(seconds):
        """Format a nonnegative elapsed duration, rather than a time of day."""
        if type(seconds) is not int or seconds < 0:
            raise ValueError("nonnegative integer seconds required")
        hours = (seconds // 3600) % 24
        minutes = (seconds // 60) % 60
        return f"{hours}:{minutes:02d}:{seconds % 60:02d}"
    ''',
    {"hours = (seconds // 3600) % 24": "hours = seconds // 3600"},
    'self.assertEqual(core.format_elapsed(3661), "1:01:01")',
    """
    def test_long_durations_and_boundaries(self):
        for seconds, expected in ((0,"0:00:00"),(59,"0:00:59"),(60,"0:01:00"),(86400,"24:00:00"),(90061,"25:01:01"),(3600000001,"1000000:00:01")):
            self.assertEqual(core.format_elapsed(seconds), expected)
    def test_invalid_values(self):
        for value in (-1, True, False, 1.5, "60", None):
            with self.assertRaises(ValueError): core.format_elapsed(value)
    """,
)

_add(
    "desk-python-daily",
    "rectangular-transpose",
    "transpose",
    "Fix transpose(rows) to reject ragged rows with ValueError instead of silently discarding cells. Keep [] -> [] and equally empty rows -> []; return fresh row lists without mutating the input or requiring numeric cells.",
    '''
    def transpose(rows):
        """Transpose a rectangular list of row lists."""
        if not rows:
            return []
        return [list(column) for column in zip(*rows)]
    ''',
    {
        "        return []\n    return": '        return []\n    if any(len(row) != len(rows[0]) for row in rows):\n        raise ValueError("ragged rows")\n    return'
    },
    "self.assertEqual(core.transpose([[1,2],[3,4]]), [[1,3],[2,4]])",
    """
    def test_ragged_and_empty_shapes(self):
        for rows in ([[1,2],[3]], [[],[1]], [[1],[]]):
            with self.assertRaises(ValueError): core.transpose(rows)
        self.assertEqual(core.transpose([]), [])
        self.assertEqual(core.transpose([[],[]]), [])
    def test_values_and_no_input_mutation(self):
        rows = [["a",None],[False,0]]
        result = core.transpose(rows)
        self.assertEqual(result, [["a",False],[None,0]])
        result[0].append("new")
        self.assertEqual(rows, [["a",None],[False,0]])
        self.assertEqual(core.transpose([[1,2,3]]), [[1],[2],[3]])
    """,
)

_add(
    "desk-python-daily",
    "calendar-month-shift",
    "shift_month",
    "Repair shift_month(date, months) and the move_due_date adapter. Add signed whole calendar months, clamping the day to the destination month's last day; preserve datetime.date output. Require a date (not datetime) and an integer month delta (not bool), raising ValueError otherwise. The adapter must forward the requested delta unchanged, including zero and negatives. Preserve the public DueItem and reschedule_due_items batch workflow: batch results must apply that same behavior, retain item IDs and order, deeply detach metadata, and leave input records unchanged.",
    '''
    import calendar
    from datetime import date, datetime

    def shift_month(value, months):
        """Move a date by calendar months, clamping a day such as January 31."""
        if not isinstance(value, date) or isinstance(value, datetime) or type(months) is not int:
            raise ValueError("date and integer month delta required")
        year, month0 = divmod(value.year * 12 + value.month - 1 + months, 12)
        return date(year, month0 + 1, value.day)
    ''',
    {
        "return date(year, month0 + 1, value.day)": "return date(year, month0 + 1, min(value.day, calendar.monthrange(year, month0 + 1)[1]))"
    },
    'self.assertEqual(api.reschedule_due_items([api.DueItem("a",date(2025,1,15))],1), [api.DueItem("a",date(2025,2,15))])',
    """
    def test_month_end_and_negative_deltas(self):
        self.assertEqual(core.shift_month(date(2024,1,31),1), date(2024,2,29))
        self.assertEqual(core.shift_month(date(2025,3,31),-1), date(2025,2,28))
        self.assertEqual(api.move_due_date(date(2025,5,15),-3), date(2025,2,15))
        self.assertEqual(api.move_due_date(date(2025,5,15),0), date(2025,5,15))
        self.assertEqual(api.move_due_date(date(2024,2,29),12), date(2025,2,28))
        items=[api.DueItem("a",date(2024,1,31)),api.DueItem("b",date(2025,3,31))]
        self.assertEqual([item.due for item in api.reschedule_due_items(items,1)],[date(2024,2,29),date(2025,4,30)])
        self.assertEqual([item.due for item in api.reschedule_due_items(items,-1)],[date(2023,12,31),date(2025,2,28)])
        self.assertEqual([item.due for item in api.reschedule_due_items(items,0)],[item.due for item in items])
    def test_types_and_year_rollover(self):
        self.assertEqual(core.shift_month(date(2025,1,1),-1), date(2024,12,1))
        self.assertEqual(api.move_due_date(date(2025,1,1),24), date(2027,1,1))
        for value, months in ((datetime(2025,1,1),1),(date(2025,1,1),True),(date(2025,1,1),1.5),("2025-01-01",1)):
            with self.assertRaises(ValueError): core.shift_month(value, months)
            with self.assertRaises(ValueError): api.move_due_date(value, months)
        item=api.DueItem("keep-id",date(2025,5,15),{"labels":["original"]})
        result=api.reschedule_due_items(iter([item]),2)
        self.assertEqual([entry.item_id for entry in result],["keep-id"])
        self.assertIsNot(result[0],item)
        result[0].metadata["labels"].append("new")
        self.assertEqual(item.metadata,{"labels":["original"]})
        self.assertEqual(item.due,date(2025,5,15))
        self.assertEqual(api.reschedule_due_items([],1),[])
    """,
    adapter='''
    from collections.abc import Iterable
    from copy import deepcopy
    from dataclasses import dataclass, field
    from datetime import date

    from .calendar_month_shift import shift_month

    @dataclass(frozen=True)
    class DueItem:
        """Reminder data shared by individual and batch edit screens."""

        item_id: str
        due: date
        metadata: dict[str, object] = field(default_factory=dict)

    def move_due_date(value, months):
        """Expose calendar shifting to the reminder screen."""
        return shift_month(value, 1 if months <= 0 else months)

    def reschedule_due_items(items: Iterable[DueItem], months: int) -> list[DueItem]:
        """Create a detached reminder batch without rewriting caller records."""
        return [
            DueItem(item.item_id, move_due_date(item.due, months), deepcopy(item.metadata))
            for item in items
        ]
    ''',
    adapter_replacements={"1 if months <= 0 else months": "months"},
)

_add(
    "desk-python-daily",
    "export-line-endings",
    "join_lines",
    "Repair join_lines(lines, *, newline='\\n', final_newline=True) and export_notes. Accept newline '\\n' or '\\r\\n' only; join the supplied string lines using that separator and append one separator iff final_newline is true and lines is nonempty. Empty input returns ''. Reject embedded CR or LF in any line and invalid separators with ValueError. export_notes must forward the requested newline and final_newline options, including false, without rewriting lines.",
    '''
    def join_lines(lines, *, newline="\\n", final_newline=True):
        """Export logical lines without adding line ending characters to data."""
        if newline not in ("\\n", "\\r\\n") or any("\\r" in line or "\\n" in line for line in lines):
            raise ValueError("invalid line or separator")
        if not lines:
            return ""
        return newline.join(lines) + newline
    ''',
    {
        "return newline.join(lines) + newline": 'return newline.join(lines) + (newline if final_newline else "")'
    },
    'self.assertEqual(api.export_notes(["a","b"]), "a\\nb\\n")',
    """
    def test_false_option_and_crlf_forwarding(self):
        self.assertEqual(core.join_lines(["a","b"],final_newline=False), "a\\nb")
        self.assertEqual(api.export_notes(["a","b"],newline="\\r\\n",final_newline=False), "a\\r\\nb")
        self.assertEqual(api.export_notes(["a"],newline="\\r\\n"), "a\\r\\n")
        self.assertEqual(api.export_notes([],newline="\\r\\n"), "")
    def test_blank_lines_validation_and_immutability(self):
        lines=["", "x", ""]
        self.assertEqual(core.join_lines(lines), "\\nx\\n\\n")
        self.assertEqual(lines,["", "x", ""])
        for separator in ("", "\\r", "--"):
            with self.assertRaises(ValueError): api.export_notes(["x"],newline=separator)
        for line in ("a\\nb","a\\rb"):
            with self.assertRaises(ValueError): core.join_lines([line])
            with self.assertRaises(ValueError): api.export_notes([line])
    """,
    adapter='''
    from .export_line_endings import join_lines

    def export_notes(lines, *, newline="\\n", final_newline=True):
        """Build a downloadable text note."""
        return join_lines(lines, final_newline=final_newline)
    ''',
    adapter_replacements={
        "return join_lines(lines, final_newline=final_newline)": "return join_lines(lines, newline=newline, final_newline=final_newline)"
    },
)

_add(
    "desk-python-daily",
    "label-ellipsis",
    "truncate_label",
    "Fix the tiny truncation bug in truncate_label: the returned label must fit within limit Unicode code points, counting the single ellipsis character. Leave strings of length <= limit unchanged; limit=0 returns ''. Keep the existing invalid-limit validation.",
    '''
    def truncate_label(value, limit):
        """Fit a label to a code-point width, using one ellipsis if shortened."""
        if type(limit) is not int or limit < 0:
            raise ValueError("nonnegative integer limit required")
        if limit == 0:
            return ""
        if len(value) <= limit:
            return value
        return value[:limit] + "…"
    ''',
    {'return value[:limit] + "…"': 'return value[:limit - 1] + "…"'},
    'self.assertEqual(core.truncate_label("abc",3), "abc")',
    """
    def test_exact_width_and_small_limits(self):
        self.assertEqual(core.truncate_label("abcdef",4), "abc…")
        self.assertEqual(core.truncate_label("abcdef",1), "…")
        self.assertEqual(core.truncate_label("abcdef",0), "")
        self.assertEqual(core.truncate_label("",0), "")
    def test_unicode_and_invalid_limits(self):
        self.assertEqual(core.truncate_label("a😀bc",3), "a😀…")
        self.assertEqual(core.truncate_label("abc",9), "abc")
        for limit in (-1, True, 1.5, "2"):
            with self.assertRaises(ValueError): core.truncate_label("abcdef",limit)
    """,
    supplied=True,
)

_add(
    "catalog-python-daily",
    "relative-indentation",
    "dedent_lines",
    "Fix dedent_lines(lines) to remove only the common ASCII-space indentation of nonblank lines, preserving relative indentation. Whitespace-only lines become empty strings; an all-blank or empty input returns the corresponding empty-string list. Do not mutate the supplied list. Inputs consist of strings using ASCII spaces for indentation.",
    '''
    def dedent_lines(lines):
        """Remove a shared left margin while preserving nested indentation."""
        return [line.lstrip(" ") for line in lines]
    ''',
    {
        'return [line.lstrip(" ") for line in lines]': 'nonblank = [line for line in lines if line.strip(" ")]\n    margin = min((len(line) - len(line.lstrip(" ")) for line in nonblank), default=0)\n    return [line[margin:] if line.strip(" ") else "" for line in lines]'
    },
    'self.assertEqual(core.dedent_lines(["  a","  b"]), ["a","b"])',
    """
    def test_relative_indentation_and_blank_lines(self):
        self.assertEqual(core.dedent_lines(["  root","    child"," ","   peer"]),["root","  child",""," peer"])
        self.assertEqual(core.dedent_lines(["root","    child"]),["root","    child"])
        self.assertEqual(core.dedent_lines(["   "," ",""]),["","",""])
    def test_new_list_and_empty_input(self):
        lines=["   a", "     b"]
        result=core.dedent_lines(lines)
        self.assertEqual(result,["a","  b"])
        self.assertEqual(lines,["   a","     b"])
        self.assertIsNot(result,lines)
        self.assertEqual(core.dedent_lines([]),[])
    """,
)

_add(
    "catalog-python-daily",
    "single-pass-partition",
    "partition",
    "Fix partition(items, predicate) so it evaluates predicate exactly once per item in input order, splitting into (accepted, rejected) lists. Preserve relative order in each list and leave the input list unchanged. Support one-shot iterable inputs and propagate predicate exceptions unchanged.",
    '''
    def partition(items, predicate):
        """Separate items using one decision per input item."""
        return ([item for item in items if predicate(item)],
                [item for item in items if not predicate(item)])
    ''',
    {
        "return ([item for item in items if predicate(item)],\n            [item for item in items if not predicate(item)])": "accepted, rejected = [], []\n    for item in items:\n        (accepted if predicate(item) else rejected).append(item)\n    return accepted, rejected"
    },
    "self.assertEqual(core.partition([1,2,3],lambda n:n%2==0), ([2],[1,3]))",
    """
    def test_one_decision_in_order_and_iterators(self):
        seen=[]
        def predicate(value):
            seen.append(value)
            return len(seen)%2==1
        self.assertEqual(core.partition(iter([1,2,3,4]),predicate),([1,3],[2,4]))
        self.assertEqual(seen,[1,2,3,4])
        calls=[]
        self.assertEqual(core.partition([2,1],lambda x:calls.append(x) or x==2),([2],[1]))
        self.assertEqual(calls,[2,1])
    def test_input_empty_and_error_identity(self):
        values=[1,2,1]
        self.assertEqual(core.partition(values,lambda x:x==1),([1,1],[2]))
        self.assertEqual(values,[1,2,1])
        self.assertEqual(core.partition([],lambda x:True),([],[]))
        error=RuntimeError("predicate")
        def fail(value): raise error
        with self.assertRaises(RuntimeError) as caught: core.partition([1],fail)
        self.assertIs(caught.exception,error)
    """,
)

_add(
    "catalog-python-daily",
    "tag-normalization",
    "normalize_tags",
    "Repair normalize_tags and tags_for_card. Trim each supplied string, discard empty strings, Unicode-casefold each tag, and remove duplicates while preserving the first surviving appearance. tags_for_card receives an iterable of complete tag strings, not comma-separated text: preserve commas inside a tag. Do not change the supplied list. Preserve CatalogCard, normalize_card_tags and cards_for_export: normalize each card through tags_for_card once, retain its ID/title/metadata and card order, and deeply detach exported metadata and normalized tag lists from inputs.",
    '''
    def normalize_tags(tags):
        """Produce stable normalized tags for a catalog card."""
        return [tag.strip().lower() for tag in tags if tag.strip()]
    ''',
    {
        "return [tag.strip().lower() for tag in tags if tag.strip()]": "result = []\n    seen = set()\n    for tag in tags:\n        normalized = tag.strip().casefold()\n        if normalized and normalized not in seen:\n            seen.add(normalized)\n            result.append(normalized)\n    return result"
    },
    'self.assertEqual(api.cards_for_export([api.CatalogCard("a","Card",[" Blue ","green"])])[0]["tags"], ["blue","green"])',
    """
    def test_dedup_casefold_and_stable_order(self):
        self.assertEqual(core.normalize_tags([" B ","a","b"," A ","ß","SS"," "]),["b","a","ss"])
        self.assertEqual(api.tags_for_card(["a,b","C","A,B"]),["a,b","c"])
        self.assertEqual(api.tags_for_card([" Straße ","STRASSE"]),["strasse"])
        cards=[api.CatalogCard("b","Second",[" B ","b","a,b"]),api.CatalogCard("a","First",["Straße","STRASSE"])]
        self.assertEqual(api.cards_for_export(cards),[{"id":"b","title":"Second","tags":["b","a,b"],"metadata":{}},{"id":"a","title":"First","tags":["strasse"],"metadata":{}}])
    def test_one_shot_input_and_no_mutation(self):
        values=[" One ","ONE","two"]
        self.assertEqual(api.tags_for_card(values),["one","two"])
        self.assertEqual(values,[" One ","ONE","two"])
        self.assertEqual(core.normalize_tags(iter([" X ","x",""])),["x"])
        self.assertEqual(api.tags_for_card([]),[])
        from unittest.mock import patch
        card=api.CatalogCard("id","Title",[" A ","a"],{"info":{"values":[1]}})
        with patch.object(api,"tags_for_card",wraps=api.tags_for_card) as called:
            exported=api.cards_for_export(iter([card]))
            self.assertEqual(called.call_count,1)
        exported[0]["tags"].append("new")
        exported[0]["metadata"]["info"]["values"].append(2)
        self.assertEqual(card.tags,[" A ","a"])
        self.assertEqual(card.metadata,{"info":{"values":[1]}})
        self.assertEqual(api.cards_for_export([]),[])
    """,
    adapter='''
    from collections.abc import Iterable
    from copy import deepcopy
    from dataclasses import dataclass, field

    from .tag_normalization import normalize_tags

    @dataclass(frozen=True)
    class CatalogCard:
        """Card data shared by the editor and offline export workflow."""

        card_id: str
        title: str
        tags: list[str]
        metadata: dict[str, object] = field(default_factory=dict)

    def tags_for_card(tags):
        """Accept complete tags from the card editor."""
        return normalize_tags(piece for tag in tags for piece in tag.split(","))

    def normalize_card_tags(card: CatalogCard) -> CatalogCard:
        """Normalize tags without altering the editor's card or metadata."""
        return CatalogCard(card.card_id, card.title, tags_for_card(card.tags), deepcopy(card.metadata))

    def cards_for_export(cards: Iterable[CatalogCard]) -> list[dict[str, object]]:
        """Build ordered JSON-compatible export records from editor state."""
        result = []
        for card in cards:
            normalized = normalize_card_tags(card)
            result.append({
                "id": normalized.card_id,
                "title": normalized.title,
                "tags": normalized.tags,
                "metadata": normalized.metadata,
            })
        return result
    ''',
    adapter_replacements={
        'normalize_tags(piece for tag in tags for piece in tag.split(","))': "normalize_tags(tags)"
    },
)

_add(
    "catalog-python-daily",
    "strict-column-projection",
    "select_columns",
    "Repair select_columns(row, columns) and export_row. Return a new dict containing exactly the requested columns in request order, including keys whose value is None, False, 0 or ''. A genuinely missing column raises KeyError; do not replace it with None or drop explicit null values. Inputs must remain unchanged, and values need not be deep-copied.",
    '''
    def select_columns(row, columns):
        """Project existing columns without interpreting their values."""
        return {name: row.get(name) for name in columns}
    ''',
    {"row.get(name)": "row[name]"},
    'self.assertEqual(api.export_row({"a":1,"b":2},["b"]), {"b":2})',
    """
    def test_missing_is_distinct_from_present_null(self):
        for operation in (core.select_columns,api.export_row):
            with self.assertRaises(KeyError): operation({"a":None},["missing"])
        self.assertEqual(api.export_row({"a":None,"b":0,"c":False,"d":""},["d","a","b","c"]),{"d":"","a":None,"b":0,"c":False})
        self.assertEqual(list(api.export_row({"a":None,"b":1},["b","a"])),["b","a"])
    def test_no_input_changes_and_empty_selection(self):
        row={"a":[1],"b":2};columns=["a"]
        result=api.export_row(row,columns)
        self.assertIsNot(result,row)
        self.assertIs(result["a"],row["a"])
        self.assertEqual(row,{"a":[1],"b":2})
        self.assertEqual(columns,["a"])
        self.assertEqual(core.select_columns(row,[]),{})
    """,
    adapter='''
    from .strict_column_projection import select_columns

    def export_row(row, columns):
        """Project the selected columns for an export."""
        return {name: value for name, value in select_columns(row, columns).items() if value is not None}
    ''',
    adapter_replacements={
        "return {name: value for name, value in select_columns(row, columns).items() if value is not None}": "return select_columns(row, columns)"
    },
)

_add(
    "catalog-python-daily",
    "saturday-weekend",
    "is_weekend",
    "Fix is_weekend(weekday): weekdays follow Python's Monday=0 through Sunday=6 convention, so both Saturday (5) and Sunday (6) are weekends. Keep the existing integer-range validation.",
    '''
    def is_weekend(weekday):
        """Return whether a Monday-zero weekday falls on the weekend."""
        if type(weekday) is not int or not 0 <= weekday <= 6:
            raise ValueError("weekday must be an integer from 0 to 6")
        return weekday == 6
    ''',
    {"return weekday == 6": "return weekday >= 5"},
    "self.assertTrue(core.is_weekend(6))",
    """
    def test_all_seven_days(self):
        self.assertEqual([core.is_weekend(day) for day in range(7)],[False,False,False,False,False,True,True])
        self.assertIs(core.is_weekend(5),True)
    def test_invalid_days(self):
        for day in (-1,7,True,False,5.0,"5",None):
            with self.assertRaises(ValueError): core.is_weekend(day)
    """,
    supplied=True,
)

_add(
    "editor-typescript-daily",
    "crlf-line-position",
    "lineColumn",
    "Fix lineColumn(text, offset) for CRLF and bare CR newlines as well as LF. Return zero-based {line,column} at a UTF-16 offset, requiring an integer offset 0..text.length. A CRLF is one newline: positions immediately after its CR and after its LF both have column 0 on the new line. Other characters, including surrogate pairs, advance by UTF-16 code units. Invalid offsets throw.",
    """
    export function lineColumn(text: string, offset: number): {line: number; column: number} {
      if (!Number.isInteger(offset) || offset < 0 || offset > text.length) throw new Error("invalid offset");
      let line = 0, column = 0;
      for (let index = 0; index < offset; index++) {
        if (text[index] === "\\n") { line++; column = 0; }
        else column++;
      }
      return {line, column};
    }
    """,
    {
        'if (text[index] === "\\n") { line++; column = 0; }\n    else column++;': 'if (text[index] === "\\r") { line++; column = 0; }\n    else if (text[index] === "\\n") { if (index === 0 || text[index - 1] !== "\\r") line++; column = 0; }\n    else column++;'
    },
    'assert.deepEqual(core.lineColumn("ab\\nc",4),{line:1,column:1})',
    r"""
    test("mixed newlines and offsets inside CRLF",()=>{
      const text="a\r\nb\rc\nd";
      const expected=[[0,0],[0,1],[1,0],[1,0],[1,1],[2,0],[2,1],[3,0],[3,1]];
      for(let offset=0;offset<=text.length;offset++) assert.deepEqual(core.lineColumn(text,offset),{line:expected[offset][0],column:expected[offset][1]});
      assert.deepEqual(core.lineColumn("\r\n\r\n",4),{line:2,column:0});
    });
    test("UTF16 offsets empty input and invalid offsets",()=>{
      assert.deepEqual(core.lineColumn("😀x",2),{line:0,column:2});
      assert.deepEqual(core.lineColumn("",0),{line:0,column:0});
      for(const offset of [-1,2,0.5,NaN,Infinity])assert.throws(()=>core.lineColumn("a",offset));
    });
    """,
)

_add(
    "editor-typescript-daily",
    "html-text-escaping",
    "escapeHtml",
    "Fix escapeHtml(text) for insertion as HTML text or a quoted attribute: escape &, <, >, double quote and apostrophe as &amp;, &lt;, &gt;, &quot; and &#39;. Escape each original character once: already entity-looking input is still plain text, so '&lt;' becomes '&amp;lt;'. Preserve other characters.",
    """
    export function escapeHtml(text: string): string {
      return text.replaceAll("<", "&lt;").replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;").replaceAll("'", "&#39;").replaceAll("&", "&amp;");
    }
    """,
    {
        'return text.replaceAll("<", "&lt;").replaceAll(">", "&gt;")\n    .replaceAll(\'"\', "&quot;").replaceAll("\'", "&#39;").replaceAll("&", "&amp;");': 'return text.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")\n    .replaceAll(\'"\', "&quot;").replaceAll("\'", "&#39;");'
    },
    'assert.equal(core.escapeHtml("hello"),"hello")',
    r"""
    test("all five special characters escaped exactly once",()=>{
      assert.equal(core.escapeHtml(`<a title="x&y">'`),"&lt;a title=&quot;x&amp;y&quot;&gt;&#39;");
      assert.equal(core.escapeHtml("&&<<"),"&amp;&amp;&lt;&lt;");
      assert.equal(core.escapeHtml("&lt; &#39;"),"&amp;lt; &amp;#39;");
    });
    test("empty Unicode and plain punctuation",()=>{
      assert.equal(core.escapeHtml(""),"");assert.equal(core.escapeHtml("café 😀 / ="),"café 😀 / =");
      assert.equal(core.escapeHtml("\n\t"),"\n\t");
    });
    """,
)

_add(
    "editor-typescript-daily",
    "literal-replace-all",
    "replaceLiteral",
    "Repair replaceLiteral(text, needle, replacement) and applyReplacement. Replace every non-overlapping literal occurrence of the nonempty needle; metacharacters and '$' are ordinary data in both needle and replacement. Reject an empty needle. The adapter must preserve whitespace in the needle instead of trimming it. Leave unmatched text unchanged. Preserve Replacement, previewReplacement and replaceBatch: previews must delegate to applyReplacement, report before/after/changed accurately and retain batch order without changing request objects.",
    """
    export function replaceLiteral(text: string, needle: string, replacement: string): string {
      if (needle.length === 0) throw new Error("empty needle");
      return text.replace(needle, replacement);
    }
    """,
    {"return text.replace(needle, replacement);": "return text.split(needle).join(replacement);"},
    'assert.deepEqual(api.replaceBatch([{text:"abc",needle:"b",replacement:"X"}]),[{before:"abc",after:"aXc",changed:true}])',
    r"""
    test("all literal occurrences and replacement metacharacters",()=>{
      assert.equal(core.replaceLiteral("a.a.a",".","$&"),"a$&a$&a");
      assert.equal(core.replaceLiteral("aaaaa","aa","x"),"xxa");
      assert.equal(api.applyReplacement("a a a"," ","_"),"a_a_a");
      assert.equal(api.applyReplacement(".x.x",".x","$1"),"$1$1");
      assert.deepEqual(api.replaceBatch([{text:"a a a",needle:" ",replacement:"$&"},{text:".x.x",needle:".x",replacement:"$1"}]),[{before:"a a a",after:"a$&a$&a",changed:true},{before:".x.x",after:"$1$1",changed:true}]);
    });
    test("empty needle whitespace and unchanged strings",()=>{
      assert.throws(()=>core.replaceLiteral("abc","","x"));
      assert.throws(()=>api.applyReplacement("abc","","x"));
      assert.equal(api.applyReplacement(" a  "," ",""),"a");
      assert.equal(core.replaceLiteral("😀ab😀","😀","é"),"éabé");
      assert.equal(api.applyReplacement("abc","z","x"),"abc");
      const request={text:"a a",needle:" ",replacement:"_"};const before=structuredClone(request);
      assert.deepEqual(api.previewReplacement(request),{before:"a a",after:"a_a",changed:true});assert.deepEqual(request,before);
      assert.deepEqual(api.previewReplacement({text:"abc",needle:"z",replacement:"x"}),{before:"abc",after:"abc",changed:false});
      assert.throws(()=>api.replaceBatch([{text:"a",needle:"",replacement:"x"}]));assert.deepEqual(api.replaceBatch([]),[]);
    });
    """,
    adapter="""
    import {replaceLiteral} from "./literal_replace_all.ts";

    export function applyReplacement(text: string, needle: string, replacement: string): string {
      return replaceLiteral(text, needle.trim(), replacement);
    }

    export type Replacement = {text: string; needle: string; replacement: string};
    export type ReplacementPreview = {before: string; after: string; changed: boolean};

    export function previewReplacement(request: Readonly<Replacement>): ReplacementPreview {
      const after = applyReplacement(request.text, request.needle, request.replacement);
      return {before: request.text, after, changed: after !== request.text};
    }

    export function replaceBatch(requests: ReadonlyArray<Readonly<Replacement>>): ReplacementPreview[] {
      return requests.map(request => previewReplacement(request));
    }
    """,
    adapter_replacements={"needle.trim()": "needle"},
)

_add(
    "editor-typescript-daily",
    "whitespace-word-spans",
    "wordSpans",
    "Repair wordSpans(text) and wordsForSelection. A word is a maximal run of non-whitespace characters according to JavaScript /\\s/; punctuation, Unicode letters, emoji and single-character words are included. Return {text,start,end} with UTF-16 offsets and exclusive end, in source order. The adapter must return every span without dropping one-character words. Empty or whitespace-only input returns [].",
    r"""
    export type WordSpan = {text: string; start: number; end: number};
    export function wordSpans(text: string): WordSpan[] {
      return Array.from(text.matchAll(/\w+/g), match => ({text: match[0], start: match.index!, end: match.index! + match[0].length}));
    }
    """,
    {r"/\w+/g": r"/\S+/g"},
    'assert.deepEqual(api.wordsForSelection("hello world").map(span=>span.text),["hello","world"])',
    r"""
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
    """,
    adapter="""
    import {wordSpans} from "./whitespace_word_spans.ts";
    import type {WordSpan} from "./whitespace_word_spans.ts";

    export function wordsForSelection(text: string): WordSpan[] {
      return wordSpans(text).filter(span => span.text.length > 1);
    }
    """,
    adapter_replacements={
        "wordSpans(text).filter(span => span.text.length > 1)": "wordSpans(text)"
    },
)

_add(
    "editor-typescript-daily",
    "inclusive-clamp",
    "clamp",
    "Fix clamp(value,min,max) to clamp to the inclusive bounds: a value equal to or above max returns max. Retain finite-number and ordered-bound validation, and preserve fractional values inside the range.",
    """
    export function clamp(value: number, min: number, max: number): number {
      if (![value,min,max].every(Number.isFinite) || min > max) throw new Error("invalid bounds");
      if (value < min) return min;
      if (value >= max) return max - 1;
      return value;
    }
    """,
    {"return max - 1;": "return max;"},
    "assert.equal(core.clamp(5,0,10),5)",
    """
    test("inclusive ends fractional and equal bounds",()=>{
      assert.equal(core.clamp(10,0,10),10);assert.equal(core.clamp(11,0,10),10);
      assert.equal(core.clamp(-1,0,10),0);assert.equal(core.clamp(2.5,0,10),2.5);
      assert.equal(core.clamp(1,3,3),3);assert.equal(core.clamp(8,3,3),3);
    });
    test("negative ranges and invalid numbers",()=>{
      assert.equal(core.clamp(0,-10,-2),-2);assert.equal(core.clamp(-20,-10,-2),-10);
      for(const args of [[NaN,0,1],[0,1,0],[0,-Infinity,1],[0,0,Infinity]]) assert.throws(()=>core.clamp(...args));
    });
    """,
    supplied=True,
)

_add(
    "inventory-typescript-daily",
    "numeric-median",
    "median",
    "Fix median(values) to compute the numeric median: sort numerically, average the two middle values for even lengths, and leave the input array unchanged. Reject an empty array or any nonfinite number. Inputs and outputs may be fractional or negative.",
    """
    export function median(values: number[]): number {
      if (values.length === 0 || values.some(value => !Number.isFinite(value))) throw new Error("finite values required");
      const sorted = values.sort();
      return sorted[Math.floor(sorted.length / 2)];
    }
    """,
    {
        "const sorted = values.sort();\n  return sorted[Math.floor(sorted.length / 2)];": "const sorted = [...values].sort((left, right) => left - right);\n  const middle = Math.floor(sorted.length / 2);\n  if (sorted.length % 2) return sorted[middle];\n  const lower = sorted[middle - 1], upper = sorted[middle];\n  const sum = lower + upper;\n  return Number.isFinite(sum) ? sum / 2 : lower / 2 + upper / 2;"
    },
    "assert.equal(core.median([1,2,3]),2)",
    """
    test("numeric ordering even lengths and fractions",()=>{
      assert.equal(core.median([2,10,3]),3);assert.equal(core.median([4,1,3,2]),2.5);
      assert.equal(core.median([-5,-1,-3,-2]),-2.5);assert.equal(core.median([1.25]),1.25);
      assert.equal(core.median([Number.MAX_VALUE,Number.MAX_VALUE]),Number.MAX_VALUE);
      assert.equal(core.median([Number.MIN_VALUE,Number.MIN_VALUE]),Number.MIN_VALUE);
      assert.equal(core.median([Number.MIN_VALUE,Number.MIN_VALUE*2]),Number.MIN_VALUE*2);
    });
    test("immutable input and validation",()=>{
      const values=[10,2,1];const before=[...values];assert.equal(core.median(values),2);assert.deepEqual(values,before);
      for(const values of [[],[NaN],[1,Infinity],[-Infinity,1]])assert.throws(()=>core.median(values));
    });
    """,
)

_add(
    "inventory-typescript-daily",
    "chunk-without-empty-tail",
    "chunk",
    "Fix chunk(items,size) so empty input returns [] and an exact multiple of size does not create an empty trailing chunk. Return consecutive fresh subarrays, preserving values and order without changing the input. Continue rejecting nonpositive or noninteger sizes.",
    """
    export function chunk<T>(items: T[], size: number): T[][] {
      if (!Number.isInteger(size) || size <= 0) throw new Error("positive integer size required");
      const result: T[][] = [];
      for (let offset = 0; offset <= items.length; offset += size) result.push(items.slice(offset, offset + size));
      return result;
    }
    """,
    {"offset <= items.length": "offset < items.length"},
    "assert.deepEqual(core.chunk([1,2,3],2),[[1,2],[3]])",
    """
    test("empty exact multiples and oversize chunks",()=>{
      assert.deepEqual(core.chunk([],2),[]);assert.deepEqual(core.chunk([1,2,3,4],2),[[1,2],[3,4]]);
      assert.deepEqual(core.chunk([1,2],1),[[1],[2]]);assert.deepEqual(core.chunk([1],5),[[1]]);
    });
    test("new containers order and invalid sizes",()=>{
      const input=["a","b","c"];const output=core.chunk(input,2);output[0].push("new");assert.deepEqual(input,["a","b","c"]);
      assert.deepEqual(core.chunk([false,null,0,""],3),[[false,null,0],[""]]);
      for(const size of [0,-1,1.5,NaN,Infinity])assert.throws(()=>core.chunk([1],size));
    });
    """,
)

_add(
    "inventory-typescript-daily",
    "signed-code-padding",
    "padCode",
    "Repair padCode(value,width) and labelCode. Format an integer in base ten, padding with zeros after any minus sign until the total string width reaches width; never truncate a longer value. Require a safe integer value and nonnegative integer width. labelCode must preserve zero, not substitute 1. Examples: padCode(-7,4)='-007', labelCode(0,3)='000'.",
    """
    export function padCode(value: number, width: number): string {
      if (!Number.isSafeInteger(value) || !Number.isInteger(width) || width < 0) throw new Error("integer value and width required");
      return String(value).padStart(width, "0");
    }
    """,
    {
        'return String(value).padStart(width, "0");': 'const sign = value < 0 ? "-" : "";\n  return sign + String(Math.abs(value)).padStart(Math.max(0, width - sign.length), "0");'
    },
    'assert.equal(api.labelCode(7,3),"007")',
    """
    test("sign position zero and short widths",()=>{
      assert.equal(core.padCode(-7,4),"-007");assert.equal(api.labelCode(0,3),"000");
      assert.equal(api.labelCode(-12,5),"-0012");assert.equal(core.padCode(-123,2),"-123");
      assert.equal(api.labelCode(123,0),"123");assert.equal(core.padCode(0,0),"0");
    });
    test("validation and normal values",()=>{
      assert.equal(api.labelCode(42,4),"0042");assert.equal(core.padCode(Number.MAX_SAFE_INTEGER,1),String(Number.MAX_SAFE_INTEGER));
      for(const args of [[1.2,3],[1,-1],[1,0.5],[Infinity,2],[Number.MAX_SAFE_INTEGER+1,2]]) {
        assert.throws(()=>core.padCode(...args));assert.throws(()=>api.labelCode(...args));
      }
    });
    """,
    adapter="""
    import {padCode} from "./signed_code_padding.ts";

    export function labelCode(value: number, width: number): string {
      return padCode(value || 1, width);
    }
    """,
    adapter_replacements={"value || 1": "value"},
)

_add(
    "inventory-typescript-daily",
    "equal-length-zip",
    "zipEqual",
    "Repair zipEqual(left,right) and pairColumns. Pair corresponding elements into fresh two-element tuples only when array lengths match; mismatched lengths in either direction must throw. The public adapter must pass both complete arrays through so a mismatch cannot be hidden by truncation. Preserve both inputs, including falsy elements; empty pairs return []. Preserve NamedColumn, PairedTable and pairTable: table headers must retain the two nonempty distinct column names, rows must use pairColumns, and output containers must be independent of input column objects and arrays.",
    """
    export function zipEqual<L,R>(left: L[], right: R[]): [L,R][] {
      return left.map((value, index) => [value, right[index]]);
    }
    """,
    {
        "  return left.map": '  if (left.length !== right.length) throw new Error("length mismatch");\n  return left.map'
    },
    'assert.deepEqual(api.pairTable({name:"label",values:["a","b"]},{name:"count",values:[1,2]}),{headers:["label","count"],rows:[["a",1],["b",2]]})',
    """
    test("both mismatch directions and empty arrays",()=>{
      for(const [left,right] of [[[1],[2,3]],[[1,2],[3]],[[],[1]],[[1],[]]]) {
        assert.throws(()=>core.zipEqual(left,right));assert.throws(()=>api.pairColumns(left,right));
        assert.throws(()=>api.pairTable({name:"left",values:left},{name:"right",values:right}));
      }
      assert.deepEqual(api.pairColumns([],[]),[]);
      assert.deepEqual(api.pairTable({name:"left",values:[]},{name:"right",values:[]}),{headers:["left","right"],rows:[]});
    });
    test("values order and fresh tuple containers",()=>{
      const left=[0,false,""],right=[null,2,3];const result=api.pairColumns(left,right);
      assert.deepEqual(result,[[0,null],[false,2],["",3]]);result[0][0]="changed";
      assert.deepEqual(left,[0,false,""]);assert.deepEqual(right,[null,2,3]);
      assert.deepEqual(core.zipEqual(["x"],[false]),[["x",false]]);
      const a={name:"left",values:[0,false,""]},b={name:"right",values:[null,2,3]};const before=structuredClone([a,b]);
      const table=api.pairTable(a,b);assert.deepEqual(table,{headers:["left","right"],rows:[[0,null],[false,2],["",3]]});
      table.headers[0]="changed";table.rows[0][0]="changed";assert.deepEqual([a,b],before);
      for(const [leftName,rightName] of [["","right"],["left",""],["same","same"]])assert.throws(()=>api.pairTable({name:leftName,values:[]},{name:rightName,values:[]}));
    });
    """,
    adapter="""
    import {zipEqual} from "./equal_length_zip.ts";

    export function pairColumns<L,R>(left: L[], right: R[]): [L,R][] {
      return zipEqual(left, right.slice(0, left.length));
    }

    export type NamedColumn<T> = {name: string; values: T[]};
    export type PairedTable<L,R> = {headers: [string,string]; rows: [L,R][]};

    export function pairTable<L,R>(left: NamedColumn<L>, right: NamedColumn<R>): PairedTable<L,R> {
      if (left.name.length === 0 || right.name.length === 0 || left.name === right.name) {
        throw new Error("nonempty distinct column names required");
      }
      return {headers: [left.name, right.name], rows: pairColumns(left.values, right.values)};
    }
    """,
    adapter_replacements={"right.slice(0, left.length)": "right"},
)

_add(
    "inventory-typescript-daily",
    "zero-count-plural",
    "pluralize",
    "Fix pluralize(count,singular,plural) to choose singular only when count is exactly 1; zero uses plural. Keep the existing validation that count is a nonnegative integer. Return the supplied word unchanged, including empty/custom words.",
    """
    export function pluralize(count: number, singular: string, plural: string): string {
      if (!Number.isInteger(count) || count < 0) throw new Error("nonnegative count required");
      return count <= 1 ? singular : plural;
    }
    """,
    {"count <= 1": "count === 1"},
    'assert.equal(core.pluralize(2,"item","items"),"items")',
    """
    test("zero one many and supplied words",()=>{
      assert.equal(core.pluralize(0,"item","items"),"items");assert.equal(core.pluralize(1,"child","children"),"child");
      assert.equal(core.pluralize(9,"child","children"),"children");assert.equal(core.pluralize(0,"x",""),"");
    });
    test("invalid counts",()=>{
      for(const count of [-1,0.5,NaN,Infinity]) assert.throws(()=>core.pluralize(count,"item","items"));
      assert.equal(core.pluralize(1000000,"one","many"),"many");
    });
    """,
    supplied=True,
)


def _task_id(spec: dict[str, Any]) -> str:
    language, family = REPOSITORIES[spec["repository"]]
    return f"{'py' if language == 'python' else 'ts'}-daily-{family}-{spec['slug']}"


def _spec(task_id: str) -> dict[str, Any]:
    for spec in SPECS:
        if _task_id(spec) == task_id:
            return spec
    raise ValueError(f"unknown task: {task_id}")


def _source_paths(spec: dict[str, Any]) -> list[str]:
    language, family = REPOSITORIES[spec["repository"]]
    directory, suffix = (family, "py") if language == "python" else ("src", "ts")
    module = spec["slug"].replace("-", "_")
    paths = [f"{directory}/{module}.{suffix}"]
    if spec["adapter_baseline"] is not None:
        paths.append(f"{directory}/{module}_api.{suffix}")
    return paths


def task_definitions() -> list[dict[str, Any]]:
    tasks = []
    for spec in SPECS:
        language, _ = REPOSITORIES[spec["repository"]]
        paths = _source_paths(spec)
        scope = "\n".join(f"- `{path}`" for path in paths)
        prompt = f"{spec['request']}\n\nThe source scope explicitly supplied for this task is:\n{scope}\n"
        if spec["supplied"]:
            prompt += "\nComplete current source for that scope is supplied below; it is sufficient context for this tiny fix:\n"
            prompt += f"\nFile: `{paths[0]}`\n```{language}\n{spec['baseline']}```\n"
        command = (
            "python -m unittest discover -s tests -v"
            if language == "python"
            else "node --test tests/*.test.mjs"
        )
        prompt += (
            f"\nImplement the fix in production source. Run the existing offline smoke tests with `{command}` "
            "and add regression tests if useful. Preserve public interfaces and existing tests. "
            "Do not change dependencies, build configuration, benchmark machinery or grading files, "
            "and do not inspect files outside this repository. Finish with a brief description and tests run."
        )
        tasks.append(
            {
                "id": _task_id(spec),
                "language": language,
                "repository": spec["repository"],
                "starting_repository": {
                    "generator": "benchmarks.corpus_daily.build_repository",
                    "repository": spec["repository"],
                    "version": CORPUS_VERSION,
                },
                "prompt": prompt,
                "focus_paths": paths,
                "target_files": paths,
                "expected_symbols": [spec["function"]],
                "context_supplied": spec["supplied"],
                "task_kind": "supplied-context"
                if spec["supplied"]
                else "integration"
                if len(paths) == 2
                else "single-source",
                "oracle_id": spec["slug"],
                "checks": {
                    "held_out_behavior": True,
                    "protected_smoke": True,
                    "typescript_typecheck": language == "typescript",
                },
            }
        )
    return tasks


def _repository_files(repository_id: str) -> dict[str, str]:
    if repository_id not in REPOSITORIES:
        raise ValueError(f"unsupported repository: {repository_id}")
    language, family = REPOSITORIES[repository_id]
    specs = [spec for spec in SPECS if spec["repository"] == repository_id]
    files = {}
    for spec in specs:
        paths = _source_paths(spec)
        files[paths[0]] = spec["baseline"]
        if len(paths) == 2:
            files[paths[1]] = spec["adapter_baseline"]
    command = (
        "python -m unittest discover -s tests -v"
        if language == "python"
        else "node --test tests/*.test.mjs"
    )
    files["README.md"] = _clean(f"""
        # {family.title()} utilities

        Small offline {language} utilities used by an everyday application.
        Production modules have local adapters only where a caller needs one.
        Run existing ordinary-use smoke tests with `{command}`.
    """)
    files["AGENTS.md"] = _clean(f"""
        # Development
        Work in this checkout and keep tests offline and deterministic.
        Run `{command}`. Preserve public interfaces and existing tests.
        Do not modify dependency/build configuration or inspect benchmark
        machinery, grading artifacts or files outside this repository.
    """)
    files[".gitignore"] = "__pycache__/\n*.pyc\nnode_modules/\n.cache/\n"
    if language == "python":
        files[f"{family}/__init__.py"] = f'"""Offline {family} utilities."""\n'
        smoke = (
            "import unittest\nfrom datetime import date\n\nclass SmokeTests(unittest.TestCase):\n"
        )
        for spec in specs:
            module = spec["slug"].replace("-", "_")
            smoke += (
                f"    def test_{module}(self):\n        from {family} import {module} as core\n"
            )
            if spec["adapter_baseline"] is not None:
                smoke += f"        from {family} import {module}_api as api\n"
            smoke += f"        {spec['smoke']}\n\n"
        files["tests/test_smoke.py"] = smoke
    else:
        files["package.json"] = (
            json.dumps(
                {
                    "name": repository_id,
                    "private": True,
                    "type": "module",
                    "scripts": {"test": command},
                },
                indent=2,
            )
            + "\n"
        )
        files["tsconfig.json"] = (
            json.dumps(
                {
                    "compilerOptions": {
                        "target": "ES2022",
                        "module": "NodeNext",
                        "moduleResolution": "NodeNext",
                        "allowImportingTsExtensions": True,
                        "noEmit": True,
                        "strict": True,
                        "skipLibCheck": True,
                        "types": [],
                    },
                    "include": ["src/**/*.ts"],
                },
                indent=2,
            )
            + "\n"
        )
        smoke = 'import test from "node:test";\nimport assert from "node:assert/strict";\n'
        for index, spec in enumerate(specs):
            paths = _source_paths(spec)
            smoke += f'import * as core{index} from "../{paths[0]}";\n'
            if len(paths) == 2:
                smoke += f'import * as api{index} from "../{paths[1]}";\n'
            statement = (
                spec["smoke"].replace("core.", f"core{index}.").replace("api.", f"api{index}.")
            )
            smoke += f"test({json.dumps(spec['slug'])},()=>{{{statement};}});\n"
        files["tests/smoke.test.mjs"] = smoke
    return files


def build_repository(repository_id: str, destination: Path) -> None:
    files = _repository_files(repository_id)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("destination must be empty")
    for relative, content in files.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _oracle(spec: dict[str, Any], worktree: Path) -> str:
    language, family = REPOSITORIES[spec["repository"]]
    paths = _source_paths(spec)
    if language == "python":
        module = spec["slug"].replace("-", "_")
        source = "import json, unittest\nfrom datetime import date, datetime\n"
        source += f"from {family} import {module} as core\n"
        if len(paths) == 2:
            source += f"from {family} import {module}_api as api\n"
        source += "\nclass BehaviorTests(unittest.TestCase):\n" + textwrap.indent(
            spec["cases"], "    "
        )
        source += _clean("""
            if __name__ == "__main__":
                suite = unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
                result = unittest.TextTestRunner(verbosity=2).run(suite)
                print("CORPUS_RESULT=" + json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
                raise SystemExit(not result.wasSuccessful())
        """)
        return source
    source = 'import test from "node:test";\nimport assert from "node:assert/strict";\n'
    source += f"import * as core from {json.dumps((worktree / paths[0]).resolve().as_uri())};\n"
    if len(paths) == 2:
        source += f"import * as api from {json.dumps((worktree / paths[1]).resolve().as_uri())};\n"
    return source + spec["cases"]


def _test_execution_integrity(command: dict[str, Any], language: str, stage: str) -> dict[str, Any]:
    """Require actual clean test completion, not merely an exit-zero process."""
    counts = command["counts"]
    total = counts.get("tests")
    count_valid = type(total) is int and (total == 2 if stage == "behavior" else total >= 5)
    if language == "typescript":
        required = ("tests", "pass", "fail", "cancelled", "skipped")
        clean = (
            all(type(counts.get(key)) is int for key in required)
            and counts["pass"] == total
            and all(counts[key] == 0 for key in ("fail", "cancelled", "skipped"))
        )
        summary_verified = clean
    else:
        stderr_path = command.get("stderr_path")
        stderr = Path(stderr_path).read_text(encoding="utf-8") if stderr_path else ""
        # unittest's decorated OK summaries include skipped/expected failures.
        # Only an undecorated OK is a clean, fully executed suite.
        summary_verified = re.search(r"^OK$", stderr, re.MULTILINE) is not None
        required = ("tests", "failures", "errors", "skipped")
        clean = summary_verified and (
            stage == "smoke"
            or (
                all(type(counts.get(key)) is int for key in required)
                and all(counts[key] == 0 for key in ("failures", "errors", "skipped"))
            )
        )
    return {
        "stage": stage,
        "valid": command["exit_code"] == 0 and count_valid and clean,
        "required_test_count": {"exact": 2} if stage == "behavior" else {"minimum": 5},
        "reported_counts": dict(counts),
        "count_requirement_met": count_valid,
        "clean_summary_verified": summary_verified,
        "zero_failures_errors_skips_cancellations": clean,
    }


def grade(task_id: str, worktree: Path, artifacts: Path) -> dict[str, Any]:
    spec = _spec(task_id)
    language, family = REPOSITORIES[spec["repository"]]
    worktree, artifacts = Path(worktree).resolve(), Path(artifacts).resolve()
    if artifacts == worktree or worktree in artifacts.parents:
        raise ValueError("grading artifacts must be outside the agent worktree")
    artifacts.mkdir(parents=True, exist_ok=True)
    protected = []
    source_prefix = family + "/" if language == "python" else "src/"
    for relative, content in _repository_files(spec["repository"]).items():
        if relative.startswith(source_prefix):
            continue
        path = worktree / relative
        actual = path.read_bytes() if path.is_file() and not path.is_symlink() else b""
        expected = content.encode("utf-8")
        protected.append(
            {
                "file": relative,
                "unchanged": actual == expected,
                "expected_sha256": hashlib.sha256(expected).hexdigest(),
                "actual_sha256": hashlib.sha256(actual).hexdigest(),
            }
        )
    environment = dict(os.environ)
    commands = []
    if language == "python":
        environment.update(PYTHONPATH=str(worktree), PYTHONDONTWRITEBYTECODE="1")
        oracle = artifacts / "held_out.py"
        oracle.write_text(_oracle(spec, worktree), encoding="utf-8")
        commands.append(
            _command([sys.executable, str(oracle)], worktree, artifacts / "behavior", environment)
        )
        commands.append(
            _command(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                worktree,
                artifacts / "smoke",
                environment,
            )
        )
    else:
        node = shutil.which("node")
        if node is None:
            raise RuntimeError("Node with native TypeScript support is required")
        oracle = artifacts / "held_out.test.mjs"
        oracle.write_text(_oracle(spec, worktree), encoding="utf-8")
        commands.append(
            _command(
                [node, "--test", "--test-reporter=tap", str(oracle)],
                worktree,
                artifacts / "behavior",
                environment,
            )
        )
        commands.append(
            _command(
                [node, "--test", "--test-reporter=tap", "tests/smoke.test.mjs"],
                worktree,
                artifacts / "smoke",
                environment,
            )
        )
        local = Path(__file__).resolve().parents[1] / "frontend/node_modules/typescript/bin/tsc"
        compiler = os.environ.get("MEMGLIDE_BENCHMARK_TSC") or (
            str(local) if local.is_file() else shutil.which("tsc")
        )
        if compiler is None:
            commands.append(
                {
                    "command": ["tsc", "--project", "tsconfig.json"],
                    "exit_code": None,
                    "counts": {},
                    "unavailable_reason": "TypeScript compiler not installed",
                }
            )
        else:
            commands.append(
                _command(
                    [node, compiler, "--project", "tsconfig.json"],
                    worktree,
                    artifacts / "typecheck",
                    environment,
                )
            )
    execution_checks = [
        _test_execution_integrity(commands[0], language, "behavior"),
        _test_execution_integrity(commands[1], language, "smoke"),
    ]
    execution_complete = all(item["valid"] for item in execution_checks)
    tamper_free = all(item["unchanged"] for item in protected)
    passed = tamper_free and execution_complete and all(item["exit_code"] == 0 for item in commands)
    result = {
        "task_id": task_id,
        "repository": spec["repository"],
        "corpus_version": CORPUS_VERSION,
        "passed": passed,
        "success": passed,
        "exit_code": 0 if passed else 1,
        "commands": commands,
        "test_count": sum(item["counts"].get("tests", 0) for item in commands),
        "protected_files_unchanged": tamper_free,
        "protected_files": protected,
        "test_execution_complete": execution_complete,
        "test_execution_integrity": execution_checks,
        "grading_separation": "held-out files outside worktree; not cryptographically hidden",
    }
    (artifacts / "grade.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def _apply_reference_fix(task_id: str, destination: Path, *, side: str = "both") -> None:
    spec = _spec(task_id)
    paths = _source_paths(spec)
    if side not in ("both", "domain", "adapter"):
        raise ValueError("unsupported reference side")
    if side != "adapter":
        (destination / paths[0]).write_text(spec["reference"], encoding="utf-8")
    if side != "domain" and len(paths) == 2:
        (destination / paths[1]).write_text(spec["adapter_reference"], encoding="utf-8")


def validate_corpus(destination: Path) -> dict[str, Any]:
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("validation destination must be empty")
    results = []
    for task in task_definitions():
        root = destination / task["id"]
        build_repository(task["repository"], root / "baseline")
        build_repository(task["repository"], root / "reference")
        baseline = grade(task["id"], root / "baseline", root / "baseline_grade")
        _apply_reference_fix(task["id"], root / "reference")
        reference = grade(task["id"], root / "reference", root / "reference_grade")
        controls = []
        if task["task_kind"] == "integration":
            for side in ("domain", "adapter"):
                worktree = root / side
                build_repository(task["repository"], worktree)
                _apply_reference_fix(task["id"], worktree, side=side)
                partial = grade(task["id"], worktree, root / f"{side}_grade")
                controls.append(
                    {
                        "side": side,
                        "result": partial,
                        "correctly_rejected": not partial["success"]
                        and partial["protected_files_unchanged"]
                        and all(command["exit_code"] == 0 for command in partial["commands"][1:]),
                    }
                )
        valid = (
            not baseline["success"]
            and baseline["commands"][0]["exit_code"] != 0
            and baseline["commands"][0]["counts"].get("tests") == 2
            and all(command["exit_code"] == 0 for command in baseline["commands"][1:])
            and baseline["protected_files_unchanged"]
            and reference["success"]
            and reference["test_count"] == 7
            and all(control["correctly_rejected"] for control in controls)
        )
        results.append(
            {
                "task_id": task["id"],
                "valid": valid,
                "baseline": baseline,
                "reference": reference,
                "half_fix_controls": controls,
            }
        )
        print(json.dumps({"task_id": task["id"], "valid": valid}), flush=True)
    report = {
        "corpus_version": CORPUS_VERSION,
        "task_count": len(results),
        "half_fix_controls": sum(len(row["half_fix_controls"]) for row in results),
        "valid": all(row["valid"] for row in results),
        "tasks": results,
    }
    (destination / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", type=Path)
    parser.add_argument("--validate", type=Path)
    args = parser.parse_args()
    if args.write_manifest:
        args.write_manifest.write_text(
            json.dumps({"corpus_version": CORPUS_VERSION, "tasks": task_definitions()}, indent=2)
            + "\n",
            encoding="utf-8",
        )
    if args.validate:
        report = validate_corpus(args.validate)
        print(json.dumps({"valid": report["valid"], "task_count": report["task_count"]}))
        raise SystemExit(not report["valid"])
