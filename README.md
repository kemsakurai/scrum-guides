# Scrum Guides

GitHub Pagesで公開するスクラム関連のMarkdownファイルを管理するリポジトリです。

スクラムガイドの公式PDFを自動的にダウンロードし、AI駆動の[marker-pdf](https://github.com/VikParuchuri/marker)を使用して高品質なMarkdown形式に変換します。

## 🎯 モチベーション

このリポジトリのリソースは、**GitHub Spaces**のインプットデータとして活用することを想定しています。    

スクラムガイドなどの公式ドキュメントをMarkdown形式で整備することで、GitHub Spacesを通じて以下のような価値を提供します:

- 📖 **コンテキストに基づいた質問応答**: スクラムやアジャイルに関する質問に対して、公式ガイドに基づいた正確な回答を提供
- 🔍 **バージョン間の比較**: 各バージョンのスクラムガイドを横断的に検索・比較し、変更点や進化を理解
- 💡 **実践的なガイダンス**: プロジェクトやチームの状況に応じた、スクラムの実践方法に関するアドバイス
- 🌐 **日本語でのアクセス**: 日本語版の公式ドキュメントをベースにした、自然な日本語での対話と情報提供

Markdown形式への変換により、AIが効率的にコンテンツを理解・活用できるため、より精度の高い情報提供が可能になります。

## 📚 対象ドキュメント

変換対象は`config.json`で管理しています（ここに書かれている内容が「ソース・オブ・トゥルース」です）。

現状、`config.json`に定義されている対象は以下です:

### スクラムガイド（日本語）

- **Scrum Guide 2020** ✅
- **Scrum Guide 2017** ✅
- **Scrum Guide 2016** ✅
- **Scrum Guide 2013** ✅
- **Scrum Guide 2011 October** ✅
- **Scrum Guide 2011 July** ✅
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

一部のファイルのみをダウンロード・変換することができます:

```bash
# 特定のファイル名で指定（config.jsonのnameフィールドと一致）
python convert_pdf_to_md.py --files "Scrum Guide 2020" "Scrum Guide 2017"

# バージョンで指定
python convert_pdf_to_md.py --versions 2020 2017

# 複数のバージョンと最適化なし（例）
python convert_pdf_to_md.py --versions 2020 2017 --no-optimize
```

**利用可能なファイル名**:
- `Scrum Guide 2020`, `Scrum Guide 2017`, `Scrum Guide 2016`, `Scrum Guide 2013`
- `Scrum Guide 2011 October`, `Scrum Guide 2011 July`
- `Scrum Guide Expansion Pack`

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

## 🧪 テスト

このプロジェクトは包括的なテストスイートを備えています。

### テスト環境のセットアップ

テストの実行には、開発用依存関係のインストールが必要です（既に`requirements.txt`に含まれています）：

```bash
pip install -r requirements.txt
```

### 基本的なテスト実行

```bash
# すべてのテストを実行
pytest tests/test_convert_pdf_to_md.py -v

# カバレッジレポート付きで実行
pytest tests/test_convert_pdf_to_md.py --cov=convert_pdf_to_md --cov-report=term

# HTMLカバレッジレポートを生成
pytest tests/test_convert_pdf_to_md.py --cov=convert_pdf_to_md --cov-report=html
# レポートは htmlcov/index.html で確認できます
```

### Phase別テスト実行

テストは開発フェーズごとにマーカーで分類されています：

```bash
# Phase 1のみ実行（基本機能テスト: 38件）
pytest tests/test_convert_pdf_to_md.py -m phase1 -v

# Phase 2のみ実行（統合テスト: 18件）
pytest tests/test_convert_pdf_to_md.py -m phase2 -v

# Phase 1 + Phase 2を実行（計56件）
pytest tests/test_convert_pdf_to_md.py -m "phase1 or phase2" -v
```

### テストカテゴリ別実行

```bash
# ユニットテストのみ実行
pytest tests/test_convert_pdf_to_md.py -m unit -v

# 統合テストのみ実行
pytest tests/test_convert_pdf_to_md.py -m integration -v

# Phase 3のみ実行（高度シナリオ）
pytest tests/test_convert_pdf_to_md.py -m phase3 -v

# 遅いテストのみ実行
pytest tests/test_convert_pdf_to_md.py -m slow -v
```

### テストカバレッジ

現在のテストカバレッジ: **94%**

```
convert_pdf_to_md.py    357行中336行カバー（94%）
```

主要な機能は全てテストでカバーされており、以下の領域を検証しています：

- ✅ 設定ファイルの読み込みと検証
- ✅ PDFダウンロード機能（正常系・異常系）
- ✅ Markdown変換とメタデータ処理
- ✅ Markdown最適化機能
- ✅ バックアップとファイル操作
- ✅ 画像抽出と参照検証
- ✅ エラーハンドリング
- ✅ CLIオプション解析
- ✅ E2Eワークフロー

### テストで使用されるフィクスチャ

テストでは以下のリソースを使用します：

- **Mozilla PDF.js サンプルPDF**: 実PDFテスト用の軽量サンプル（103KB, 290KB）
- **モック化されたmarker-pdf**: 高速なテスト実行のため、marker-pdfは完全にモック化
- **一時ディレクトリ**: 各テストは独立した一時ディレクトリで実行され、クリーンアップも自動

### CI/CDでのテスト実行

```bash
# クイック検証（Phase 1のみ、目安: 数秒）
pytest tests/test_convert_pdf_to_md.py -m phase1 -q

# 完全検証（Phase 1+2、カバレッジ付き、目安: 〜10秒）
pytest tests/test_convert_pdf_to_md.py -m "phase1 or phase2" --cov=convert_pdf_to_md --cov-report=term -q
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

## 📄 ライセンス & 帰属表示

### 複数ライセンス構造

このリポジトリは、**スクリプトコード**と**変換されたコンテンツ**で異なるライセンスが適用されます：

#### 1. スクリプトコード（Python変換ツール） - MIT ライセンス

このリポジトリのPython変換スクリプト（`convert_pdf_to_md.py`等）はMITライセンスの下で公開されています。

**ライセンス全文**: [LICENSE-MIT](./LICENSE-MIT)

#### 2. 変換されたコンテンツ（docs/）のライセンス

`docs/`ディレクトリ内のMarkdownファイルは、原著作物（PDF）のライセンスに従います。

スクラムガイド（Scrum Guide）は、一般に **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** の下で提供されています。

**ライセンス全文**: [LICENSE-CC-BY-SA-4.0](./LICENSE-CC-BY-SA-4.0)  
**ライセンス概要**: https://creativecommons.org/licenses/by-sa/4.0/  
**法的条文**: https://creativecommons.org/licenses/by-sa/4.0/legalcode

### 原著作物への帰属表示

スクラムガイドおよび関連ドキュメントは以下の著者により作成されています：

- **Ken Schwaber** (Scrum.org)
- **Jeff Sutherland** (Scrum Inc.)

**原著作物のソース**: https://scrumguides.org/

すべてのコンテンツは原著者の知的財産であり、CC-BY-SA 4.0の条件の下で、教育および参考目的のためにここで提供されています。

### 派生作品について

このリポジトリは、[marker-pdf](https://github.com/VikParuchuri/marker)ツールを使用したAI変換によるMarkdown版を含んでいます。これらの変換は、元のマテリアルのコンテンツと構造を維持しながら、以下を提供します：

- 検索可能なテキスト形式
- GitHub上での閲覧性向上
- Markdownベースのドキュメントシステムとの互換性
- アクセシビリティの向上

### 本リポジトリのコンテンツを再利用する場合の適切な帰属表示

本リポジトリからコンテンツを再利用する場合、CC-BY-SA 4.0の帰属表示要件に基づいて、以下の情報（**TASLフレームワーク**）を使用して適切な帰属表示を提供する必要があります：

- **タイトル（Title）**: ドキュメント名（例：スクラムガイド）
- **著者（Author）**: Ken Schwaber, Jeff Sutherland
- **ソース（Source）**: https://scrumguides.org/ および本リポジトリ
- **ライセンス（License）**: CC-BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)
- **注記**: 「本著作物は原著作物のMarkdown変換版です」

#### 帰属表示の例

> **Scrum Guide** by Ken Schwaber and Jeff Sutherland (https://scrumguides.org/) is licensed under [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This Markdown version was converted from the original PDF using [marker-pdf](https://github.com/VikParuchuri/marker).

詳細なガイダンスについては、https://creativecommons.org/use-remix/attribution/ を参照してください。

### 利用者の義務

本リポジトリの**スクラムガイドコンテンツ**を使用、適応、または修正する場合、以下の義務があります：

- ✅ **帰属表示** - 原著者（Ken Schwaber, Jeff Sutherland）とソース（scrumguides.org）を表示する
- ✅ **ライセンス保持** - 派生作品についてもCC-BY-SA 4.0ライセンスを使用する
- ✅ **変更の明示** - 行った変更や改変を表示する
- ✅ **ライセンステキストへのリンク** - https://creativecommons.org/licenses/by-sa/4.0/ へリンクを張る

CC-BY-SA要件の詳細については、[Creative Commons BY-SA Deed](https://creativecommons.org/licenses/by-sa/4.0/deed.ja)を参照してください。

## 🔗 関連リンク

- [Scrum Guides 公式サイト](https://scrumguides.org/)
- [Scrum Guide Expansion Pack](https://scrumexpansion.org/ja/scrum-guide-expanded/)
- [marker-pdf GitHub](https://github.com/VikParuchuri/marker)
- [スクラムガイド日本語版一覧 (ryuzee.com)](https://www.ryuzee.com/faq/0085/)

## 🤝 貢献

バグ報告や機能追加の提案は、Issuesまたはプルリクエストでお願いします。

## 📝 更新履歴

- 2026-03-15: README更新
  - `config.json`/`docs/`の現状に合わせて対象ドキュメント・出力例・リンクを整理

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
