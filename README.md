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

### PDFをMarkdownに変換

仮想環境を有効化した状態で、以下のコマンドを実行します:

```bash
python convert_pdf_to_md.py
```

### 実行内容

スクリプトは以下の処理を自動的に実行します:

1. `config.json`から変換対象のPDFリストを読み込み
2. 各PDFを順次ダウンロード
3. marker-pdfを使用してMarkdown形式に変換
4. 変換結果を`docs/`ディレクトリに保存
5. PDF内の画像を`docs/images/`ディレクトリに抽出・保存
6. 処理時間と進捗状況をリアルタイムで表示

### 出力ファイル

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
└── images/
    ├── scrum-guide-2020_image_1.png
    ├── scrum-guide-2020_image_2.png
    └── ...
```

**注意**: 生成されたMarkdownファイル内の画像パスは、GitHub Pagesでの公開に合わせて自動的に修正されています。画像ファイルは`docs/images/`ディレクトリに保存され、相対パスで参照されます。

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

- 2026-01-31: 初期リリース
  - 7つの日本語スクラムガイドPDFの変換スクリプトを追加
  - marker-pdfによる高品質Markdown変換をサポート
  - 画像自動抽出機能を実装
