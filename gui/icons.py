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


def _detect_scaling(root: tk.Misc | None = None) -> float:
    """現在の Tk の表示スケール（1.0 = 96 DPI）を返す。"""
    try:
        if root is None:
            root = tk._default_root  # type: ignore[attr-defined]
        if root is None:
            return 1.0
        # tk scaling は "pixels per point" を返す (72pt = 1inch)
        pixels_per_point = float(root.tk.call("tk", "scaling"))
        return pixels_per_point * 72.0 / 96.0
    except Exception:
        return 1.0


class IconSet:
    """アイコンの PhotoImage をまとめて保持するコンテナ。

    tkinter は PhotoImage への参照が途切れると画像を GC するため、
    ウィンドウ側からこのインスタンスを属性として保持する。
    HiDPI 環境では ``<name>@2x.png`` が存在すればそれを採用する。
    """

    def __init__(self, names: list[str], root: tk.Misc | None = None) -> None:
        self._images: dict[str, tk.PhotoImage] = {}
        icons_dir = _assets_root() / "icons"
        use_hidpi = _detect_scaling(root) >= 1.5
        for name in names:
            hidpi_path = icons_dir / f"{name}@2x.png"
            std_path = icons_dir / f"{name}.png"
            path = hidpi_path if (use_hidpi and hidpi_path.exists()) else std_path
            if path.exists():
                self._images[name] = tk.PhotoImage(file=str(path))

    def get(self, name: str) -> tk.PhotoImage | None:
        return self._images.get(name)
