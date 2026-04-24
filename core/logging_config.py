"""アプリ全体のロギング設定。

- ファイルログ: ``config/dircraft.log`` にローテーション付きで記録
- 標準エラー: WARNING 以上のみ出力（PyInstaller --windowed では失われる
  が、--console デバッグ版では確認できる）

``configure_logging()`` はアプリ起動時に一度だけ呼び出す。
"""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
_CONFIGURED = False


def configure_logging(log_dir: str | Path = "config", *, level: int = logging.INFO) -> Path:
    """ルートロガーにファイル/コンソールハンドラを追加する。

    戻り値はログファイルのパス。
    """
    global _CONFIGURED

    log_path = Path(log_dir) / "dircraft.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if _CONFIGURED:
        return log_path

    formatter = logging.Formatter(_LOG_FORMAT)

    file_handler = RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(stream_handler)

    _CONFIGURED = True
    return log_path
