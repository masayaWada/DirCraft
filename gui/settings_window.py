import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from core.config_manager import ConfigManager


class SettingsWindow:
    """設定画面クラス"""

    def __init__(self, parent, config_manager: ConfigManager):
        self.parent = parent
        self.config_manager = config_manager

        # メインウィンドウへの参照を保持
        self.main_window = None
        # 親ウィンドウからメインウィンドウを検索
        if hasattr(parent, 'winfo_children'):
            for child in parent.winfo_children():
                if hasattr(child, 'update_settings'):
                    self.main_window = child
                    break

        # 設定画面ウィンドウを作成
        self.window = tk.Toplevel(parent)
        self.window.title("設定")
        self.window.geometry("600x600")
        self.window.resizable(False, False)

        # 親ウィンドウの中央に配置
        self.window.transient(parent)
        self.window.grab_set()

        # 設定値を保持する変数
        self.last_name_var = tk.StringVar()
        self.default_directory_var = tk.StringVar()
        self.team_group_name_var = tk.StringVar()

        # UI要素を初期化
        self._init_ui()
        self._load_current_settings()

        # ウィンドウが閉じられたときの処理
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _init_ui(self):
        """UI要素を初期化"""
        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトル
        title_label = ttk.Label(main_frame, text="設定",
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 設定項目フレーム
        settings_frame = ttk.LabelFrame(
            main_frame, text="ユーザー設定", padding="15")
        settings_frame.pack(fill=tk.X, pady=(0, 20))

        # 苗字
        self._create_setting_row(settings_frame, "苗字:", self.last_name_var, 0)

        # デフォルトディレクトリ
        self._create_directory_row(
            settings_frame, "デフォルトディレクトリ:", self.default_directory_var, 1)

        # グループ名
        self._create_setting_row(
            settings_frame, "グループ名:", self.team_group_name_var, 2)

        # その他作業用テンプレート設定フレーム
        template_frame = ttk.LabelFrame(
            main_frame, text="その他作業用テンプレート設定", padding="15")
        template_frame.pack(fill=tk.X, pady=(0, 20))

        # テンプレート設定用の変数
        self.aws_other_template_var = tk.StringVar()
        self.azure_other_template_var = tk.StringVar()
        self.hybrid_other_template_var = tk.StringVar()

        # 各クラウド用のテンプレート設定
        self._create_template_row(
            template_frame, "AWS用テンプレート:", self.aws_other_template_var, 0)
        self._create_template_row(
            template_frame, "Azure用テンプレート:", self.azure_other_template_var, 1)
        self._create_template_row(
            template_frame, "AWS-Azure用テンプレート:", self.hybrid_other_template_var, 2)

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))

        # 保存ボタン
        save_btn = ttk.Button(
            button_frame, text="保存", command=self._save_settings, style="Accent.TButton")
        save_btn.pack(side=tk.LEFT, padx=(0, 10))

        # キャンセルボタン
        cancel_btn = ttk.Button(
            button_frame, text="キャンセル", command=self._on_closing)
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))

        # デフォルトに戻すボタン
        reset_btn = ttk.Button(button_frame, text="デフォルトに戻す",
                               command=self._reset_to_default)
        reset_btn.pack(side=tk.LEFT)

    def _create_setting_row(self, parent, label_text, variable, row):
        """設定項目の行を作成"""
        ttk.Label(parent, text=label_text).grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        entry = ttk.Entry(parent, textvariable=variable, width=40)
        entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        parent.columnconfigure(1, weight=1)

    def _create_directory_row(self, parent, label_text, variable, row):
        """ディレクトリ選択の行を作成"""
        ttk.Label(parent, text=label_text).grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))

        # ディレクトリ選択フレーム
        dir_frame = ttk.Frame(parent)
        dir_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)

        entry = ttk.Entry(dir_frame, textvariable=variable, width=30)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = ttk.Button(dir_frame, text="参照",
                                command=self._browse_directory)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))

        parent.columnconfigure(1, weight=1)

    def _create_template_row(self, parent, label_text, variable, row):
        """テンプレートファイル選択の行を作成"""
        ttk.Label(parent, text=label_text).grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))

        # ファイル選択フレーム
        file_frame = ttk.Frame(parent)
        file_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)

        entry = ttk.Entry(file_frame, textvariable=variable, width=30)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = ttk.Button(file_frame, text="参照",
                                command=lambda: self._browse_template_file(variable))
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))

        parent.columnconfigure(1, weight=1)

    def _browse_directory(self):
        """ディレクトリ選択ダイアログを表示"""
        directory = filedialog.askdirectory()
        if directory:
            self.default_directory_var.set(directory)

    def _browse_template_file(self, variable):
        """テンプレートファイル選択ダイアログを表示"""
        file_path = filedialog.askopenfilename(
            title="テンプレートファイルを選択",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            variable.set(file_path)

    def _load_current_settings(self):
        """現在の設定を読み込み"""
        self.last_name_var.set(
            self.config_manager.get_user_setting("last_name") or "")
        self.default_directory_var.set(
            self.config_manager.get_user_setting("default_directory") or "")
        self.team_group_name_var.set(
            self.config_manager.get_user_setting("team_group_name") or "")

        # その他作業用テンプレートの設定を読み込み
        procedures = self.config_manager.load_procedures()
        other_templates = procedures.get("other_work_templates", {})

        aws_templates = other_templates.get("AWS", [])
        self.aws_other_template_var.set(
            aws_templates[0] if aws_templates else "")

        azure_templates = other_templates.get("Azure", [])
        self.azure_other_template_var.set(
            azure_templates[0] if azure_templates else "")

        hybrid_templates = other_templates.get("AWS-Azure", [])
        self.hybrid_other_template_var.set(
            hybrid_templates[0] if hybrid_templates else "")

    def _save_settings(self):
        """設定を保存"""
        try:
            # 入力値の検証
            errors = self._validate_inputs()
            if errors:
                error_message = "以下のエラーがあります:\n\n" + \
                    "\n".join(f"• {error}" for error in errors)
                messagebox.showerror("入力エラー", error_message)
                return

            # 設定を保存
            self.config_manager.set_user_setting(
                "last_name", self.last_name_var.get().strip())
            self.config_manager.set_user_setting(
                "default_directory", self.default_directory_var.get().strip())
            self.config_manager.set_user_setting(
                "team_group_name", self.team_group_name_var.get().strip())

            # その他作業用テンプレートの設定を保存
            self._save_other_work_templates()

            # 成功メッセージを表示
            messagebox.showinfo("保存完了", "設定が正常に保存されました。")

            # 親ウィンドウの設定を更新
            self._update_parent_settings()

            # 設定画面を閉じる
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました:\n{str(e)}")

    def _save_other_work_templates(self):
        """その他作業用テンプレートの設定を保存"""
        procedures = self.config_manager.load_procedures()

        # その他作業用テンプレートの設定を更新
        other_work_templates = {
            "AWS": [self.aws_other_template_var.get().strip()] if self.aws_other_template_var.get().strip() else [],
            "Azure": [self.azure_other_template_var.get().strip()] if self.azure_other_template_var.get().strip() else [],
            "AWS-Azure": [self.hybrid_other_template_var.get().strip()] if self.hybrid_other_template_var.get().strip() else []
        }

        procedures["other_work_templates"] = other_work_templates
        self.config_manager.save_procedures(procedures)

    def _validate_inputs(self):
        """入力値の検証"""
        errors = []

        # 苗字の検証
        if not self.last_name_var.get().strip():
            errors.append("苗字は必須です")

        # デフォルトディレクトリの検証
        default_dir = self.default_directory_var.get().strip()
        if not default_dir:
            errors.append("デフォルトディレクトリは必須です")
        elif not Path(default_dir).exists():
            errors.append("指定されたディレクトリが存在しません")
        elif not Path(default_dir).is_dir():
            errors.append("指定されたパスはディレクトリではありません")

        # PFGrの検証
        if not self.team_group_name_var.get().strip():
            errors.append("PFGrは必須です")

        return errors

    def _reset_to_default(self):
        """デフォルト設定に戻す"""
        if messagebox.askyesno("確認", "設定をデフォルトに戻しますか？\n現在の設定は失われます。"):
            # デフォルト設定を読み込み
            self.config_manager._create_default_config()
            self._load_current_settings()
            messagebox.showinfo("完了", "設定をデフォルトに戻しました。")

    def _update_parent_settings(self):
        """親ウィンドウの設定を更新"""
        try:
            # メインウィンドウの設定を更新
            if self.main_window and hasattr(self.main_window, 'update_settings'):
                self.main_window.update_settings()
            # 親ウィンドウの設定を更新するメソッドがある場合
            elif hasattr(self.parent, 'update_settings'):
                self.parent.update_settings()
        except Exception:
            pass  # 設定更新に失敗した場合は無視

    def _on_closing(self):
        """ウィンドウが閉じられるときの処理"""
        # 変更があるかチェック
        current_last_name = self.config_manager.get_user_setting(
            "last_name") or ""
        current_default_dir = self.config_manager.get_user_setting(
            "default_directory") or ""
        current_team_group_name = self.config_manager.get_user_setting(
            "team_group_name") or ""

        has_changes = (
            self.last_name_var.get().strip() != current_last_name or
            self.default_directory_var.get().strip() != current_default_dir or
            self.team_group_name_var.get().strip() != current_team_group_name
        )

        if has_changes:
            if messagebox.askyesno("確認", "変更が保存されていません。\n保存せずに閉じますか？"):
                self.window.destroy()
        else:
            self.window.destroy()
