from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

import ttkbootstrap as ttk
from ttkbootstrap.constants import (
    W, E, LEFT, RIGHT, X, BOTH,
    SUCCESS, INFO, SECONDARY, WARNING, DANGER, OUTLINE,
)
from ttkbootstrap.tooltip import ToolTip

from core.config_manager import ConfigManager
from .icons import IconSet, resource_path

if TYPE_CHECKING:
    from .main_window import MainWindow


FONT_FAMILY = "Yu Gothic UI"
FONT_BASE = (FONT_FAMILY, 10)
FONT_TITLE = (FONT_FAMILY, 20, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 11)


class SettingsWindow:
    """設定画面クラス"""

    def __init__(
        self,
        parent: tk.Misc,
        config_manager: ConfigManager,
        main_window: "MainWindow | None" = None,
    ) -> None:
        self.parent = parent
        self.config_manager = config_manager
        self.main_window = main_window

        self.window = ttk.Toplevel(parent)
        self.window.title("設定")
        self.window.geometry("640x640")
        self.window.resizable(False, False)
        ico_path = resource_path("DirCraft.ico")
        if ico_path.exists():
            try:
                self.window.iconbitmap(str(ico_path))
            except tk.TclError:
                pass

        self.window.transient(parent)
        self.window.grab_set()

        # ショートカット: Enter=保存, Esc=キャンセル
        self.window.bind("<Return>", lambda _e: self._save_settings())
        self.window.bind("<Escape>", lambda _e: self._on_closing())

        self.icons = IconSet(
            ["folder", "file", "check", "cancel", "reload"],
            root=self.window,
        )

        self.last_name_var = tk.StringVar()
        self.default_directory_var = tk.StringVar()
        self.team_group_name_var = tk.StringVar()
        self.theme_var = tk.StringVar()

        # フィールドキー → ウィジェット
        self._field_widgets: dict[str, tk.Widget] = {}

        self._init_ui()
        self._load_current_settings()

        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _init_ui(self) -> None:
        """UI要素を初期化"""
        main_frame = ttk.Frame(self.window, padding=24)
        main_frame.pack(fill=BOTH, expand=True)

        # ヘッダー
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 8))

        ttk.Label(header_frame, text="設定", font=FONT_TITLE).pack(anchor=W)
        ttk.Label(
            header_frame,
            text="アプリケーションの動作をカスタマイズします",
            font=FONT_SUBTITLE,
            foreground="#6c757d",
        ).pack(anchor=W, pady=(2, 0))

        ttk.Separator(main_frame, orient="horizontal").pack(fill=X, pady=(8, 16))

        # ユーザー設定セクション
        settings_frame = ttk.Labelframe(
            main_frame, text=" ユーザー設定 ", padding=16
        )
        settings_frame.pack(fill=X, pady=(0, 16))

        last_name_entry = self._create_setting_row(
            settings_frame, "苗字", self.last_name_var, 0
        )
        dir_entry = self._create_directory_row(
            settings_frame, "デフォルトディレクトリ", self.default_directory_var, 1
        )
        group_entry = self._create_setting_row(
            settings_frame, "グループ名", self.team_group_name_var, 2
        )
        self._register_field("last_name", last_name_entry)
        self._register_field("default_directory", dir_entry)
        self._register_field("team_group_name", group_entry)
        self._create_theme_row(settings_frame, 3)

        # テンプレート設定セクション
        template_frame = ttk.Labelframe(
            main_frame, text=" その他作業用テンプレート設定 ", padding=16
        )
        template_frame.pack(fill=X, pady=(0, 16))

        self.aws_other_template_var = tk.StringVar()
        self.azure_other_template_var = tk.StringVar()
        self.hybrid_other_template_var = tk.StringVar()

        self._create_template_row(
            template_frame, "AWS用テンプレート", self.aws_other_template_var, 0
        )
        self._create_template_row(
            template_frame, "Azure用テンプレート", self.azure_other_template_var, 1
        )
        self._create_template_row(
            template_frame, "AWS-Azure用テンプレート", self.hybrid_other_template_var, 2
        )

        ttk.Separator(main_frame, orient="horizontal").pack(fill=X, pady=(8, 16))

        # エラーバナー（初期は非表示。エラー時に ボタン行の直前に差し込む）
        self._error_banner = ttk.Label(
            main_frame,
            text="",
            bootstyle=(DANGER, "inverse"),
            padding=(12, 8),
            anchor=W,
            justify=LEFT,
            wraplength=560,
        )
        # ボタン行
        self._button_frame = ttk.Frame(main_frame)
        self._button_frame.pack(fill=X)
        button_frame = self._button_frame

        reset_btn = ttk.Button(
            button_frame,
            text=" デフォルトに戻す",
            image=self.icons.get("reload"),
            compound=LEFT,
            command=self._reset_to_default,
            bootstyle=(WARNING, OUTLINE),
        )
        reset_btn.pack(side=LEFT)
        ToolTip(
            reset_btn,
            text="全ての設定を初期値に戻します\n（現在の設定は破棄されます）",
            bootstyle=INFO,
        )

        save_btn = ttk.Button(
            button_frame,
            text=" 保存",
            image=self.icons.get("check"),
            compound=LEFT,
            command=self._save_settings,
            bootstyle=SUCCESS,
            width=14,
        )
        save_btn.pack(side=RIGHT)
        ToolTip(save_btn, text="設定を保存して閉じる (Enter)", bootstyle=INFO)

        cancel_btn = ttk.Button(
            button_frame,
            text=" キャンセル",
            image=self.icons.get("cancel"),
            compound=LEFT,
            command=self._on_closing,
            bootstyle=(SECONDARY, OUTLINE),
        )
        cancel_btn.pack(side=RIGHT, padx=(0, 8))
        ToolTip(cancel_btn, text="変更を破棄して閉じる (Esc)", bootstyle=INFO)

    def _create_setting_row(
        self,
        parent: tk.Widget,
        label_text: str,
        variable: tk.StringVar,
        row: int,
    ) -> ttk.Entry:
        """設定項目の行を作成し、作成した Entry を返す。"""
        ttk.Label(parent, text=label_text, foreground="#495057").grid(
            row=row, column=0, sticky=W, pady=8, padx=(0, 14)
        )
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, sticky=(W, E), pady=8)
        parent.columnconfigure(1, weight=1)
        return entry

    def _create_directory_row(
        self,
        parent: tk.Widget,
        label_text: str,
        variable: tk.StringVar,
        row: int,
    ) -> ttk.Entry:
        """ディレクトリ選択の行を作成し、作成した Entry を返す。"""
        ttk.Label(parent, text=label_text, foreground="#495057").grid(
            row=row, column=0, sticky=W, pady=8, padx=(0, 14)
        )

        dir_frame = ttk.Frame(parent)
        dir_frame.grid(row=row, column=1, sticky=(W, E), pady=8)
        dir_frame.columnconfigure(0, weight=1)

        entry = ttk.Entry(dir_frame, textvariable=variable)
        entry.grid(row=0, column=0, sticky=(W, E))

        browse_btn = ttk.Button(
            dir_frame,
            text=" 参照",
            image=self.icons.get("folder"),
            compound=LEFT,
            command=self._browse_directory,
            bootstyle=(SECONDARY, OUTLINE),
        )
        browse_btn.grid(row=0, column=1, padx=(8, 0))

        parent.columnconfigure(1, weight=1)
        return entry

    # 表示名 → ttkbootstrap テーマ名
    _THEME_CHOICES = {
        "ライト (cosmo)": "cosmo",
        "ライト (flatly)": "flatly",
        "ライト (litera)": "litera",
        "ダーク (darkly)": "darkly",
        "ダーク (superhero)": "superhero",
        "ダーク (cyborg)": "cyborg",
    }

    def _create_theme_row(self, parent: tk.Widget, row: int) -> None:
        """テーマ（配色）選択行を作成。"""
        ttk.Label(parent, text="テーマ", foreground="#495057").grid(
            row=row, column=0, sticky=W, pady=8, padx=(0, 14)
        )
        combo = ttk.Combobox(
            parent,
            textvariable=self.theme_var,
            values=list(self._THEME_CHOICES.keys()),
            state="readonly",
        )
        combo.grid(row=row, column=1, sticky=(W, E), pady=8)
        ToolTip(
            combo,
            text="配色テーマを切り替えます（保存時に反映）",
            bootstyle=INFO,
        )

    def _create_template_row(
        self,
        parent: tk.Widget,
        label_text: str,
        variable: tk.StringVar,
        row: int,
    ) -> None:
        """テンプレートファイル選択の行を作成"""
        ttk.Label(parent, text=label_text, foreground="#495057").grid(
            row=row, column=0, sticky=W, pady=8, padx=(0, 14)
        )

        file_frame = ttk.Frame(parent)
        file_frame.grid(row=row, column=1, sticky=(W, E), pady=8)
        file_frame.columnconfigure(0, weight=1)

        entry = ttk.Entry(file_frame, textvariable=variable)
        entry.grid(row=0, column=0, sticky=(W, E))

        browse_btn = ttk.Button(
            file_frame,
            text=" 参照",
            image=self.icons.get("file"),
            compound=LEFT,
            command=lambda: self._browse_template_file(variable),
            bootstyle=(SECONDARY, OUTLINE),
        )
        browse_btn.grid(row=0, column=1, padx=(8, 0))

        parent.columnconfigure(1, weight=1)

    def _browse_directory(self) -> None:
        """ディレクトリ選択ダイアログを表示"""
        directory = filedialog.askdirectory()
        if directory:
            self.default_directory_var.set(directory)

    def _browse_template_file(self, variable: tk.StringVar) -> None:
        """テンプレートファイル選択ダイアログを表示"""
        file_path = filedialog.askopenfilename(
            title="テンプレートファイルを選択",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if file_path:
            variable.set(file_path)

    def _load_current_settings(self) -> None:
        """現在の設定を読み込み"""
        self.last_name_var.set(
            self.config_manager.get_user_setting("last_name") or ""
        )
        self.default_directory_var.set(
            self.config_manager.get_user_setting("default_directory") or ""
        )
        self.team_group_name_var.set(
            self.config_manager.get_user_setting("team_group_name") or ""
        )
        current_theme = self.config_manager.get_user_setting("theme") or "cosmo"
        # テーマ名から表示ラベルへの逆引き
        display = next(
            (label for label, name in self._THEME_CHOICES.items() if name == current_theme),
            "ライト (cosmo)",
        )
        self.theme_var.set(display)

        procedures = self.config_manager.load_procedures()
        other_templates = procedures.get("other_work_templates", {})

        aws_templates = other_templates.get("AWS", [])
        self.aws_other_template_var.set(
            aws_templates[0] if aws_templates else ""
        )

        azure_templates = other_templates.get("Azure", [])
        self.azure_other_template_var.set(
            azure_templates[0] if azure_templates else ""
        )

        hybrid_templates = other_templates.get("AWS-Azure", [])
        self.hybrid_other_template_var.set(
            hybrid_templates[0] if hybrid_templates else ""
        )

    def _save_settings(self) -> None:
        """設定を保存"""
        try:
            errors = self._validate_inputs()
            if errors:
                self._show_validation_errors(errors)
                return
            self._clear_validation_errors()

            self.config_manager.set_user_setting(
                "last_name", self.last_name_var.get().strip()
            )
            self.config_manager.set_user_setting(
                "default_directory", self.default_directory_var.get().strip()
            )
            self.config_manager.set_user_setting(
                "team_group_name", self.team_group_name_var.get().strip()
            )
            theme_name = self._THEME_CHOICES.get(self.theme_var.get(), "cosmo")
            self.config_manager.set_user_setting("theme", theme_name)

            self._save_other_work_templates()

            messagebox.showinfo("保存完了", "設定が正常に保存されました。")

            self._update_parent_settings()

            self.window.destroy()

        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました:\n{str(e)}")

    def _save_other_work_templates(self) -> None:
        """その他作業用テンプレートの設定を保存"""
        procedures = self.config_manager.load_procedures()

        other_work_templates = {
            "AWS": [self.aws_other_template_var.get().strip()] if self.aws_other_template_var.get().strip() else [],
            "Azure": [self.azure_other_template_var.get().strip()] if self.azure_other_template_var.get().strip() else [],
            "AWS-Azure": [self.hybrid_other_template_var.get().strip()] if self.hybrid_other_template_var.get().strip() else [],
        }

        procedures["other_work_templates"] = other_work_templates
        self.config_manager.save_procedures(procedures)

    def _validate_inputs(self) -> dict[str, str]:
        """入力値の検証。フィールド名 → エラーメッセージの辞書を返す。"""
        errors: dict[str, str] = {}

        if not self.last_name_var.get().strip():
            errors["last_name"] = "苗字は必須です"

        default_dir = self.default_directory_var.get().strip()
        if not default_dir:
            errors["default_directory"] = "デフォルトディレクトリは必須です"
        elif not Path(default_dir).exists():
            errors["default_directory"] = "指定されたディレクトリが存在しません"
        elif not Path(default_dir).is_dir():
            errors["default_directory"] = "指定されたパスはディレクトリではありません"

        if not self.team_group_name_var.get().strip():
            errors["team_group_name"] = "グループ名は必須です"

        return errors

    def _register_field(self, key: str, widget: tk.Widget) -> None:
        self._field_widgets[key] = widget
        widget.bind(
            "<FocusIn>",
            lambda _e, k=key: self._clear_field_error(k),
            add="+",
        )

    def _show_validation_errors(self, errors: dict[str, str]) -> None:
        if not errors:
            self._clear_validation_errors()
            return
        lines = ["入力を確認してください:"]
        lines.extend(f"• {msg}" for msg in errors.values())
        self._error_banner.configure(text="\n".join(lines))
        self._error_banner.pack(fill=X, pady=(0, 12), before=self._button_frame)

        for key in errors:
            widget = self._field_widgets.get(key)
            if widget is not None:
                try:
                    widget.configure(bootstyle=DANGER)
                except tk.TclError:
                    pass

        first_key = next(iter(errors))
        first_widget = self._field_widgets.get(first_key)
        if first_widget is not None:
            try:
                first_widget.focus_set()
            except tk.TclError:
                pass

    def _clear_validation_errors(self) -> None:
        self._error_banner.configure(text="")
        self._error_banner.pack_forget()
        for widget in self._field_widgets.values():
            try:
                widget.configure(bootstyle="")
            except tk.TclError:
                pass

    def _clear_field_error(self, key: str) -> None:
        widget = self._field_widgets.get(key)
        if widget is None:
            return
        try:
            widget.configure(bootstyle="")
        except tk.TclError:
            pass

    def _reset_to_default(self) -> None:
        """デフォルト設定に戻す"""
        if messagebox.askyesno("確認", "設定をデフォルトに戻しますか？\n現在の設定は失われます。"):
            self.config_manager._create_default_config()
            self._load_current_settings()
            messagebox.showinfo("完了", "設定をデフォルトに戻しました。")

    def _update_parent_settings(self) -> None:
        """親ウィンドウの設定を更新"""
        try:
            if self.main_window and hasattr(self.main_window, "update_settings"):
                self.main_window.update_settings()
            elif hasattr(self.parent, "update_settings"):
                self.parent.update_settings()
        except Exception:
            pass

    def _on_closing(self) -> None:
        """ウィンドウが閉じられるときの処理"""
        current_last_name = self.config_manager.get_user_setting("last_name") or ""
        current_default_dir = self.config_manager.get_user_setting("default_directory") or ""
        current_team_group_name = self.config_manager.get_user_setting("team_group_name") or ""

        has_changes = (
            self.last_name_var.get().strip() != current_last_name
            or self.default_directory_var.get().strip() != current_default_dir
            or self.team_group_name_var.get().strip() != current_team_group_name
        )

        if has_changes:
            if messagebox.askyesno("確認", "変更が保存されていません。\n保存せずに閉じますか？"):
                self.window.destroy()
        else:
            self.window.destroy()
