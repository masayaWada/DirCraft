# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

DirCraftは、クラウドインフラ変更作業用のディレクトリ構造をテンプレートから自動生成するPython GUIツール。tkinter + ttkbootstrap で構築され、PyInstallerでWindows向けexeにパッケージされる。

## コマンド

```bash
# 実行
python main.py

# テスト
python -m unittest discover -s tests -v

# 単一テスト
python -m unittest tests.test_validate_inputs -v

# 依存関係インストール
pip install -r requirements.txt

# exe ビルド (Windows PowerShell)
./build_pyinstaller.ps1
```

## アーキテクチャ

### レイヤー構成

- **main.py** — エントリーポイント。ロギング初期化後に `MainWindow` を起動
- **core/** — ビジネスロジック（GUI非依存）
  - `ConfigManager` — `config/config.json`（ユーザー設定）と `config/procedures.json`（テンプレートマッピング）の読み書き。ファイルが無ければデフォルト値で自動生成
  - `DirectoryCreator` — ディレクトリ名生成（`変更番号-日付-グループ-苗字-変更申請書-【クラウド】システム_作業内容_作業日`）、サブディレクトリ（手順書/証跡/メール）作成、テンプレートxlsxのコピー。`validate_inputs()` で入力検証しエラー辞書を返す
  - `logging_config` — RotatingFileHandler で `config/dircraft.log` に出力
- **gui/** — tkinter/ttkbootstrap UI
  - `MainWindow` — メイン画面。クラウド選択で作業内容コンボボックスを動的更新。バリデーションエラーはインラインバナー＋フィールド赤枠で表示。作成後にOS標準ファイラーで自動オープン
  - `SettingsWindow` — モーダル設定画面（苗字、グループ名、デフォルトディレクトリ、テーマ、その他作業テンプレート）
  - `icons.py` — `assets/icons/` からPNGアイコンを読み込み。PyInstaller `sys._MEIPASS` とHiDPI（@2x）に対応

### 設定ファイル

- `config/config.json` — `user_settings.last_name`, `team_group_name`, `default_directory`, `theme`
- `config/procedures.json` — クラウド×作業内容→テンプレートファイルパスのマッピング（`procedures`）、共通テンプレート（`common_templates`）、その他作業テンプレート（`other_work_templates`）
- 両ファイルとも `.gitignore` で除外されており、存在しなければ `ConfigManager` がデフォルト値で自動生成する

### データフロー

1. ユーザーがクラウドを選択 → `procedures.json` から作業内容の候補を動的ロード
2. 「ディレクトリ作成」→ `DirectoryCreator.validate_inputs()` → エラーがあればインラインバナー表示
3. 検証通過 → 既存ディレクトリ衝突チェック（マージ確認ダイアログ） → `create_work_directory()` でディレクトリ＋テンプレートコピー
4. 作成後のパスをクリップボードコピー可能

## 注意点

- GUI フレームワークは `ttkbootstrap`（tkinter拡張）。`ttk.Window` がルートウィンドウ
- テンプレートファイル（`.xlsx`）は `templates/` 配下だが `.gitignore` で除外。実環境では手動配置が必要
- テストは `unittest` ベース。`ConfigManager` はモックで差し替え可能
- Windows向けexe配布が主ターゲット。macOS/Linuxでも `python main.py` で動作するがファイラー連携部分が `platform.system()` で分岐

## Gotchas

- `build_pyinstaller.ps1` は Shift-JIS でエンコードされている。macOS/Linux では文字化けするが Windows PowerShell 環境専用なので問題ない
- `config/*.json` と `templates/*.xlsx` は `.gitignore` で除外。クローン直後は存在しないが、`ConfigManager` が初回アクセス時にデフォルト JSON を自動生成する。テンプレート xlsx は手動配置が必要
- ディレクトリ名に日本語（全角文字）を含む。Windows のパス長制限（260文字）に注意
- 作業内容で「その他」を選択すると自由入力フィールドが有効化され、`other_work_templates` から別系統のテンプレートが使われる
- `DateEntry` は ttkbootstrap 固有ウィジェット（tkinter 標準にはない）。`entry.get()` でフォーマット済み文字列を取得する
