#!/usr/bin/env python3
import os
from pathlib import Path

docs_dir = 'docs'
for md_file in Path(docs_dir).glob('*.md'):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '![](' in line:
                print(f'{md_file}:{i}: {line.strip()}')