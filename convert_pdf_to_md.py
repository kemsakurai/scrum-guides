#!/usr/bin/env python3
"""
Scrum Guides PDF to Markdown Converter

このスクリプトは、config.jsonで定義されたスクラムガイドPDFをダウンロードし、
marker-pdfを使用してMarkdown形式に変換します。
"""

import json
import os
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
            # ![](_page_X_Picture_Y.jpeg) や ![](_page_X_Figure_Y.jpeg) を置換
            import re
            for old_name, new_path in image_mapping.items():
                # Markdown内の画像参照を検索して置換
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


def process_pdf(pdf_info: dict, config: dict, index: int, total: int) -> bool:
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


def main():
    """メイン処理"""
    print("🚀 Scrum Guides PDF to Markdown Converter")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 設定を読み込む
    config = load_config()
    
    # ディレクトリを作成
    ensure_directories(config)
    
    # PDFリストを取得
    pdfs = config.get("pdfs", [])
    if not pdfs:
        print("❌ エラー: config.jsonにPDFが定義されていません")
        sys.exit(1)
    
    print(f"\n📚 処理対象: {len(pdfs)}件のPDFファイル")
    print()
    
    # 各PDFを処理
    total_start = time.time()
    success_count = 0
    failed_count = 0
    
    for index, pdf_info in enumerate(pdfs, start=1):
        if process_pdf(pdf_info, config, index, len(pdfs)):
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
