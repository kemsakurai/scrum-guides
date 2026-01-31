#!/usr/bin/env python3
"""
Scrum Guides PDF to Markdown Converter

このスクリプトは、config.jsonで定義されたスクラムガイドPDFをダウンロードし、
marker-pdfを使用してMarkdown形式に変換します。

機能:
- PDFのダウンロードとMarkdown変換
- 画像の自動抽出と参照パス修正
- Markdownの最適化（空行削減、行末空白削除など）
- 画像参照の検証
- 特定ファイルのみの処理
- バックアップ機能
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path
from datetime import datetime
import requests
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered


def load_config(config_path: str = "config.json") -> dict:
    """設定ファイルを読み込む"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ エラー: {config_path} が見つかりません")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ エラー: {config_path} の解析に失敗しました: {e}")
        sys.exit(1)


def ensure_directories(config: dict) -> None:
    """必要なディレクトリを作成する"""
    dirs = [
        config.get("output_dir", "docs"),
        config.get("image_dir", "docs/images"),
        config.get("temp_dir", "temp"),
        "backups",
    ]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"✅ ディレクトリを作成しました: {', '.join(dirs)}")


def download_pdf(url: str, output_path: str) -> None:
    """PDFファイルをダウンロードする"""
    try:
        print(f"  📥 ダウンロード中: {url}")
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\r  進捗: {progress:.1f}%", end="", flush=True)
        
        print()  # 改行
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  ✅ ダウンロード完了 ({file_size:.2f} MB)")
    except requests.exceptions.RequestException as e:
        print(f"\n  ❌ ダウンロードエラー: {e}")
        raise


def optimize_markdown_content(content: str) -> str:
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


def backup_markdown_file(md_path: str) -> str:
    """Markdownファイルをバックアップ"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = Path(md_path).name
    backup_path = backup_dir / f"{filename}.{timestamp}.bak"
    
    shutil.copy2(md_path, backup_path)
    return str(backup_path)


def optimize_markdown_file(md_path: str) -> tuple[int, int]:
    """Markdownファイルを最適化（バックアップを作成）"""
    path = Path(md_path)
    
    if not path.exists():
        print(f"  ⚠️  ファイルが見つかりません: {md_path}")
        return 0, 0
    
    # 元のサイズを取得
    original_size = path.stat().st_size
    
    # バックアップを作成
    backup_path = backup_markdown_file(md_path)
    print(f"  💾 バックアップ作成: {backup_path}")
    
    # ファイルを読み込み
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 最適化
    optimized_content = optimize_markdown_content(content)
    
    # ファイルに書き込み
    with open(path, 'w', encoding='utf-8') as f:
        f.write(optimized_content)
    
    # 新しいサイズを取得
    new_size = path.stat().st_size
    
    return original_size, new_size


def verify_images(md_path: str, image_dir: str) -> dict:
    """画像参照の検証"""
    result = {
        'file': Path(md_path).name,
        'references': [],
        'missing': [],
        'found': []
    }
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        image_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        
        for alt, path in image_refs:
            result['references'].append((alt, path))
            
            # 相対パスを解決
            full_path = Path(md_path).parent / path
            if full_path.exists():
                result['found'].append(path)
            else:
                result['missing'].append(path)
    
    return result


def convert_pdf_to_markdown(pdf_path: str, output_md_path: str, image_dir: str) -> None:
    """marker-pdfを使用してPDFをMarkdownに変換する"""
    try:
        print(f"  🔄 Markdown変換中...")
        
        # marker-pdfの変換器を初期化
        converter = PdfConverter(
            artifact_dict=create_model_dict(),
        )
        
        # PDFを変換
        rendered = converter(pdf_path)
        markdown_text, metadata, images = text_from_rendered(rendered)
        
        # Markdownファイルを保存
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        
        print(f"  ✅ Markdown保存完了: {output_md_path}")
        
        # 画像を保存し、名前マッピングを作成
        image_mapping = {}
        if images:
            print(f"  🖼️  画像を保存中... ({len(images)}枚)")
            Path(image_dir).mkdir(parents=True, exist_ok=True)
            
            base_name = Path(output_md_path).stem
            for idx, (img_name, img_data) in enumerate(images.items()):
                img_filename = f"{base_name}_image_{idx + 1}.png"
                img_path = os.path.join(image_dir, img_filename)
                
                # img_dataがPIL Imageの場合、bytesに変換
                if hasattr(img_data, 'save'):
                    # PIL Imageの場合
                    img_data.save(img_path, 'PNG')
                else:
                    # bytesの場合
                    with open(img_path, "wb") as img_file:
                        img_file.write(img_data)
                
                # マッピングを作成: PDF内の画像名 -> 保存したファイル名
                image_mapping[img_name] = f"images/{img_filename}"
            
            print(f"  ✅ 画像保存完了: {len(images)}枚")
        else:
            print(f"  ℹ️  画像なし")
        
        # Markdown内の画像参照を修正
        if image_mapping:
            print(f"  🔧 画像参照を修正中...")
            with open(output_md_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 画像参照のパターンを置換
            for old_name, new_path in image_mapping.items():
                pattern = r'!\[\]\(' + re.escape(old_name) + r'\)'
                replacement = f'![{old_name}]({new_path})'
                content = re.sub(pattern, replacement, content)
            
            # 更新した内容を保存
            with open(output_md_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"  ✅ 画像参照修正完了")
        
        # メタデータ情報を表示
        if metadata and isinstance(metadata, dict):
            print(f"  📊 ページ数: {metadata.get('page_stats', {}).get('pages', 'N/A')}")
        elif metadata:
            print(f"  📊 メタデータ: {type(metadata)}")
        
    except Exception as e:
        print(f"  ❌ 変換エラー: {e}")
        raise


def format_duration(seconds: float) -> str:
    """処理時間を人間が読みやすい形式にフォーマットする"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}時間"


