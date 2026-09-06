<div align="center">

# ⚡ Kapsel

**次世代インテリジェントターミナルカプセル＆クロスプラットフォーム人間工学シェルマルチプレクサ**

[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/kapsel-cli/)
[![Platform Support](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4D4D4D.svg?style=flat-square&logo=linux&logoColor=white)](https://github.com/MrEiu/Kapsel)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

<p align="center">
  <i>「複雑さを包み込み、シンプルさを公開する。」</i><br>
  ゼロ汚染・コンテキスト認識型コマンド抽象化レイヤー、そして高性能インタラクティブカプセル環境。<br>
  Windows PowerShell、macOS Zsh、Linux Bash にわたる一貫した開発者ワークフローを実現します。
</p>

---

[主要機能](#-主要機能) •
[クイックインストール](#-クイックインストール) •
[アーキテクチャ](#-アーキテクチャと哲学) •
[プラグインエコシステム](#-公式プラグインエコシステム) •
[比較](#-機能マトリックスと比較) •
[チートシート](#-コマンドリファレンス) •
[🇨🇳 简体中文](README_zh.md)

---

</div>

```text
╭─ kapsel [pwsh] ~/Projects/Kapsel 14:32:05
╰─ ❯ git checkout -b feature/dynamic-specs
✔ 0  git checkout -b feature/dynamic-specs  ⏱ 24ms
```

---

## 🌟 概要

開発者は日々、異なるオペレーティングシステムを行き来しながら、断片化されたターミナルの操作性に悩まされています：
- 筋肉記憶の衝突（`rm -rf` と `Remove-Item`、`cat` と `type`、`ls -la` と `dir /a`）；
- 脆弱なグローバルドットファイルが `.bashrc`、`config.fish`、または `$PROFILE` を汚染；
- シェル間で一貫性のないオートコンプリートエンジン。

**Kapsel** は、**非侵襲的でサンドボックス化されたターミナルカプセル**を導入することで、この問題を解決します。これは、**グローバルシステムへの汚染を一切行わず**にコマンドライン操作をインターセプトして強化する、人間工学に基づいた実行レイヤーとして動作し、サブミリ秒の非同期オートコンプリート、Linuxファーストのユニバーサルマッピング、自動化された環境分離を実現します。

## 🚀 主な機能

### 1. デュアルステート実行マルチプレクサ
- **ネイティブ実行レイヤー（デフォルトモード）**:
  すべてのシステム実行ファイル（`git`、`docker`、`npm`、`cargo`、`python`、`vim`）に対する直接的でゼロオーバーヘッドなパススルー。完全なTTY対話、リアルタイムシグナル処理、標準ストリームパイピングを保持します。
- **統合カプセルパイプライン（`kps <cmd>` / `kapsel <cmd>`）**:
  汎用コマンド、プラグインユーティリティ、システム設定のための単一エントリポイント。実行プレフィックスを除去し、クロスプラットフォームコマンドをホスト最適化されたプリミティブにその場で変換します。
- **非同期ディープ自動提案**:
  永続的で分離されたSQLite統計ストア（`~/.kapsel/history.db`）を利用した、ミュートされたインラインヒストリー予測。`→`（右矢印）で提案を即座に受け入れます。

### 2. マルチシェル動的オートコンプリート（Carapace搭載）
- **1,000以上のコマンドカバレッジ**:
  [Carapace](https://carapace.sh)との直接統合により、マルチシェル、マルチレベルの引数およびコンテキスト補完（gitブランチ/タグ、dockerコンテナ/イメージ、kubectlポッド、npmスクリプト）を実現します。
- **ゼロセットアップブートストラップ**:
  初回起動時に、Kapselは公式プラットフォームバイナリを**管理者/root権限ゼロ**で`~/.kapsel/bin/`へ静かにブートストラップします。

### 3. デュアルルート仕様＆衝突センチネル
- **名前空間付きルートツリー（`kps.yaml` & `kapsel.yaml`）**:
  コア組み込みコマンドとプラグイン仕様を、`kps`および`kapsel`配下の分離されたルートツリーへ動的にコンパイルします。
- **ホスト名前空間衝突センチネル**:
  ホストシェルの組み込みコマンド（`alias`、`help`、`install`、`history`、`profile`、`ps`、`kill`、`dir`）を厳密にガードします。ホストとの衝突の可能性があるコマンドは`kps`名前空間内に封印され、**ネイティブシェルコマンド（例：PowerShellの`Get-Alias`）が100%乗っ取られないことを保証します**。
- **ディープパラメータ補完**:
  `kps alias add <Tab>`と入力すると、任意のターミナルでリッチなマルチレベルフラグ補完（`--from`、`--to`、`--shell`、`--global`）が提供されます。

### 4. モジュール式でクラッシュプルーフなプラグインサブシステム
- **分離アーキテクチャ**: プラグインは分離されたメモリ境界で動作します。誤動作するプラグインがKapsel Coreをクラッシュさせることは決してありません。
- **宣言的仕様標準**: すべてのプラグインは、Carapace仕様に準拠した独立した宣言的YAML仕様を定義します。

### 5. ミニマリストなボックス型ターミナル美学
- **カードフレーミング**: モダンなボックス型フレーミング（`╭─ ❯`および`╰─`）を使用した、コマンド入力と出力の明確な視覚的境界。
- **テレメトリフィードバック**: 実行終了コード（`✔ 0`または`✘ exit 1`）と正確なウォールクロック経過時間（`⏱ 38ms`）の即時表示。
- **ネイティブ多言語エンジン（i18n）**: 7言語（`en`、`zh_CN`、`ja`、`es`、`fr`、`de`、`ru`）での完全なローカライゼーション。

## ⚡ クイックインストール

ご自身の環境に最適なインストール方法をお選びください：

- [📦 パッケージマネージャー（PyPI / Scoop / Homebrew / APT）](#1-パッケージマネージャー)
- [💾 プリコンパイル済みスタンドアロンバイナリ](#2-プリコンパイル済みスタンドアロンバイナリ-依存関係ゼロ)
- [🌐 自動ツールチェーンインストーラー](#3-自動ツールチェーンインストーラー)
- [🛠️ ソースコードからのビルド](#4-ソースコードからのビルド)

> 🇨🇳 **中国本土ユーザー向け**：中国国内にお住まいで、高速ミラーアクセラレーション（ghproxy、Tsinghua PyPIミラー、国内ダウンロードスクリプト）が必要な場合は、**[README_zh.md](README_zh.md)** または [docs/INSTALLATION.md](docs/INSTALLATION.md) を参照してください。

---

### 1. 📦 パッケージマネージャー

#### PyPI（Python 3.9+）

```bash
# 推奨：pipxによる分離環境（グローバルなPython環境の汚染を防止）
pipx install kapsel-cli

# または標準的なpipインストール
pip install --upgrade kapsel-cli
```

#### Windows：Scoop

```powershell
# Kapsel公式バケットを追加してインストール
scoop bucket add kapsel https://github.com/MrEiu/scoop-bucket
scoop install kapsel
```

#### macOS & Linux：Homebrew

```bash
# Kapsel公式tapを追加してインストール
brew tap MrEiu/tap
brew install kapsel
```

#### Debian & Ubuntu：APT & DPKG（.deb）

```bash
curl -LO https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb
sudo dpkg -i kapsel_amd64.deb || sudo apt-get install -f -y
```

---

### 2. 💾 プリコンパイル済みスタンドアロンバイナリ（依存関係ゼロ）

Pythonランタイムや外部パッケージマネージャーは不要です。解凍して実行するだけです：

| プラットフォーム / アーキテクチャ | リリース成果物 | 公式GitHubダウンロード |
| :--- | :--- | :--- |
| **Windows x86_64** | `kapsel-windows-x86_64.zip` | [ダウンロード](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-windows-x86_64.zip) |
| **Linux x86_64** | `kapsel-linux-x86_64.tar.gz` | [ダウンロード](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-linux-x86_64.tar.gz) |
| **macOS（ユニバーサル）** | `kapsel-macos-universal.tar.gz` | [ダウンロード](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel-macos-universal.tar.gz) |
| **Debian / Ubuntu** | `kapsel_amd64.deb` | [ダウンロード](https://github.com/MrEiu/Kapsel/releases/latest/download/kapsel_amd64.deb) |

> 💡 **使用上のヒント**：アーカイブを解凍し、`kapsel`（または `kapsel.exe`）と `kps`（または `kps.exe`）をシステムの `PATH` が通っている任意のディレクトリ（例：`~/.kapsel/bin` や `/usr/local/bin`）に配置してください。

---

### 3. 🌐 自動ツールチェーンインストーラー

お使いのプラットフォームを自動検出し、Kapselをセットアップするとともに、最新のコマンドラインユーティリティ（`carapace`、`zoxide`、`mise`、`chsrc`、`aichat`、`pueue`、`chezmoi`、`pet`、`tealdeer`、`fzf`）を設定します：

```powershell
# Windows（PowerShell）：
irm https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_windows.ps1 | iex
```

```bash
# macOS：
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_macos.sh | bash

# Linux（Debian / Ubuntu / Fedora / Arch）：
curl -fsSL https://raw.githubusercontent.com/MrEiu/Kapsel/master/scripts/install_tools_linux.sh | bash
```

---

### 4. 🛠️ ソースコードからのビルド

Kapselコアへの貢献やカスタムプラグインの開発を希望する開発者に最適です：

```bash
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel
pip install -e .
kps completion sync
```

---

## 🧩 公式プラグインエコシステム

Kapselは、現代のエンジニアリングワークフローを満たすために設計された、モジュール式で疎結合なプラグインスイートを維持しています:

| プラグイン | コマンド | コアテクノロジー | 説明 |
| :--- | :--- | :--- | :--- |
| **`init`** | `kps init` | **`mise`** (Rust) | プロジェクトツールチェーン＆ポリグロットランタイムマネージャー（nvm、pyenv、rbenvを置き換え）。 |
| **`portal`** | `kps portal` / `z` | **`zoxide`** (Rust) | 頻度と再帰性に基づく重み付けされたディレクトリテレポートーションとファジーナビゲーション。 |
| **`shore`** | `kps shore` | **`chsrc`** (C) | 自動化された超高速ミラー切り替え（PyPI、Rust、Node、Go、OSミラー）。 |
| **`install`** | `kps install` | **`mpm`** (Python) | 20以上のパッケージマネージャーを統合する統一CLIパッケージマネージャー。 |
| **`alias`** | `kps alias` | *ネイティブエンジン* | ユニバーサルコマンドエイリアス変換とマルチターミナルクロスマッピング。 |
| **`ai`** | `kps ai` | **`aichat`** (Rust) | OpenAI、Claude、Gemini、DeepSeek、OllamaをサポートするターミナルAIコパイロット。 |
| **`autopilot`**| `kps autopilot`| **`pueue`** (Rust) | 自律的なバックグラウンドタスクキューと長時間実行デーモン実行マネージャー。 |
| **`fuck`** | `kps fuck` | **`thefuck`** (Python) | インテリジェントなターミナル入力エラー修正と自動構文修正。 |
| **`help`** | `kps help <cmd>`| **`tealdeer`** (Rust) | 即座に利用可能な実践的なコマンドチートシートとクイックルックアップ（tldr）。 |
| **`profile`** | `kps profile` | **`chezmoi`** (Go) | クロスプラットフォームのドットファイル、シェルプロファイル、シークレット暗号化環境マネージャー。 |
| **`rec`** | `kps rec` | **`pet`** (Go) | インタラクティブなCLIスニペットレコーダー、引数パラメータ化、ランナー。 |

---

## 📊 機能マトリクスと比較

| 機能 | Kapsel | 標準シェル (Bash/Zsh/Pwsh) | Starship | Oh-My-Zsh |
| :--- | :---: | :---: | :---: | :---: |
| **非侵襲型ランタイム（プロファイル改変ゼロ）** | **対応** | 非対応 | 非対応 | 非対応 |
| **1,000以上のコマンドコンテキスト補完（Carapace）** | **対応** | 手動プラグイン | 非対応（プロンプトのみ） | 一部対応（低速） |
| **クロスプラットフォームLinuxファーストマッピング（`kps`）** | **対応** | 非対応 | 非対応 | 非対応 |
| **デュアルルート仕様アーキテクチャ（衝突防止）** | **対応** | 非対応 | 非対応 | 非対応 |
| **ボックス型ターミナル実行フレーミング** | **対応** | 非対応 | プロンプトのみ | 非対応 |
| **分離サンドボックス状態（`~/.kapsel/`）** | **対応** | 断片的 | 非対応 | 断片的 |
| **サブミリ秒の非同期UI応答** | **対応** | 環境依存 | 対応 | 低速な場合が多い |

---

## 📖 コマンドリファレンス

### 対話型シェルモード（`kapsel` / `kps`）

Kapselを対話型シェルセッションとして起動します：
```bash
kapsel
```

カプセルセッション内では、以下の統合コマンドが利用可能です：

```text
help                    Kapselマニュアル、対話メカニズム、コマンドチートシートを表示
status                  OS環境、アクティブなホストシェル、Gitブランチ、サンドボックス状態を検査
upgrade [plugin]        Kapselコアと公式プラグインの2段階アップグレードチェックを変更ログ付きで実行
search [-a]             公式プラグインをバージョンとインストール状態付きで検索・発見
enable <plugin>         インストール済みプラグインを有効化し、オートコンプリートを同期
disable <plugin>        ローカルファイルを削除せずにアクティブなプラグインを無効化
config                  コア設定（~/.kapsel/config.yaml）を検査または編集
  config path           物理設定ファイルのパスを表示
  config edit           デフォルトの外部エディタで設定を開く
  config get <key>      設定キーの値を取得
  config set <k> <v>    ターミナルから設定値を更新
  config reload         セッションを再起動せずにディスクから設定をホットリロード
completion              宣言型Carapace仕様の管理、検査、同期
  completion ls         アクティブな補完仕様、スコープ、マウント状態を一覧表示
  completion sync       デュアルルート仕様（kps.yamlとkapsel.yaml）を強制コンパイルおよび同期
  completion new <cmd>  新しい宣言型仕様テンプレートを生成
  completion path       アクティブな仕様ディレクトリを表示
datadir                 データストレージサンドボックスディレクトリを検査または安全に再配置
language <lang>         アクティブなUI言語を切り替え（en、zh_CN、ja、es、fr、de、ru）
toggle                  Kapselのデフォルトターミナルモードを切り替え（1回目の呼び出しで開く、2回目で閉じる）
clear                   ターミナル画面をクリアし、ヘッダーバナーを再描画
exit                    Kapselをクリーンに終了し、ネイティブホストシェルに戻る
```

### ワンショット外部実行

標準シェルから任意のカプセルまたはプラグインコマンドを直接実行します：

```bash
# 管理と診断
kps status
kps completion ls
kps config edit

# プラグインコマンド
kps portal ls
kps shore get
kps init use node@22

# クロスプラットフォーム対応コマンド
kps rm -rf dist/
kps ls -la
```

---

## 🔒 ディレクトリサンドボックスと状態モデル

Kapselは**ゼロポリューション保証**を厳格に遵守します。すべてのデータ、バイナリ、キャッシュ、ログは、ユーザーサンドボックスディレクトリ内にのみ存在します：

```text
~/.kapsel/
├── config.yaml          # システム全体のUI設定（色、カード枠線、言語）
├── history.db           # コマンド履歴と統計を保存する永続SQLiteデータベース
├── bin/                 # ユーザー空間のスタンドアロンバイナリツール（carapace、zoxide、mise、chsrc...）
├── specs/               # ユーザーカスタムの宣言型オートコンプリート仕様
├── plugins/             # インストール済みの公式およびコミュニティプラグインパッケージ
└── logs/                # セッションログとクラッシュ診断

## 🧪 テストと品質保証

Kapselコードベースは、厳格な型チェックと分離されたフィクスチャにより、徹底したテストカバレッジを実施しています：

```bash
# リポジトリのクローン
git clone https://github.com/MrEiu/Kapsel.git
cd Kapsel

# テスト依存関係のインストール
pip install -e ".[test]"

# 全テストスイートの実行
pytest tests/ -v
```

全79件の自動化ユニットテストが、スペックマネージャーの検出、衝突センチネルブロッキング、カラパス統合、プラグインライフサイクル、およびi18n解決を検証します。

---

## 🤝 コントリビューション & コミュニティ

コントリビューションを歓迎します！
- [issues](https://github.com/MrEiu/Kapsel/issues) を確認して、タスクを見つけたりバグを報告したりしてください。
- プラグインの開発や提出については、[プラグインガイド](https://github.com/MrEiu/plugins) を参照してください。

---

## 📄 ライセンス

Kapselは、**[MITライセンス](LICENSE)** の下で提供されるオープンソースソフトウェアです。

<div align="center">
  <sub>MrEiuとKapselオープンソースチームによって、モダンなターミナル人間工学に基づいて構築されました。</sub>
</div>
