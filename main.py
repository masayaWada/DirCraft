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
    import logging
    from core.logging_config import configure_logging

    log_path = configure_logging(project_root / "config")
    logger = logging.getLogger("dircraft")
    logger.info("DirCraft アプリケーションを起動中... (log: %s)", log_path)

    try:
        from gui.main_window import MainWindow

        app = MainWindow()
        app.run()

    except ImportError as e:
        logger.exception("必要なモジュールのインポートに失敗しました: %s", e)
        sys.stderr.write(
            "\n起動に失敗しました。以下を確認してください:\n"
            "  1. 必要な Python パッケージがインストールされているか\n"
            "  2. プロジェクト構造が正しいか\n"
            "  3. 設定ファイルが正しく配置されているか\n"
            f"  ログ: {log_path}\n"
        )
        sys.exit(1)

    except Exception as e:
        logger.exception("アプリケーションの実行中にエラーが発生しました: %s", e)
        sys.stderr.write(f"\n想定外のエラーが発生しました。詳細は {log_path} を参照してください。\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
