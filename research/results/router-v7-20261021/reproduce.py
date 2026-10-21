"""Reproduce the published statistics from the portable CSVs; no model calls."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(actual, expected, name):
    require(
        math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10),
        f"{name}: {actual} != {expected}",
    )


def truth(value):
    require(value in ("True", "False"), "Missing or invalid Boolean")
    return value == "True"


def table(name):
    with (HERE / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def verify_checksums():
    path = HERE / "checksums.json"
    if path.exists():
        for name, expected in json.loads(path.read_text())["files"].items():
            target = HERE / name
            require(
                not target.is_symlink() and target.is_file(), "Missing/linked artifact: " + name
            )
            require(
                hashlib.sha256(target.read_bytes()).hexdigest() == expected["sha256"],
                "Changed artifact: " + name,
            )


def paired(rows, metric):
    tasks = sorted({row["task_id"] for row in rows})
    values = []
    for task in tasks:
        means = {}
        for arm in ("A", "M"):
            cells = [row for row in rows if row["task_id"] == task and row["configuration"] == arm]
            require(
                {int(row["repeat"]) for row in cells} == {1, 2} and len(cells) == 2,
                "Missing/duplicate paired cell",
            )
            means[arm] = sum(float(row[metric]) for row in cells) / 2
        values.append((task, means["A"], means["M"], means["M"] - means["A"]))
    return values


def calculate(values):
    a = np.asarray([v[1] for v in values])
    m = np.asarray([v[2] for v in values])
    delta = m - a
    n = len(delta)
    mean = float(np.mean(delta))
    sd = float(np.std(delta, ddof=1))
    se = sd / math.sqrt(n)
    require(n == 28 and se > 0, "Primary analysis needs 28 complete nondegenerate task differences")
    statistic = mean / se
    margin = float(stats.t.ppf(0.975, n - 1)) * se
    p = float(stats.t.cdf(statistic, n - 1))
    return {
        "n": n,
        "df": n - 1,
        "A_mean": float(np.mean(a)),
        "M_mean": float(np.mean(m)),
        "mean_delta": mean,
        "paired_sd": sd,
        "standard_error": se,
        "t_statistic": statistic,
        "one_sided_p_M_less_A": p,
        "pointwise_95_t_interval": [mean - margin, mean + margin],
        "relative_change_percent": mean / float(np.mean(a)) * 100,
        "passes_one_sided_alpha_0_025_and_upper_below_zero": p <= 0.025 and mean + margin < 0,
    }


def bootstrap(values):
    rng = random.Random(20261102)
    n = len(values)
    deltas = []
    relative = []
    for _ in range(10000):
        selected = [values[rng.randrange(n)] for _ in range(n)]
        a = sum(row[1] for row in selected) / n
        m = sum(row[2] for row in selected) / n
        deltas.append(m - a)
        relative.append((m - a) / a * 100)
    return {
        "mean_delta_percentile_95_interval": np.quantile(
            deltas, [0.025, 0.975], method="linear"
        ).tolist(),
        "relative_change_percentile_95_interval_percent": np.quantile(
            relative, [0.025, 0.975], method="linear"
        ).tolist(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    verify_checksums()
    summary = json.loads((HERE / "analysis-summary.json").read_text())
    rows = table("primary-112-runs.csv")
    all_rows = table("all-128-runs.csv")
    require(len(rows) == 112 and len(all_rows) == 128, "Wrong panel size")
    require(
        [int(row["order"]) for row in all_rows] == list(range(17, 145)), "Wrong complete-pool order"
    )
    require(len({row["run_id"] for row in all_rows}) == 128, "Repeated run ID")
    by_id = {row["run_id"]: row for row in all_rows}
    for row in rows:
        require(
            row == by_id[row["run_id"]] and truth(row["primary"]),
            "Primary is not the exact complete-pool subset",
        )
    require(sum(truth(row["primary"]) for row in all_rows) == 112, "Wrong primary membership")
    for row in all_rows:
        for key in (
            "native_valid",
            "native_identity_valid",
            "usage_complete",
            "grade_valid",
            "source_policy_valid",
            "native_transport_valid",
            "evidence_preservation_valid",
            "source_protection_valid",
            "source_unchanged",
            "grade_infrastructure_valid",
            "grading_source_reconstructed",
            "reconstructed_source_unchanged",
            "reconstructed_source_matches_native",
        ):
            require(truth(row[key]), "Unattested public measurement: " + row["run_id"] + "/" + key)
        require(not truth(row["model_generated_caches_reused"]), "Model cache reused for grading")
        i, c, o = (
            int(row[key]) for key in ("input_tokens", "cached_input_tokens", "output_tokens")
        )
        require(i > 0 and o > 0 and 0 <= c <= i, "Invalid token accounting")
        close(
            float(row["uniform_long_usd"]),
            ((i - c) * 5 + c * 0.2 + o * 15) / 1000000,
            "Per-run uniform tariff",
        )
    output = {
        "version": "portable-v7-statistical-reproduction-1",
        "model_calls": 0,
        "all_checks_pass": True,
        "primary_rows": 112,
        "complete_pool_rows": 128,
        "paired_task_clusters": 28,
        "primary": {},
    }
    paired_table = {row["task_id"]: row for row in table("paired-28-tasks.csv")}
    for metric, prefix in (("uniform_long_usd", "cost"), ("workflow_wall_seconds", "workflow")):
        values = paired(rows, metric)
        result = calculate(values)
        expected = summary["primary"][metric]["primary_t"]
        for key in (
            "A_mean",
            "M_mean",
            "mean_delta",
            "paired_sd",
            "standard_error",
            "t_statistic",
            "one_sided_p_M_less_A",
            "relative_change_percent",
        ):
            close(result[key], expected[key], metric + "/" + key)
        for actual, wanted in zip(
            result["pointwise_95_t_interval"], expected["pointwise_95_t_interval"]
        ):
            close(actual, wanted, metric + "/CI")
        for task, a, m, delta in values:
            for suffix, actual in (("A", a), ("M", m), ("delta", delta)):
                close(actual, float(paired_table[task][prefix + "_" + suffix]), "Paired CSV")
        result["bootstrap_sensitivity"] = bootstrap(values)
        for key, actual in result["bootstrap_sensitivity"].items():
            for x, y in zip(actual, summary["primary"][metric]["bootstrap_sensitivity"][key]):
                close(x, y, metric + "/bootstrap")
        output["primary"][metric] = result
    output["quality"] = {}
    for arm in ("A", "M"):
        successes = sum(truth(r["strict_success"]) for r in rows if r["configuration"] == arm)
        pool_successes = sum(
            truth(r["strict_success"]) for r in all_rows if r["configuration"] == arm
        )
        require(
            successes == summary["quality"]["strict_success_counts_of_56"][arm],
            "Primary quality mismatch",
        )
        require(
            pool_successes == summary["pooled_all128_descriptive"][arm]["strict_successes_known"],
            "Pool quality mismatch",
        )
        output["quality"][arm] = {
            "primary_strict_successes": successes,
            "primary_sessions": 56,
            "complete_pool_strict_successes": pool_successes,
            "complete_pool_sessions": 64,
        }
        for metric in (
            "uniform_long_usd",
            "workflow_wall_seconds",
            "native_wall_seconds",
            "input_tokens",
            "cached_input_tokens",
            "output_tokens",
        ):
            total = sum(float(r[metric]) for r in rows if r["configuration"] == arm)
            close(
                total, summary["arms"][arm]["metrics"][metric]["complete_total"], metric + "/total"
            )
    harmful = sum(
        truth(r["A_both_pass"]) and not truth(r["M_both_pass"]) for r in paired_table.values()
    )
    upper = float(stats.beta.ppf(0.975, harmful + 1, 28 - harmful))
    close(
        upper,
        summary["quality"]["harmful_loss_exact_one_sided_97_5_upper"],
        "Harmful-discordance bound",
    )
    output["harmful_discordant_tasks"] = harmful
    output["harmful_loss_exact_one_sided_97_5_upper"] = upper
    joint = all(
        v["passes_one_sided_alpha_0_025_and_upper_below_zero"] for v in output["primary"].values()
    )
    joint = (
        joint
        and output["quality"]["M"]["primary_strict_successes"]
        >= output["quality"]["A"]["primary_strict_successes"]
    )
    require(
        joint == summary["joint_decision"]["joint_efficiency_supported_on_this_panel"],
        "Decision mismatch",
    )
    output["joint_efficiency_supported_on_this_panel"] = joint
    text = json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if options.output:
        options.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
