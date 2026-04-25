from __future__ import annotations

import logging
import os
import platform
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import (
    W, E, N, S, LEFT, RIGHT, X, BOTH,
    SUCCESS, INFO, SECONDARY, DANGER, WARNING,
    OUTLINE,
)
from ttkbootstrap.tooltip import ToolTip

from core.config_manager import ConfigManager
from core.directory_creator import DirectoryCreator
from .icons import IconSet, resource_path

logger = logging.getLogger(__name__)


FONT_FAMILY = "Yu Gothic UI"
FONT_BASE = (FONT_FAMILY, 10)
FONT_TITLE = (FONT_FAMILY, 22, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 11)
FONT_LABEL = (FONT_FAMILY, 10)


class MainWindow:
    """メインウィンドウクラス"""

    def __init__(self) -> None:
        # ConfigManager を先に生成してテーマ設定を反映
        self.config_manager = ConfigManager()
        self.directory_creator = DirectoryCreator(self.config_manager)
        theme = self.config_manager.get_user_setting("theme") or "cosmo"

        self.root = ttk.Window(
            title="DirCraft - 作業用フォルダ作成ツール",
            themename=theme,
        )
        self.root.geometry("840x660")
        self.root.minsize(720, 560)

        self._set_window_icon()
        self._configure_styles()

        self.icons = IconSet(
            ["settings", "folder", "add", "copy", "clear"],
            root=self.root,
        )

        self.created_directory_path = None

        self._init_ui()
        self._bind_shortcuts()
        self._load_user_settings()

    def _set_window_icon(self) -> None:
        """タスクバー/ウィンドウタイトルバーのアイコンを設定。"""
        ico_path = resource_path("DirCraft.ico")
        if ico_path.exists():
            try:
                self.root.iconbitmap(default=str(ico_path))
                return
            except tk.TclError:
                pass  # Windows 以外は .ico 非対応
        # フォールバック: PNG 版があれば iconphoto で設定
        png_path = resource_path("assets", "icons", "add.png")
        if png_path.exists():
            try:
                self._window_icon_image = tk.PhotoImage(file=str(png_path))
                self.root.iconphoto(True, self._window_icon_image)
            except tk.TclError:
                pass

    def _bind_shortcuts(self) -> None:
        """キーボードショートカットを登録。"""
        # Ctrl+Enter: ディレクトリ作成
        self.root.bind_all("<Control-Return>", lambda _e: self._create_directory())
        # Ctrl+,: 設定画面を開く
        self.root.bind_all("<Control-comma>", lambda _e: self._open_settings())
        # Escape: 終了（フォーカス位置によらず）
        self.root.bind_all("<Escape>", lambda _e: self.root.quit())

    def _configure_styles(self) -> None:
        """ベースフォントとカスタムスタイルを設定"""
        style = ttk.Style()
        style.configure(".", font=FONT_BASE)
        style.configure("TLabel", font=FONT_LABEL)
        style.configure("TButton", font=FONT_BASE, padding=(12, 6))
        style.configure("TEntry", padding=4)
        style.configure("TCombobox", padding=4)
        style.configure("Title.TLabel", font=FONT_TITLE)
        style.configure("Subtitle.TLabel", font=FONT_SUBTITLE, foreground="#6c757d")
        style.configure("FieldLabel.TLabel", font=FONT_LABEL, foreground="#495057")

    def _init_ui(self) -> None:
        """UI要素を初期化"""
        main_frame = ttk.Frame(self.root, padding=24)
        main_frame.grid(row=0, column=0, sticky=(W, E, N, S))

        self._create_header(main_frame)

        ttk.Separator(main_frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky=(W, E), pady=(4, 16)
        )

        # フィールドキー → ウィジェット（バリデーション結果の反映先）
        self._field_widgets: dict[str, tk.Widget] = {}

        self._create_input_fields(main_frame)
        self._create_error_banner(main_frame)
        self._create_action_buttons(main_frame)
        self._create_status_bar(main_frame)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def _create_error_banner(self, parent: tk.Widget) -> None:
        """バリデーションエラーを表示するインラインバナー（初期は非表示）。"""
        self._error_banner = ttk.Label(
            parent,
            text="",
            bootstyle=(DANGER, "inverse"),
            padding=(12, 8),
            anchor=W,
            justify=LEFT,
            wraplength=760,
        )
        self._error_banner.grid(
            row=9, column=0, columnspan=2, sticky=(W, E), pady=(0, 12)
        )
        self._error_banner.grid_remove()

    def _create_header(self, parent: tk.Widget) -> None:
        """ヘッダー（タイトル + 設定ボタン）を作成"""
        header = ttk.Frame(parent)
        header.grid(row=0, column=0, columnspan=2, sticky=(W, E), pady=(0, 4))
        header.columnconfigure(0, weight=1)

        text_frame = ttk.Frame(header)
        text_frame.grid(row=0, column=0, sticky=W)

        ttk.Label(text_frame, text="DirCraft", style="Title.TLabel").pack(anchor=W)
        ttk.Label(
            text_frame,
            text="作業用フォルダ作成ツール",
            style="Subtitle.TLabel",
        ).pack(anchor=W, pady=(2, 0))

        settings_btn = ttk.Button(
            header,
            text=" 設定",
            image=self.icons.get("settings"),
            compound=LEFT,
            command=self._open_settings,
            bootstyle=(SECONDARY, OUTLINE),
        )
        settings_btn.grid(row=0, column=1, sticky=E, padx=(12, 0))
        ToolTip(settings_btn, text="ユーザー設定を開く (Ctrl+,)", bootstyle=INFO)

    def _create_input_fields(self, parent: tk.Widget) -> None:
        """入力フィールドを作成"""
        row_pady = 8
        label_padx = (0, 14)
        field_padx = (0, 0)

        # 変更番号
        ttk.Label(parent, text="変更番号", style="FieldLabel.TLabel").grid(
            row=3, column=0, sticky=W, pady=row_pady, padx=label_padx
        )
        self.change_number_var = tk.StringVar()
        self.change_number_entry = ttk.Entry(
            parent, textvariable=self.change_number_var
        )
        self.change_number_entry.grid(
            row=3, column=1, sticky=(W, E), pady=row_pady, padx=field_padx
        )
        ToolTip(
            self.change_number_entry,
            text="例: CHG0001234\n'CHG' で始まる変更番号を入力します",
            bootstyle=INFO,
        )
        self._register_field("change_number", self.change_number_entry)

        # 対象クラウド
        ttk.Label(parent, text="対象クラウド", style="FieldLabel.TLabel").grid(
            row=4, column=0, sticky=W, pady=row_pady, padx=label_padx
        )
        self.cloud_var = tk.StringVar()
        cloud_combo = ttk.Combobox(
            parent,
            textvariable=self.cloud_var,
            values=["AWS", "Azure", "AWS-Azure"],
            state="readonly",
        )
        cloud_combo.grid(row=4, column=1, sticky=(W, E), pady=row_pady, padx=field_padx)
        cloud_combo.bind("<<ComboboxSelected>>", self._on_cloud_selected)
        ToolTip(
            cloud_combo,
            text="作業対象のクラウド基盤を選択\n選択すると作業内容の候補が更新されます",
            bootstyle=INFO,
        )
        self._register_field("cloud", cloud_combo)

        # 作業内容
        ttk.Label(parent, text="作業内容", style="FieldLabel.TLabel").grid(
            row=5, column=0, sticky=W, pady=row_pady, padx=label_padx
        )
        work_type_frame = ttk.Frame(parent)
        work_type_frame.grid(
            row=5, column=1, sticky=(W, E), pady=row_pady, padx=field_padx
        )
        work_type_frame.columnconfigure(0, weight=1)
        work_type_frame.columnconfigure(1, weight=1)

        self.work_type_var = tk.StringVar()
        self.work_type_combo = ttk.Combobox(
            work_type_frame, textvariable=self.work_type_var, state="readonly"
        )
        self.work_type_combo.grid(row=0, column=0, sticky=(W, E), padx=(0, 6))

        self.other_work_type_var = tk.StringVar()
        self.other_work_type_entry = ttk.Entry(
            work_type_frame,
            textvariable=self.other_work_type_var,
            state="disabled",
        )
        self.other_work_type_entry.grid(row=0, column=1, sticky=(W, E))

        self.work_type_options = []
        self.work_type_combo.bind(
            "<<ComboboxSelected>>", self._on_work_type_selected
        )
        ToolTip(
            self.work_type_combo,
            text="対応する手順書テンプレートを自動で選択します\n候補に無い場合は「その他」を選択",
            bootstyle=INFO,
        )
        ToolTip(
            self.other_work_type_entry,
            text="「その他」選択時の作業内容を自由入力",
            bootstyle=INFO,
        )
        self._register_field("work_type", self.work_type_combo)

        # 作業日（DateEntry: カレンダーポップアップ付き）
        ttk.Label(parent, text="作業日", style="FieldLabel.TLabel").grid(
            row=6, column=0, sticky=W, pady=row_pady, padx=label_padx
        )
        self.work_date_entry = ttk.DateEntry(
            parent,
            dateformat="%Y-%m-%d",
            firstweekday=0,
            bootstyle=SECONDARY,
            startdate=datetime.now(),
        )
        self.work_date_entry.grid(
            row=6, column=1, sticky=(W, E), pady=row_pady, padx=field_padx
        )
        ToolTip(
            self.work_date_entry,
            text="作業実施日。右端のカレンダーから選択するか直接入力",
            bootstyle=INFO,
        )
        self._register_field("work_date", self.work_date_entry)

        # 変更対象システム名
        ttk.Label(parent, text="変更対象システム名", style="FieldLabel.TLabel").grid(
            row=7, column=0, sticky=W, pady=row_pady, padx=label_padx
        )
        self.system_name_var = tk.StringVar()
        self.system_name_entry = ttk.Entry(parent, textvariable=self.system_name_var)
        self.system_name_entry.grid(
            row=7, column=1, sticky=(W, E), pady=row_pady, padx=field_padx
        )
        ToolTip(
            self.system_name_entry,
            text="変更対象のシステム名を入力\nフォルダ名・証跡ファイル名に使われます",
            bootstyle=INFO,
        )
        self._register_field("system_name", self.system_name_entry)

        # 親ディレクトリ
        ttk.Label(parent, text="親ディレクトリ", style="FieldLabel.TLabel").grid(
            row=8, column=0, sticky=W, pady=row_pady, padx=label_padx
        )
        dir_frame = ttk.Frame(parent)
        dir_frame.grid(row=8, column=1, sticky=(W, E), pady=row_pady, padx=field_padx)
        dir_frame.columnconfigure(0, weight=1)

        self.parent_dir_var = tk.StringVar()
        self.parent_dir_entry = ttk.Entry(dir_frame, textvariable=self.parent_dir_var)
        self.parent_dir_entry.grid(row=0, column=0, sticky=(W, E))
        ToolTip(
            self.parent_dir_entry,
            text="作業フォルダの作成先となる親ディレクトリ",
            bootstyle=INFO,
        )
        self._register_field("parent_directory", self.parent_dir_entry)

        browse_btn = ttk.Button(
            dir_frame,
            text=" 参照",
            image=self.icons.get("folder"),
            compound=LEFT,
            command=self._browse_directory,
            bootstyle=(SECONDARY, OUTLINE),
        )
        browse_btn.grid(row=0, column=1, padx=(8, 0))
        ToolTip(browse_btn, text="ディレクトリ選択ダイアログを開く", bootstyle=INFO)

        parent.columnconfigure(1, weight=1)

    def _create_action_buttons(self, parent: tk.Widget) -> None:
        """アクションボタン群を作成"""
        ttk.Separator(parent, orient="horizontal").grid(
            row=10, column=0, columnspan=2, sticky=(W, E), pady=(16, 12)
        )

        button_frame = ttk.Frame(parent)
        button_frame.grid(row=11, column=0, columnspan=2, sticky=(W, E))
        button_frame.columnconfigure(0, weight=1)

        # 右寄せグループ（副ボタン）と左寄せグループ（主ボタン）
        primary_frame = ttk.Frame(button_frame)
        primary_frame.grid(row=0, column=0, sticky=W)

        secondary_frame = ttk.Frame(button_frame)
        secondary_frame.grid(row=0, column=1, sticky=E)

        create_btn = ttk.Button(
            primary_frame,
            text=" ディレクトリ作成",
            image=self.icons.get("add"),
            compound=LEFT,
            command=self._create_directory,
            bootstyle=SUCCESS,
            width=22,
        )
        create_btn.pack(side=LEFT)
        ToolTip(
            create_btn,
            text="入力内容を元に作業用ディレクトリを作成 (Ctrl+Enter)",
            bootstyle=INFO,
        )

        copy_btn = ttk.Button(
            secondary_frame,
            text=" パスをコピー",
            image=self.icons.get("copy"),
            compound=LEFT,
            command=self._copy_path_to_clipboard,
            bootstyle=(INFO, OUTLINE),
        )
        copy_btn.pack(side=LEFT, padx=(0, 8))
        ToolTip(
            copy_btn,
            text="直前に作成したディレクトリのフルパスをクリップボードへコピー",
            bootstyle=INFO,
        )

        clear_btn = ttk.Button(
            secondary_frame,
            text=" クリア",
            image=self.icons.get("clear"),
            compound=LEFT,
            command=self._clear_fields,
            bootstyle=(SECONDARY, OUTLINE),
        )
        clear_btn.pack(side=LEFT)
        ToolTip(clear_btn, text="入力フィールドをリセット", bootstyle=INFO)

    def _create_status_bar(self, parent: tk.Widget) -> None:
        """フラットなステータスバーを作成"""
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            parent,
            textvariable=self.status_var,
            anchor=W,
            padding=(10, 6),
            bootstyle=SECONDARY,
        )
        self.status_bar.grid(
            row=12, column=0, columnspan=2, sticky=(W, E), pady=(16, 0)
        )
        self._update_status("準備完了", "normal")

    def _register_field(self, key: str, widget: tk.Widget) -> None:
        """フィールドウィジェットを登録し、フォーカス時のエラー解除を結線。"""
        self._field_widgets[key] = widget
        widget.bind(
            "<FocusIn>",
            lambda _e, k=key: self._clear_field_error(k),
            add="+",
        )

    def _show_validation_errors(self, errors: dict[str, str]) -> None:
        """エラー辞書をインラインバナーと入力欄の赤枠で表示する。"""
        if not errors:
            self._clear_validation_errors()
            return

        lines = ["入力を確認してください:"]
        lines.extend(f"• {msg}" for msg in errors.values())
        self._error_banner.configure(text="\n".join(lines))
        self._error_banner.grid()

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
        """エラーバナーと全フィールドの赤枠を解除。"""
        self._error_banner.configure(text="")
        self._error_banner.grid_remove()
        for widget in self._field_widgets.values():
            try:
                widget.configure(bootstyle="")
            except tk.TclError:
                pass

    def _clear_field_error(self, key: str) -> None:
        """特定フィールドの赤枠のみ解除する（ユーザーが編集に入った瞬間）。"""
        widget = self._field_widgets.get(key)
        if widget is None:
            return
        try:
            widget.configure(bootstyle="")
        except tk.TclError:
            pass

    def _load_user_settings(self) -> None:
        """ユーザー設定を読み込み"""
        default_dir = self.config_manager.get_user_setting("default_directory")
        if default_dir:
            self.parent_dir_var.set(default_dir)

    def _browse_directory(self) -> None:
        """ディレクトリ選択ダイアログを表示"""
        directory = filedialog.askdirectory()
        if directory:
            self.parent_dir_var.set(directory)
            self.config_manager.set_user_setting("default_directory", directory)

    def _on_cloud_selected(self, event: tk.Event | None = None) -> None:
        """対象クラウドが選択されたときの処理"""
        selected_cloud = self.cloud_var.get()
        if selected_cloud:
            self._update_work_type_options(selected_cloud)

    def _update_work_type_options(self, cloud: str) -> None:
        """作業内容の選択肢を更新"""
        try:
            procedures = self.config_manager.load_procedures()
            cloud_procedures = procedures.get("procedures", {}).get(cloud, {})

            self.work_type_options = list(cloud_procedures.keys())
            self.work_type_options.append("その他")

            self.work_type_combo["values"] = self.work_type_options
            self.work_type_var.set("")
            self.other_work_type_var.set("")
            self.other_work_type_entry.config(state="disabled")

        except Exception as e:
            messagebox.showerror("エラー", f"作業内容の取得に失敗しました:\n{str(e)}")

    def _on_work_type_selected(self, event: tk.Event | None = None) -> None:
        """作業内容が選択されたときの処理"""
        selected_work_type = self.work_type_var.get()

        if selected_work_type == "その他":
            self.other_work_type_entry.config(state="normal")
            self.other_work_type_entry.focus()
        else:
            self.other_work_type_entry.config(state="disabled")
            self.other_work_type_var.set("")

    def _open_settings(self) -> None:
        """設定画面を開く"""
        from .settings_window import SettingsWindow
        SettingsWindow(self.root, self.config_manager, main_window=self)

    def _create_directory(self) -> None:
        """作業用ディレクトリを作成"""
        try:
            change_number = self.change_number_var.get().strip()
            cloud = self.cloud_var.get()

            selected_work_type = self.work_type_var.get()
            if selected_work_type == "その他":
                work_type = self.other_work_type_var.get().strip()
            else:
                work_type = selected_work_type.strip()

            work_date = self.work_date_entry.entry.get().strip()
            system_name = self.system_name_var.get().strip()
            parent_directory = self.parent_dir_var.get().strip()

            errors = self.directory_creator.validate_inputs(
                change_number, cloud, work_type, work_date, system_name, parent_directory
            )

            if errors:
                self._show_validation_errors(errors)
                self._update_status("入力エラーがあります", "error")
                return
            self._clear_validation_errors()

            # 既存ディレクトリとの衝突チェック
            allow_existing = False
            target_path = self.directory_creator.compute_directory_path(
                change_number, cloud, work_type, work_date, system_name, parent_directory
            )
            if target_path.exists():
                proceed = messagebox.askyesno(
                    "ディレクトリが既に存在します",
                    (
                        "同名の作業用ディレクトリが既に存在します。\n\n"
                        f"{target_path}\n\n"
                        "テンプレートをこのディレクトリにコピー（マージ）しますか？\n"
                        "※ 既存のファイルと同名のテンプレートは上書きされます。"
                    ),
                    icon="warning",
                )
                if not proceed:
                    self._update_status("作成をキャンセルしました", "normal")
                    return
                allow_existing = True

            work_dir_path = self.directory_creator.create_work_directory(
                change_number, cloud, work_type, work_date, system_name, parent_directory,
                allow_existing=allow_existing,
            )

            self.created_directory_path = work_dir_path

            self._open_directory_in_explorer(work_dir_path)

            success_message = f"作業用ディレクトリが正常に作成されました。\n\nパス: {work_dir_path}"
            messagebox.showinfo("作成完了", success_message)

            self._clear_input_fields_only()
            self._update_status(f"ディレクトリ作成完了: {work_dir_path}", "success")

        except Exception as e:
            logger.exception("ディレクトリの作成に失敗しました")
            messagebox.showerror("エラー", f"ディレクトリの作成に失敗しました:\n{str(e)}")
            self._update_status("エラーが発生しました", "error")

    def _clear_input_fields_only(self) -> None:
        """入力フィールドのみをクリア（パスは保持）"""
        self.change_number_var.set("")
        self.cloud_var.set("")
        self.work_type_var.set("")
        self.other_work_type_var.set("")
        self.system_name_var.set("")

        self.work_type_combo["values"] = []
        self.work_type_options = []
        self.other_work_type_entry.config(state="disabled")

    def _clear_fields(self) -> None:
        """入力フィールドをクリア"""
        self.change_number_var.set("")
        self.cloud_var.set("")
        self.work_type_var.set("")
        self.other_work_type_var.set("")
        self.system_name_var.set("")

        self.work_type_combo["values"] = []
        self.work_type_options = []
        self.other_work_type_entry.config(state="disabled")

        self.created_directory_path = None
        self._clear_validation_errors()
        self._update_status("フィールドをクリアしました", "normal")

    def _open_directory_in_explorer(self, directory_path: str) -> None:
        """作成されたディレクトリをエクスプローラーで開く"""
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(directory_path)
            elif system == "Darwin":
                subprocess.run(["open", directory_path])
            else:
                subprocess.run(["xdg-open", directory_path])
        except Exception:
            logger.exception("ディレクトリを開く際にエラーが発生しました: %s", directory_path)

    def _copy_path_to_clipboard(self) -> None:
        """作成されたディレクトリのパスをクリップボードにコピー"""
        if self.created_directory_path:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.created_directory_path)
                self._update_status("パスをクリップボードにコピーしました", "success")
            except Exception:
                self._update_status("クリップボードへのコピーに失敗しました", "error")
        else:
            self._update_status("コピーするパスがありません", "error")

    def _update_status(self, message: str, status_type: str = "normal") -> None:
        """ステータスバーの表示を更新（bootstyle で色分け）"""
        self.status_var.set(message)

        if status_type == "success":
            self.status_bar.configure(bootstyle=SUCCESS)
        elif status_type == "error":
            self.status_bar.configure(bootstyle=DANGER)
        else:
            self.status_bar.configure(bootstyle=SECONDARY)

    def update_settings(self) -> None:
        """設定が変更された後に呼び出されるメソッド"""
        self._load_user_settings()
        theme = self.config_manager.get_user_setting("theme") or "cosmo"
        try:
            current = ttk.Style().theme_use()
            if current != theme:
                ttk.Style().theme_use(theme)
                self._configure_styles()  # フォント等を新テーマに再適用
        except tk.TclError:
            logger.exception("テーマ切り替えに失敗: %s", theme)
        self._update_status("設定を更新しました", "success")

    def run(self) -> None:
        """アプリケーションを実行"""
        self.root.mainloop()
