#!/usr/bin/env python3
"""
Markdownファイルを最適化してファイルサイズを削減するスクリプト
体裁は変えずに以下の最適化を実行：
1. 連続する3行以上の空行を2行に削減
2. 行末の空白を削除
3. 不要な空のテーブル行を削除
4. コメント行（/* ... */）を削除
"""

import re
from pathlib import Path


def optimize_markdown(content):
    """Markdownコンテンツを最適化"""
    lines = content.split('\n')
    optimized_lines = []
    empty_line_count = 0
    
    for line in lines:
        # 行末の空白を削除
        line = line.rstrip()
        
        # コメント行をスキップ（/* Lines ... omitted */など）
        if re.match(r'^\s*/\*.*\*/\s*$', line):
            continue
        
        # 空のテーブル行をスキップ
        if re.match(r'^\s*\|\s*\|.*\|\s*$', line):
            # すべてのセルが空の場合
            cells = line.split('|')
            non_empty_cells = [c for c in cells if c.strip()]
            if not non_empty_cells:
                continue
        
        # 空行のカウント
        if not line:
            empty_line_count += 1
            # 最大2行の空行まで許可
            if empty_line_count <= 2:
                optimized_lines.append(line)
        else:
            empty_line_count = 0
            optimized_lines.append(line)
    
    # 最後の空行を削除
    while optimized_lines and not optimized_lines[-1]:
        optimized_lines.pop()
    
    return '\n'.join(optimized_lines) + '\n'


def optimize_file(filepath):
    """ファイルを最適化"""
    path = Path(filepath)
    
    # 元のサイズを取得
    original_size = path.stat().st_size
    
    # ファイルを読み込み
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 最適化
    optimized_content = optimize_markdown(content)
    
    # ファイルに書き込み
    with open(path, 'w', encoding='utf-8') as f:
        f.write(optimized_content)
    
    # 新しいサイズを取得
    new_size = path.stat().st_size
    
    reduction = original_size - new_size
    percentage = (reduction / original_size * 100) if original_size > 0 else 0
    
    return original_size, new_size, reduction, percentage


def main():
    docs_dir = Path('docs')
    
    if not docs_dir.exists():
        print("❌ docs/ ディレクトリが見つかりません")
        return
    
    md_files = sorted(docs_dir.glob('*.md'))
    
    if not md_files:
        print("❌ Markdownファイルが見つかりません")
        return
    
    print("📝 Markdownファイルの最適化を開始します...\n")
    
    total_original = 0
    total_new = 0
    
    for md_file in md_files:
        original_size, new_size, reduction, percentage = optimize_file(md_file)
        total_original += original_size
        total_new += new_size
        
        print(f"✓ {md_file.name}")
        print(f"  元のサイズ: {original_size:,} bytes")
        print(f"  新サイズ  : {new_size:,} bytes")
        print(f"  削減量    : {reduction:,} bytes ({percentage:.1f}%)\n")
    
    total_reduction = total_original - total_new
    total_percentage = (total_reduction / total_original * 100) if total_original > 0 else 0
    
    print("=" * 50)
    print(f"合計削減量: {total_reduction:,} bytes ({total_percentage:.1f}%)")
    print(f"元の合計  : {total_original:,} bytes")
    print(f"新しい合計: {total_new:,} bytes")
    print("\n✅ 最適化が完了しました！")


if __name__ == '__main__':
    main()
