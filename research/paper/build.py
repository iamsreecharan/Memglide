"""Build the named preprint and supplement without changing class typography."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main-only', action='store_true')
    options = parser.parse_args()
    for name in ('pandoc', 'pdflatex', 'bibtex'):
        if shutil.which(name) is None:
            raise SystemExit('Missing required typesetting command: ' + name)
    env = os.environ.copy()
    env['TEXINPUTS'] = str(HERE / 'vendor/acmart') + os.pathsep + env.get('TEXINPUTS', '')
    env['BSTINPUTS'] = str(HERE / 'vendor/acmart') + os.pathsep + env.get('BSTINPUTS', '')
    env['BIBINPUTS'] = str(HERE) + os.pathsep + env.get('BIBINPUTS', '')
    env['SOURCE_DATE_EPOCH'] = '1792540800'
    fonts = ROOT / '.local/paper-writing/font-extract/usr/share/texlive/texmf-dist'
    if fonts.is_dir():
        env['TEXMFHOME'] = str(fonts)
        env['TEXMFVAR'] = str(ROOT / '.local/paper-writing/texmf-var')
        env['TEXMFCONFIG'] = str(ROOT / '.local/paper-writing/texmf-config')
    output = HERE / '.build'
    output.mkdir(exist_ok=True)
    runs = []
    documents = [('manuscript.md', 'memglide-paper')]
    if not options.main_only:
        documents.append(('supplement.md', 'memglide-supplement'))
    for source, stem in documents:
        commands = [
            ['pandoc', source, '--from=markdown+citations+raw_tex', '--to=latex',
             '--standalone', '--natbib', '--template=acm-template.tex',
             '--lua-filter=break-long-code.lua',
             '--output=' + stem + '.tex'],
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
             '-output-directory=.build', stem + '.tex'],
            ['bibtex', stem],
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
             '-output-directory=.build', stem + '.tex'],
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
             '-output-directory=.build', stem + '.tex'],
        ]
        for index, argv in enumerate(commands):
            log = output / f'{stem}-{index}.log'
            started = time.monotonic()
            with log.open('w') as stream:
                command_cwd = output if argv[0] == 'bibtex' else HERE
                result = subprocess.run(argv, cwd=command_cwd, env=env, stdout=stream,
                                        stderr=subprocess.STDOUT)
            runs.append(dict(argv=argv, exit_code=result.returncode,
                             cwd=str(command_cwd),
                             elapsed_seconds=time.monotonic() - started,
                             log=str(log.relative_to(HERE))))
            if result.returncode:
                raise SystemExit(f'Typesetting failed; inspect {log}')
        shutil.copyfile(output / (stem + '.pdf'), HERE / (stem + '.pdf'))
    files = {str(path.relative_to(HERE)): hashlib.sha256(path.read_bytes()).hexdigest()
             for _, stem in documents for path in (HERE / (stem + '.pdf'), HERE / (stem + '.tex'))}
    (output / 'build-receipt.json').write_text(json.dumps(dict(commands=runs, files_sha256=files),
                                                        indent=2) + '\n')
    print(json.dumps(dict(built=list(files), receipt='.build/build-receipt.json')))


if __name__ == '__main__':
    main()
