import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import os
import subprocess
import platform

import ttkbootstrap as ttk
from ttkbootstrap.constants import (
    W, E, N, S, LEFT, RIGHT, X, BOTH,
    SUCCESS, INFO, SECONDARY, DANGER, WARNING, LINK,
    OUTLINE,
)

from core.config_manager import ConfigManager
from core.directory_creator import DirectoryCreator


FONT_FAMILY = "Yu Gothic UI"
FONT_BASE = (FONT_FAMILY, 10)
FONT_TITLE = (FONT_FAMILY, 22, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 11)
FONT_LABEL = (FONT_FAMILY, 10)


class MainWindow:
    """メインウィンドウクラス"""

    def __init__(self):
        self.root = ttk.Window(
            title="DirCraft - 作業用フォルダ作成ツール",
            themename="cosmo",
        )
        self.root.geometry("840x660")
        self.root.minsize(720, 560)

        self._configure_styles()

        self.config_manager = ConfigManager()
        self.directory_creator = DirectoryCreator(self.config_manager)

        self.created_directory_path = None

        self._init_ui()
        self._load_user_settings()

    def _configure_styles(self):
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

    def _init_ui(self):
        """UI要素を初期化"""
        main_frame = ttk.Frame(self.root, padding=24)
        main_frame.grid(row=0, column=0, sticky=(W, E, N, S))

        self._create_header(main_frame)

        ttk.Separator(main_frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky=(W, E), pady=(4, 16)
        )

        self._create_input_fields(main_frame)
        self._create_action_buttons(main_frame)
        self._create_status_bar(main_frame)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def _create_header(self, parent):
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
            text="⚙  設定",
            command=self._open_settings,
            bootstyle=(SECONDARY, OUTLINE),
        )
        settings_btn.grid(row=0, column=1, sticky=E, padx=(12, 0))

    def _create_input_fields(self, parent):
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

        # 作業日
        ttk.Label(parent, text="作業日", style="FieldLabel.TLabel").grid(
            row=6, column=0, sticky=W, pady=row_pady, padx=label_padx
        )
        self.work_date_var = tk.StringVar()
        self.work_date_entry = ttk.Entry(parent, textvariable=self.work_date_var)
        self.work_date_entry.grid(
            row=6, column=1, sticky=(W, E), pady=row_pady, padx=field_padx
        )

        # 変更対象システム名
        ttk.Label(parent, text="変更対象システム名", style="FieldLabel.TLabel").grid(
            row=7, column=0, sticky=W, pady=row_pady, padx=label_padx
        )
        self.system_name_var = tk.StringVar()
        self.system_name_entry = ttk.Entry(parent, textvariable=self.system_name_var)
        self.system_name_entry.grid(
            row=7, column=1, sticky=(W, E), pady=row_pady, padx=field_padx
        )

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

        browse_btn = ttk.Button(
            dir_frame,
            text="📁  参照",
            command=self._browse_directory,
            bootstyle=(SECONDARY, OUTLINE),
        )
        browse_btn.grid(row=0, column=1, padx=(8, 0))

        parent.columnconfigure(1, weight=1)

    def _create_action_buttons(self, parent):
        """アクションボタン群を作成"""
        ttk.Separator(parent, orient="horizontal").grid(
            row=9, column=0, columnspan=2, sticky=(W, E), pady=(16, 12)
        )

        button_frame = ttk.Frame(parent)
        button_frame.grid(row=10, column=0, columnspan=2, sticky=(W, E))
        button_frame.columnconfigure(0, weight=1)

        # 右寄せグループ（副ボタン）と左寄せグループ（主ボタン）
        primary_frame = ttk.Frame(button_frame)
        primary_frame.grid(row=0, column=0, sticky=W)

        secondary_frame = ttk.Frame(button_frame)
        secondary_frame.grid(row=0, column=1, sticky=E)

        create_btn = ttk.Button(
            primary_frame,
            text="📂  ディレクトリ作成",
            command=self._create_directory,
            bootstyle=SUCCESS,
            width=22,
        )
        create_btn.pack(side=LEFT)

        copy_btn = ttk.Button(
            secondary_frame,
            text="📋  パスをコピー",
            command=self._copy_path_to_clipboard,
            bootstyle=(INFO, OUTLINE),
        )
        copy_btn.pack(side=LEFT, padx=(0, 8))

        clear_btn = ttk.Button(
            secondary_frame,
            text="🧹  クリア",
            command=self._clear_fields,
            bootstyle=(SECONDARY, OUTLINE),
        )
        clear_btn.pack(side=LEFT, padx=(0, 8))

        exit_btn = ttk.Button(
            secondary_frame,
            text="✕  終了",
            command=self.root.quit,
            bootstyle=(SECONDARY, LINK),
        )
        exit_btn.pack(side=LEFT)

    def _create_status_bar(self, parent):
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
            row=11, column=0, columnspan=2, sticky=(W, E), pady=(16, 0)
        )
        self._update_status("準備完了", "normal")

    def _load_user_settings(self):
        """ユーザー設定を読み込み"""
        default_dir = self.config_manager.get_user_setting("default_directory")
        if default_dir:
            self.parent_dir_var.set(default_dir)

        today = datetime.now().strftime("%Y-%m-%d")
        self.work_date_var.set(today)

    def _browse_directory(self):
        """ディレクトリ選択ダイアログを表示"""
        directory = filedialog.askdirectory()
        if directory:
            self.parent_dir_var.set(directory)
            self.config_manager.set_user_setting("default_directory", directory)

    def _on_cloud_selected(self, event=None):
        """対象クラウドが選択されたときの処理"""
        selected_cloud = self.cloud_var.get()
        if selected_cloud:
            self._update_work_type_options(selected_cloud)

    def _update_work_type_options(self, cloud):
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

    def _on_work_type_selected(self, event=None):
        """作業内容が選択されたときの処理"""
        selected_work_type = self.work_type_var.get()

        if selected_work_type == "その他":
            self.other_work_type_entry.config(state="normal")
            self.other_work_type_entry.focus()
        else:
            self.other_work_type_entry.config(state="disabled")
            self.other_work_type_var.set("")

    def _open_settings(self):
        """設定画面を開く"""
        from .settings_window import SettingsWindow
        SettingsWindow(self.root, self.config_manager)

    def _create_directory(self):
        """作業用ディレクトリを作成"""
        try:
            change_number = self.change_number_var.get().strip()
            cloud = self.cloud_var.get()

            selected_work_type = self.work_type_var.get()
            if selected_work_type == "その他":
                work_type = self.other_work_type_var.get().strip()
            else:
                work_type = selected_work_type.strip()

            work_date = self.work_date_var.get().strip()
            system_name = self.system_name_var.get().strip()
            parent_directory = self.parent_dir_var.get().strip()

            errors = self.directory_creator.validate_inputs(
                change_number, cloud, work_type, work_date, system_name, parent_directory
            )

            if errors:
                error_message = "以下のエラーがあります:\n\n" + \
                    "\n".join(f"• {error}" for error in errors)
                messagebox.showerror("入力エラー", error_message)
                return

            work_dir_path = self.directory_creator.create_work_directory(
                change_number, cloud, work_type, work_date, system_name, parent_directory
            )

            self.created_directory_path = work_dir_path

            self._open_directory_in_explorer(work_dir_path)

            success_message = f"作業用ディレクトリが正常に作成されました。\n\nパス: {work_dir_path}"
            messagebox.showinfo("作成完了", success_message)

            self._clear_input_fields_only()
            self._update_status(f"ディレクトリ作成完了: {work_dir_path}", "success")

        except Exception as e:
            messagebox.showerror("エラー", f"ディレクトリの作成に失敗しました:\n{str(e)}")
            self._update_status("エラーが発生しました", "error")

    def _clear_input_fields_only(self):
        """入力フィールドのみをクリア（パスは保持）"""
        self.change_number_var.set("")
        self.cloud_var.set("")
        self.work_type_var.set("")
        self.other_work_type_var.set("")
        self.system_name_var.set("")

        self.work_type_combo["values"] = []
        self.work_type_options = []
        self.other_work_type_entry.config(state="disabled")

    def _clear_fields(self):
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
        self._update_status("フィールドをクリアしました", "normal")

    def _open_directory_in_explorer(self, directory_path: str):
        """作成されたディレクトリをエクスプローラーで開く"""
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(directory_path)
            elif system == "Darwin":
                subprocess.run(["open", directory_path])
            else:
                subprocess.run(["xdg-open", directory_path])
        except Exception as e:
            print(f"ディレクトリを開く際にエラーが発生しました: {str(e)}")

    def _copy_path_to_clipboard(self):
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

    def _update_status(self, message: str, status_type: str = "normal"):
        """ステータスバーの表示を更新（bootstyle で色分け）"""
        self.status_var.set(message)

        if status_type == "success":
            self.status_bar.configure(bootstyle=SUCCESS)
        elif status_type == "error":
            self.status_bar.configure(bootstyle=DANGER)
        else:
            self.status_bar.configure(bootstyle=SECONDARY)

    def update_settings(self):
        """設定が変更された後に呼び出されるメソッド"""
        self._load_user_settings()
        self._update_status("設定を更新しました", "success")

    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()
