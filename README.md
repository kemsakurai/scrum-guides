# Scrum Guides

GitHub Pagesで公開するスクラム関連のMarkdownファイルを管理するリポジトリです。

スクラムガイドの公式PDFを自動的にダウンロードし、AI駆動の[marker-pdf](https://github.com/VikParuchuri/marker)を使用して高品質なMarkdown形式に変換します。

## 📚 対象ドキュメント

このリポジトリでは、以下の日本語版スクラムガイドを変換・管理しています:

- **Scrum Guide 2020** (最新版) ✅
- **Scrum Guide 2017** ✅
- **Scrum Guide 2016** ✅
- **Scrum Guide 2013** ⚠️ (部分的に変換)
- **Scrum Guide 2011 October** ✅
- **Scrum Guide 2011 July** ✅
- **Nexus Guide 2021** (スケーリング拡張ガイド) ✅
- **Scrum Guide Expansion Pack** ✅

## 🚀 セットアップ

### 前提条件

- Python 3.10以上
- pip (Pythonパッケージマネージャー)

### 1. リポジトリをクローン

```bash
git clone https://github.com/kemsakurai/scrum-guides.git
cd scrum-guides
```

### 2. 仮想環境を作成

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化 (macOS/Linux)
source venv/bin/activate

# 仮想環境を有効化 (Windows)
venv\Scripts\activate
```

### 3. 依存関係をインストール

```bash
pip install -r requirements.txt
```

**注意**: marker-pdfは初回実行時に必要なAIモデル(数GB)を自動的にダウンロードします。インターネット接続と十分なディスク容量を確保してください。

## 💻 使用方法

### 基本的な使い方

仮想環境を有効化した状態で、以下のコマンドを実行します:

```bash
# すべてのPDFを変換（自動最適化あり）
python convert_pdf_to_md.py
```

### 特定のファイルのみ処理

```bash
# 特定のファイル名で指定
python convert_pdf_to_md.py --files "Scrum Guide 2020" "Nexus Guide 2021"

# バージョンで指定
python convert_pdf_to_md.py --versions 2020 2017
```

### 既存のMarkdownファイルを最適化

```bash
# 既存のMarkdownファイルを最適化のみ実行
python convert_pdf_to_md.py --optimize-only
```

### 画像参照の検証

```bash
# 既存のMarkdownファイルの画像参照を検証
python convert_pdf_to_md.py --verify-only

# 変換時に画像参照も検証
python convert_pdf_to_md.py --verify
```

### その他のオプション

```bash
# 最適化なしで変換
python convert_pdf_to_md.py --no-optimize

# カスタム設定ファイルを使用
python convert_pdf_to_md.py --config custom_config.json

# ヘルプを表示
python convert_pdf_to_md.py --help
```

## 🔧 機能

### 自動処理機能

スクリプトは以下の処理を自動的に実行します:

1. **PDFダウンロード**: `config.json`から変換対象のPDFリストを読み込み、各PDFを順次ダウンロード
2. **Markdown変換**: marker-pdfを使用してMarkdown形式に変換
3. **画像抽出**: PDF内の画像を`docs/images/`ディレクトリに抽出・保存
4. **画像パス修正**: 画像参照パスを相対パスに自動修正
5. **Markdown最適化**: 空行削減、行末空白削除、コメント削除（自動実行）
6. **バックアップ**: 最適化時に元のファイルを`backups/`に自動保存
7. **進捗表示**: 処理時間と進捗状況をリアルタイムで表示

### コマンドライン引数

| 引数 | 説明 |
|------|------|
| `--files NAME [NAME ...]` | 処理するPDFの名前を指定 |
| `--versions VERSION [VERSION ...]` | 処理するPDFのバージョンを指定 |
| `--no-optimize` | Markdown最適化をスキップ |
| `--optimize-only` | 既存のMarkdownファイルを最適化のみ |
| `--verify` | 変換後に画像参照の整合性を検証 |
| `--verify-only` | 既存のMarkdownファイルの画像参照を検証のみ |
| `--config PATH` | 設定ファイルのパス（デフォルト: config.json） |

## 📁 出力ファイル

変換が完了すると、以下のファイルが生成されます:

```
docs/
├── scrum-guide-2020.md
├── scrum-guide-2017.md
├── scrum-guide-2016.md
├── scrum-guide-2013.md
├── scrum-guide-2011-october.md
├── scrum-guide-2011-july.md
├── nexus-guide-2021.md
├── scrum-guide-expansion-pack.md
└── images/
    ├── scrum-guide-2020_image_1.png
    ├── scrum-guide-2020_image_2.png
    └── ...

backups/
├── scrum-guide-2020.md.20260201_123456.bak
└── ...
```

**注意**: 
- 生成されたMarkdownファイル内の画像パスは、GitHub Pagesでの公開に合わせて自動的に修正されています
- 画像ファイルは`docs/images/`ディレクトリに保存され、相対パスで参照されます
- 最適化時には元のファイルが`backups/`ディレクトリに自動保存されます

## ⚙️ 設定のカスタマイズ

`config.json`を編集することで、変換対象のPDFや出力設定をカスタマイズできます:

```json
{
  "pdfs": [
    {
      "name": "表示名",
      "url": "PDFのURL",
      "output_filename": "出力ファイル名.md",
      "version": "バージョン"
    }
  ],
  "output_dir": "docs",
  "image_dir": "docs/images",
  "temp_dir": "temp"
}
```

## 🛠️ トラブルシューティング

### ダウンロードが失敗する

- インターネット接続を確認してください
- URLが正しいか確認してください
- Internet Archiveのリンクは一時的に利用できない場合があります

### 特定のファイルが見つからない

- `--files`で指定した名前が`config.json`の`name`フィールドと完全一致しているか確認してください
- `--versions`で指定したバージョンが`config.json`の`version`フィールドと一致しているか確認してください
- 不一致の場合は警告が表示され、処理は継続されます

### メモリ不足エラー

- marker-pdfはAI処理のため、メモリを多く使用します
- 大きなPDFファイルの場合、8GB以上のRAMを推奨します

### 処理が遅い

- marker-pdfはCPU/GPUで高度な処理を行うため、時間がかかります
- 1つのPDFあたり数分〜10分程度かかる場合があります
- GPUが利用可能な環境では処理が高速化されます

## 📄 ライセンス

このリポジトリのスクリプトはMITライセンスの下で公開されています。

変換元のスクラムガイドおよびNexusガイドの著作権は、Ken SchwaberとJeff Sutherlandに帰属します。

## 🔗 関連リンク

- [Scrum Guides 公式サイト](https://scrumguides.org/)
- [Nexus Guide 公式サイト](https://www.scrum.org/resources/nexus-guide)
- [marker-pdf GitHub](https://github.com/VikParuchuri/marker)
- [スクラムガイド日本語版一覧 (ryuzee.com)](https://www.ryuzee.com/faq/0085/)

## 🤝 貢献

バグ報告や機能追加の提案は、Issuesまたはプルリクエストでお願いします。

## 📝 更新履歴

- 2026-02-01: スクリプト統合と機能拡張
  - 複数の補助スクリプトを統合
  - 特定ファイルのみの処理機能を追加
  - 自動最適化機能を追加
  - バックアップ機能を追加
  - 画像参照検証機能を追加
  
- 2026-01-31: 初期リリース
  - 7つの日本語スクラムガイドPDFの変換スクリプトを追加
  - marker-pdfによる高品質Markdown変換をサポート
  - 画像自動抽出機能を実装
