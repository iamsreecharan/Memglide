"""Fresh forty-task coding corpus with independent, external behavioral oracles.

These four synthetic repositories are new material, not renamed Atlas tasks.
Reference implementations and assertions are never copied into model worktrees.
The separation is procedural, not a host filesystem security boundary.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Any

from benchmarks.corpus import _command

CORPUS_VERSION = "2.0.0"
REPOSITORIES = {
    "ledger-python-v2": ("python", "ledger"),
    "workflow-python-v2": ("python", "workflow"),
    "stream-typescript-v2": ("typescript", "stream"),
    "config-typescript-v2": ("typescript", "config"),
}
SPECS: list[dict[str, Any]] = []


def _clean(value: str) -> str:
    return textwrap.dedent(value).lstrip("\n").rstrip() + "\n"


def _add(
    repository: str,
    slug: str,
    function: str,
    signature: str,
    request: str,
    baseline: str,
    reference: str,
    smoke: str,
    cases: str,
) -> None:
    if REPOSITORIES[repository][0] == "typescript":
        # JavaScript's $ also matches before a final newline. These contracts
        # require complete input consumption, including newline rejection.
        baseline = baseline.replace("$/", r"$(?![\s\S])/")
        reference = reference.replace("$/", r"$(?![\s\S])/")
    SPECS.append(
        {
            "repository": repository,
            "slug": slug,
            "function": function,
            "signature": signature,
            "request": request,
            "baseline": _clean(baseline),
            "reference": _clean(reference),
            "smoke": smoke,
            "cases": _clean(cases),
        }
    )


_add(
    "ledger-python-v2",
    "weighted-allocation",
    "allocate",
    "total, weights",
    "Distribute nonnegative integer cents using largest remainders: floor each proportional share, then award leftover cents by descending remainder and original index for ties. Reject negative/non-integer amounts or weights and zero total weight; preserve input. Both the ledger module and public API must agree.",
    """
     def allocate(total, weights):
         if type(total) is not int or total < 0 or not weights or any(type(w) is not int or w < 0 for w in weights) or sum(weights) == 0:
             raise ValueError("invalid allocation")
         return [total * w // sum(weights) for w in weights]
     """,
    """
     def allocate(total, weights):
         if type(total) is not int or total < 0 or not weights or any(type(w) is not int or w < 0 for w in weights) or sum(weights) == 0:
             raise ValueError("invalid allocation")
         denominator = sum(weights)
         shares = [total * w // denominator for w in weights]
         order = sorted(range(len(weights)), key=lambda i: (-(total * weights[i] % denominator), i))
         for i in order[:total - sum(shares)]:
             shares[i] += 1
         return shares
     """,
    "self.assertEqual(api.allocate(6, [1, 2]), [2, 4])",
    r"""
     def test_remainders_and_conservation(self):
         self.assertEqual(api.allocate(5, [1, 1, 1]), [2, 2, 1])
         self.assertEqual(core.allocate(11, [0, 2, 1]), [0, 7, 4])
         self.assertEqual(sum(api.allocate(10**19 + 7, [3, 5, 9])), 10**19 + 7)
     def test_validation_and_immutability(self):
         weights = [1, 3, 2]
         self.assertEqual(api.allocate(0, weights), [0, 0, 0])
         self.assertEqual(weights, [1, 3, 2])
         for total, values in ((-1, [1]), (True, [1]), (1, [0, 0]), (1, [-1, 2]), (1, [1.5]), (1, [])):
             with self.assertRaises(ValueError): api.allocate(total, values)
     """,
)

_add(
    "ledger-python-v2",
    "signed-tax-rounding",
    "tax_cents",
    "amount, basis_points",
    "Compute tax in integer cents at a nonnegative integer basis-point rate (0 through 10000). Round the rational result to nearest cent with exact halves away from zero, including refunds. Reject booleans and non-integers. Keep integer accuracy for large amounts.",
    """
     def tax_cents(amount, basis_points):
         if type(amount) is not int or type(basis_points) is not int or not 0 <= basis_points <= 10000:
             raise ValueError("invalid money or rate")
         return amount * basis_points // 10000
     """,
    """
     def tax_cents(amount, basis_points):
         if type(amount) is not int or type(basis_points) is not int or not 0 <= basis_points <= 10000:
             raise ValueError("invalid money or rate")
         numerator = abs(amount) * basis_points
         value = numerator // 10000 + (2 * (numerator % 10000) >= 10000)
         return -value if amount < 0 else value
     """,
    "self.assertEqual(api.tax_cents(1000, 1000), 100)",
    r"""
     def test_refunds_half_ties_and_large_integers(self):
         for amount, rate, expected in ((5,1000,1),(-5,1000,-1),(-4,1000,0),(15,1000,2),(-15,1000,-2),(10**20+5,1000,10**19+1)):
             self.assertEqual(api.tax_cents(amount, rate), expected)
             self.assertEqual(core.tax_cents(amount, rate), expected)
     def test_rates_and_types(self):
         self.assertEqual(api.tax_cents(-123, 10000), -123)
         self.assertEqual(api.tax_cents(11, 0), 0)
         for args in ((True,1),(1,True),(1,-1),(1,10001),(1.5,50)):
             with self.assertRaises(ValueError): api.tax_cents(*args)
     """,
)

_add(
    "ledger-python-v2",
    "atomic-transfer",
    "transfer",
    "balances, source, destination, amount",
    "Make transfers atomic. Require distinct existing account IDs, a positive integer amount (not bool), and sufficient source funds. Any invalid request raises ValueError before either balance changes. Successful transfer mutates the supplied balance mapping once and returns a detached snapshot.",
    """
     def transfer(balances, source, destination, amount):
         if type(amount) is not int or amount <= 0 or source == destination or source not in balances or destination not in balances:
             raise ValueError("invalid transfer")
         balances[source] -= amount
         if balances[source] < 0:
             raise ValueError("insufficient funds")
         balances[destination] += amount
         return balances
     """,
    """
     def transfer(balances, source, destination, amount):
         if type(amount) is not int or amount <= 0 or source == destination or source not in balances or destination not in balances:
             raise ValueError("invalid transfer")
         if balances[source] < amount:
             raise ValueError("insufficient funds")
         balances[source] -= amount
         balances[destination] += amount
         return dict(balances)
     """,
    'self.assertEqual(api.transfer({"a": 5, "b": 0}, "a", "b", 2), {"a": 3, "b": 2})',
    r"""
     def test_failure_has_no_partial_write(self):
         for args in (("a","b",6),("a","missing",1),("a","a",1),("a","b",True),("a","b",0)):
             balances = {"a":5,"b":2}
             with self.assertRaises(ValueError): api.transfer(balances, *args)
             self.assertEqual(balances, {"a":5,"b":2})
     def test_snapshot_and_exact_drain(self):
         balances = {"a":5,"b":2}
         result = core.transfer(balances,"a","b",5)
         self.assertEqual(balances,{"a":0,"b":7})
         result["a"] = 999
         self.assertEqual(balances["a"],0)
     """,
)

_add(
    "ledger-python-v2",
    "statement-timezones",
    "statement",
    "records, start, end",
    "Select statement records in the half-open interval [start,end), comparing instants across timezone offsets. Accept only timezone-aware datetime objects in bounds and record timestamps, reject reversed bounds, sort chronologically with stable ties, and return deeply detached records without changing inputs.",
    """
     from copy import deepcopy
     from datetime import datetime
     def statement(records, start, end):
         if any(not isinstance(value,datetime) or value.utcoffset() is None for value in [start,end]+[r["at"] for r in records]) or start > end:
             raise ValueError("aware ordered datetimes required")
         return sorted([deepcopy(r) for r in records if start <= r["at"] <= end], key=lambda r: r["at"])
     """,
    """
     from copy import deepcopy
     from datetime import datetime
     def statement(records, start, end):
         if any(not isinstance(value,datetime) or value.utcoffset() is None for value in [start,end]+[r["at"] for r in records]) or start > end:
             raise ValueError("aware ordered datetimes required")
         return sorted([deepcopy(r) for r in records if start <= r["at"] < end], key=lambda r: r["at"])
     """,
    "self.assertEqual(api.statement([], datetime(2026,1,1,tzinfo=timezone.utc), datetime(2026,1,2,tzinfo=timezone.utc)), [])",
    r"""
     def test_half_open_offsets_and_stability(self):
         start = datetime.fromisoformat("2026-01-01T00:00:00+00:00")
         end = datetime.fromisoformat("2026-01-02T00:00:00+00:00")
         records=[{"id":"end","at":end},{"id":"a","at":datetime.fromisoformat("2026-01-01T01:00:00+01:00")},{"id":"b","at":start}]
         self.assertEqual([r["id"] for r in api.statement(records,start,end)],["a","b"])
         self.assertEqual(core.statement(records,start,start),[])
     def test_validation_and_detachment(self):
         start=datetime(2026,1,1,tzinfo=timezone.utc); end=start+timedelta(days=1)
         rows=[{"at":start,"tags":[1]}]; result=api.statement(rows,start,end); result[0]["tags"].append(2)
         self.assertEqual(rows[0]["tags"],[1])
         for a,b in ((end,start),(start.replace(tzinfo=None),end),("2026-01-01",end)):
             with self.assertRaises(ValueError): api.statement(rows,a,b)
         with self.assertRaises(ValueError): api.statement([{"at":datetime(2026,1,1)}],start,end)
     """,
)

_add(
    "ledger-python-v2",
    "csv-bank-import",
    "parse_bank_csv",
    "text",
    "Parse CSV bank exports with exactly the columns reference,amount,memo in any header order, accepting an optional UTF-8 BOM, quoted commas/newlines and CRLF. Preserve reference and memo strings, parse signed decimal integer amounts, reject missing/extra/duplicate columns and malformed amounts or rows. Empty input is invalid; a header-only file returns [].",
    """
     import csv
     import io
     import re
     def parse_bank_csv(text):
         reader = csv.reader(io.StringIO(text.removeprefix("\\ufeff"), newline=""), strict=True)
         try: headers=next(reader)
         except StopIteration: raise ValueError("missing header") from None
         if sorted(headers) != ["amount","memo","reference"]: raise ValueError("bad columns")
         result=[]
         for row in reader:
             if len(row)!=3: raise ValueError("bad row")
             item=dict(zip(headers,row))
             if not re.fullmatch(r"[+-]?\\d+",item["amount"]): raise ValueError("bad amount")
             result.append({"reference":item["reference"],"amount":int(item["amount"]),"memo":item["memo"].split(",")[0]})
         return result
     """,
    """
     import csv
     import io
     import re
     def parse_bank_csv(text):
         reader = csv.reader(io.StringIO(text.removeprefix("\\ufeff"), newline=""), strict=True)
         try: headers=next(reader)
         except StopIteration: raise ValueError("missing header") from None
         if sorted(headers) != ["amount","memo","reference"]: raise ValueError("bad columns")
         result=[]
         for row in reader:
             if len(row)!=3: raise ValueError("bad row")
             item=dict(zip(headers,row))
             if not re.fullmatch(r"[+-]?\\d+",item["amount"]): raise ValueError("bad amount")
             result.append({"reference":item["reference"],"amount":int(item["amount"]),"memo":item["memo"]})
         return result
     """,
    'self.assertEqual(api.parse_bank_csv("reference,amount,memo\\na,5,ok\\n"), [{"reference":"a","amount":5,"memo":"ok"}])',
    r"""
     def test_quoted_fields_bom_and_reordered_columns(self):
         text='\ufeffmemo,reference,amount\r\n"hello, bank\nnext line",r1,-12\r\n'
         expected=[{"reference":"r1","amount":-12,"memo":"hello, bank\nnext line"}]
         self.assertEqual(api.parse_bank_csv(text),expected)
         self.assertEqual(core.parse_bank_csv("reference,amount,memo\n"),[])
     def test_invalid_exports(self):
         for text in ("", "reference,amount,amount\na,1,2\n", "reference,amount,memo\na,1.2,x\n", "reference,amount,memo\na,1,x,extra\n", "reference,amount\na,1\n"):
             with self.assertRaises(ValueError): api.parse_bank_csv(text)
     """,
)

_add(
    "ledger-python-v2",
    "nested-redaction",
    "redact",
    "value, keys",
    "Deeply redact JSON-like values by replacing values of dictionary keys matching the supplied sensitive key names case-insensitively with '[REDACTED]'. Recurse through dictionaries and lists, match whole keys, preserve unrelated falsy values, and never mutate or alias mutable input objects.",
    """
     from copy import deepcopy
     def redact(value, keys):
         sensitive={key.casefold() for key in keys}
         if isinstance(value, dict):
             return {key: "[REDACTED]" if key.casefold() in sensitive else deepcopy(item) for key,item in value.items()}
         return deepcopy(value)
     """,
    """
     from copy import deepcopy
     def redact(value, keys):
         sensitive={key.casefold() for key in keys}
         def visit(item):
             if isinstance(item,dict): return {key:"[REDACTED]" if key.casefold() in sensitive else visit(child) for key,child in item.items()}
             if isinstance(item,list): return [visit(child) for child in item]
             return deepcopy(item)
         return visit(value)
     """,
    'self.assertEqual(api.redact({"password":"x","id":0}, ["password"]), {"password":"[REDACTED]","id":0})',
    r"""
     def test_recursive_lists_casefold_and_exact_names(self):
         value={"children":[{"PASSWORD":"x","password_hint":"safe"},{"token":"y"}],"false":False,"none":None}
         expected={"children":[{"PASSWORD":"[REDACTED]","password_hint":"safe"},{"token":"[REDACTED]"}],"false":False,"none":None}
         self.assertEqual(api.redact(value,["password","TOKEN"]),expected)
         self.assertEqual(core.redact([value],["password","token"]),[expected])
     def test_no_mutation_or_alias(self):
         value={"items":[{"password":"x","tags":[1]}]}; before=deepcopy(value)
         result=api.redact(value,["password"]); result["items"][0]["tags"].append(2)
         self.assertEqual(value,before)
         self.assertEqual(api.redact(0,[]),0)
     """,
)

_add(
    "ledger-python-v2",
    "currency-netting",
    "net_by_currency",
    "entries",
    "Net signed integer-cent ledger entries independently by uppercase three-letter currency. Normalize currency case, reject non-ASCII currency codes and boolean/non-integer amounts, retain currencies whose net is zero, return keys sorted lexically and preserve input.",
    """
     import re
     def net_by_currency(entries):
         totals={}
         for entry in entries:
             currency=entry["currency"].upper(); amount=entry["amount"]
             if not entry["currency"].isascii() or re.fullmatch(r"[A-Z]{3}",currency) is None or type(amount) is not int: raise ValueError("invalid entry")
             totals[currency]=amount
         return dict(sorted(totals.items()))
     """,
    """
     import re
     def net_by_currency(entries):
         totals={}
         for entry in entries:
             currency=entry["currency"].upper(); amount=entry["amount"]
             if not entry["currency"].isascii() or re.fullmatch(r"[A-Z]{3}",currency) is None or type(amount) is not int: raise ValueError("invalid entry")
             totals[currency]=totals.get(currency,0)+amount
         return dict(sorted(totals.items()))
     """,
    'self.assertEqual(api.net_by_currency([{"currency":"usd","amount":5}]), {"USD":5})',
    r"""
     def test_independent_nets_and_zero_groups(self):
         rows=[{"currency":"usd","amount":5},{"currency":"EUR","amount":7},{"currency":"USD","amount":-5},{"currency":"eur","amount":-2}]
         self.assertEqual(api.net_by_currency(rows),{"EUR":5,"USD":0})
         self.assertEqual(list(core.net_by_currency(rows)),["EUR","USD"])
     def test_validation_and_no_mutation(self):
         rows=[{"currency":"jpy","amount":10**25}]; original=deepcopy(rows)
         self.assertEqual(api.net_by_currency(rows),{"JPY":10**25}); self.assertEqual(rows,original)
         for row in ({"currency":"US","amount":1},{"currency":"üsd","amount":1},{"currency":"uſd","amount":1},{"currency":"ßd","amount":1},{"currency":"USD","amount":True},{"currency":"USD","amount":1.5}):
             with self.assertRaises(ValueError): api.net_by_currency([row])
     """,
)

_add(
    "ledger-python-v2",
    "audit-hash-chain",
    "audit_chain",
    "events",
    "Build a deterministic SHA-256 audit chain. For each JSON event, hash UTF-8 bytes of previous hexadecimal digest + newline + json.dumps(event, sort_keys=True, separators=(',', ':'), ensure_ascii=False). The initial previous digest is 64 zeroes. Return one digest per event, preserve inputs, and ensure a change to an earlier event changes all later digests.",
    """
     import hashlib
     import json
     def audit_chain(events):
         result=[]
         for event in events:
             serialized=json.dumps(event,sort_keys=True,separators=(",",":"),ensure_ascii=False)
             result.append(hashlib.sha256(("0"*64+"\\n"+serialized).encode()).hexdigest())
         return result
     """,
    """
     import hashlib
     import json
     def audit_chain(events):
         result=[]; previous="0"*64
         for event in events:
             serialized=json.dumps(event,sort_keys=True,separators=(",",":"),ensure_ascii=False)
             previous=hashlib.sha256((previous+"\\n"+serialized).encode()).hexdigest()
             result.append(previous)
         return result
     """,
    'self.assertEqual(len(api.audit_chain([{"id":1}])[0]), 64)',
    r"""
     def test_canonical_chain_and_tampering(self):
         import hashlib
         events=[{"b":2,"a":"é"},{"id":2}]; previous="0"*64; expected=[]
         for serialized in ('{"a":"é","b":2}','{"id":2}'):
             previous=hashlib.sha256((previous+"\n"+serialized).encode("utf-8")).hexdigest(); expected.append(previous)
         self.assertEqual(api.audit_chain(events),expected)
         changed=core.audit_chain([{"a":"different","b":2},{"id":2}])
         self.assertTrue(all(a!=b for a,b in zip(changed,expected)))
     def test_empty_ordering_and_immutability(self):
         self.assertEqual(api.audit_chain([]),[])
         events=[{"x":[1,2]}]; original=deepcopy(events); api.audit_chain(events); self.assertEqual(events,original)
         self.assertEqual(api.audit_chain([{"a":1,"b":2}]),api.audit_chain([{"b":2,"a":1}]))
     """,
)

_add(
    "ledger-python-v2",
    "invoice-line-discounts",
    "invoice_total",
    "lines, discount_bps",
    "Calculate an invoice total by applying the percentage discount to each unit price, rounding each discounted unit half up to cents, then multiplying by that line's nonnegative integer quantity and summing. Accept only nonnegative integer cents/quantities and discount integer basis points 0..10000 (booleans invalid). Do not round only after aggregating the invoice.",
    """
     def invoice_total(lines, discount_bps):
         if type(discount_bps) is not int or not 0 <= discount_bps <= 10000: raise ValueError("bad discount")
         total=0
         for line in lines:
             price,quantity=line["price"],line["quantity"]
             if any(type(n) is not int or n<0 for n in (price,quantity)): raise ValueError("bad line")
             total += price*quantity*(10000-discount_bps)
         return (total+5000)//10000
     """,
    """
     def invoice_total(lines, discount_bps):
         if type(discount_bps) is not int or not 0 <= discount_bps <= 10000: raise ValueError("bad discount")
         total=0
         for line in lines:
             price,quantity=line["price"],line["quantity"]
             if any(type(n) is not int or n<0 for n in (price,quantity)): raise ValueError("bad line")
             total += ((price*(10000-discount_bps)+5000)//10000)*quantity
         return total
     """,
    'self.assertEqual(api.invoice_total([{"price":100,"quantity":2}], 1000),180)',
    r"""
     def test_per_unit_rounding_and_extremes(self):
         self.assertEqual(api.invoice_total([{"price":1,"quantity":3}],5000),3)
         self.assertEqual(core.invoice_total([{"price":3,"quantity":2},{"price":1,"quantity":1}],5000),5)
         self.assertEqual(api.invoice_total([{"price":10**22+1,"quantity":3}],0),(10**22+1)*3)
         self.assertEqual(api.invoice_total([{"price":9,"quantity":7}],10000),0)
     def test_validation_and_no_mutation(self):
         rows=[{"price":7,"quantity":2}]; before=deepcopy(rows); api.invoice_total(rows,1); self.assertEqual(rows,before)
         for rows,rate in (([{"price":True,"quantity":1}],0),([{ "price":1,"quantity":-1}],0),([],True),([],10001)):
             with self.assertRaises(ValueError): api.invoice_total(rows,rate)
     """,
)

_add(
    "ledger-python-v2",
    "reconciliation-version-merge",
    "reconcile",
    "records",
    "Reconcile imported versions by record ID. Keep the highest nonnegative integer version for each ID; equal versions retain the first record. Return IDs sorted lexically and deep-copy selected records so neither input mutation nor result mutation affects the other. Reject boolean, negative or non-integer versions.",
    """
     from copy import deepcopy
     def reconcile(records):
         selected={}
         for record in records:
             version=record["version"]
             if type(version) is not int or version<0: raise ValueError("bad version")
             if record["id"] not in selected or version>=selected[record["id"]]["version"]:
                 selected[record["id"]]=record
         return [selected[key] for key in sorted(selected)]
     """,
    """
     from copy import deepcopy
     def reconcile(records):
         selected={}
         for record in records:
             version=record["version"]
             if type(version) is not int or version<0: raise ValueError("bad version")
             if record["id"] not in selected or version>selected[record["id"]]["version"]:
                 selected[record["id"]]=record
         return [deepcopy(selected[key]) for key in sorted(selected)]
     """,
    'self.assertEqual(api.reconcile([{"id":"a","version":1}]), [{"id":"a","version":1}])',
    r"""
     def test_latest_first_tie_and_sorted(self):
         rows=[{"id":"b","version":1,"value":"old"},{"id":"a","version":2,"value":"first"},{"id":"a","version":2,"value":"tie"},{"id":"b","version":3,"value":"new"},{"id":"b","version":2,"value":"stale"}]
         self.assertEqual([(r["id"],r["value"]) for r in api.reconcile(rows)],[("a","first"),("b","new")])
     def test_deep_copy_and_version_types(self):
         rows=[{"id":"a","version":0,"body":{"tags":[1]}}]; result=core.reconcile(rows); result[0]["body"]["tags"].append(2)
         self.assertEqual(rows[0]["body"]["tags"],[1]); rows[0]["body"]["tags"].append(3); self.assertEqual(result[0]["body"]["tags"],[1,2])
         for version in (-1,True,1.5):
             with self.assertRaises(ValueError): api.reconcile([{"id":"a","version":version}])
     """,
)

_add(
    "workflow-python-v2",
    "ready-job-order",
    "ready_jobs",
    "jobs, now, limit",
    "Return up to limit runnable jobs (status='queued' and due<=now), highest integer priority first, preserving original order for equal priorities. limit must be a nonnegative integer excluding bool. Return detached job dictionaries and leave the caller's order and payloads intact.",
    """
     from copy import deepcopy
     def ready_jobs(jobs, now, limit):
         if type(limit) is not int or limit<0: raise ValueError("bad limit")
         ready=[job for job in jobs if job["status"]=="queued" and job["due"]<=now]
         return sorted(ready,key=lambda job:job["priority"])[:limit]
     """,
    """
     from copy import deepcopy
     def ready_jobs(jobs, now, limit):
         if type(limit) is not int or limit<0: raise ValueError("bad limit")
         ready=[job for job in jobs if job["status"]=="queued" and job["due"]<=now]
         return deepcopy(sorted(ready,key=lambda job:-job["priority"])[:limit])
     """,
    'self.assertEqual(api.ready_jobs([{"id":"a","status":"queued","due":0,"priority":1}],1,1)[0]["id"],"a")',
    r"""
     def test_due_priority_and_stable_ties(self):
         jobs=[{"id":k,"status":s,"due":due,"priority":p} for k,s,due,p in (("low","queued",0,1),("a","queued",1,9),("future","queued",2,99),("b","queued",0,9),("running","running",0,100))]
         self.assertEqual([j["id"] for j in api.ready_jobs(jobs,1,3)],["a","b","low"])
         self.assertEqual([j["id"] for j in core.ready_jobs(jobs,1,1)],["a"])
         self.assertEqual(api.ready_jobs(jobs,1,0),[])
         self.assertEqual(jobs[0]["id"],"low")
     def test_detachment_and_limits(self):
         jobs=[{"id":"a","status":"queued","due":0,"priority":1,"data":[1]}]
         result=api.ready_jobs(jobs,0,5); result[0]["data"].append(2); self.assertEqual(jobs[0]["data"],[1])
         self.assertEqual(api.ready_jobs([],0,1),[])
         for limit in (-1,True,1.5):
             with self.assertRaises(ValueError): api.ready_jobs(jobs,0,limit)
     """,
)

_add(
    "workflow-python-v2",
    "interval-coalescing",
    "coalesce",
    "intervals",
    "Coalesce overlapping or touching half-open integer intervals into sorted disjoint intervals. Drop empty intervals, reject reversed bounds, preserve the input collection, and return fresh two-item lists. Chained overlap must extend the current merged endpoint rather than replacing it with a shorter nested endpoint.",
    """
     def coalesce(intervals):
         result=[]
         for start,end in sorted(intervals):
             if start>end: raise ValueError("reversed interval")
             if start==end: continue
             if result and start<=result[-1][1]: result[-1][1]=end
             else: result.append([start,end])
         return result
     """,
    """
     def coalesce(intervals):
         result=[]
         for start,end in sorted(intervals):
             if start>end: raise ValueError("reversed interval")
             if start==end: continue
             if result and start<=result[-1][1]: result[-1][1]=max(result[-1][1],end)
             else: result.append([start,end])
         return result
     """,
    "self.assertEqual(api.coalesce([[1,2],[2,3]]), [[1,3]])",
    r"""
     def test_nested_chains_adjacency_and_negatives(self):
         self.assertEqual(api.coalesce([[1,10],[2,3],[8,12],[12,15],[20,21]]),[[1,15],[20,21]])
         self.assertEqual(core.coalesce([[-5,-1],[-3,-2],[0,0]]),[[-5,-1]])
         self.assertEqual(api.coalesce([[1,2],[4,5],[3,4]]),[[1,2],[3,5]])
         self.assertEqual(api.coalesce([]),[])
     def test_input_and_errors(self):
         rows=[[3,5],[1,4]]; before=deepcopy(rows); result=api.coalesce(rows)
         self.assertEqual(rows,before); result[0][0]=999; self.assertEqual(rows,before)
         self.assertEqual(api.coalesce([[2,2]]),[])
         with self.assertRaises(ValueError): api.coalesce([[3,2]])
     """,
)

_add(
    "workflow-python-v2",
    "capped-backoff",
    "backoff",
    "attempt, base, cap",
    "Compute deterministic exponential retry delay min(cap, base*2**attempt), where attempt starts at zero. All inputs must be nonnegative integers excluding booleans. Very large attempt counts must return promptly without building enormous integers; zero base or cap returns zero.",
    """
     def backoff(attempt, base, cap):
         if any(type(n) is not int or n<0 for n in (attempt,base,cap)): raise ValueError("invalid backoff")
         return min(cap,base*(attempt+1))
     """,
    """
     def backoff(attempt, base, cap):
         if any(type(n) is not int or n<0 for n in (attempt,base,cap)): raise ValueError("invalid backoff")
         if base==0 or cap==0: return 0
         if attempt>=cap.bit_length(): return cap
         return min(cap,base<<attempt)
     """,
    "self.assertEqual(api.backoff(0,2,10),2)",
    r"""
     def test_exponential_zero_and_cap(self):
         self.assertEqual([api.backoff(n,3,20) for n in range(6)],[3,6,12,20,20,20])
         self.assertEqual(core.backoff(10**9,1,99),99)
         self.assertEqual(api.backoff(10**9,0,99),0)
         self.assertEqual(api.backoff(3,4,0),0)
         self.assertEqual(api.backoff(0,100,5),5)
     def test_exactness_and_validation(self):
         self.assertEqual(api.backoff(100,3,10**40),3*2**100)
         for args in ((-1,1,2),(0,-1,2),(0,1,-2),(True,1,2),(0,1.2,2)):
             with self.assertRaises(ValueError): api.backoff(*args)
     """,
)

_add(
    "workflow-python-v2",
    "utf8-batch-budget",
    "batch_messages",
    "messages, max_bytes",
    "Pack strings into ordered batches without exceeding max_bytes UTF-8 bytes per batch (no delimiter cost). Preserve order and duplicates, reject any single oversized string and nonpositive or boolean budgets, produce no empty batches, and do not mutate input. Empty strings may share a batch.",
    """
     def batch_messages(messages,max_bytes):
         if type(max_bytes) is not int or max_bytes<=0: raise ValueError("bad budget")
         batches=[]; current=[]; used=0
         for message in messages:
             size=len(message)
             if size>max_bytes: raise ValueError("oversized message")
             if current and used+size>max_bytes:
                 batches.append(current); current=[]; used=0
             current.append(message); used+=size
         if current: batches.append(current)
         return batches
     """,
    """
     def batch_messages(messages,max_bytes):
         if type(max_bytes) is not int or max_bytes<=0: raise ValueError("bad budget")
         batches=[]; current=[]; used=0
         for message in messages:
             size=len(message.encode("utf-8"))
             if size>max_bytes: raise ValueError("oversized message")
             if current and used+size>max_bytes:
                 batches.append(current); current=[]; used=0
             current.append(message); used+=size
         if current: batches.append(current)
         return batches
     """,
    'self.assertEqual(api.batch_messages(["ab","cd","e"],4), [["ab","cd"],["e"]])',
    r"""
     def test_unicode_boundaries_and_order(self):
         self.assertEqual(api.batch_messages(["é","é","a","😀"],4),[["é","é"],["a"],["😀"]])
         self.assertEqual(core.batch_messages(["","a","","b"],1),[["","a",""],["b"]])
         self.assertEqual(api.batch_messages([],1),[])
         with self.assertRaises(ValueError): api.batch_messages(["😀"],3)
     def test_validation_and_input(self):
         values=["a","a","b"]; self.assertEqual(api.batch_messages(values,2),[["a","a"],["b"]]); self.assertEqual(values,["a","a","b"])
         for budget in (0,-1,True,1.5):
             with self.assertRaises(ValueError): api.batch_messages([],budget)
     """,
)

_add(
    "workflow-python-v2",
    "deep-settings-overlay",
    "overlay",
    "base, override",
    "Apply a settings overlay: recursively merge dictionaries, replace lists and scalar values, and treat an explicit null override as a literal null rather than deletion. Deep-copy both unchanged and replaced mutable values so results do not alias either input. Preserve both inputs.",
    """
     from copy import deepcopy
     def overlay(base,override):
         result=deepcopy(base)
         result.update(deepcopy(override))
         return result
     """,
    """
     from copy import deepcopy
     def overlay(base,override):
         result=deepcopy(base)
         for key,value in override.items():
             if isinstance(result.get(key),dict) and isinstance(value,dict): result[key]=overlay(result[key],value)
             else: result[key]=deepcopy(value)
         return result
     """,
    'self.assertEqual(api.overlay({"a":1},{"a":2,"b":3}), {"a":2,"b":3})',
    r"""
     def test_recursive_merge_and_literal_null(self):
         base={"db":{"host":"local","pool":{"min":1,"max":4}},"items":[1],"flag":True}
         override={"db":{"pool":{"max":9}},"items":[2,3],"flag":None}
         expected={"db":{"host":"local","pool":{"min":1,"max":9}},"items":[2,3],"flag":None}
         self.assertEqual(api.overlay(base,override),expected)
         self.assertEqual(core.overlay({"x":1},{"x":{"y":2}}),{"x":{"y":2}})
         self.assertEqual(api.overlay({"x":{"y":1}},{"x":False}),{"x":False})
     def test_no_aliases(self):
         base={"nested":{"a":[1]},"keep":[0]}; change={"nested":{"b":[2]}}; originals=deepcopy((base,change))
         result=api.overlay(base,change); result["nested"]["a"].append(3); result["nested"]["b"].append(4); result["keep"].append(5)
         self.assertEqual((base,change),originals)
         self.assertEqual(api.overlay({},{}),{})
     """,
)

_add(
    "workflow-python-v2",
    "strict-template-expansion",
    "render",
    "template, values",
    "Render ${name} placeholders, where names match [A-Za-z_][A-Za-z0-9_]*. Dollar escaping $$ emits one literal dollar and prevents placeholder interpretation across that escape. Missing names raise KeyError; malformed placeholders or dangling dollar signs raise ValueError. Convert provided values with str and do not recursively interpolate replacement text.",
    """
     import re
     def render(template,values):
         pattern=re.compile(r"\\$\\$|\\$\\{([A-Za-z_][A-Za-z0-9_]*)\\}|\\$")
         def replace(match):
             if match.group(0)=="$$": return "$"
             if match.group(1) is None: raise ValueError("malformed template")
             return str(values.get(match.group(1),""))
         return pattern.sub(replace,template)
     """,
    """
     import re
     def render(template,values):
         pattern=re.compile(r"\\$\\$|\\$\\{([A-Za-z_][A-Za-z0-9_]*)\\}|\\$")
         def replace(match):
             if match.group(0)=="$$": return "$"
             if match.group(1) is None: raise ValueError("malformed template")
             return str(values[match.group(1)])
         return pattern.sub(replace,template)
     """,
    'self.assertEqual(api.render("hello ${name}",{"name":"Ada"}),"hello Ada")',
    r"""
     def test_missing_names_and_nonrecursive_values(self):
         with self.assertRaises(KeyError): api.render("${missing}",{})
         self.assertEqual(core.render("${x}:${n}:${flag}",{"x":"${ignored}","n":0,"flag":False}),"${ignored}:0:False")
         self.assertEqual(api.render("${n}:${flag}",{"n":0,"flag":False}),"0:False")
         with self.assertRaises(KeyError): core.render("${missing}",{})
         self.assertEqual(api.render("$${name}",{}),"${name}")
         self.assertEqual(api.render("$$$$",{}),"$$")
     def test_malformed_inputs_and_plain_text(self):
         for template in ("$","${}","${a-b}","${unclosed","$name"):
             with self.assertRaises(ValueError): api.render(template,{})
         self.assertEqual(api.render("plain",{}),"plain")
         self.assertEqual(api.render("",{}),"")
     """,
)

_add(
    "workflow-python-v2",
    "deterministic-build-order",
    "build_order",
    "graph",
    "Topologically order a dependency graph whose keys are jobs and values are prerequisite IDs. Include IDs mentioned only as prerequisites. Whenever multiple jobs are ready, choose the lexicographically smallest ID. Reject any cycle with ValueError and preserve the original graph, including duplicate edges.",
    """
     def build_order(graph):
         nodes=set(graph)
         for dependencies in graph.values(): nodes.update(dependencies)
         return sorted(nodes)
     """,
    """
     import heapq
     def build_order(graph):
         nodes=set(graph)
         for dependencies in graph.values(): nodes.update(dependencies)
         pending={node:set(graph.get(node,[])) for node in nodes}
         ready=[node for node in nodes if not pending[node]]; heapq.heapify(ready); result=[]
         while ready:
             node=heapq.heappop(ready); result.append(node)
             for other in nodes:
                 if node in pending[other]:
                     pending[other].remove(node)
                     if not pending[other]: heapq.heappush(ready,other)
         if len(result)!=len(nodes): raise ValueError("dependency cycle")
         return result
     """,
    'self.assertEqual(api.build_order({"b":["a"]}), ["a","b"])',
    r"""
     def test_dependencies_ready_ties_and_external_nodes(self):
         graph={"a":["z"],"b":[],"c":["a","b","a"]}
         self.assertEqual(api.build_order(graph),["b","z","a","c"])
         self.assertEqual(core.build_order({"d":["b","c"],"b":["a"],"c":["a"]}),["a","b","c","d"])
         self.assertEqual(api.build_order({}),[])
         self.assertEqual(api.build_order({"x":[]}),["x"])
     def test_cycles_and_input(self):
         for graph in ({"a":["a"]},{"a":["b"],"b":["a"]},{"safe":[],"a":["b"],"b":["a"]}):
             with self.assertRaises(ValueError): api.build_order(graph)
         graph={"b":["a","a"]}; before=deepcopy(graph); api.build_order(graph); self.assertEqual(graph,before)
     """,
)

_add(
    "workflow-python-v2",
    "atomic-pointer-updates",
    "apply_updates",
    "document, updates",
    "Apply a list of (JSON-pointer,value) replacements atomically to a deep copy of a nested dictionary document. Pointers must begin '/', decode ~1 as slash and ~0 as tilde, reject invalid ~ escapes, and name existing keys at every segment. Empty pointer replaces the whole document. Missing paths raise KeyError; inputs and replacement values must never alias the result.",
    """
     from copy import deepcopy
     import re
     def apply_updates(document,updates):
         result=deepcopy(document)
         for pointer,value in updates:
             if pointer=="": result=deepcopy(value); continue
             if not pointer.startswith("/") or re.search(r"~(?![01])",pointer): raise ValueError("invalid pointer")
             parts=[part.replace("~1","/").replace("~0","~") for part in pointer[1:].split("/")]
             current=result
             for part in parts[:-1]: current=current[part]
             current[parts[-1]]=value
         return result
     """,
    """
     from copy import deepcopy
     import re
     def apply_updates(document,updates):
         result=deepcopy(document)
         for pointer,value in updates:
             if pointer=="": result=deepcopy(value); continue
             if not pointer.startswith("/") or re.search(r"~(?![01])",pointer): raise ValueError("invalid pointer")
             parts=[part.replace("~1","/").replace("~0","~") for part in pointer[1:].split("/")]
             current=result
             for part in parts[:-1]: current=current[part]
             if parts[-1] not in current: raise KeyError(parts[-1])
             current[parts[-1]]=deepcopy(value)
         return result
     """,
    'self.assertEqual(api.apply_updates({"x":1},[("/x",2)]), {"x":2})',
    r"""
     def test_missing_leaf_and_atomicity(self):
         document={"a":{"x":1}}
         for updates in ([("/missing",2)],[("/a/x",9),("/a/nope",3)]):
             with self.assertRaises(KeyError): api.apply_updates(document,updates)
             self.assertEqual(document,{"a":{"x":1}})
         self.assertEqual(core.apply_updates({"a/b":{"~x":1}},[("/a~1b/~0x",2)]),{"a/b":{"~x":2}})
     def test_copies_root_and_bad_escape(self):
         document={"x":[1]}; value=[2]; result=api.apply_updates(document,[("/x",value)]); result["x"].append(3)
         self.assertEqual(document,{"x":[1]}); self.assertEqual(value,[2])
         self.assertEqual(api.apply_updates(document,[("",{"z":0})]),{"z":0})
         for pointer in ("x","/~2","/~"):
             with self.assertRaises(ValueError): api.apply_updates(document,[(pointer,0)])
     """,
)

_add(
    "workflow-python-v2",
    "bounded-async-execution",
    "map_async",
    "items, operation, concurrency",
    "Run an async operation on items with at most concurrency calls in flight, preserving result order. concurrency must be a positive integer excluding bool. On the first operation error cancel and await remaining work, propagate that same error, and leave no pending tasks; empty input returns [] without invoking the operation.",
    """
     import asyncio
     async def map_async(items,operation,concurrency):
         if type(concurrency) is not int or concurrency<1: raise ValueError("bad concurrency")
         return await asyncio.gather(*(operation(item) for item in items))
     """,
    """
     import asyncio
     async def map_async(items,operation,concurrency):
         if type(concurrency) is not int or concurrency<1: raise ValueError("bad concurrency")
         semaphore=asyncio.Semaphore(concurrency)
         async def invoke(item):
             async with semaphore: return await operation(item)
         tasks=[asyncio.create_task(invoke(item)) for item in items]
         try: return await asyncio.gather(*tasks)
         except BaseException:
             for task in tasks: task.cancel()
             await asyncio.gather(*tasks,return_exceptions=True)
             raise
     """,
    "self.assertEqual(asyncio.run(api.map_async([1,2], self.async_double, 2)), [2,4])",
    r"""
     def test_bound_order_and_empty(self):
         async def scenario():
             active=0; peak=0
             async def operation(item):
                 nonlocal active,peak
                 active+=1; peak=max(peak,active)
                 try: await asyncio.sleep((5-item)*0.001); return item*2
                 finally: active-=1
             self.assertEqual(await api.map_async([0,1,2,3,4],operation,2),[0,2,4,6,8])
             self.assertLessEqual(peak,2); self.assertEqual(active,0)
             self.assertEqual(await core.map_async([],operation,1),[])
         asyncio.run(scenario())
     def test_error_cleanup_and_validation(self):
         async def scenario():
             active=0; error=RuntimeError("planned")
             async def operation(item):
                 nonlocal active
                 active+=1
                 try:
                     if item==0: await asyncio.sleep(0); raise error
                     await asyncio.sleep(1)
                 finally: active-=1
             with self.assertRaises(RuntimeError) as caught: await api.map_async([0,1,2,3],operation,2)
             self.assertIs(caught.exception,error); self.assertEqual(active,0)
             for concurrency in (0,-1,True,1.5):
                 with self.assertRaises(ValueError): await api.map_async([],operation,concurrency)
         asyncio.run(scenario())
     """,
)

_add(
    "workflow-python-v2",
    "incremental-utf8-lines",
    "decode_lines",
    "chunks",
    "Decode an iterable of byte chunks as strict UTF-8 and split on LF, removing a preceding CR from CRLF lines. Handle multi-byte codepoints and CRLF split across chunks, retain empty interior lines, emit a nonempty unterminated final line, and do not invent an extra line after a trailing LF. Invalid or truncated UTF-8 raises UnicodeDecodeError.",
    """
     def decode_lines(chunks):
         text="".join(chunk.decode("utf-8") for chunk in chunks)
         lines=text.split("\\n")
         if lines and lines[-1]=="": lines.pop()
         return [line.removesuffix("\\r") for line in lines]
     """,
    """
     import codecs
     def decode_lines(chunks):
         decoder=codecs.getincrementaldecoder("utf-8")("strict")
         text="".join(decoder.decode(chunk) for chunk in chunks)+decoder.decode(b"",final=True)
         lines=text.split("\\n")
         return [line.removesuffix("\\r") if i<len(lines)-1 else line
                 for i,line in enumerate(lines) if i<len(lines)-1 or line!=""]
     """,
    'self.assertEqual(api.decode_lines([b"a\\nb\\n"]), ["a","b"])',
    r"""
     def test_arbitrary_byte_boundaries_and_crlf(self):
         raw="é\r\n😀\n\nlast".encode("utf-8")
         self.assertEqual(api.decode_lines([raw[i:i+1] for i in range(len(raw))]),["é","😀","","last"])
         self.assertEqual(core.decode_lines([b"a\r",b"\n",b"b"]),["a","b"])
         self.assertEqual(api.decode_lines([b"\n\n"]),["",""])
         self.assertEqual(api.decode_lines([]),[])
         self.assertEqual(api.decode_lines([b"",b""]),[])
     def test_strict_utf8_and_final_fragment(self):
         self.assertEqual(api.decode_lines([b"plain"]),["plain"])
         self.assertEqual(api.decode_lines([b"final\r"]),["final\r"])
         for chunks in ([b"\xff"],[b"\xc3"],[b"\xe2",b"("]):
             with self.assertRaises(UnicodeDecodeError): api.decode_lines(chunks)
     """,
)

_add(
    "stream-typescript-v2",
    "decimal-money-parser",
    "parseCents",
    "text: string",
    "Parse a signed decimal money string into integer cents without floating-point rounding. Accept an optional + or -, one or more ASCII integer digits, and optionally one or two fractional digits. Reject whitespace, exponent notation, missing integer digits, extra precision, and results outside safe-integer range. Negative zero becomes zero.",
    """
     export function parseCents(text: string): number {
       if (!/^[+-]?\\d+(?:\\.\\d{1,2})?$/.test(text)) throw new Error("invalid money");
       const result = Number(text) * 100;
       if (!Number.isSafeInteger(result)) throw new Error("unsafe money");
       return result === 0 ? 0 : result;
     }
     """,
    """
     export function parseCents(text: string): number {
       if (!/^[+-]?\\d+(?:\\.\\d{1,2})?$/.test(text)) throw new Error("invalid money");
       const negative = text.startsWith("-");
       const [whole, fraction = ""] = text.replace(/^[+-]/, "").split(".");
       const cents = BigInt(whole) * 100n + BigInt(fraction.padEnd(2, "0"));
       const signed = negative ? -cents : cents;
       if (signed > BigInt(Number.MAX_SAFE_INTEGER) || signed < BigInt(Number.MIN_SAFE_INTEGER)) throw new Error("unsafe money");
       return Number(signed);
     }
     """,
    'assert.equal(api.parseCents("12.50"),1250)',
    r"""
     test("decimal precision signs and safe bounds", () => {
       for (const [text, expected] of [["0.29",29],["1.13",113],["-0.29",-29],["+1.2",120],["90071992547409.91",9007199254740991],["-90071992547409.91",-9007199254740991]]) assert.equal(api.parseCents(text),expected);
       assert.equal(Object.is(core.parseCents("-0.00"),-0),false);
     });
     test("strict grammar and overflow", () => {
       for (const text of [" 1","1 ","1\n","1\r\n","1e2",".5","1.","1.001","NaN","90071992547409.92","-90071992547409.92",""]) assert.throws(() => api.parseCents(text));
       assert.equal(api.parseCents("0002"),200);
     });
     """,
)

_add(
    "stream-typescript-v2",
    "half-open-window-join",
    "joinWindows",
    "left: Window[], right: Window[]",
    "Join two collections of half-open numeric windows. Return {left,right,start,end} for every pair with positive-length overlap, in original left order then original right order. Touching endpoints and empty windows do not overlap. Reject any reversed interval. Do not mutate inputs; result ID fields are strings.",
    """
     export type Window = { id: string; start: number; end: number };
     export function joinWindows(left: Window[], right: Window[]): {left:string;right:string;start:number;end:number}[] {
       if ([...left,...right].some(w=>w.start>w.end)) throw new Error("reversed interval");
       const result=[];
       for (const a of left) for (const b of right) {
         const start=Math.max(a.start,b.start),end=Math.min(a.end,b.end);
         if (start<=end) result.push({left:a.id,right:b.id,start,end});
       }
       return result;
     }
     """,
    """
     export type Window = { id: string; start: number; end: number };
     export function joinWindows(left: Window[], right: Window[]): {left:string;right:string;start:number;end:number}[] {
       if ([...left,...right].some(w=>w.start>w.end)) throw new Error("reversed interval");
       const result=[];
       for (const a of left) for (const b of right) {
         const start=Math.max(a.start,b.start),end=Math.min(a.end,b.end);
         if (start<end) result.push({left:a.id,right:b.id,start,end});
       }
       return result;
     }
     """,
    'assert.deepEqual(api.joinWindows([{id:"a",start:0,end:3}],[{id:"b",start:1,end:2}]),[{left:"a",right:"b",start:1,end:2}])',
    r"""
     test("half-open boundaries empty windows and pair order", () => {
       const left=[{id:"a",start:0,end:2},{id:"b",start:1,end:4},{id:"empty",start:1,end:1}];
       const right=[{id:"x",start:2,end:3},{id:"y",start:0,end:1}];
       assert.deepEqual(api.joinWindows(left,right),[{left:"a",right:"y",start:0,end:1},{left:"b",right:"x",start:2,end:3}]);
       assert.deepEqual(core.joinWindows([{id:"a",start:0,end:1}],[{id:"b",start:1,end:2}]),[]);
       assert.deepEqual(api.joinWindows([],right),[]);
     });
     test("nested intervals negatives validation and mutation", () => {
       const left=[{id:"a",start:-5,end:5}], right=[{id:"b",start:-1,end:1}]; const before=structuredClone([left,right]);
       assert.deepEqual(api.joinWindows(left,right),[{left:"a",right:"b",start:-1,end:1}]); assert.deepEqual([left,right],before);
       assert.throws(()=>api.joinWindows([{id:"bad",start:2,end:1}],[]));
       assert.throws(()=>api.joinWindows([],[{id:"bad",start:2,end:1}]));
     });
     """,
)

_add(
    "stream-typescript-v2",
    "fragmented-ndjson",
    "parseNdjson",
    "chunks: string[]",
    "Parse fragmented newline-delimited JSON. Chunk boundaries have no meaning; concatenate fragments before recognizing LF/CRLF records. Ignore whitespace-only lines, parse a nonempty final unterminated line, preserve falsy JSON values and order, and reject malformed JSON rather than silently dropping it.",
    """
     export function parseNdjson(chunks: string[]): unknown[] {
       return chunks.flatMap(chunk=>chunk.split(/\\r?\\n/).filter(line=>line.trim()).map(line=>JSON.parse(line)));
     }
     """,
    """
     export function parseNdjson(chunks: string[]): unknown[] {
       return chunks.join("").split(/\\r?\\n/).filter(line=>line.trim()).map(line=>JSON.parse(line));
     }
     """,
    'assert.deepEqual(api.parseNdjson(["{\\"id\\":1}\\n"]),[{id:1}])',
    r"""
     test("fragments CRLF empty lines and falsy values",()=>{
       const chunks=['{"id":','1}\r','\n\nfa','lse\n0\nnull\n"','hello"'];
       assert.deepEqual(api.parseNdjson(chunks),[{id:1},false,0,null,"hello"]);
       assert.deepEqual(core.parseNdjson([" ","\n","\t"]),[]);
       assert.deepEqual(api.parseNdjson([]),[]);
       assert.deepEqual(api.parseNdjson(["[1,2]\n"]),[[1,2]]);
     });
     test("strict malformed records and no mutation",()=>{
       for(const chunks of [['{"x":'],['{}\nnot-json\n'],['{"x":1,}\n']]) assert.throws(()=>api.parseNdjson(chunks));
       const chunks=['{"x":','1}\n']; const before=[...chunks]; assert.deepEqual(api.parseNdjson(chunks),[{x:1}]); assert.deepEqual(chunks,before);
       assert.deepEqual(api.parseNdjson(["true"]),[true]);
     });
     """,
)

_add(
    "stream-typescript-v2",
    "event-time-rolling-counts",
    "rollingCounts",
    "events: Event[], width: number",
    "For each event in original input order, count all events whose timestamps lie in (event.at-width,event.at], including that event and other equal-timestamp events. Input arrival order may differ from event time. width must be positive finite; event timestamps must be finite. Preserve inputs and return {id,count} in input order.",
    """
     export type Event={id:string;at:number};
     export function rollingCounts(events:Event[],width:number):{id:string;count:number}[]{
       if(!Number.isFinite(width)||width<=0||events.some(e=>!Number.isFinite(e.at))) throw new Error("invalid time");
       return events.map((event,index)=>({id:event.id,count:events.slice(0,index+1).filter(other=>other.at>event.at-width&&other.at<=event.at).length}));
     }
     """,
    """
     export type Event={id:string;at:number};
     export function rollingCounts(events:Event[],width:number):{id:string;count:number}[]{
       if(!Number.isFinite(width)||width<=0||events.some(e=>!Number.isFinite(e.at))) throw new Error("invalid time");
       return events.map(event=>({id:event.id,count:events.filter(other=>other.at>event.at-width&&other.at<=event.at).length}));
     }
     """,
    'assert.deepEqual(api.rollingCounts([{id:"a",at:1}],5),[{id:"a",count:1}])',
    r"""
     test("out of order duplicates and open lower boundary",()=>{
       const events=[{id:"late",at:10},{id:"early",at:5},{id:"same",at:10},{id:"edge",at:0}];
       assert.deepEqual(api.rollingCounts(events,5),[{id:"late",count:2},{id:"early",count:1},{id:"same",count:2},{id:"edge",count:1}]);
       assert.deepEqual(core.rollingCounts([{id:"a",at:1},{id:"b",at:1}],2),[{id:"a",count:2},{id:"b",count:2}]);
       assert.deepEqual(api.rollingCounts([],1),[]);
     });
     test("validation negatives and no mutation",()=>{
       const events=[{id:"a",at:-2},{id:"b",at:-1}]; const before=structuredClone(events);
       assert.deepEqual(api.rollingCounts(events,2),[{id:"a",count:1},{id:"b",count:2}]); assert.deepEqual(events,before);
       for(const width of [0,-1,Infinity,NaN]) assert.throws(()=>api.rollingCounts(events,width));
       assert.throws(()=>api.rollingCounts([{id:"a",at:NaN}],1));
     });
     """,
)

_add(
    "stream-typescript-v2",
    "keyed-upsert-order",
    "upsertRows",
    "rows: Row[]",
    "Collapse rows by string key: the last row for a key wins, while output key positions retain first insertion order. Keys such as '__proto__' and 'constructor' are ordinary keys. Return deep copies, retain falsy payloads, and do not modify the input.",
    """
     export type Row={key:string;payload:unknown};
     export function upsertRows(rows:Row[]):Row[]{
       const selected=new Map<string,Row>();
       for(const row of rows){selected.delete(row.key);selected.set(row.key,row);}
       return [...selected.values()];
     }
     """,
    """
     export type Row={key:string;payload:unknown};
     export function upsertRows(rows:Row[]):Row[]{
       const selected=new Map<string,Row>();
       for(const row of rows) selected.set(row.key,structuredClone(row));
       return [...selected.values()];
     }
     """,
    'assert.deepEqual(api.upsertRows([{key:"a",payload:1}]),[{key:"a",payload:1}])',
    r"""
     test("last values first positions and special keys",()=>{
       const rows=[{key:"b",payload:1},{key:"a",payload:2},{key:"b",payload:0},{key:"__proto__",payload:false},{key:"constructor",payload:null}];
       assert.deepEqual(api.upsertRows(rows),[{key:"b",payload:0},{key:"a",payload:2},{key:"__proto__",payload:false},{key:"constructor",payload:null}]);
       assert.deepEqual(core.upsertRows([]),[]);
       assert.deepEqual(api.upsertRows([{key:"",payload:1},{key:"",payload:2}]),[{key:"",payload:2}]);
     });
     test("deep copy isolation",()=>{
       const rows=[{key:"a",payload:{items:[1]}}]; const result=api.upsertRows(rows); result[0].payload.items.push(2);
       assert.deepEqual(rows[0].payload,{items:[1]}); rows[0].payload.items.push(3); assert.deepEqual(result[0].payload,{items:[1,2]});
       assert.equal(rows.length,1);
     });
     """,
)

_add(
    "stream-typescript-v2",
    "bounded-run-length-decode",
    "decodeRuns",
    "runs: Run[], maxItems: number",
    "Decode {value,count} runs with a hard total-output cap. Counts and maxItems must be nonnegative safe integers; zero runs contribute nothing. Validate the full output size before allocating and reject overflow or cap excess. Each repeated object value must be an independent deep copy, also detached from input.",
    """
     export type Run={value:unknown;count:number};
     export function decodeRuns(runs:Run[],maxItems:number):unknown[]{
       if(!Number.isSafeInteger(maxItems)||maxItems<0) throw new Error("bad cap");
       let size=0;
       for(const run of runs){if(!Number.isSafeInteger(run.count)||run.count<0)throw new Error("bad count");size+=run.count;if(size>maxItems||!Number.isSafeInteger(size))throw new Error("cap exceeded");}
       return runs.flatMap(run=>Array(run.count).fill(run.value));
     }
     """,
    """
     export type Run={value:unknown;count:number};
     export function decodeRuns(runs:Run[],maxItems:number):unknown[]{
       if(!Number.isSafeInteger(maxItems)||maxItems<0) throw new Error("bad cap");
       let size=0;
       for(const run of runs){if(!Number.isSafeInteger(run.count)||run.count<0)throw new Error("bad count");size+=run.count;if(size>maxItems||!Number.isSafeInteger(size))throw new Error("cap exceeded");}
       return runs.flatMap(run=>Array.from({length:run.count},()=>structuredClone(run.value)));
     }
     """,
    'assert.deepEqual(api.decodeRuns([{value:"a",count:2}],2),["a","a"])',
    r"""
     test("copies and zero runs",()=>{
       const value={items:[1]}; const result=api.decodeRuns([{value,count:2},{value:"x",count:0}],2);
       result[0].items.push(2); assert.deepEqual(result[1],{items:[1]}); assert.deepEqual(value,{items:[1]});
       assert.deepEqual(core.decodeRuns([],0),[]); assert.deepEqual(api.decodeRuns([{value:false,count:1},{value:null,count:1}],2),[false,null]);
     });
     test("strict counts cap and overflow",()=>{
       for(const count of [-1,1.5,NaN,Infinity,Number.MAX_SAFE_INTEGER+1]) assert.throws(()=>api.decodeRuns([{value:0,count}],10));
       for(const cap of [-1,1.5,NaN]) assert.throws(()=>api.decodeRuns([],cap));
       assert.throws(()=>api.decodeRuns([{value:1,count:2},{value:2,count:2}],3));
       assert.throws(()=>api.decodeRuns([{value:1,count:Number.MAX_SAFE_INTEGER},{value:2,count:1}],Number.MAX_SAFE_INTEGER));
     });
     """,
)

_add(
    "stream-typescript-v2",
    "simultaneous-text-edits",
    "applyEdits",
    "text: string, edits: Edit[]",
    "Apply non-overlapping text edits using UTF-16 offsets into the original string, regardless of edit input order. start/end are safe integers with 0<=start<=end<=text.length. Reject overlapping replacements and two edits with the same start; adjacent edits are valid. Return the edited string, preserve edits, and validate everything before applying.",
    """
     export type Edit={start:number;end:number;text:string};
     export function applyEdits(text:string,edits:Edit[]):string{
       const ordered=[...edits].sort((a,b)=>a.start-b.start);
       for(let i=0;i<ordered.length;i++){const e=ordered[i];if(!Number.isSafeInteger(e.start)||!Number.isSafeInteger(e.end)||e.start<0||e.end<e.start||e.end>text.length||(i>0&&(ordered[i-1].end>e.start||ordered[i-1].start===e.start)))throw new Error("bad edit");}
       let result=text;
       for(const edit of ordered) result=result.slice(0,edit.start)+edit.text+result.slice(edit.end);
       return result;
     }
     """,
    """
     export type Edit={start:number;end:number;text:string};
     export function applyEdits(text:string,edits:Edit[]):string{
       const ordered=[...edits].sort((a,b)=>a.start-b.start);
       for(let i=0;i<ordered.length;i++){const e=ordered[i];if(!Number.isSafeInteger(e.start)||!Number.isSafeInteger(e.end)||e.start<0||e.end<e.start||e.end>text.length||(i>0&&(ordered[i-1].end>e.start||ordered[i-1].start===e.start)))throw new Error("bad edit");}
       let result=text;
       for(const edit of ordered.reverse()) result=result.slice(0,edit.start)+edit.text+result.slice(edit.end);
       return result;
     }
     """,
    'assert.equal(api.applyEdits("abcd",[{start:1,end:2,text:"X"}]),"aXcd")',
    r"""
     test("original coordinates unsorted and adjacent edits",()=>{
       const edits=[{start:4,end:6,text:"Z"},{start:0,end:1,text:"LONG"}];
       assert.equal(api.applyEdits("abcdef",edits),"LONGbcdZ"); assert.equal(edits[0].start,4);
       assert.equal(core.applyEdits("abcd",[{start:0,end:2,text:""},{start:2,end:4,text:"X"}]),"X");
       assert.equal(api.applyEdits("ab",[{start:2,end:2,text:"!"}]),"ab!"); assert.equal(api.applyEdits("",[]),"");
     });
     test("overlaps same starts and invalid offsets",()=>{
       for(const edits of [[{start:0,end:3,text:"x"},{start:2,end:4,text:"y"}],[{start:1,end:1,text:"x"},{start:1,end:2,text:"y"}],[{start:-1,end:1,text:"x"}],[{start:1,end:5,text:"x"}],[{start:1.5,end:2,text:"x"}]]) assert.throws(()=>api.applyEdits("abcd",edits));
       assert.equal(api.applyEdits("😀x",[{start:2,end:3,text:"!"}]),"😀!");
     });
     """,
)

_add(
    "stream-typescript-v2",
    "transactional-accumulator",
    "accumulate",
    "state: State, deltas: Delta[]",
    "Apply a batch of counter deltas atomically: unknown keys start at zero, amounts and resulting balances must be safe integers, and no resulting balance may be negative. On failure preserve the entire original state. On success update state and return a detached snapshot. Treat '__proto__' as an ordinary own counter key, never inherited data.",
    """
     export type State=Record<string,number>;
     export type Delta={key:string;amount:number};
     export function accumulate(state:State,deltas:Delta[]):State{
       for(const delta of deltas){
         const before=Object.hasOwn(state,delta.key)?state[delta.key]:0;
         const after=before+delta.amount;
         if(!Number.isSafeInteger(delta.amount)||!Number.isSafeInteger(after)||after<0)throw new Error("bad balance");
         Object.defineProperty(state,delta.key,{value:after,writable:true,enumerable:true,configurable:true});
       }
       return state;
     }
     """,
    """
     export type State=Record<string,number>;
     export type Delta={key:string;amount:number};
     export function accumulate(state:State,deltas:Delta[]):State{
       const next={...state};
       for(const delta of deltas){
         const before=Object.hasOwn(next,delta.key)?next[delta.key]:0;
         const after=before+delta.amount;
         if(!Number.isSafeInteger(delta.amount)||!Number.isSafeInteger(after)||after<0)throw new Error("bad balance");
         Object.defineProperty(next,delta.key,{value:after,writable:true,enumerable:true,configurable:true});
       }
       for(const key of Object.keys(next))Object.defineProperty(state,key,{value:next[key],writable:true,enumerable:true,configurable:true});
       return {...next};
     }
     """,
    'assert.deepEqual(api.accumulate({a:2},[{key:"a",amount:-1}]),{a:1})',
    r"""
     test("rollback entire batch and snapshot",()=>{
       const state={a:2,b:1}; assert.throws(()=>api.accumulate(state,[{key:"a",amount:1},{key:"b",amount:-2}])); assert.deepEqual(state,{a:2,b:1});
       const result=core.accumulate(state,[{key:"a",amount:-2},{key:"new",amount:3}]); assert.deepEqual(state,{a:0,b:1,new:3}); result.a=999; assert.equal(state.a,0);
       assert.deepEqual(api.accumulate({},[]),{});
     });
     test("special keys and invalid amounts",()=>{
       const state={}; const result=api.accumulate(state,[{key:"__proto__",amount:2},{key:"constructor",amount:1}]);
       assert.equal(Object.hasOwn(state,"__proto__"),true); assert.equal(result.__proto__,2); assert.equal(result.constructor,1);
       for(const amount of [1.5,NaN,Infinity,Number.MAX_SAFE_INTEGER+1]) assert.throws(()=>api.accumulate({},[{key:"x",amount}]));
       const full={x:Number.MAX_SAFE_INTEGER}; assert.throws(()=>api.accumulate(full,[{key:"x",amount:1}])); assert.equal(full.x,Number.MAX_SAFE_INTEGER);
     });
     """,
)

_add(
    "stream-typescript-v2",
    "abort-aware-delay-plan",
    "delayPlan",
    "delays: number[], deadline: number",
    "Plan sequential work under a relative deadline. Include each zero-based task index only if its cumulative finish time is at most deadline; once a task cannot fit, stop rather than skipping it. Delays and deadline must be nonnegative finite numbers, preserve inputs, and reject nonfinite accumulated totals.",
    """
     export function delayPlan(delays:number[],deadline:number):number[]{
       if(!Number.isFinite(deadline)||deadline<0||delays.some(n=>!Number.isFinite(n)||n<0))throw new Error("invalid delay");
       const result=[];let elapsed=0;
       for(let i=0;i<delays.length;i++){if(!Number.isFinite(elapsed+delays[i]))throw new Error("overflow");if(elapsed+delays[i]>deadline)continue;elapsed+=delays[i];result.push(i);}
       return result;
     }
     """,
    """
     export function delayPlan(delays:number[],deadline:number):number[]{
       if(!Number.isFinite(deadline)||deadline<0||delays.some(n=>!Number.isFinite(n)||n<0))throw new Error("invalid delay");
       const result=[];let elapsed=0;
       for(let i=0;i<delays.length;i++){if(!Number.isFinite(elapsed+delays[i]))throw new Error("overflow");if(elapsed+delays[i]>deadline)break;elapsed+=delays[i];result.push(i);}
       return result;
     }
     """,
    "assert.deepEqual(api.delayPlan([1,2],3),[0,1])",
    r"""
     test("prefix deadline boundaries and zero work",()=>{
       assert.deepEqual(api.delayPlan([2,10,1],4),[0]); assert.deepEqual(core.delayPlan([10,1],2),[]);
       assert.deepEqual(api.delayPlan([0,0,1],0),[0,1]); assert.deepEqual(api.delayPlan([1,2,0],3),[0,1,2]); assert.deepEqual(api.delayPlan([],0),[]);
     });
     test("validation fractions and input preservation",()=>{
       const delays=[0.5,0.25,1]; assert.deepEqual(api.delayPlan(delays,0.75),[0,1]); assert.deepEqual(delays,[0.5,0.25,1]);
       for(const delays of [[-1],[NaN],[Infinity]])assert.throws(()=>api.delayPlan(delays,2));
       for(const deadline of [-1,NaN,Infinity])assert.throws(()=>api.delayPlan([],deadline));
       assert.throws(()=>api.delayPlan([Number.MAX_VALUE,Number.MAX_VALUE],Number.MAX_VALUE));
     });
     """,
)

_add(
    "stream-typescript-v2",
    "escaped-record-codec",
    "decodeRecord",
    "text: string",
    "Decode a pipe-delimited record where backslash escapes only pipe and backslash. Retain empty and trailing fields, preserve all other characters, and reject unknown escapes or a dangling backslash. Decode in a single left-to-right pass so an escaped backslash does not escape the following separator.",
    """
     export function decodeRecord(text:string):string[]{
       if(/\\\\(?:[^|\\\\]|$)/.test(text))throw new Error("invalid escape");
       return text.split("|").map(part=>part.replace(/\\\\([|\\\\])/g,"$1"));
     }
     """,
    """
     export function decodeRecord(text:string):string[]{
       const result=[""]; let escaped=false;
       for(const char of text){
         if(escaped){if(char!=="|"&&char!=="\\\\")throw new Error("invalid escape");result[result.length-1]+=char;escaped=false;}
         else if(char==="\\\\")escaped=true;
         else if(char==="|")result.push("");
         else result[result.length-1]+=char;
       }
       if(escaped)throw new Error("invalid escape");
       return result;
     }
     """,
    'assert.deepEqual(api.decodeRecord("a|b"),["a","b"])',
    r"""
     test("escaped delimiters backslashes and empty fields",()=>{
       assert.deepEqual(api.decodeRecord(String.raw`a\|b|c`),["a|b","c"]);
       assert.deepEqual(core.decodeRecord(String.raw`a\\|b`),["a\\","b"]);
       assert.deepEqual(api.decodeRecord("|a||"),["","a","",""]);
       assert.deepEqual(api.decodeRecord(""),[""]);
       assert.deepEqual(api.decodeRecord("é|😀"),["é","😀"]);
     });
     test("invalid escapes and repeated escaped separators",()=>{
       assert.throws(()=>api.decodeRecord("a\\")); assert.throws(()=>api.decodeRecord(String.raw`a\q`));
       assert.deepEqual(api.decodeRecord(String.raw`\|\|`),["||"]);
       assert.deepEqual(api.decodeRecord(String.raw`\\\\`),["\\\\"]);
     });
     """,
)

_add(
    "config-typescript-v2",
    "repeated-query-values",
    "parseQuery",
    "query: string",
    "Parse a query string, optionally beginning '?', into own-property arrays of strings. Decode percent escapes and '+' as space separately for each key/value, split on only the first '=', accumulate repeated keys in arrival order, accept flags as empty values, ignore empty '&' fields and reject malformed URI escapes. Prototype-looking names must remain ordinary own keys.",
    """
     export function parseQuery(query:string):Record<string,string[]>{
       const result:Record<string,string[]>=Object.create(null);
       for(const field of query.replace(/^\\?/,"").split("&")){
         if(!field)continue;
         const index=field.indexOf("=");const key=decodeURIComponent((index<0?field:field.slice(0,index)).replace(/\\+/g," "));
         const value=decodeURIComponent((index<0?"":field.slice(index+1)).replace(/\\+/g," "));
         result[key]=[value];
       }
       return result;
     }
     """,
    """
     export function parseQuery(query:string):Record<string,string[]>{
       const result:Record<string,string[]>=Object.create(null);
       for(const field of query.replace(/^\\?/,"").split("&")){
         if(!field)continue;
         const index=field.indexOf("=");const key=decodeURIComponent((index<0?field:field.slice(0,index)).replace(/\\+/g," "));
         const value=decodeURIComponent((index<0?"":field.slice(index+1)).replace(/\\+/g," "));
         (result[key]??=[]).push(value);
       }
       return result;
     }
     """,
    'assert.deepEqual({...api.parseQuery("x=1")},{x:["1"]})',
    r"""
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
     """,
)

_add(
    "config-typescript-v2",
    "safe-local-redirects",
    "localRedirect",
    "base: string, target: string",
    "Resolve redirect targets against an HTTP(S) base and allow them only when the normalized URL has exactly the same origin (scheme, hostname, effective port). Reject credentials, non-HTTP(S) schemes, cross-origin and malformed URLs. Return pathname+search+hash, preserving percent encodings; relative targets and normalized default ports are allowed.",
    """
     export function localRedirect(base:string,target:string):string{
       const source=new URL(base),destination=new URL(target,source);
       if(!["http:","https:"].includes(source.protocol)||!["http:","https:"].includes(destination.protocol)||destination.hostname!==source.hostname||destination.username||destination.password)throw new Error("unsafe redirect");
       return destination.pathname+destination.search+destination.hash;
     }
     """,
    """
     export function localRedirect(base:string,target:string):string{
       const source=new URL(base),destination=new URL(target,source);
       if(!["http:","https:"].includes(source.protocol)||!["http:","https:"].includes(destination.protocol)||destination.origin!==source.origin||source.username||source.password||destination.username||destination.password)throw new Error("unsafe redirect");
       return destination.pathname+destination.search+destination.hash;
     }
     """,
    'assert.equal(api.localRedirect("https://app.example/a","/next"),"/next")',
    r"""
     test("origin includes scheme and port",()=>{
       for(const target of ["http://app.example/a","https://app.example:444/a","//evil.example/a","https://user:pass@app.example/a","javascript:alert(1)"]) assert.throws(()=>api.localRedirect("https://app.example/base",target));
       assert.equal(core.localRedirect("https://APP.example:443/a","https://app.example/b?x=1#top"),"/b?x=1#top");
       assert.equal(api.localRedirect("http://app.example:8080/a","http://app.example:8080/b"),"/b");
     });
     test("relative normalization malformed URL and encoding",()=>{
       assert.equal(api.localRedirect("https://app.example/a/b","../c%20d?q=%2F#x"),"/c%20d?q=%2F#x");
       assert.equal(api.localRedirect("https://app.example/a","?q=1"),"/a?q=1");
       assert.throws(()=>api.localRedirect("https://user@app.example/a","https://app.example/b")); assert.throws(()=>api.localRedirect("file:///tmp/a","b")); assert.throws(()=>api.localRedirect("https://app.example/a","http://[broken"));
     });
     """,
)

_add(
    "config-typescript-v2",
    "unicode-ascii-slugs",
    "slugify",
    "value: string",
    "Generate an ASCII slug by Unicode NFKD normalization, removing combining marks, lowercasing, replacing each maximal run of non-ASCII-alphanumeric characters with one hyphen, and trimming edge hyphens. The empty result is valid. Unicode compatibility characters such as fullwidth Latin must normalize before filtering.",
    """
     export function slugify(value:string):string{
       return value.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"");
     }
     """,
    """
     export function slugify(value:string):string{
       return value.normalize("NFKD").replace(/\\p{M}+/gu,"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"");
     }
     """,
    'assert.equal(api.slugify("Hello World!"),"hello-world")',
    r"""
     test("accents compatibility marks and punctuation",()=>{
       assert.equal(api.slugify("Crème brûlée"),"creme-brulee"); assert.equal(core.slugify("Ｆｕｌｌ １２"),"full-12");
       assert.equal(api.slugify("Cafe\u0301"),"cafe"); assert.equal(api.slugify("---a__b!!!"),"a-b"); assert.equal(api.slugify("ﬃ ①"),"ffi-1");
     });
     test("empty non Latin digits and stable output",()=>{
       for(const value of ["","   ","😀","東京"]) assert.equal(api.slugify(value),"");
       assert.equal(api.slugify(" A1 B2 "),"a1-b2"); assert.equal(api.slugify(api.slugify("Ångström")),"angstrom");
     });
     """,
)

_add(
    "config-typescript-v2",
    "quoted-env-values",
    "parseEnv",
    "text: string",
    "Parse offline .env lines of KEY=VALUE with optional 'export ', blank lines and full-line comments. Keys match [A-Za-z_][A-Za-z0-9_]*; last duplicate wins. Unquoted values trim surrounding whitespace and comments beginning '#'; single/double-quoted values preserve spaces and '#', require a closing matching quote and permit only whitespace or a comment afterwards. Double quotes decode newline, carriage-return, tab, backslash and double-quote escape sequences; single quotes are literal. Reject malformed assignments and unknown double-quote escapes.",
    """
     export function parseEnv(text:string):Record<string,string>{
       const result:Record<string,string>=Object.create(null);
       for(let line of text.split(/\\r?\\n/)){
         line=line.trim();if(!line||line.startsWith("#"))continue;line=line.replace(/^export\\s+/,"");
         const match=/^([A-Za-z_][A-Za-z0-9_]*)\\s*=\\s*(.*)$/.exec(line);if(!match)throw new Error("invalid assignment");
         const raw=match[2].split("#")[0].trim();
         result[match[1]]=raw.replace(/^["']|["']$/g,"");
       }
       return result;
     }
     """,
    r"""
     export function parseEnv(text:string):Record<string,string>{
       const result:Record<string,string>=Object.create(null);
       for(let line of text.split(/\r?\n/)){
         line=line.trim();if(!line||line.startsWith("#"))continue;line=line.replace(/^export\s+/,"");
         const match=/^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/.exec(line);if(!match)throw new Error("invalid assignment");
         const raw=match[2];let value="";
         if(raw.startsWith('"')||raw.startsWith("'")){
           const quote=raw[0];let closed=false;let index=1;
           for(;index<raw.length;index++){
             const char=raw[index];
             if(char===quote){closed=true;index++;break;}
             if(char==="\\"&&quote==='"'){
               const escaped=raw[++index];const escapes:Record<string,string>={n:"\n",r:"\r",t:"\t","\\":"\\",'"':'"'};
               if(!Object.hasOwn(escapes,escaped))throw new Error("invalid escape");value+=escapes[escaped];
             }else value+=char;
           }
           if(!closed||!/^\s*(?:#.*)?$/.test(raw.slice(index)))throw new Error("invalid quote");
         }else value=raw.split("#")[0].trim();
         Object.defineProperty(result,match[1],{value,writable:true,enumerable:true,configurable:true});
       }
       return result;
     }
     """,
    'assert.deepEqual({...api.parseEnv("A=hello\\n")},{A:"hello"})',
    r"""
     test("quotes embedded hashes escaped values and duplicates",()=>{
       const text="export A=plain # comment\nB=\" x#y \" # outside\nC='a#b'\nD=\"one\\ntwo\\t\\\"q\\\"\"\nA=last\n";
       assert.deepEqual({...api.parseEnv(text)},{A:"last",B:" x#y ",C:"a#b",D:'one\ntwo\t"q"'});
       assert.deepEqual({...core.parseEnv("#comment\r\n EMPTY=\r\n")},{EMPTY:""});
       assert.equal(api.parseEnv("X='a\\nb'").X,"a\\nb");
     });
     test("malformed lines and ordinary special keys",()=>{
       for(const text of ["bad-line","1KEY=x","X=\"unclosed","X='a'junk",String.raw`X="bad\q"`])assert.throws(()=>api.parseEnv(text));
       const result=api.parseEnv("__proto__=safe\nconstructor=value"); assert.equal(Object.hasOwn(result,"__proto__"),true); assert.equal(result.__proto__,"safe");
       assert.deepEqual({...api.parseEnv("")},{});
     });
     """,
)

_add(
    "config-typescript-v2",
    "semantic-version-precedence",
    "compareVersions",
    "left: string, right: string",
    "Compare strict semantic versions and return -1, 0 or 1. Core is three nonnegative integers without leading zeroes; optional prerelease identifiers are ASCII alphanumeric/hyphen, dot-separated, with numeric identifiers disallowing leading zeroes. Numeric identifiers compare numerically and precede nonnumeric identifiers; a shorter equal-prefix prerelease precedes a longer one; release versions outrank prereleases. Ignore valid build metadata. Reject invalid syntax and preserve exact comparison of arbitrarily large numeric identifiers.",
    """
     function parts(value:string):string[]{
       if(!/^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-[0-9A-Za-z-]+(?:\\.[0-9A-Za-z-]+)*)?(?:\\+[0-9A-Za-z-]+(?:\\.[0-9A-Za-z-]+)*)?$/.test(value))throw new Error("invalid version");
       const main=value.split("+")[0];const dash=main.indexOf("-");const pre=dash<0?[]:main.slice(dash+1).split(".");
       if(pre.some(p=>/^\\d+$/.test(p)&&p.length>1&&p.startsWith("0")))throw new Error("leading zero");
       return [dash<0?main:main.slice(0,dash),...pre];
     }
     export function compareVersions(left:string,right:string):number{
       const a=parts(left).join("-"),b=parts(right).join("-");return a===b?0:a<b?-1:1;
     }
     """,
    r"""
     function parts(value:string):string[]{
       if(!/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/.test(value))throw new Error("invalid version");
       const main=value.split("+")[0];const dash=main.indexOf("-");const pre=dash<0?[]:main.slice(dash+1).split(".");
       if(pre.some(p=>/^\d+$/.test(p)&&p.length>1&&p.startsWith("0")))throw new Error("leading zero");
       return [dash<0?main:main.slice(0,dash),...pre];
     }
     export function compareVersions(left:string,right:string):number{
       const a=parts(left),b=parts(right);const ac=a[0].split("."),bc=b[0].split(".");
       for(let i=0;i<3;i++){const x=BigInt(ac[i]),y=BigInt(bc[i]);if(x!==y)return x<y?-1:1;}
       if(a.length===1||b.length===1)return a.length===b.length?0:a.length===1?1:-1;
       for(let i=1;i<Math.min(a.length,b.length);i++){
         if(a[i]===b[i])continue;const an=/^\d+$/.test(a[i]),bn=/^\d+$/.test(b[i]);
         if(an&&bn)return BigInt(a[i])<BigInt(b[i])?-1:1;if(an!==bn)return an?-1:1;return a[i]<b[i]?-1:1;
       }
       return a.length===b.length?0:a.length<b.length?-1:1;
     }
     """,
    'assert.equal(api.compareVersions("1.0.0","2.0.0"),-1)',
    r"""
     test("numeric core and prerelease ordering",()=>{
       const ordered=["1.0.0-alpha","1.0.0-alpha.1","1.0.0-alpha.2","1.0.0-alpha.10","1.0.0-beta","1.0.0","1.10.0","2.0.0"];
       for(let i=1;i<ordered.length;i++){assert.equal(api.compareVersions(ordered[i-1],ordered[i]),-1);assert.equal(core.compareVersions(ordered[i],ordered[i-1]),1);}
       assert.equal(api.compareVersions("1.0.0+build.1","1.0.0+different"),0);
       assert.equal(api.compareVersions("99999999999999999999.0.0","100000000000000000000.0.0"),-1);
     });
     test("strict syntax and numeric identifier rules",()=>{
       for(const value of ["1.0","01.0.0","1.0.0-01","1.0.0-","1.0.0+","v1.0.0","1.0.0-a..b","1.0.0\n","1.0.0\r\n"])assert.throws(()=>api.compareVersions(value,"1.0.0"));
       assert.equal(api.compareVersions("0.0.0-0","0.0.0-a"),-1);assert.equal(api.compareVersions("1.0.0-a","1.0.0-a"),0);
     });
     """,
)

_add(
    "config-typescript-v2",
    "strict-pointer-lookup",
    "lookup",
    "document: unknown, pointer: string",
    "Read a JSON pointer without losing falsy values. Empty pointer returns the root; decode ~1 then ~0, reject invalid escapes, require own object keys, and use canonical nonnegative decimal indices for arrays (no leading zero except 0, '-' or out-of-range). Missing paths throw. Return a deep copy, including for the root.",
    """
     export function lookup(document:unknown,pointer:string):unknown{
       if(pointer==="")return structuredClone(document);
       if(!pointer.startsWith("/")||/~(?![01])/.test(pointer))throw new Error("invalid pointer");
       let current:unknown=document;
       for(const encoded of pointer.slice(1).split("/")){
         const key=encoded.replace(/~1/g,"/").replace(/~0/g,"~");
         if(Array.isArray(current)){if(!/^(0|[1-9]\\d*)$/.test(key)||Number(key)>=current.length)throw new Error("missing index");current=current[Number(key)];}
         else if(current!==null&&typeof current==="object"&&Object.hasOwn(current,key))current=(current as Record<string,unknown>)[key];
         else throw new Error("missing key");
         if(!current)throw new Error("missing value");
       }
       return structuredClone(current);
     }
     """,
    """
     export function lookup(document:unknown,pointer:string):unknown{
       if(pointer==="")return structuredClone(document);
       if(!pointer.startsWith("/")||/~(?![01])/.test(pointer))throw new Error("invalid pointer");
       let current:unknown=document;
       for(const encoded of pointer.slice(1).split("/")){
         const key=encoded.replace(/~1/g,"/").replace(/~0/g,"~");
         if(Array.isArray(current)){if(!/^(0|[1-9]\\d*)$/.test(key)||Number(key)>=current.length)throw new Error("missing index");current=current[Number(key)];}
         else if(current!==null&&typeof current==="object"&&Object.hasOwn(current,key))current=(current as Record<string,unknown>)[key];
         else throw new Error("missing key");
       }
       return structuredClone(current);
     }
     """,
    'assert.equal(api.lookup({a:1},"/a"),1)',
    r"""
     test("falsy values escapes and root",()=>{
       const document={"a/b":{"~x":[false,0,"",null]}};
       for(const [index,expected] of [[0,false],[1,0],[2,""],[3,null]])assert.equal(api.lookup(document,`/a~1b/~0x/${index}`),expected);
       assert.deepEqual(core.lookup(document,""),document); assert.equal(api.lookup({"":7},"/"),7);
     });
     test("strict arrays own keys and copy isolation",()=>{
       for(const pointer of ["/arr/01","/arr/-","/arr/2","/arr/-1","/arr/0.0","/missing","/~2","not-pointer"])assert.throws(()=>api.lookup({arr:[1,2]},pointer));
       assert.throws(()=>api.lookup({},"/constructor"));const document={a:{items:[1]}};const result=api.lookup(document,"/a");result.items.push(2);assert.deepEqual(document,{a:{items:[1]}});
       assert.throws(()=>api.lookup({x:null},"/x/a"));
     });
     """,
)

_add(
    "config-typescript-v2",
    "utf8-feature-cohorts",
    "inCohort",
    "user: string, salt: string, basisPoints: number",
    "Assign users deterministically to rollout cohorts. Compute unsigned 32-bit FNV-1a over UTF-8 bytes of salt + ':' + user (offset 2166136261, prime 16777619, wrapping after each multiply), then include iff hash % 10000 < basisPoints. Validate integer basis points 0..10000. Unicode must hash as UTF-8 bytes, not UTF-16 code units.",
    """
     export function inCohort(user:string,salt:string,basisPoints:number):boolean{
       if(!Number.isInteger(basisPoints)||basisPoints<0||basisPoints>10000)throw new Error("bad rate");
       let hash=2166136261;const value=salt+":"+user;
       for(let i=0;i<value.length;i++)hash=Math.imul(hash^value.charCodeAt(i),16777619)>>>0;
       return hash%10000<basisPoints;
     }
     """,
    """
     export function inCohort(user:string,salt:string,basisPoints:number):boolean{
       if(!Number.isInteger(basisPoints)||basisPoints<0||basisPoints>10000)throw new Error("bad rate");
       let hash=2166136261;
       for(const byte of new TextEncoder().encode(salt+":"+user))hash=Math.imul(hash^byte,16777619)>>>0;
       return hash%10000<basisPoints;
     }
     """,
    'assert.equal(api.inCohort("alice","v1",0),false)',
    r"""
     test("UTF8 reference vectors and strict threshold",()=>{
       function expectedBucket(user,salt){let hash=2166136261;for(const byte of Buffer.from(salt+":"+user,"utf8"))hash=Number((BigInt(hash^byte)*16777619n)&0xffffffffn)>>>0;return hash%10000;}
       for(const [user,salt] of [["é","v1"],["😀","salt"],["東京","β"],["alice","v1"],["",""]]){
         const bucket=expectedBucket(user,salt);assert.equal(api.inCohort(user,salt,bucket),false);assert.equal(core.inCohort(user,salt,bucket+1),true);
       }
     });
     test("rate extremes determinism and validation",()=>{
       assert.equal(api.inCohort("user","salt",0),false);assert.equal(api.inCohort("user","salt",10000),true);
       assert.equal(api.inCohort("user","salt",5000),api.inCohort("user","salt",5000));
       for(const rate of [-1,10001,1.5,NaN,Infinity])assert.throws(()=>api.inCohort("a","b",rate));
     });
     """,
)

_add(
    "config-typescript-v2",
    "complete-form-errors",
    "validateSignup",
    "input: Signup",
    "Validate a signup form and return every applicable error in this fixed order: email, password, confirmation, age. Email is a string matching nonwhitespace@nonwhitespace.dot-nonwhitespace; password is a string of at least 8 characters; confirmation must exactly equal a string password; age is an integer 18..120. Do not coerce fields, stop early or mutate input. Return [] for valid input.",
    """
     export type Signup={email:unknown;password:unknown;confirmation:unknown;age:unknown};
     export function validateSignup(input:Signup):string[]{
       const errors:string[]=[];
       if(typeof input.email!=="string"||!/^\\S+@\\S+\\.\\S+$/.test(input.email))errors.push("email");
       else if(typeof input.password!=="string"||input.password.length<8)errors.push("password");
       else if(typeof input.password!=="string"||input.confirmation!==input.password)errors.push("confirmation");
       else if(typeof input.age!=="number"||!Number.isInteger(input.age)||input.age<18||input.age>120)errors.push("age");
       return errors;
     }
     """,
    """
     export type Signup={email:unknown;password:unknown;confirmation:unknown;age:unknown};
     export function validateSignup(input:Signup):string[]{
       const errors:string[]=[];
       if(typeof input.email!=="string"||!/^\\S+@\\S+\\.\\S+$/.test(input.email))errors.push("email");
       if(typeof input.password!=="string"||input.password.length<8)errors.push("password");
       if(typeof input.password!=="string"||input.confirmation!==input.password)errors.push("confirmation");
       if(typeof input.age!=="number"||!Number.isInteger(input.age)||input.age<18||input.age>120)errors.push("age");
       return errors;
     }
     """,
    'assert.deepEqual(api.validateSignup({email:"a@b.co",password:"password",confirmation:"password",age:18}),[])',
    r"""
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
     """,
)

_add(
    "config-typescript-v2",
    "specific-route-matching",
    "matchRoute",
    "routes: Route[], path: string",
    "Match slash-separated routes containing literal segments or ':name' single-segment parameters. Decode request segments exactly once and reject malformed escapes or decoded slash/backslash. Require equal segment counts. Pick the matching route with the most literal segments, preserving input order for ties; return {id,params} or null. Literal comparisons use decoded path values; do not mutate route order.",
    """
     export type Route={id:string;pattern:string};
     export function matchRoute(routes:Route[],path:string):{id:string;params:Record<string,string>}|null{
       const values=path.split("/").map(p=>decodeURIComponent(p));if(values.some(p=>/[\\/\\\\]/.test(p)))throw new Error("unsafe segment");
       for(const route of routes){
         const parts=route.pattern.split("/");if(parts.length!==values.length)continue;const params:Record<string,string>=Object.create(null);let valid=true;
         for(let i=0;i<parts.length;i++){if(parts[i].startsWith(":"))params[parts[i].slice(1)]=values[i];else if(parts[i]!==values[i])valid=false;}
         if(valid)return {id:route.id,params};
       }
       return null;
     }
     """,
    """
     export type Route={id:string;pattern:string};
     export function matchRoute(routes:Route[],path:string):{id:string;params:Record<string,string>}|null{
       const values=path.split("/").map(p=>decodeURIComponent(p));if(values.some(p=>/[\\/\\\\]/.test(p)))throw new Error("unsafe segment");
       const ordered=routes.map((route,index)=>({route,index,score:route.pattern.split("/").filter(p=>!p.startsWith(":")).length})).sort((a,b)=>b.score-a.score||a.index-b.index);
       for(const {route} of ordered){
         const parts=route.pattern.split("/");if(parts.length!==values.length)continue;const params:Record<string,string>=Object.create(null);let valid=true;
         for(let i=0;i<parts.length;i++){if(parts[i].startsWith(":"))params[parts[i].slice(1)]=values[i];else if(parts[i]!==values[i])valid=false;}
         if(valid)return {id:route.id,params};
       }
       return null;
     }
     """,
    'assert.equal(api.matchRoute([{id:"user",pattern:"/users/:id"}],"/users/a").id,"user")',
    r"""
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
     """,
)

_add(
    "config-typescript-v2",
    "casefold-header-collection",
    "collectHeaders",
    "headers: [string,string][]",
    "Collect HTTP-style headers case-insensitively into a lower-case-keyed map of string arrays, retaining first key appearance order and all duplicate values in arrival order (including Set-Cookie). Trim outer value whitespace, reject CR/LF in names or values and names outside ASCII HTTP token syntax. Prototype-looking valid names are ordinary own keys. Do not mutate inputs or combine values with commas.",
    r"""
     export function collectHeaders(headers:[string,string][]):Record<string,string[]>{
       const result:Record<string,string[]>=Object.create(null);
       for(const [name,value] of headers){
         if(!/^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/.test(name)||/[\r\n]/.test(value))throw new Error("invalid header");
         result[name.toLowerCase()]=[value.trim()];
       }
       return result;
     }
     """,
    r"""
     export function collectHeaders(headers:[string,string][]):Record<string,string[]>{
       const result:Record<string,string[]>=Object.create(null);
       for(const [name,value] of headers){
         if(!/^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/.test(name)||/[\r\n]/.test(value))throw new Error("invalid header");
         (result[name.toLowerCase()]??=[]).push(value.trim());
       }
       return result;
     }
     """,
    'assert.deepEqual({...api.collectHeaders([["X-Test"," ok "]])},{"x-test":["ok"]})',
    r"""
     test("duplicate names cookie order and trimmed values",()=>{
       const headers=[["X-A","1"],["Set-Cookie","a=1"],["x-a"," 2 "],["set-cookie","b=2"],["X-Z",""]];
       const result=api.collectHeaders(headers);assert.deepEqual({...result},{"x-a":["1","2"],"set-cookie":["a=1","b=2"],"x-z":[""]});
       assert.deepEqual(Object.keys(result),["x-a","set-cookie","x-z"]);assert.deepEqual({...core.collectHeaders([])},{});
       assert.equal(headers[2][1]," 2 ");
     });
     test("injection names and own special keys",()=>{
       for(const header of [["Bad Name","x"],["X\r\nInjected","x"],["X","a\nb"],["X","a\rb"],["","x"]])assert.throws(()=>api.collectHeaders([header]));
       const result=api.collectHeaders([["__proto__","safe"],["Constructor","value"]]);assert.equal(Object.hasOwn(result,"__proto__"),true);assert.deepEqual(result.__proto__,["safe"]);assert.deepEqual(result.constructor,["value"]);
     });
     """,
)

# Public adapters intentionally have independent integration defects for these
# tasks. Fixing only the domain function does not satisfy the public contract.
FACADE_BASELINES = {
    "atomic-transfer": "try:\n    return DOMAIN.transfer(balances, source, destination, amount)\nexcept ValueError:\n    return None",
    "csv-bank-import": "try:\n    return DOMAIN.parse_bank_csv(text)\nexcept ValueError:\n    return []",
    "currency-netting": "try:\n    return DOMAIN.net_by_currency(entries)\nexcept ValueError:\n    return {}",
    "ready-job-order": "return DOMAIN.ready_jobs(jobs, now, max(1, limit))",
    "utf8-batch-budget": "try:\n    return DOMAIN.batch_messages(messages, max_bytes)\nexcept ValueError:\n    return []",
    "strict-template-expansion": "return DOMAIN.render(template, {key: value if value else '' for key, value in values.items()})",
    "bounded-async-execution": "try:\n    return await DOMAIN.map_async(items, operation, concurrency)\nexcept RuntimeError:\n    return []",
    "decimal-money-parser": "try{return DOMAIN.parseCents(...args);}catch{return 0;}",
    "fragmented-ndjson": "return DOMAIN.parseNdjson(...args).filter(Boolean);",
    "keyed-upsert-order": "return DOMAIN.upsertRows([...args[0]].sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0));",
    "transactional-accumulator": "return DOMAIN.accumulate({...args[0]},args[1]);",
    "repeated-query-values": "const result=DOMAIN.parseQuery(...args);for(const key of Object.keys(result))if(result[key].every(value=>value===''))delete result[key];return result;",
    "safe-local-redirects": "return DOMAIN.localRedirect(...args).split('#')[0];",
    "complete-form-errors": "return DOMAIN.validateSignup(...args).slice(0,1);",
    "specific-route-matching": "return DOMAIN.matchRoute(args[0],decodeURIComponent(args[1]));",
    "casefold-header-collection": "const result=DOMAIN.collectHeaders(...args);for(const key of Object.keys(result))result[key]=[result[key].join(', ')];return result;",
}


def _spec(task_id: str) -> dict[str, Any]:
    for spec in SPECS:
        if _task_id(spec) == task_id:
            return spec
    raise ValueError(f"unknown task: {task_id}")


def _task_id(spec: dict[str, Any]) -> str:
    language, family = REPOSITORIES[spec["repository"]]
    return f"{'py' if language == 'python' else 'ts'}2-{family}-{spec['slug']}"


def task_definitions() -> list[dict[str, Any]]:
    tasks = []
    for spec in SPECS:
        language, family = REPOSITORIES[spec["repository"]]
        directory = family if language == "python" else "src"
        suffix = "py" if language == "python" else "ts"
        module = spec["slug"].replace("-", "_")
        tasks.append(
            {
                "id": _task_id(spec),
                "language": language,
                "repository": spec["repository"],
                "starting_repository": {
                    "generator": "benchmarks.corpus_v2.build_repository",
                    "repository": spec["repository"],
                    "version": CORPUS_VERSION,
                },
                "prompt": f"In this {language.title()} {family} application, {spec['request']}\n\nThe public API adapter and domain module must implement the same contract; check their interaction as well as the domain logic. Implement the change in production source. Run the existing offline smoke tests and add focused regression tests if useful. Preserve public interfaces. Do not inspect or modify benchmark machinery, grading files or files outside this repository. Do not change dependency/build configuration or weaken existing tests. Finish with a brief description and the tests you ran.",
                "target_files": [f"{directory}/{module}.{suffix}", f"{directory}/api.{suffix}"],
                "expected_symbols": [
                    f"{directory}.{module}.{spec['function']}",
                    f"{directory}.api.{spec['function']}",
                ],
                "oracle_id": spec["slug"],
                "checks": {
                    "held_out_behavior": True,
                    "public_api_integration": True,
                    "smoke": True,
                    "typescript_typecheck": language == "typescript",
                },
            }
        )
    return tasks


def _facade(spec: dict[str, Any], reference: bool = False) -> str:
    language, _ = REPOSITORIES[spec["repository"]]
    module = spec["slug"].replace("-", "_")
    name = spec["function"]
    if language == "python":
        is_async = name == "map_async"
        body = ("await " if is_async else "") + f"_{module}.{name}({spec['signature']})"
        body = "return " + body
        if not reference and spec["slug"] in FACADE_BASELINES:
            body = FACADE_BASELINES[spec["slug"]].replace("DOMAIN", f"_{module}")
        return (
            f"{'async ' if is_async else ''}def {name}({spec['signature']}):\n"
            + textwrap.indent(body, "    ")
            + "\n"
        )
    body = f"return _{module}.{name}(...args);"
    if not reference and spec["slug"] in FACADE_BASELINES:
        body = FACADE_BASELINES[spec["slug"]].replace("DOMAIN", f"_{module}")
    return f"export function {name}(...args: Parameters<typeof _{module}.{name}>): ReturnType<typeof _{module}.{name}> {{\n  {body}\n}}\n"


def _repository_files(repository_id: str) -> dict[str, str]:
    if repository_id not in REPOSITORIES:
        raise ValueError(f"unsupported repository: {repository_id}")
    language, family = REPOSITORIES[repository_id]
    specs = [spec for spec in SPECS if spec["repository"] == repository_id]
    directory = family if language == "python" else "src"
    suffix = "py" if language == "python" else "ts"
    files = {
        f"{directory}/{spec['slug'].replace('-', '_')}.{suffix}": spec["baseline"] for spec in specs
    }
    imports = []
    for spec in specs:
        module = spec["slug"].replace("-", "_")
        imports.append(
            f"from . import {module} as _{module}\n"
            if language == "python"
            else f'import * as _{module} from "./{module}.ts";\n'
        )
    files[f"{directory}/api.{suffix}"] = (
        "".join(imports) + "\n" + "\n".join(_facade(spec) for spec in specs)
    )
    smoke = (
        "python -m unittest discover -s tests -v"
        if language == "python"
        else "node --test tests/*.test.mjs"
    )
    files["README.md"] = _clean(f"""
        # {family.title()} offline application ({language})

        Domain modules implement ledger processing, workflow planning, stream
        transforms or application configuration. The public `api.{suffix}` adapter
        connects callers to those modules. All inputs are local; there are no
        credentials, services, package downloads or network requirements.

        Run smoke tests: `{smoke}`. Existing tests cover ordinary usage; callers
        also depend on boundary cases, atomic failures and detached data.
    """)
    files["AGENTS.md"] = _clean(f"""
        # Development
        Use this isolated checkout. Production source is in `{directory}/`.
        Run `{smoke}`. Preserve public interfaces and existing smoke tests.
        Keep tests offline and deterministic. Do not read or modify benchmark
        machinery or grading files outside this repository. Implement changes
        in production code, without weakening tests or changing build settings.
    """)
    files[".gitignore"] = "__pycache__/\n*.pyc\nnode_modules/\n.cache/\n"
    if language == "python":
        files[f"{family}/__init__.py"] = '"""Offline ' + family + ' application."""\n'
        tests = (
            "import asyncio\nimport unittest\nfrom datetime import datetime, timezone\nfrom "
            + family
            + " import api\n\nclass SmokeTests(unittest.TestCase):\n"
        )
        tests += "    @staticmethod\n    async def async_double(value):\n        return value*2\n\n"
        for spec in specs:
            tests += (
                f"    def test_{spec['slug'].replace('-', '_')}(self):\n        {spec['smoke']}\n\n"
            )
        files["tests/test_smoke.py"] = tests
    else:
        files["package.json"] = (
            json.dumps(
                {
                    "name": repository_id,
                    "private": True,
                    "type": "module",
                    "scripts": {"test": "node --test tests/*.test.mjs"},
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
        tests = 'import test from "node:test";\nimport assert from "node:assert/strict";\nimport * as api from "../src/api.ts";\n\n'
        for spec in specs:
            tests += f"test({json.dumps(spec['slug'])},()=>{{ {spec['smoke']}; }});\n"
        files["tests/smoke.test.mjs"] = tests
    return files


def build_repository(repository_id: str, destination: Path) -> None:
    """Write one deterministic repository; never write oracle/reference material."""
    files = _repository_files(repository_id)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError(f"destination must be empty: {destination}")
    for relative, content in files.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _oracle(spec: dict[str, Any], worktree: Path) -> str:
    language, family = REPOSITORIES[spec["repository"]]
    module = spec["slug"].replace("-", "_")
    if language == "python":
        header = "import asyncio, json, unittest\nfrom copy import deepcopy\nfrom datetime import datetime, timedelta, timezone\n"
        header += f"from {family} import api\nfrom {family} import {module} as core\n\nclass BehaviorTests(unittest.TestCase):\n"
        footer = _clean("""
            if __name__=="__main__":
                suite=unittest.defaultTestLoader.loadTestsFromTestCase(BehaviorTests)
                result=unittest.TextTestRunner(verbosity=2).run(suite)
                print("CORPUS_RESULT="+json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
                raise SystemExit(not result.wasSuccessful())
        """)
        return header + textwrap.indent(spec["cases"], "    ") + "\n" + footer
    api_uri = (worktree / "src/api.ts").resolve().as_uri()
    core_uri = (worktree / "src" / f"{module}.ts").resolve().as_uri()
    return (
        'import test from "node:test";\nimport assert from "node:assert/strict";\n'
        + f"import * as api from {json.dumps(api_uri)};\nimport * as core from {json.dumps(core_uri)};\n\n"
        + spec["cases"]
    )


def grade(task_id: str, worktree: Path, artifacts: Path) -> dict[str, Any]:
    """Run fixed external oracles, unchanged smoke tests and strict TS compilation."""
    spec = _spec(task_id)
    language, family = REPOSITORIES[spec["repository"]]
    worktree, artifacts = Path(worktree).resolve(), Path(artifacts).resolve()
    if artifacts == worktree or worktree in artifacts.parents:
        raise ValueError("grading artifacts must be outside the agent worktree")
    artifacts.mkdir(parents=True, exist_ok=True)
    protected = []
    prefix = family + "/" if language == "python" else "src/"
    for relative, content in _repository_files(spec["repository"]).items():
        if relative.startswith(prefix):
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
    tamper_free = all(item["unchanged"] for item in protected)
    passed = tamper_free and all(item["exit_code"] == 0 for item in commands)
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
        "grading_separation": "held-out files outside worktree; not cryptographically hidden",
    }
    (artifacts / "grade.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def _apply_reference_fix(task_id: str, destination: Path) -> None:
    """Validation only: write just this task's domain and adapter fixes."""
    spec = _spec(task_id)
    language, family = REPOSITORIES[spec["repository"]]
    directory = family if language == "python" else "src"
    suffix = "py" if language == "python" else "ts"
    (destination / directory / f"{spec['slug'].replace('-', '_')}.{suffix}").write_text(
        spec["reference"], encoding="utf-8"
    )
    api = destination / directory / f"api.{suffix}"
    source = api.read_text(encoding="utf-8")
    old, new = _facade(spec), _facade(spec, reference=True)
    if source.count(old) != 1:
        raise ValueError("unexpected adapter source")
    api.write_text(source.replace(old, new), encoding="utf-8")


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
        valid = (
            baseline["commands"][0]["exit_code"] != 0
            and baseline["commands"][0]["counts"].get("tests") == 2
            and all(command["exit_code"] == 0 for command in baseline["commands"][1:])
            and baseline["protected_files_unchanged"]
            and reference["passed"]
            and reference["test_count"] == 12
        )
        results.append(
            {
                "task_id": task["id"],
                "repository": task["repository"],
                "baseline_failed": not baseline["passed"],
                "reference_passed": reference["passed"],
                "valid": valid,
                "baseline": baseline,
                "reference": reference,
            }
        )
        print(json.dumps({"task_id": task["id"], "valid": valid}), flush=True)
    report = {
        "corpus_version": CORPUS_VERSION,
        "task_count": len(results),
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
