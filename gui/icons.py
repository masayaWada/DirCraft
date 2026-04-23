"""OOUI PNG アイコンを読み込むためのローダー。

PyInstaller で onefile ビルドされた際は assets/ が ``sys._MEIPASS`` 以下に
展開されるため、両方のパスを解決する。
"""
from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path


def _assets_root() -> Path:
    """開発時/PyInstaller 同梱時のどちらでも assets ディレクトリを返す。"""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass) / "assets"
    return Path(__file__).resolve().parent.parent / "assets"


class IconSet:
    """アイコンの PhotoImage をまとめて保持するコンテナ。

    tkinter は PhotoImage への参照が途切れると画像を GC するため、
    ウィンドウ側からこのインスタンスを属性として保持する。
    """

    def __init__(self, names: list[str]) -> None:
        self._images: dict[str, tk.PhotoImage] = {}
        icons_dir = _assets_root() / "icons"
        for name in names:
            path = icons_dir / f"{name}.png"
            if path.exists():
                self._images[name] = tk.PhotoImage(file=str(path))

    def get(self, name: str) -> tk.PhotoImage | None:
        return self._images.get(name)
