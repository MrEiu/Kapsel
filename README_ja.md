<div align="center">

# ⚡ Kapsel

**よりクリーンで一貫したコマンドライン体験を実現する、クロスプラットフォーム・ターミナルカプセル。**

[![PyPI Version](https://img.shields.io/pypi/v/kapsel-cli?color=3776AB&logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/kapsel-cli/)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[クイックスタート](#-クイックスタート) ·
[機能](#-機能) ·
[プラグイン](#-プラグインエコシステム) ·
[インストール](#-インストール) ·
[アーキテクチャ](#-アーキテクチャ) ·
[ドキュメント](#-ドキュメント)

[English](README.md) ·
[🇨🇳 简体中文](README_zh.md) ·
[🇷🇺 Русский](README_ru.md) ·
[🇩🇪 Deutsch](README_de.md) ·
[🇪🇸 Español](README_es.md) ·
[🇫🇷 Français](README_fr.md) ·
[🇵🇱 Polski](README_pl.md)

</div>

---

## 📺 デモ

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

> **複雑さを包み込み、シンプルさを届ける。**
>
> ネイティブシェルとシステムコマンドはそのままに、Kapsel が統一コマンドレイヤー、コンテキスト対応補完、インライン履歴提案、拡張可能なプラグイン環境をシームレスに追加します。すべて `~/.kapsel/` 内に安全にカプセル化されます。

---

## 💡 なぜ Kapsel なのか？

端末での開発ワークフローは、未だに使用している OS やシェルによって大きく分断されています。

日常的な同じ作業であっても、Windows、macOS、Linux で異なるコマンドや構文が必要です。シェルの設定は `.bashrc`、`.zshrc`、PowerShell プロファイルなどに分散し、自動補完や開発ツールは個別に導入・設定しなければなりません。

Kapsel は既存のターミナルを侵食することなく、その周囲に軽量なカプセルレイヤーを提供します：

| 課題 | 従来の環境 | Kapsel |
| :--- | :--- | :--- |
| **クロスプラットフォーム** | OSごとに異なるコマンド構文 | Linux-First の統一コマンドレイヤー |
| **シェル設定** | グローバルプロファイルに散乱 | `~/.kapsel/` に完全に自己完結 |
| **自動補完** | 各シェル・ツール個別の複雑な設定 | Carapace エンジンによる高度な文脈補完 |
| **開発ツール** | ツールごとに異なる設定と管理方法 | `kps` 名前空間下の統一プラグイン環境 |
| **拡張性** | シェル固有のスクリプト依存 | 独立したモジュール式プラグイン構造 |

Kapsel は既存のシェルやシステムコマンドを置き換えるものではありません。それらの隣に位置し、一貫した快適な実行環境を提供します。

---

## ✨ 機能

### 🌐 ネイティブ実行＆クロスプラットフォーム

普段使用しているシステムコマンドをそのまま実行できます：

```bash
git
docker
python
npm
cargo
vim
```

同時に、よく使われるクロスプラットフォーム操作のために Linux-First の統一レイヤーを提供します：

```bash
ls -la
cat package.json
rm -rf ./dist
grep -r "TODO" .
```

ネイティブシェルの組み込みコマンドは誤った上書きから確実に保護されます。

---

### ⚡ コンテキスト対応の高度な自動補完

Kapsel は [Carapace](https://carapace.sh) と連携し、高度な文脈認識補完を提供します：

コマンド、引数、フラグだけでなく、以下の動的コンテキストを深く理解します：

- Git ブランチとタグ
- Docker コンテナ名とイメージ
- Kubernetes リソース
- npm スクリプト
- その他 1,000 以上の CLI ツール仕様

補完仕様は宣言的に管理され、プラグインやカスタム仕様で簡単に拡張できます。

---

### 💡 インライン履歴自動提案

ローカルの SQLite 履歴ストアを活用し、タイピング中に入力履歴に基づいた提案をリアルタイムに表示します。

`→` キーを押すだけで提案を採用できます。

すべての履歴と状態は Kapsel のサンドボックス内に安全に保持されます。

---

### 🛡️ 汚染ゼロの独立サンドボックス

Kapsel の設定、バイナリ、履歴、補完仕様、プラグイン、ログはすべて以下に集約されます：

```text
~/.kapsel/
```

既存のシェル設定ファイルを変更することはありません：

```text
.bashrc
.zshrc
config.fish
PowerShell profiles
```

ホストシェルの純粋性を完全に保ちます。

---

### 🧩 モジュール式プラグイン設計

`kps` 名前空間のもとでプラグインランタイムを提供します。

プラグインは Kapsel コアに手を加えることなく、新しいコマンド、ワークフロー、補完仕様、外部ツールを追加できます。

公式プラグインとコミュニティプラグインは共通の拡張アーキテクチャを共有しています。

---

### 🎨 モダンなインタラクティブ体験

直感的で美しい 2 行表示カードレイアウト：

```text
╭─ ...
╰─ ❯ ...
✔ 0  ...  ⏱ 24ms
```

コマンド実行後には終了コードとミリ秒単位の経過時間を即座に表示。インターフェースは多言語ローカライズに対応しています。

---

# 🚀 クイックスタート

## 1. インストール

推奨インストール方法（`pipx`）：

```bash
pipx install kapsel-cli
```

または `pip`：

```bash
pip install --upgrade kapsel-cli
```

## 2. Kapsel の起動

```bash
kapsel
```

普段通りにコマンドを実行できます：

```bash
git status
docker ps
python --version
```

必要に応じてクロスプラットフォームコマンドも利用可能です：

```bash
ls -la
cat package.json
rm -rf ./temp
```

## 3. Kapsel コマンドの使用

`kps` から拡張機能にアクセスできます：

```bash
kps status
kps config
kps portal
kps ai
```

使用例：

```bash
kps portal work
kps ai "explain git rebase"
kps shore get
```

## 4. 単発実行（非対話モード）

対話型カプセルに入らなくても、既存のシェルから直接 `kps` を実行できます：

```bash
kps status
kps portal
kps ai "find large files"
```

スクリプト、エイリアス、自動化ワークフローに最適です。

---

# 🧩 プラグインエコシステム

Kapsel は肥大化したモノリシック設計ではなく、プラグイン駆動のターミナル環境として設計されています。

## 公式プラグイン

| プラグイン | コマンド | 説明 | 駆動エンジン |
| :--- | :--- | :--- | :--- |
| **`portal`** | `kps portal` / `z` | 頻度・直近性に基づく超高速ディレクトリジャンプ | [zoxide](https://github.com/ajeetdsouza/zoxide) |
| **`ai`** | `kps ai` | コマンド生成・解説・トラブル診断を行う AI アシスタント | OpenAI / Claude / Ollama |
| **`init`** | `kps init` | Node、Python、Go、Rust 等のランタイム・ツールチェーン管理 | [mise](https://github.com/jdx/mise) |
| **`shore`** | `kps shore` | パッケージマネージャーと OS の最速ミラー検出・切り替え | [chsrc](https://github.com/AkihiroSuda/chsrc) |
| **`install`** | `kps install` | 複数パッケージマネージャーを横断した統一ソフト導入 | [mpm](https://github.com/MrEiu/mpm) |
| **`alias`** | `kps alias` | プラットフォーム差分を解消するクロスプラットフォームエイリアス | ネイティブエンジン |
| **`autopilot`** | `kps autopilot` | バックグラウンドタスクキューと長時間プロセスの監視 | [pueue](https://github.com/Nukesor/pueue) |
| **`help`** | `kps help <cmd>` | 実践的なコマンドチートシートと解説 | [tealdeer](https://github.com/dbrgn/tealdeer) |
| **`fuck`** | `kps fuck` | タイプミスしたコマンドの自動修正と再実行 | [thefuck](https://github.com/nvbn/thefuck) |
| **`profile`** | `kps profile` | ドットファイルと開発環境設定のバージョン管理 | [chezmoi](https://github.com/twpayne/chezmoi) |
| **`rec`** | `kps rec` | CLI スニペットのブックマーク・パラメータ化・実行 | [pet](https://github.com/knqyf263/pet) |

---

## 🌍 コミュニティプラグイン

開発者は自由にプラグインを開発・共有できます：

- 新しいコマンドや外部ツール
- クラウドや開発ワークフローの統合
- カスタム Carapace 補完仕様
- 自動化ユーティリティ

**[Kapsel プラグインリポジトリ](https://github.com/MrEiu/plugins)** から貢献できます。

---

# 📦 インストール

## 推奨方式

### pipx

```bash
pipx install kapsel-cli
```

### pip

```bash
pip install --upgrade kapsel-cli
```

---

## ワンライン自動インストーラー

### macOS & Linux

```bash
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install.ps1 | iex
```

---

## スタンドアロンバイナリ

Python 環境が不要なビルド済みバイナリも提供しています：

| プラットフォーム / アーキテクチャ | 配布物 |
| :--- | :--- |
| **Windows x86_64** | `kapsel-windows-x86_64.zip` |
| **Linux x86_64** | `kapsel-linux-x86_64.tar.gz` |
| **macOS Universal** | `kapsel-macos-universal.tar.gz` |
| **Debian / Ubuntu** | `kapsel_amd64.deb` |

最新リリースは **[GitHub Releases](https://github.com/MrEiu/Kapsel/releases/latest)** をご覧ください。

---

## パッケージマネージャー

- **Scoop**
- **Homebrew**
- **Debian / Ubuntu (.deb)**

詳細は **[インストールガイド](docs/INSTALLATION.md)** をご覧ください。

---

## ソースからビルド

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
pip install -e .
kps completion sync
```

---

# ⚙️ 設定

設定ファイルパス：

```text
~/.kapsel/config.yaml
```

ターミナルから直接設定を確認・変更可能：

```bash
kps config
```

エディタで設定を開く：

```bash
kps config edit
```

キーバリューの直接設定：

```bash
kps config set ui.enable_banner false
kps config set interaction.autosuggest_sensitivity 0.2
```

変更はセッションの再起動なしに即座に反映されます。詳細は **[設定ガイド](docs/configuration.md)** をご覧ください。

---

# 🏛️ アーキテクチャ

Kapsel は既存のホストシェルの外側に位置する非侵襲レイヤーとして機能します。

```text
                     ホストターミナル
                            │
                            ▼
                 ┌─────────────────────┐
                 │       Kapsel        │
                 │                     │
                 │  コマンドディスパッチャ │
                 │  補完エンジン        │
                 │  プラグインレジストリ  │
                 │  履歴・状態管理      │
                 └──────────┬──────────┘
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
           ネイティブコマンド     Kapsel コマンド
           git / docker / ...     kps <command>
```

## 二重状態実行パイプライン (Dual-State Execution)

- **ネイティブ実行**：システムコマンドはそのまま透過的にホスト環境へ渡され、TTY、シグナル、ストリームが完全維持されます。
- **Kapsel 実行**：`kps` 名前空間とプラグインシステムを通じて安全に処理されます。

## 衝突防止名前空間 (Collision-Safe Namespaces)

`alias`、`help`、`install`、`history`、`profile`、`ps`、`kill`、`dir` などのコマンドは `kps` 名前空間内に分離され、ホストシェルの内蔵コマンドを乗っ取ることはありません。

## 汚染ゼロのディレクトリ構造

```text
~/.kapsel/
├── config.yaml          # 設定ファイル
├── history.db           # SQLite 履歴データベース
├── bin/                 # ユーザー空間バイナリ
├── specs/               # Carapace 補完仕様
├── plugins/             # インストール済みプラグイン
└── logs/                # 診断・ログ
```

---

# 📚 ドキュメント

| ドキュメント | 説明 |
| :--- | :--- |
| [インストールガイド](docs/INSTALLATION.md) | プラットフォームごとの詳細なセットアップ手順 |
| [設定ガイド](docs/configuration.md) | 設定オプションとパラメータ一覧 |
| [コマンドリファレンス](docs/commands.md) | 利用可能な全コマンドとオプション |
| [プラグイン](docs/plugins.md) | プラグインの機能と使い方 |
| [プラグイン開発](https://github.com/MrEiu/plugins) | プラグインの作成と公開手順 |
| [アーキテクチャ](docs/architecture.md) | 内部設計とアーキテクチャ解説 |

---

# 🧪 開発とテスト

リポジトリのクローン：

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
```

依存関係のインストール：

```bash
pip install -e ".[test]"
```

テストの実行：

```bash
pytest tests/ -v
```

---

# 🤝 貢献

Kapsel へのコントリビューションを心より歓迎します。

- **コア開発**：バグ修正、機能追加、パフォーマンス改善
- **プラグイン開発**：**[プラグインリポジトリ](https://github.com/MrEiu/plugins)** での新規ツール公開
- **ドキュメント**：ガイドの改善、翻訳、サンプルコードの充実

---

# 📄 ライセンス

Kapsel は **[MIT License](LICENSE)** に基づいて公開されているオープンソースソフトウェアです。

---

<div align="center">

**Kapsel — 複雑さを包み込み、シンプルさを届ける。**

Built by [MrEiu](https://github.com/MrEiu) and open-source contributors.

</div>
