# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [2.0.0] - 2026-04-26

### Added
- ttkbootstrap によるモダンUIテーマシステム
- Wikimedia OOUI アイコンセット（HiDPI @2x 対応）
- インラインバリデーションバナーとフィールド赤枠表示
- ディレクトリ作成後の OS ファイラー自動オープン
- 設定画面でのテーマ切り替え機能
- 「その他」作業テンプレートの設定機能
- 型ヒント（type hints）の追加
- テストケースの拡充（14テスト）
- CLAUDE.md によるプロジェクトドキュメント

### Changed
- GUI フレームワークを標準 tkinter から ttkbootstrap に移行
- ボタンアイコンを Wikimedia OOUI のアイコンセットに置換
- レイアウトとスペーシングの全面最適化
- UI/運用品質の改善

### Removed
- 終了ボタン（ウィンドウの閉じるボタンに統一）

## [1.3.0] - 2025-10-20

### Changed
- ビルドシステムを Nuitka から PyInstaller へ移行
- PowerShell ビルドスクリプトの提供
- .spec ファイルによるカスタマイズ対応

### Added
- ディレクトリ作成後の自動オープン機能

## [1.2.0] - 2025-08-15

### Added
- 自動ビルドスクリプトの提供
- 本番版とデバッグ版の生成

## [1.1.0] - 2025-08-15

### Added
- ステータスバーの色分け表示（成功：緑、エラー：赤、通常：黒）
- パスをクリップボードにコピーするボタン
- 「その他」作業内容選択時の専用テンプレート機能

## [1.0.0] - 2025-08-15

### Added
- 基本的なディレクトリ作成機能
- 標準雛形ファイル（xlsx）のコピー機能
- シンプルな GUI インターフェース
- JSON 形式の設定ファイル管理（config.json, procedures.json）
- exe 形式での配布対応（Nuitka）
