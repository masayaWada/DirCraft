#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DirCraft - 作業用フォルダ作成ツール
メインアプリケーションファイル
"""

import sys
import os
import traceback
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """メイン関数"""
    try:
        # 高速起動のため、最小限のログ出力
        print("DirCraft アプリケーションを起動中...")

        # 設定ファイルの存在確認（自動生成される）
        config_dir = project_root / "config"
        if not config_dir.exists():
            print("設定ファイルを初期化中...")

        # 必要なモジュールのインポート
        from gui.main_window import MainWindow

        # メインウィンドウを作成して実行
        app = MainWindow()
        app.run()

    except ImportError as e:
        print(f"エラー: 必要なモジュールのインポートに失敗しました: {e}")
        print("詳細なエラー情報:")
        traceback.print_exc()
        print("\n以下の点を確認してください:")
        print("1. 必要なPythonパッケージがインストールされているか")
        print("2. プロジェクトの構造が正しいか")
        print("3. 設定ファイルが正しく配置されているか")
        input("\nEnterキーを押して終了してください...")
        sys.exit(1)

    except Exception as e:
        print(f"エラー: アプリケーションの実行中にエラーが発生しました: {e}")
        print("詳細なエラー情報:")
        traceback.print_exc()
        input("\nEnterキーを押して終了してください...")
        sys.exit(1)


if __name__ == "__main__":
    main()
