"""OOUI PNG アイコンを読み込むためのローダー。

PyInstaller で onefile ビルドされた際は assets/ が ``sys._MEIPASS`` 以下に
展開されるため、両方のパスを解決する。
"""
from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """プロジェクトルート基準のリソースパスを返す。

    PyInstaller で onefile バンドル化された場合は ``sys._MEIPASS`` 以下の
    展開先を基準にする。
    """
    meipass = getattr(sys, "_MEIPASS", None)
    base = Path(meipass) if meipass else Path(__file__).resolve().parent.parent
    return base.joinpath(*parts)


def _assets_root() -> Path:
    return resource_path("assets")


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
