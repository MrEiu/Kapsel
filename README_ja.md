<div align="center">

# ⚡ Kapsel

**シェルを統合コマンド、コンテキスト認識型オートコンプリート、そしてグローバル環境の汚染ゼロで包み込む、クロスプラットフォームなターミナル環境。**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[なぜKapselなのか？](#-なぜkapselなのか) •
[特徴](#-特徴) •
[クイックスタート](#-クイックスタート) •
[内蔵プラグイン](#-内蔵プラグイン) •
[インストール](#-インストール) •
[アーキテクチャ](#-アーキテクチャ--サンドボックス化) •
[🇨🇳 简体中文](README_zh.md)

</div>

---

### 📺 動作中のインタラクティブカプセル

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **複雑さを包み込み、シンプルさを公開する。**
> 通常通りネイティブシェルの実行ファイルを実行しながら、自動コマンド翻訳、インライン提案、リッチな補完仕様、そしてモジュール式ツールチェーンをすべて `~/.kapsel/` 内にサンドボックス化して利用できます。

---

## 💡 なぜKapselなのか？

オペレーティングシステムを切り替えると、壊れた筋肉記憶、散らかったドットファイル、断片化されたオートコンプリート設定に悩まされることがよくあります。Kapselは、非侵襲的なカプセル層でこのギャップを埋めます：

| 課題 | 従来のシェル設定 | Kapselを使用した場合 |
| :--- | :--- | :--- |
| **クロスプラットフォームの摩擦** | OS間でコマンドが断片化（`dir` vs `ls`、`rmdir` vs `rm -rf`） | Windows、macOS、Linux間で統一されたLinuxファーストのコマンド層 |
| **シェルプロファイルの汚染** | 肥大化した`.bashrc`や`$PROFILE`に脆弱なグローバルスクリプトが混在 | `~/.kapsel/`内に100%自己完結型サンドボックス（グローバルな変更はゼロ） |
| **オートコンプリートの設定** | シェルごとに手動設定が必要で、不完全または遅いことが多い | Carapaceによる1,000以上のCLIツール向けの即時コンテキスト認識型コンプリート |
| **ツールチェーンと同期の散在** | バラバラなツールで反復的な手動インストールが必要 | ランタイム、ミラー、ディレクトリジャンプ、同期のための統合`kps`プラグイン |

---

## ✨ 特徴

- **🌐 クロスプラットフォームなコマンド一貫性**: どのターミナルでも標準コマンド（`ls -la`、`cat`、`rm -rf`、`grep`）を自然に入力でき、ホストの組み込み機能を乗っ取ることなく、ホストネイティブのプリミティブに自動変換されます。
- **⚡ コンテキストを認識したオートコンプリート**: [Carapace](https://carapace.sh) と統合し、PowerShell、Bash、Zsh 全体で多段階の引数およびコンテキスト補完（Git ブランチ、Docker イメージ、npm スクリプト）を提供します。
- **🛡️ ゼロ汚染サンドボックス化**: すべて（バイナリ、SQLite 履歴、宣言型仕様、プラグイン、ログ）は `~/.kapsel/` 内に格納されます。ホストのシェル設定ファイルは完全に変更されません。
- **🧩 厳選されたプラグインエコシステム**: 強力な開発者向けユーティリティ（`zoxide`、`mise`、`chsrc`、`pueue`、AI アシスタント）に、統一された `kps` コマンドから直接アクセスできます。
- **🎨 モダンなカードフレーム美学**: 終了コードバッジ（`✔ 0` / `✘ 1`）、実行ストップウォッチ計時、7 言語にわたるネイティブ i18n サポートを備えた、クリーンなビジュアルコマンドカードフレーミング。

---

## 🚀 クイックスタート

インタラクティブなカプセルシェルを起動します:

```bash
kapsel
```

Kapsel 内では、コマンドは拡張されたフィードバックとともにネイティブに実行されます:

```bash
# 1. タイミングと終了コードカード付きのネイティブパススルー
git status
docker ps

# 2. あらゆるOSでのユニバーサルコマンド変換
rm -rf ./temp_dir
cat package.json

# 3. いつでも内蔵プラグインを使用
kps portal work        # ディレクトリへジャンプ (zoxide)
kps ai "explain git rebase"  # ターミナルAIアシスタントに質問
kps shore get          # 最速のパッケージミラーを自動選択

# 4. カプセルの状態を確認
kps status
```

> **ワンショット実行**: 通常のシェルから `kps <command>` (例: `kps portal`、`kps status`、`kps ai`) を使用して、Kapsel ツールを直接呼び出すこともできます。

---

## 🧩 組み込みプラグイン

Kapselには、`kps`名前空間の下に、分離された公式プラグインが11個プリインストールされています：

| プラグイン | コマンド | 機能 | 基盤技術 |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | frecency重み付けによる高速ディレクトリジャンプ | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | コマンド生成・説明のためのターミナルAIコパイロット | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | マルチ言語ツールチェーンランタイムマネージャー（Node、Python、Go、Rust） | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | 最速のパッケージ＆OSダウンロードミラーをベンチマークし切り替え | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | 20以上のパッケージマネージャーを統合するユニバーサルソフトウェアインストーラー | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | 名前空間の衝突がゼロのクロスプラットフォームエイリアス変換 | ネイティブエンジン |
| **`autopilot`**| `kps autopilot`| バックグラウンドキュー＆自律デーモンタスクランナー | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>`| 即時利用可能なコミュニティ駆動の実践的コマンドチートシート | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | 誤入力コマンドのインテリジェント自動修正＆構文修正 | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | クロスプラットフォームのドットファイル＆ワークステーション設定同期 | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | インタラクティブCLIコマンドスニペットのブックマーク＆ランナー | [pet](https://github.com/knqyf263/pet) |

---

## 📦 インストール

### 推奨方法（pipx / pip）

```bash
# pipx による分離インストール（推奨）
pipx install kapsel-cli

# または標準の pip
pip install --upgrade kapsel-cli
```

### ワンライン自動インストーラー

OS を自動検出し、シェルの補完設定まで行うクイックブートストラップスクリプト：

```bash
# macOS & Linux:
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash

# Windows (PowerShell):
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

### その他のインストール方法

- **スタンドアロン版プリコンパイル済みバイナリ**: [GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest) から実行可能なリリースをダウンロードできます。
- **パッケージマネージャー**: Scoop（`scoop install kapsel`）、Homebrew、Debian/Ubuntu の `.deb` パッケージで利用可能です。
- **ソースからビルド**: `git clone https://github.com/MrEiu/Kapsel.git && cd Kapsel && pip install -e .`

👉 *中国国内向けミラー高速化や、各プラットフォームのパッケージマネージャーの詳細については、**[docs/INSTALLATION.md](docs/INSTALLATION.md)** を参照してください。*

---

## ⚙️ 設定

Kapsel は設定を `~/.kapsel/config.yaml` に保存します。ターミナルから直接設定を管理できます：

```bash
# 設定ダッシュボードを表示
kps config

# 外部エディタで設定ファイルを開く
kps config edit

# 設定をその場で調整
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

---

## 🏛️ アーキテクチャとサンドボックス化

Kapselは**ゼロ汚染の原則**に従います。すべてのランタイム状態は厳密に格納されます：

```text
~/.kapsel/
├── config.yaml          # システム全体のUI設定、テーマ、および対話設定
├── history.db           # コマンド履歴と統計を保存する永続的なSQLiteデータベース
├── bin/                 # ユーザー空間のスタンドアロンバイナリツール（carapace、zoxide、mise...）
├── specs/               # 宣言型オートコンプリートYAML仕様
├── plugins/             # インストール済みの公式およびコミュニティプラグイン拡張機能
└── logs/                # 診断ログとセッションメトリクス
```

- **デュアルステートエンジン**: ネイティブ実行可能ファイルはホストサブシェルのパススルーを介して直接実行されます。カプセルユーティリティは統合された`kps`レジストリを介して実行されます。
- **衝突防止センチネル**: ネイティブシェルの組み込みコマンド（例：PowerShellの`Get-Alias`、`Get-Help`）がインターセプトまたはハイジャックされないことを保証します。
- **分離されたプラグイン**: プラグインは独立して実行され、サードパーティの拡張機能がコアシェルをクラッシュさせることができないようにします。

---

## 🧪 開発とテスト

```bash
# リポジトリをクローン
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# テスト依存関係を含む編集可能なパッケージをインストール
pip install -e ".[test]"

# ユニットテストスイートを実行
pytest tests/ -v
```

---

## 📄 ライセンス

**[MITライセンス](LICENSE)** の下で配布されています。MrEiuとオープンソースの貢献者によって構築されました。
