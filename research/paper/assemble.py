"""Assemble the named preprint from the reviewed section sources."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ABSTRACT = """Providing repository context before a coding task can reduce search work,
but preparation and verification also consume time. Memglide selects bounded
current-source context using lexical and static syntax evidence and can supply
verified public commands even when source selection abstains. We compare the
installed workflow with pass-through Codex on an amended fixed panel of 28
author-designed feature tasks, with two repetitions per method: 112 native
sessions. Both methods pass 54 of 56 frozen strict assessments. At fixed prices
applied to measured tokens, mean API-equivalent cost is $0.16094 for Codex and
$0.15316 with Memglide, an observed 4.84% reduction. Mean full-workflow time is
59.59 and 60.29 seconds, respectively, an observed 1.17% increase. Paired
task-level 95% intervals for Memglide minus Codex are [-$0.02524, $0.00968]
and [-3.02, 4.42] seconds; neither resource-superiority test passes. Native
execution is 2.06 seconds shorter on average, offset by 2.75 seconds of added
workflow overhead. All 128 sessions in the completed comparison pool have
valid measurement and grading records; 16 previously exposed task sessions
remain descriptive. Source-policy and transport-handling amendments followed
partial collection, so inference is nominal rather than a fully prospective
confirmation. The study identifies an overhead bottleneck and preserves the
uncertainty: token-price estimates are not invoices, equal observed success
counts do not establish quality equivalence, and joint cost-and-speed
superiority is not established."""


def figure(name, caption, description, width='\\textwidth'):
    return ('\n\\begin{figure}[tbp]\n\\centering\n'
            '\\includegraphics[width=' + width + ',height=0.70\\textheight,keepaspectratio]{figures/' + name + '.pdf}\n'
            '\\caption{' + caption + '}\n\\Description{' + description + '}\n'
            '\\end{figure}\n')


def main():
    title = 'Memglide: Measuring the Cost and Latency of Bounded Repository Context for Coding Agents'
    metadata = '---\ntitle: "' + title + '"\nabstract: |\n' + ''.join(
        '  ' + line + '\n' for line in ABSTRACT.splitlines()) + '---\n\n'
    pieces = [metadata]
    for stem in ('introduction', 'related-work', 'system', 'methods', 'development',
                 'results', 'limitations', 'conclusion', 'data-availability', 'assistance'):
        pieces.append((HERE / (stem + '.md')).read_text().rstrip() + '\n')
        if stem == 'system':
            pieces.append(figure('v7-architecture',
                "The evaluated A/M workflow. A disables preparation. M uses bounded source selection and "
                "opt-in verified commands, including a commands-only route after source abstention. "
                "The separately authorized verifier produces baseline facts; it is not an automatic model call. "
                "Interactive memory and dashboard services are outside the measured path.",
                "Pass-through Codex is compared with a launcher that may supply source and commands, "
                "commands alone, or the unchanged task. Verified receipts and current-source checks precede "
                "the same external coding agent.", '.95\\textwidth'))
        if stem == 'results':
            pieces.append(figure('v7-paired-differences',
                "Task-level Memglide-minus-Codex differences for all 28 primary tasks, averaging two repeats "
                "per method. Negative values favor Memglide. The aggregate mean and nominal 95\\% paired-t "
                "interval use tasks as clusters; both resource intervals cross zero.",
                "Two panels show each task's token-price difference and complete-workflow time difference. "
                "The overall mean cost is lower and overall workflow time higher; both intervals include zero."))
            pieces.append(figure('v7-workflow-components',
                "Mean complete-workflow components over 56 sessions per method. Fresh indexing, public "
                "baseline verification, cleanup and launcher preparation are included. Other overhead is the "
                "workflow total less nonoverlapping recorded components. Native execution includes process "
                "handling and external-model waiting; it is not isolated inference latency.",
                "Two stacked bars compare Codex and Memglide. Native execution is shorter with Memglide, "
                "while additional preparation makes the complete workflow slightly longer."))
    (HERE / 'manuscript.md').write_text('\n\n'.join(pieces))
    print('Assembled manuscript.md from section sources; no model calls.')


if __name__ == '__main__':
    main()