def process_pdf(pdf_info: dict, config: dict, args, index: int, total: int) -> bool:
    """1つのPDFを処理する"""
    name = pdf_info["name"]
    url = pdf_info["url"]
    output_filename = pdf_info["output_filename"]
    
    print(f"\n{'='*70}")
    print(f"📄 [{index}/{total}] {name}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    # 一時PDFファイルのパス
    temp_pdf = os.path.join(config.get("temp_dir", "temp"), f"temp_{index}.pdf")
    
    # 出力Markdownファイルのパス
    output_md = os.path.join(config.get("output_dir", "docs"), output_filename)
    
    try:
        # PDFをダウンロード
        download_start = time.time()
        download_pdf(url, temp_pdf)
        download_time = time.time() - download_start
        print(f"  ⏱️  ダウンロード時間: {format_duration(download_time)}")
        
        # Markdownに変換
        convert_start = time.time()
        convert_pdf_to_markdown(temp_pdf, output_md, config.get("image_dir", "docs/images"))
        convert_time = time.time() - convert_start
        print(f"  ⏱️  変換時間: {format_duration(convert_time)}")
        
        # Markdownを最適化（デフォルトで実行、--no-optimizeで無効化可能）
        if not args.no_optimize:
            print(f"  🔧 Markdown最適化中...")
            optimize_start = time.time()
            original_size, new_size = optimize_markdown_file(output_md)
            optimize_time = time.time() - optimize_start
            
            if original_size > 0:
                reduction = original_size - new_size
                percentage = (reduction / original_size * 100) if original_size > 0 else 0
                print(f"  ✅ 最適化完了: {reduction:,} bytes削減 ({percentage:.1f}%)")
                print(f"  ⏱️  最適化時間: {format_duration(optimize_time)}")
        
        # 画像参照を検証（--verifyフラグが指定された場合）
        if args.verify:
            print(f"  🔍 画像参照を検証中...")
            verify_result = verify_images(output_md, config.get("image_dir", "docs/images"))
            if verify_result['references']:
                print(f"  📊 画像参照数: {len(verify_result['references'])}枚")
                print(f"  ✅ 検出: {len(verify_result['found'])}枚")
                if verify_result['missing']:
                    print(f"  ⚠️  見つからない: {len(verify_result['missing'])}枚")
                    for missing in verify_result['missing']:
                        print(f"     - {missing}")
        
        # 一時PDFファイルを削除
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)
            print(f"  🗑️  一時ファイル削除完了")
        
        # 合計処理時間
        total_time = time.time() - start_time
        print(f"  ⏱️  合計処理時間: {format_duration(total_time)}")
        print(f"  ✅ 処理完了: {name}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 処理失敗: {name}")
        print(f"  エラー詳細: {e}")
        
        # 一時ファイルをクリーンアップ
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)
        
        return False


