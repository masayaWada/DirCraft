import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Optional
import os
import subprocess
import platform
from core.config_manager import ConfigManager
from core.directory_creator import DirectoryCreator


class MainWindow:
    """メインウィンドウクラス"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DirCraft - 作業用フォルダ作成ツール")
        self.root.geometry("800x600")

        # 設定マネージャーとディレクトリ作成クラスを初期化
        self.config_manager = ConfigManager()
        self.directory_creator = DirectoryCreator(self.config_manager)

        # 作成されたディレクトリのパスを保存
        self.created_directory_path = None

        # GUI要素を初期化
        self._init_ui()
        self._load_user_settings()

    def _init_ui(self):
        """UI要素を初期化"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # タイトル
        title_label = ttk.Label(
            main_frame, text="DirCraft", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        subtitle_label = ttk.Label(
            main_frame, text="作業用フォルダ作成ツール", font=("Arial", 12))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # 入力フィールド
        self._create_input_fields(main_frame)

        # ボタン
        self._create_buttons(main_frame)

        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN,
            bg="white", fg="black", anchor=tk.W, padx=5, pady=2)
        self.status_bar.grid(row=10, column=0, columnspan=2,
                             sticky=(tk.W, tk.E), pady=(10, 0))

        # 初期ステータスを設定
        self._update_status("準備完了", "normal")

        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def _create_input_fields(self, parent):
        """入力フィールドを作成"""
        # 変更番号
        ttk.Label(parent, text="変更番号:").grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.change_number_var = tk.StringVar()
        self.change_number_entry = ttk.Entry(
            parent, textvariable=self.change_number_var, width=30)
        self.change_number_entry.grid(
            row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # 対象クラウド
        ttk.Label(parent, text="対象クラウド:").grid(
            row=3, column=0, sticky=tk.W, pady=5)
        self.cloud_var = tk.StringVar()
        cloud_combo = ttk.Combobox(parent, textvariable=self.cloud_var,
                                   values=["AWS", "Azure", "AWS-Azure"], state="readonly", width=27)
        cloud_combo.grid(row=3, column=1, sticky=(
            tk.W, tk.E), pady=5, padx=(10, 0))

        # 対象クラウドの選択時に作業内容を更新
        cloud_combo.bind('<<ComboboxSelected>>', self._on_cloud_selected)

        # 作業内容
        ttk.Label(parent, text="作業内容:").grid(
            row=4, column=0, sticky=tk.W, pady=5)

        # 作業内容選択フレーム
        work_type_frame = ttk.Frame(parent)
        work_type_frame.grid(row=4, column=1, sticky=(
            tk.W, tk.E), pady=5, padx=(10, 0))

        self.work_type_var = tk.StringVar()
        self.work_type_combo = ttk.Combobox(work_type_frame, textvariable=self.work_type_var,
                                            state="readonly", width=27)
        self.work_type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # その他の作業内容入力フィールド
        self.other_work_type_var = tk.StringVar()
        self.other_work_type_entry = ttk.Entry(work_type_frame, textvariable=self.other_work_type_var,
                                               width=27, state="disabled")
        self.other_work_type_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 作業内容の選択肢を更新するための変数
        self.work_type_options = []

        # 作業内容の選択時に処理を実行
        self.work_type_combo.bind(
            '<<ComboboxSelected>>', self._on_work_type_selected)

        parent.columnconfigure(1, weight=1)

        # 作業日
        ttk.Label(parent, text="作業日:").grid(
            row=5, column=0, sticky=tk.W, pady=5)
        self.work_date_var = tk.StringVar()
        self.work_date_entry = ttk.Entry(
            parent, textvariable=self.work_date_var, width=30)
        self.work_date_entry.grid(row=5, column=1, sticky=(
            tk.W, tk.E), pady=5, padx=(10, 0))

        # 変更対象システム名
        ttk.Label(parent, text="変更対象システム名:").grid(
            row=6, column=0, sticky=tk.W, pady=5)
        self.system_name_var = tk.StringVar()
        self.system_name_entry = ttk.Entry(
            parent, textvariable=self.system_name_var, width=30)
        self.system_name_entry.grid(
            row=6, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # 親ディレクトリ
        ttk.Label(parent, text="親ディレクトリ:").grid(
            row=7, column=0, sticky=tk.W, pady=5)
        dir_frame = ttk.Frame(parent)
        dir_frame.grid(row=7, column=1, sticky=(
            tk.W, tk.E), pady=5, padx=(10, 0))

        self.parent_dir_var = tk.StringVar()
        self.parent_dir_entry = ttk.Entry(
            dir_frame, textvariable=self.parent_dir_var, width=25)
        self.parent_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = ttk.Button(dir_frame, text="参照",
                                command=self._browse_directory)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 設定ボタン
        settings_btn = ttk.Button(
            parent, text="設定", command=self._open_settings)
        settings_btn.grid(row=8, column=0, columnspan=2, pady=20)

    def _create_buttons(self, parent):
        """ボタンを作成"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)

        create_btn = ttk.Button(button_frame, text="ディレクトリ作成",
                                command=self._create_directory, style="Accent.TButton")
        create_btn.pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = ttk.Button(button_frame, text="クリア",
                               command=self._clear_fields)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        copy_btn = ttk.Button(button_frame, text="パスをコピー",
                              command=self._copy_path_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))

        exit_btn = ttk.Button(button_frame, text="終了", command=self.root.quit)
        exit_btn.pack(side=tk.LEFT)

    def _load_user_settings(self):
        """ユーザー設定を読み込み"""
        default_dir = self.config_manager.get_user_setting("default_directory")
        if default_dir:
            self.parent_dir_var.set(default_dir)

        # 今日の日付を設定
        today = datetime.now().strftime("%Y-%m-%d")
        self.work_date_var.set(today)

    def update_settings(self):
        """設定画面から呼び出される設定更新メソッド"""
        # デフォルトディレクトリの設定を更新
        default_dir = self.config_manager.get_user_setting("default_directory")
        if default_dir:
            self.parent_dir_var.set(default_dir)

    def _browse_directory(self):
        """ディレクトリ選択ダイアログを表示"""
        directory = filedialog.askdirectory()
        if directory:
            self.parent_dir_var.set(directory)
            # 設定を保存
            self.config_manager.set_user_setting(
                "default_directory", directory)

    def _on_cloud_selected(self, event=None):
        """対象クラウドが選択されたときの処理"""
        selected_cloud = self.cloud_var.get()
        if selected_cloud:
            # 作業内容の選択肢を更新
            self._update_work_type_options(selected_cloud)

    def _update_work_type_options(self, cloud):
        """作業内容の選択肢を更新"""
        try:
            # procedures.jsonから作業内容を取得
            procedures = self.config_manager.load_procedures()
            cloud_procedures = procedures.get("procedures", {}).get(cloud, {})

            # 作業内容のリストを作成
            self.work_type_options = list(cloud_procedures.keys())
            self.work_type_options.append("その他")

            # コンボボックスの値を更新
            self.work_type_combo['values'] = self.work_type_options

            # 作業内容をクリア
            self.work_type_var.set("")
            self.other_work_type_var.set("")

            # その他の入力フィールドを無効化
            self.other_work_type_entry.config(state="disabled")

        except Exception as e:
            messagebox.showerror("エラー", f"作業内容の取得に失敗しました:\n{str(e)}")

    def _on_work_type_selected(self, event=None):
        """作業内容が選択されたときの処理"""
        selected_work_type = self.work_type_var.get()

        if selected_work_type == "その他":
            # その他の場合は手動入力フィールドを有効化
            self.other_work_type_entry.config(state="normal")
            self.other_work_type_entry.focus()
        else:
            # その他以外の場合は手動入力フィールドを無効化
            self.other_work_type_entry.config(state="disabled")
            self.other_work_type_var.set("")

    def _open_settings(self):
        """設定画面を開く"""
        from .settings_window import SettingsWindow
        SettingsWindow(self.root, self.config_manager)

    def _create_directory(self):
        """作業用ディレクトリを作成"""
        try:
            # 入力値を取得
            change_number = self.change_number_var.get().strip()
            cloud = self.cloud_var.get()

            # 作業内容の値を取得（その他の場合は手動入力値を使用）
            selected_work_type = self.work_type_var.get()
            if selected_work_type == "その他":
                work_type = self.other_work_type_var.get().strip()
            else:
                work_type = selected_work_type.strip()

            work_date = self.work_date_var.get().strip()
            system_name = self.system_name_var.get().strip()
            parent_directory = self.parent_dir_var.get().strip()

            # 入力値の検証
            errors = self.directory_creator.validate_inputs(
                change_number, cloud, work_type, work_date, system_name, parent_directory
            )

            if errors:
                error_message = "以下のエラーがあります:\n\n" + \
                    "\n".join(f"• {error}" for error in errors)
                messagebox.showerror("入力エラー", error_message)
                return

            # 作業用ディレクトリを作成
            work_dir_path = self.directory_creator.create_work_directory(
                change_number, cloud, work_type, work_date, system_name, parent_directory
            )

            # 作成されたディレクトリのパスを保存
            self.created_directory_path = work_dir_path

            # 作成したディレクトリをエクスプローラーで開く
            self._open_directory_in_explorer(work_dir_path)

            # 成功メッセージを表示
            success_message = f"作業用ディレクトリが正常に作成されました。\n\nパス: {work_dir_path}"
            messagebox.showinfo("作成完了", success_message)

            # フィールドのみをクリア（パスは保持）
            self._clear_input_fields_only()

            # ステータスを更新
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

        # 作業内容の選択肢をクリア
        self.work_type_combo['values'] = []
        self.work_type_options = []

        # その他の入力フィールドを無効化
        self.other_work_type_entry.config(state="disabled")

        # 作業日と親ディレクトリは保持
        # 作成されたディレクトリのパスも保持

    def _clear_fields(self):
        """入力フィールドをクリア"""
        self.change_number_var.set("")
        self.cloud_var.set("")
        self.work_type_var.set("")
        self.other_work_type_var.set("")
        self.system_name_var.set("")

        # 作業内容の選択肢をクリア
        self.work_type_combo['values'] = []
        self.work_type_options = []

        # その他の入力フィールドを無効化
        self.other_work_type_entry.config(state="disabled")

        # 作成されたディレクトリのパスをクリア
        self.created_directory_path = None

        # 作業日と親ディレクトリは保持
        self._update_status("フィールドをクリアしました", "normal")

    def _open_directory_in_explorer(self, directory_path: str):
        """作成されたディレクトリをエクスプローラーで開く"""
        try:
            system = platform.system()
            if system == "Windows":
                # Windowsの場合
                os.startfile(directory_path)
            elif system == "Darwin":
                # macOSの場合
                subprocess.run(["open", directory_path])
            else:
                # Linuxなどの場合
                subprocess.run(["xdg-open", directory_path])
        except Exception as e:
            # エラーが発生しても処理は続行
            print(f"ディレクトリを開く際にエラーが発生しました: {str(e)}")

    def _copy_path_to_clipboard(self):
        """作成されたディレクトリのパスをクリップボードにコピー"""
        if self.created_directory_path:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.created_directory_path)
                self._update_status("パスをクリップボードにコピーしました", "success")
            except Exception as e:
                self._update_status("クリップボードへのコピーに失敗しました", "error")
        else:
            self._update_status("コピーするパスがありません", "error")

    def _update_status(self, message: str, status_type: str = "normal"):
        """ステータスバーの表示を更新（色分け対応）"""
        self.status_var.set(message)

        if status_type == "success":
            # 成功時：緑文字
            self.status_bar.config(fg="green", bg="white")
        elif status_type == "error":
            # エラー時：赤文字
            self.status_bar.config(fg="red", bg="white")
        else:
            # 通常時：黒文字
            self.status_bar.config(fg="black", bg="white")

    def update_settings(self):
        """設定が変更された後に呼び出されるメソッド"""
        # 設定を再読み込み
        self._load_user_settings()
        self._update_status("設定を更新しました", "success")

    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()
