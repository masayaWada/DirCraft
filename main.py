#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DirCraft - 作業用フォルダ作成ツール
メインアプリケーションファイル
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from gui.main_window import MainWindow

    def main():
        """メイン関数"""
        try:
            # メインウィンドウを作成して実行
            app = MainWindow()
            app.run()
        except Exception as e:
            print(f"アプリケーションの実行中にエラーが発生しました: {e}")
            sys.exit(1)

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"必要なモジュールのインポートに失敗しました: {e}")
    print("以下の点を確認してください:")
    print("1. 必要なPythonパッケージがインストールされているか")
    print("2. プロジェクトの構造が正しいか")
    sys.exit(1)
