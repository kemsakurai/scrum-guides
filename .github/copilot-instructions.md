# Project Guidelines

## Overview

スクラムガイドPDFを高品質なMarkdown形式に変換するPythonプロジェクト。marker-pdf（AI駆動）を使用し、GitHub Pagesで公開できる形式で出力。

## Code Style

- **言語**: 日本語のdocstring・コメント、変数名とログメッセージも日本語優先
- **型ヒント**: 全関数シグネチャに必須（例: `-> dict`, `-> tuple[int, int]`）
- **絵文字**: 進捗表示に必須（🚀起動、📥DL、✅成功、❌失敗、⚠️警告）
- **文字列フォーマット**: f-stringsのみ、`.format()`や`%`は不可
- **パス操作**: `pathlib.Path`推奨、`os.path`は必要時のみ
- **エンコーディング**: ファイル操作は常に`encoding="utf-8"`指定

**参考実装**: [convert_pdf_to_md.py](convert_pdf_to_md.py#L1-L50)の関数定義

## Architecture

### 関数型パイプライン構造

クラスなし、11の純粋関数で構成。処理フロー: Download → Convert → Optimize → Verify

#### コア関数群

```python
# 設定読込（起動時1回）
load_config(config_path: str) -> dict

# ディレクトリ構築
ensure_directories(config: dict) -> None

# PDFダウンロード（プログレスバー付き）
download_pdf(url: str, output_path: str) -> None

# PDF→Markdown変換（marker-pdf使用）
convert_pdf_to_markdown(pdf_path: str, output_md_path: str, image_dir: str) -> None

# Markdown最適化（3パス処理）
optimize_markdown_content(content: str) -> str
optimize_markdown_file(md_path: str) -> tuple[int, int]  # (削減bytes, 削減%)

# 画像検証
verify_images(md_path: str, image_dir: str) -> dict

# バックアップ（タイムスタンプ自動付与）
backup_markdown_file(md_path: str) -> str
```

### エラーハンドリングパターン

1. **設定エラー**: `sys.exit(1)`で即終了（[L32-35](convert_pdf_to_md.py#L32-L35)）
2. **ネットワークエラー**: `raise`で呼び出し元へ伝播（[L71-73](convert_pdf_to_md.py#L71-L73)）
3. **非クリティカル**: センチネル値返却（[L140-143](convert_pdf_to_md.py#L140-L143)）

## Build and Test

### 環境セットアップ

```bash
# 仮想環境作成・有効化
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 依存関係インストール
pip install -r requirements.txt
```

**⚠️ 重要**: marker-pdf初回実行時に数GBのAIモデルをダウンロード（数時間）

### テスト実行

```bash
# フェーズ1テスト（基礎機能、3秒）
pytest tests/test_convert_pdf_to_md.py -m phase1 -q

# フェーズ1+2（統合テスト含む、6秒）
pytest tests/test_convert_pdf_to_md.py -m "phase1 or phase2" --cov=convert_pdf_to_md --cov-report=term

# 全テスト実行（92%カバレッジ目標）
pytest
```

### アプリケーション実行

```bash
# 全PDF処理
python convert_pdf_to_md.py

# 特定ファイルのみ
python convert_pdf_to_md.py --files "Scrum Guide 2020" "Nexus Guide 2021"

# 既存Markdown最適化のみ
python convert_pdf_to_md.py --optimize-only

# 画像参照検証のみ
python convert_pdf_to_md.py --verify-only
```

## Project Conventions

### 1. 自動バックアップ機構

ファイル変更前に**必ず**タイムスタンプ付きバックアップ作成（[L124-134](convert_pdf_to_md.py#L124-L134)）:

```python
backup_path = backup_markdown_file(md_path)
# → backups/scrum-guide-2020.md.20260207_143022.bak
```

### 2. Markdown最適化ルール

3パス処理（[L85-122](convert_pdf_to_md.py#L85-L122)）:

- **Pass 1**: 行末空白削除（`.rstrip()`）
- **Pass 2**: コメント行スキップ（`/* Lines ... omitted */`）
- **Pass 3**: 空テーブル行除去（全セル空白の`| | |`）
- **Pass 4**: 連続空行を最大2行に制限
- **Pass 5**: 末尾空行削除

### 3. 画像パス規約

**必須**: GitHub Pages互換の相対パス（[L237-260](convert_pdf_to_md.py#L237-L260)）

```python
# NG: 絶対パス
img_path = "/Users/user/project/docs/images/image.png"

# OK: 相対パス
img_path = "images/scrum-guide-2020_image_1.png"

# 命名規則: {base_name}_image_{n}.png
```

### 4. テストでのモック必須

**絶対厳守**: marker-pdfのモック（[tests/conftest.py](tests/conftest.py#L40-L50)）

```python
@pytest.fixture
def mock_marker_pdf():
    """モデルDL回避（実行すると数GB・数時間）"""
    with patch('convert_pdf_to_md.PdfConverter'), \
         patch('convert_pdf_to_md.create_model_dict'), \
         patch('convert_pdf_to_md.text_from_rendered'):
        yield
```

### 5. フェーズ別テストマーカー

増分開発用の3段階構成（[pytest.ini](pytest.ini#L7-L9)）:

- `@pytest.mark.phase1`: 基礎機能（38テスト）
- `@pytest.mark.phase2`: 統合テスト（18テスト）
- `@pytest.mark.phase3`: 高度シナリオ（8テスト）

## Integration Points

### marker-pdf（外部AI依存）

```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

converter = PdfConverter(artifact_dict=create_model_dict())
rendered = converter(pdf_path)
markdown_text, metadata, images = text_from_rendered(rendered)

# imagesは dict[str, PIL.Image | bytes]
# → 両型のハンドリング必須（L245-252参照）
```

**注意点**:
- 初回実行で自動モデルDL（~数GB）
- GPU利用可能時は自動検出・使用
- `images`の値型が不定（PIL Image/bytes両対応必須）

### requests（ストリーミングDL）

```python
response = requests.get(url, timeout=60, stream=True)
response.raise_for_status()

# プログレスバー実装（L62-72）
total_size = int(response.headers.get('content-length', 0))
for chunk in response.iter_content(chunk_size=8192):
    # 進捗: XX.X% 表示
```

## Security

### ダウンロード検証

- タイムアウト必須: `timeout=60`
- HTTPステータスチェック: `.raise_for_status()`
- Content-Length検証あり

### ファイル操作の安全性

- `Path().mkdir(parents=True, exist_ok=True)`: ディレクトリ作成
- `shutil.copy2()`: メタデータ保持コピー
- バックアップ必須: 上書き前に自動バックアップ

## Common Pitfalls

❌ **絶対避けるべきミス**:

1. `sys.path.insert`なしでテストからmainスクリプトimport
2. テストで実際のmarker-pdf実行（fixtureでモック済み）
3. ハードコードパス（必ず`config`辞書の値使用）
4. `--files`/`--versions`フィルタリング壊す修正
5. バックアップのタイムスタンプ形式変更（他ツール依存）

✅ **推奨パターン**:

- 新機能追加時は適切なphaseマーカー付与
- `tmp_path` fixture使用、実`docs/`への書込み禁止
- 94%+カバレッジ維持
- 絵文字付き進捗表示保持

## File Structure

```
scrum-guides/
├── convert_pdf_to_md.py      # メインスクリプト（645行）
├── config.json                # PDF定義（11エントリ）
├── requirements.txt           # 7依存関係
├── pytest.ini                 # テスト設定
│
├── docs/                      # 出力先（Git管理対象）
│   ├── *.md                   # 生成Markdown
│   └── images/                # 抽出画像
│
├── backups/                   # 自動バックアップ（Git無視）
│   └── *.md.YYYYMMDD_HHMMSS.bak
│
├── temp/                      # 一時DL（Git無視）
│
└── tests/
    ├── conftest.py            # 共有fixture
    ├── test_convert_pdf_to_md.py  # メインテスト（1175行）
    └── fixtures/              # テストデータ
        ├── configs/           # JSON設定バリエーション
        ├── markdowns/         # サンプルMarkdown
        ├── pdfs/              # 実PDF（100-300KB）
        └── images/            # テスト画像
```

## Quick Reference

### CLIモード3種

```bash
# モード1: 通常（DL→変換→最適化）
python convert_pdf_to_md.py [--files "Name"] [--versions "2020"]

# モード2: 最適化のみ
python convert_pdf_to_md.py --optimize-only

# モード3: 検証のみ
python convert_pdf_to_md.py --verify-only
```

### デバッグ用コマンド

```bash
# 特定テストのみ実行
pytest tests/test_convert_pdf_to_md.py::test_load_config -v

# カバレッジHTML生成
pytest --cov=convert_pdf_to_md --cov-report=html

# 設定ファイル検証
python -c "import json; print(json.load(open('config.json')))"
```

## Additional Notes

- **ライセンス**: MIT + CC BY-SA 4.0（ドキュメント）
- **対象**: Scrum Guide全バージョン（2011-2020）+ 関連ガイド
- **出力形式**: GitHub Pages用Markdown（Jekyll互換）
- **日本語**: プロジェクト全体で日本語使用（コード・コメント・ログ）
