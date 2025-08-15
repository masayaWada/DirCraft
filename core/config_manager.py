import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """設定ファイルの管理を行うクラス"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.procedures_file = self.config_dir / "procedures.json"

        # 設定ディレクトリが存在しない場合は作成
        self.config_dir.mkdir(exist_ok=True)

        # 設定ファイルが存在しない場合は初期化
        self._initialize_config_files()

        # 設定ファイルの存在を確認
        if not self.config_file.exists() or not self.procedures_file.exists():
            print("設定ファイルが不足しています。再初期化を実行します。")
            self._initialize_config_files()

    def _initialize_config_files(self):
        """設定ファイルが存在しない場合の初期化"""
        if not self.config_file.exists():
            self._create_default_config()

        if not self.procedures_file.exists():
            self._create_default_procedures()

    def _create_default_config(self):
        """デフォルトのconfig.jsonを作成"""
        default_config = {
            "user_settings": {
                "last_name": "山田",
                "default_directory": str(Path.home() / "Documents" / "DirCraft_Projects"),
                "team_group_name": "グループ名"
            }
        }
        self.save_config(default_config)

    def _create_default_procedures(self):
        """デフォルトのprocedures.jsonを作成"""
        default_procedures = {
            "procedures": {
                "AWS": {
                    "IAM改廃": ["templates/aws/iam_procedure.xlsx"],
                    "EC2設定変更": ["templates/aws/ec2_procedure.xlsx"]
                },
                "Azure": {
                    "NSG改廃": ["templates/azure/nsg_procedure.xlsx"]
                },
                "AWS-Azure": {
                    "ハイブリッド設定変更": ["templates/hybrid/hybrid_procedure.xlsx"]
                }
            },
            "common_templates": {
                "必須手順書": [
                    "templates/common/required_procedure.xlsx"
                ],
                "証跡": "templates/common/evidence.xlsx",
                "準備調整チェックシート": "templates/common/reception_checklist.xlsx"
            }
        }
        self.save_procedures(default_procedures)

    def load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._create_default_config()
            return self.load_config()

    def save_config(self, config: Dict[str, Any]):
        """設定ファイルを保存"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def load_procedures(self) -> Dict[str, Any]:
        """手順書設定ファイルを読み込み"""
        try:
            with open(self.procedures_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._create_default_procedures()
            return self.load_procedures()

    def save_procedures(self, procedures: Dict[str, Any]):
        """手順書設定ファイルを保存"""
        with open(self.procedures_file, 'w', encoding='utf-8') as f:
            json.dump(procedures, f, ensure_ascii=False, indent=2)

    def get_user_setting(self, key: str) -> Optional[str]:
        """ユーザー設定の値を取得"""
        config = self.load_config()
        return config.get("user_settings", {}).get(key)

    def set_user_setting(self, key: str, value: str):
        """ユーザー設定の値を設定"""
        config = self.load_config()
        if "user_settings" not in config:
            config["user_settings"] = {}
        config["user_settings"][key] = value
        self.save_config(config)

    def get_procedure_templates(self, cloud: str, work_type: str) -> list:
        """指定されたクラウド・作業内容の手順書テンプレートを取得"""
        procedures = self.load_procedures()
        return procedures.get("procedures", {}).get(cloud, {}).get(work_type, [])

    def get_common_template(self, template_name: str) -> Optional[str]:
        """共通テンプレートのパスを取得"""
        procedures = self.load_procedures()
        template_path = procedures.get(
            "common_templates", {}).get(template_name)

        # 配列形式の場合は最初の要素を返す
        if isinstance(template_path, list) and template_path:
            return template_path[0]
        elif isinstance(template_path, str):
            return template_path

        return None
