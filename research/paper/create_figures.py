"""Render the amended v7 comparison from portable, published numerical data.

The renderer uses recorded estimates and intervals; it performs no significance
analysis, model calls, or changes to experimental evidence. The historical v6
figures are retained under their original filenames.
"""
from __future__ import annotations

# Matplotlib must be configured before it is imported.
# ruff: noqa: E402
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_RESULTS = ROOT / 'research/results/router-v7-20261021'
FROZEN_ANALYSIS_SHA256 = 'fcd5ded7f3c73799cad03a1fda0554294bc974ba34625b6680ee323ef5c94b26'
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.local/paper-writing/matplotlib'))
os.environ.setdefault('SOURCE_DATE_EPOCH', '1792540800')

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

METRICS = ('uniform_long_usd', 'workflow_wall_seconds')
COMPONENTS = (
    ('native_wall_seconds', 'Native Codex execution', '#72a08b'),
    ('index_wall_seconds', 'Indexing', '#2e6f9e'),
    ('verification_wall_seconds', 'Public verification', '#d29240'),
    ('cleanup_wall_seconds', 'Verification cleanup', '#e7bf83'),
    ('installed_launcher_preparation_wall_seconds', 'Launcher preparation', '#8db0c9'),
    ('other', 'Other local overhead', '#b5b5b5'),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_data(analysis: Path | None, results_dir: Path):
    if analysis is not None:
        if sha256(analysis) != FROZEN_ANALYSIS_SHA256:
            raise ValueError('The supplied frozen analysis has an unexpected SHA-256')
        data = json.loads(analysis.read_text())
        if not data['confirmatory_panel_integrity']['valid']:
            raise ValueError('Complete main-panel integrity is required')
        if len(data['all_scheduled_rows']) != 112:
            raise ValueError('This rendering requires the complete 112-session main panel')
        paired = {key: data['primary'][key]['paired_task_values'] for key in METRICS}
        inputs = {analysis.name: sha256(analysis)}
        return data, paired, inputs
    summary = results_dir / 'summary.json'
    paired_csv = results_dir / 'paired-28-tasks.csv'
    data = json.loads(summary.read_text())
    with paired_csv.open(newline='') as stream:
        records = list(csv.DictReader(stream))
    paired = {}
    for metric, prefix in zip(METRICS, ('cost', 'workflow')):
        paired[metric] = [
            {'task_id': row['task_id'], 'A': float(row[prefix + '_A']),
             'M': float(row[prefix + '_M']), 'delta': float(row[prefix + '_delta'])}
            for row in records
        ]
    inputs = {summary.name: sha256(summary), paired_csv.name: sha256(paired_csv)}
    return data, paired, inputs


def save_figure(figure, output: Path, stem: str):
    for extension in ('pdf', 'svg', 'png'):
        figure.savefig(output / f'{stem}.{extension}', dpi=220,
                       bbox_inches='tight', metadata={'Creator': 'Memglide recorded-data renderer'})
    plt.close(figure)


def paired_figure(data, paired, output):
    tasks = sorted(row['task_id'] for row in paired[METRICS[0]])
    if len(tasks) != 28 or len(set(tasks)) != 28:
        raise ValueError('Exactly 28 distinct main-panel tasks are required')
    figure, axes = plt.subplots(1, 2, figsize=(7.2, 6.8), sharey=True)
    for axis, metric, title, xlabel in zip(
        axes, METRICS,
        ('Token-tariff cost', 'Full workflow time'),
        ('Memglide minus Codex (USD / session)', 'Memglide minus Codex (seconds / session)'),
    ):
        points = {row['task_id']: row for row in paired[metric]}
        if set(points) != set(tasks):
            raise ValueError('Task identities differ between endpoints')
        axis.axvline(0, color='#555555', lw=.85, zorder=0)
        for y, task in enumerate(tasks):
            delta = points[task]['delta']
            if abs(points[task]['M'] - points[task]['A'] - delta) > 1e-10:
                raise ValueError('Published paired difference does not match arm means')
            axis.hlines(y, min(0, delta), max(0, delta), color='#c8d4df', lw=1.1)
            axis.plot(delta, y, 'o', ms=4, color='#235f91', zorder=3)
        estimate = data['primary'][metric]['primary_t']
        low, high = estimate['pointwise_95_t_interval']
        y = len(tasks) + .65
        axis.axhline(len(tasks) - .25, color='#dddddd', lw=.7)
        axis.hlines(y, low, high, color='#161616', lw=1.5)
        axis.plot(estimate['mean_delta'], y, 'D', color='#161616', ms=5)
        axis.set_title(title, fontsize=10, weight='semibold', pad=9)
        axis.set_xlabel(xlabel, fontsize=8.5)
        axis.grid(axis='x', alpha=.15)
        axis.tick_params(axis='both', labelsize=8)
        axis.set_ylim(len(tasks) + 1.55, -1)
    axes[0].set_yticks([*range(len(tasks)), len(tasks) + .65], tasks + ['28-task mean'])
    figure.legend(handles=[
        Line2D([], [], marker='o', ls='', color='#235f91', ms=4,
               label='Task mean: two repetitions per arm'),
        Line2D([], [], marker='D', color='#161616', ms=4,
               label='Panel mean and nominal 95% paired-t interval'),
    ], loc='lower center', bbox_to_anchor=(.5, -.002), ncol=1,
       frameon=False, fontsize=8)
    figure.tight_layout(rect=(0, .065, 1, 1), w_pad=2)
    save_figure(figure, output, 'v7-paired-differences')


def workflow_figure(data, output):
    means = {}
    for arm in ('A', 'M'):
        metrics = data['arms'][arm]['metrics']
        means[arm] = {key: metrics[key]['known_mean'] for key, _, _ in COMPONENTS if key != 'other'}
        means[arm]['workflow'] = metrics['workflow_wall_seconds']['known_mean']
        means[arm]['other'] = means[arm]['workflow'] - sum(
            means[arm][key] for key, _, _ in COMPONENTS if key != 'other')
        if means[arm]['other'] < -1e-8:
            raise ValueError('Recorded components exceed total workflow time')
        means[arm]['local'] = means[arm]['workflow'] - means[arm]['native_wall_seconds']
    figure, axes = plt.subplots(1, 2, figsize=(7.2, 3.0),
                                gridspec_kw={'width_ratios': [1.55, 1]}, sharey=True)
    labels = ['A: Codex', 'M: Memglide']
    for axis, local in zip(axes, (False, True)):
        left = [0., 0.]
        for key, label, color in COMPONENTS:
            if local and key == 'native_wall_seconds':
                continue
            values = [max(0., means[arm][key]) for arm in ('A', 'M')]
            axis.barh(range(2), values, left=left, color=color, label=label,
                      height=.52, linewidth=.3, edgecolor='white')
            left = [x + y for x, y in zip(left, values)]
        for y, arm in enumerate(('A', 'M')):
            value = means[arm]['local' if local else 'workflow']
            axis.text(value + (.08 if local else .65), y, f'{value:.2f} s',
                      va='center', fontsize=8)
        axis.set_xlim(0, max(left) * (1.25 if local else 1.15))
        axis.set_title('Local overhead (zoom)' if local else 'Complete workflow',
                       fontsize=10, weight='semibold', pad=8)
        axis.set_xlabel('Mean seconds per session', fontsize=8.5)
        axis.grid(axis='x', alpha=.12)
        axis.set_axisbelow(True)
        axis.tick_params(axis='both', labelsize=8)
        axis.set_yticks(range(2), labels)
        axis.set_ylim(1.6, -.6)
    handles, names = axes[0].get_legend_handles_labels()
    figure.legend(handles, names, loc='lower center', ncol=3,
                  frameon=False, fontsize=7.8, bbox_to_anchor=(.5, -.01))
    figure.tight_layout(rect=(0, .19, 1, 1), w_pad=1.5)
    save_figure(figure, output, 'v7-workflow-components')
    return means


def architecture_figure(output):
    figure, axis = plt.subplots(figsize=(7.2, 5.7))
    axis.set_xlim(0, 7.2)
    axis.set_ylim(0, 5.7)
    axis.axis('off')
    blue = '#e7f0f7'
    orange = '#fff0db'
    gray = '#f1f1f1'

    def box(x, y, width, height, text, fill=blue, size=8.5):
        axis.add_patch(FancyBboxPatch((x - width/2, y - height/2), width, height,
                                     boxstyle='round,pad=0.045,rounding_size=0.05',
                                     facecolor=fill, edgecolor='#5b7182', lw=.8))
        axis.text(x, y, text, ha='center', va='center', fontsize=size,
                  linespacing=1.35)

    def arrow(start, end, color='#46647b', dashed=False, connection='arc3,rad=0'):
        axis.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=10,
                                      color=color, lw=.95,
                                      linestyle='--' if dashed else '-',
                                      connectionstyle=connection))

    box(3.6, 5.28, 5.6, .55, 'Same task and approved current Git repository', fill=gray, size=9)
    box(1.35, 4.35, 2.25, .63, 'A: Codex pass-through\nOriginal task; preparation off')
    box(5.02, 4.35, 3.05, .63, 'M: bounded source selection\nLexical + static syntax evidence')
    box(5.02, 3.40, 3.05, .63, 'Selected complete current files\nor source-selection abstention')
    box(5.02, 2.35, 3.05, .78,
        'Optional verified-command card\nMay remain active after source abstention\nCommands precede source when supplied', size=8)
    box(1.35, 2.35, 2.25, .92,
        'Separately authorized verifier\nPublic commands + baseline counts\nPinned receipt outside source', fill=orange, size=8)
    box(5.02, 1.27, 3.05, .65, 'Source / receipt / prompt revalidation\nExact handoff to installed Codex', size=8)
    box(3.6, .36, 5.55, .53, 'Same native Codex CLI and external coding model', fill=gray, size=9)
    arrow((2.15, 5.00), (1.35, 4.70))
    arrow((5.0, 5.00), (5.02, 4.70))
    arrow((5.02, 4.00), (5.02, 3.76))
    arrow((5.02, 3.05), (5.02, 2.78))
    arrow((2.52, 2.35), (3.44, 2.35), color='#a16e2b')
    arrow((5.02, 1.91), (5.02, 1.63))
    arrow((5.02, .91), (4.72, .66))
    # Route A around, rather than through, separately authorized verification.
    axis.plot([1.35, .04, .04], [4.0, 4.0, .66], color='#46647b', lw=.95)
    arrow((.04, .66), (.87, .36))
    axis.text(.52, 3.45, 'A', fontsize=8, color='#46647b', ha='center')
    figure.tight_layout(pad=.3)
    save_figure(figure, output, 'v7-architecture')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis', type=Path,
                        help='Original frozen analysis (SHA-256 checked); normally use portable results')
    parser.add_argument('--results-dir', type=Path, default=DEFAULT_RESULTS)
    parser.add_argument('--output-dir', type=Path, default=HERE / 'figures')
    options = parser.parse_args()
    data, paired, inputs = load_data(options.analysis, options.results_dir)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'pdf.fonttype': 42, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'memglide-v7-20261021'})
    options.output_dir.mkdir(parents=True, exist_ok=True)
    paired_figure(data, paired, options.output_dir)
    means = workflow_figure(data, options.output_dir)
    architecture_figure(options.output_dir)
    receipt = {
        'frozen_analysis_sha256': FROZEN_ANALYSIS_SHA256,
        'inputs_sha256': inputs,
        'renderer_sha256': sha256(Path(__file__)),
        'main_panel_sessions': 112,
        'task_clusters': 28,
        'workflow_component_means': means,
        'figure_scope': 'Recorded data and nominal frozen intervals; no new hypothesis tests, model calls, or outcome selection',
        'files_sha256': {p.name: sha256(p) for pattern in
                         ('v7-paired-differences.*', 'v7-workflow-components.*', 'v7-architecture.*')
                         for p in sorted(options.output_dir.glob(pattern))},
    }
    (options.output_dir / 'v7-generation-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'figures': len(receipt['files_sha256']), 'additional_model_calls': 0}))


if __name__ == '__main__':
    main()
