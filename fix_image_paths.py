#!/usr/bin/env python3
"""
Fix image paths in generated Markdown files
"""

import os
import re
from pathlib import Path

def fix_image_paths(md_file, images_dir):
    """Markdownファイル内の画像パスを修正する"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 画像ファイルのリストを取得
    base_name = Path(md_file).stem
    images_path = Path(images_dir)
    if images_path.exists():
        image_files = list(images_path.glob(f'{base_name}_image_*.png'))
        image_files.sort()

        # Markdown内の画像参照を検索
        picture_refs = re.findall(r'!\[\]\((_page_\d+_Picture_\d+\.jpeg)\)', content)
        figure_refs = re.findall(r'!\[\]\((_page_\d+_Figure_\d+\.jpeg)\)', content)
        all_refs = picture_refs + figure_refs

        print(f'  見つかった画像参照: {all_refs}')
        print(f'  利用可能な画像ファイル: {[f.name for f in image_files]}')

        # 画像マッピングを作成 (順番に対応させる)
        image_mapping = {}
        for idx, ref in enumerate(all_refs):
            if idx < len(image_files):
                image_mapping[ref] = f'images/{image_files[idx].name}'

        print(f'  マッピング: {image_mapping}')

        # Markdown内の画像参照を置換
        modified = False
        for old_name, new_path in image_mapping.items():
            pattern = r'!\[\]\(' + re.escape(old_name) + r'\)'
            replacement = f'![{old_name}]({new_path})'
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                print(f'  修正: {old_name} -> {new_path}')

        if modified:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✅ {md_file} を修正しました')
        else:
            print(f'ℹ️ {md_file} は修正不要です')
    else:
        print(f'⚠️ 画像ディレクトリが見つかりません: {images_dir}')

def main():
    """メイン処理"""
    docs_dir = 'docs'
    images_dir = 'docs/images'

    for md_file in Path(docs_dir).glob('*.md'):
        print(f'処理中: {md_file}')
        fix_image_paths(md_file, images_dir)

if __name__ == "__main__":
    main()