def optimize_only_mode(config: dict):
    """既存のMarkdownファイルを最適化のみ実行"""
    print("🔧 Markdown最適化モード")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    docs_dir = Path(config.get("output_dir", "docs"))
    
    if not docs_dir.exists():
        print(f"❌ エラー: {docs_dir} ディレクトリが見つかりません")
        sys.exit(1)
    
    md_files = sorted(docs_dir.glob('*.md'))
    
    if not md_files:
        print(f"❌ エラー: {docs_dir} にMarkdownファイルが見つかりません")
        sys.exit(1)
    
    print(f"📚 処理対象: {len(md_files)}件のMarkdownファイル\n")
    
    total_original = 0
    total_new = 0
    
    for md_file in md_files:
        print(f"{'='*70}")
        print(f"📄 {md_file.name}")
        print(f"{'='*70}")
        
        original_size, new_size = optimize_markdown_file(str(md_file))
        
        if original_size > 0:
            total_original += original_size
            total_new += new_size
            
            reduction = original_size - new_size
            percentage = (reduction / original_size * 100) if original_size > 0 else 0
            
            print(f"  元のサイズ: {original_size:,} bytes")
            print(f"  新サイズ  : {new_size:,} bytes")
            print(f"  削減量    : {reduction:,} bytes ({percentage:.1f}%)")
            print(f"  ✅ 最適化完了\n")
    
    total_reduction = total_original - total_new
    total_percentage = (total_reduction / total_original * 100) if total_original > 0 else 0
    
    print(f"{'='*70}")
    print(f"🎉 すべての最適化が完了しました")
    print(f"{'='*70}")
    print(f"合計削減量: {total_reduction:,} bytes ({total_percentage:.1f}%)")
    print(f"元の合計  : {total_original:,} bytes")
    print(f"新しい合計: {total_new:,} bytes")
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def verify_only_mode(config: dict):
    """既存のMarkdownファイルの画像参照を検証のみ実行"""
    print("🔍 画像参照検証モード")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    docs_dir = Path(config.get("output_dir", "docs"))
    image_dir = config.get("image_dir", "docs/images")
    
    if not docs_dir.exists():
        print(f"❌ エラー: {docs_dir} ディレクトリが見つかりません")
        sys.exit(1)
    
    md_files = sorted(docs_dir.glob('*.md'))
    
    if not md_files:
        print(f"❌ エラー: {docs_dir} にMarkdownファイルが見つかりません")
        sys.exit(1)
    
    print(f"📚 検証対象: {len(md_files)}件のMarkdownファイル\n")
    
    total_refs = 0
    total_found = 0
    total_missing = 0
    
    for md_file in md_files:
        verify_result = verify_images(str(md_file), image_dir)
        
        if verify_result['references']:
            print(f"{'='*70}")
            print(f"📄 {verify_result['file']}")
            print(f"{'='*70}")
            
            for alt, path in verify_result['references']:
                status = "✅" if path in verify_result['found'] else "❌"
                print(f"  {status} {alt or '(no alt)'} -> {path}")
            
            total_refs += len(verify_result['references'])
            total_found += len(verify_result['found'])
            total_missing += len(verify_result['missing'])
            
            print(f"  📊 参照数: {len(verify_result['references'])}枚 "
                  f"(検出: {len(verify_result['found'])}枚, "
                  f"見つからない: {len(verify_result['missing'])}枚)\n")
    
    print(f"{'='*70}")
    print(f"🎉 検証が完了しました")
    print(f"{'='*70}")
    print(f"総画像参照数: {total_refs}枚")
    print(f"✅ 検出: {total_found}枚")
    if total_missing > 0:
        print(f"❌ 見つからない: {total_missing}枚")
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def filter_pdfs(pdfs: list, args) -> list:
    """コマンドライン引数に基づいてPDFリストをフィルタリング"""
    if args.files:
        filtered = [p for p in pdfs if p["name"] in args.files]
        not_found = set(args.files) - {p["name"] for p in filtered}
        if not_found:
            print(f"⚠️  警告: 以下のファイルがconfig.jsonに見つかりません:")
            for name in not_found:
                print(f"  - {name}")
        return filtered
    elif args.versions:
        filtered = [p for p in pdfs if p["version"] in args.versions]
        not_found = set(args.versions) - {p["version"] for p in filtered}
        if not_found:
            print(f"⚠️  警告: 以下のバージョンがconfig.jsonに見つかりません:")
            for ver in not_found:
                print(f"  - {ver}")
        return filtered
    return pdfs


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="Scrum Guides PDF to Markdown Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # すべてのPDFを処理（自動最適化あり）
  %(prog)s
  
  # 特定のファイルのみ処理
  %(prog)s --files "Scrum Guide 2020" "Nexus Guide 2021"
  
  # 特定のバージョンのみ処理
  %(prog)s --versions 2020 2017
  
  # 最適化なしで処理
  %(prog)s --no-optimize
  
  # 既存のMarkdownファイルを最適化のみ
  %(prog)s --optimize-only
  
  # 画像参照の検証のみ
  %(prog)s --verify-only
  
  # 処理時に画像参照も検証
  %(prog)s --verify
        """
    )
    
    # ファイル選択
    parser.add_argument(
        "--files", "-f",
        nargs="+",
        metavar="NAME",
        help="処理するPDFの名前を指定（config.jsonのnameフィールドと一致）"
    )
    
    parser.add_argument(
        "--versions", "-v",
        nargs="+",
        metavar="VERSION",
        help="処理するPDFのバージョンを指定（例: 2020 2017）"
    )
    
    # 最適化オプション
    parser.add_argument(
        "--no-optimize",
        action="store_true",
        help="Markdown最適化をスキップ"
    )
    
    parser.add_argument(
        "--optimize-only",
        action="store_true",
        help="既存のMarkdownファイルを最適化のみ実行（ダウンロード・変換なし）"
    )
    
    # 検証オプション
    parser.add_argument(
        "--verify",
        action="store_true",
        help="変換後に画像参照の整合性を検証"
    )
    
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="既存のMarkdownファイルの画像参照を検証のみ実行"
    )
    
    # その他
    parser.add_argument(
        "--config", "-c",
        default="config.json",
        metavar="PATH",
        help="設定ファイルのパス（デフォルト: config.json）"
    )
    
    args = parser.parse_args()
    
    # 設定を読み込む
    config = load_config(args.config)
    
    # 最適化のみモード
    if args.optimize_only:
        optimize_only_mode(config)
        return
    
    # 検証のみモード
    if args.verify_only:
        verify_only_mode(config)
        return
    
    # 通常モード（ダウンロード・変換）
    print("🚀 Scrum Guides PDF to Markdown Converter")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ディレクトリを作成
    ensure_directories(config)
    
    # PDFリストを取得
    pdfs = config.get("pdfs", [])
    if not pdfs:
        print("❌ エラー: config.jsonにPDFが定義されていません")
        sys.exit(1)
    
    # PDFリストをフィルタリング
    pdfs = filter_pdfs(pdfs, args)
    
    if not pdfs:
        print("❌ エラー: 処理対象のPDFがありません")
        sys.exit(1)
    
    print(f"\n📚 処理対象: {len(pdfs)}件のPDFファイル")
    print()
    
    # 各PDFを処理
    total_start = time.time()
    success_count = 0
    failed_count = 0
    
    for index, pdf_info in enumerate(pdfs, start=1):
        if process_pdf(pdf_info, config, args, index, len(pdfs)):
            success_count += 1
        else:
            failed_count += 1
    
    # 最終結果を表示
    total_time = time.time() - total_start
    print(f"\n{'='*70}")
    print(f"🎉 すべての処理が完了しました")
    print(f"{'='*70}")
    print(f"✅ 成功: {success_count}件")
    if failed_count > 0:
        print(f"❌ 失敗: {failed_count}件")
    print(f"⏱️  総処理時間: {format_duration(total_time)}")
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 一時ディレクトリをクリーンアップ
    temp_dir = config.get("temp_dir", "temp")
    if os.path.exists(temp_dir) and not os.listdir(temp_dir):
        os.rmdir(temp_dir)
        print(f"🗑️  一時ディレクトリを削除しました: {temp_dir}")
    
    # 失敗があった場合は終了コード1を返す
    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
