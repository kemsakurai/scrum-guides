#!/usr/bin/env python3
from pathlib import Path
import re

docs_dir = 'docs'
for md_file in Path(docs_dir).glob('*.md'):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        image_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        if image_refs:
            print(f'{md_file.name}:')
            for alt, path in image_refs:
                print(f'  {alt} -> {path}')
            print()