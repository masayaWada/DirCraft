import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from .config_manager import ConfigManager


class DirectoryCreator:
    """作業用ディレクトリの作成とファイルのコピーを行うクラス"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def create_work_directory(
        self,
        change_number: str,
        cloud: str,
        work_type: str,
        work_date: str,
        system_name: str,
        parent_directory: str
    ) -> str:
        """
        作業用ディレクトリを作成し、必要なファイルをコピー

        Args:
            change_number: 変更番号
            cloud: 対象クラウド
            work_type: 作業内容
            work_date: 作業日
            system_name: 変更対象システム名
            parent_directory: 親ディレクトリのパス

        Returns:
            作成された作業用ディレクトリのパス
        """
        try:
            # 作業用ディレクトリ名を生成
            directory_name = self._generate_directory_name(
                change_number, cloud, work_type, work_date, system_name
            )

            # 作業用ディレクトリのパス
            work_dir_path = Path(parent_directory) / directory_name

            # ディレクトリが既に存在する場合はエラー
            if work_dir_path.exists():
                raise FileExistsError(f"作業用ディレクトリが既に存在します: {work_dir_path}")

            # 作業用ディレクトリとサブディレクトリを作成
            self._create_directory_structure(work_dir_path)

            # 共通テンプレートファイルをコピー
            self._copy_common_templates(work_dir_path)

            # 作業内容に応じたテンプレートファイルをコピー
            self._copy_work_templates(work_dir_path, cloud, work_type)

            return str(work_dir_path)

        except Exception as e:
            raise Exception(f"作業用ディレクトリの作成に失敗しました: {str(e)}")

    def _generate_directory_name(
        self,
        change_number: str,
        cloud: str,
        work_type: str,
        work_date: str,
        system_name: str
    ) -> str:
        """作業用ディレクトリ名を生成"""
        today = datetime.now().strftime("%Y%m%d")
        last_name = self.config_manager.get_user_setting("last_name")
        team_group_name = self.config_manager.get_user_setting(
            "team_group_name")

        return f"{change_number}-{today}-{team_group_name}-{last_name}-変更申請書-【{cloud}】{system_name}_{work_type}_{work_date}"

    def _create_directory_structure(self, work_dir_path: Path):
        """作業用ディレクトリの構造を作成"""
        # メインディレクトリ
        work_dir_path.mkdir(parents=True, exist_ok=True)

        # サブディレクトリ
        (work_dir_path / "手順書").mkdir(exist_ok=True)
        (work_dir_path / "証跡").mkdir(exist_ok=True)
        (work_dir_path / "メール").mkdir(exist_ok=True)

    def _copy_common_templates(self, work_dir_path: Path):
        """共通テンプレートファイルをコピー"""
        common_templates = {
            "必須手順書": "手順書/必須手順書.xlsx",
            "作業手順書": "手順書/作業手順書.xlsx",
            "受付チェックシート": "メール/受付チェックシート.xlsx"
        }

        for template_name, target_path in common_templates.items():
            source_path = self.config_manager.get_common_template(
                template_name)
            if source_path and Path(source_path).exists():
                target_file = work_dir_path / target_path
                shutil.copy2(source_path, target_file)

        # 証跡ファイルもここでコピー（名前変更して）
        evidence_template = self.config_manager.get_common_template("証跡")
        if evidence_template and Path(evidence_template).exists():
            # 証跡ファイル名を生成（作業用ディレクトリ名から取得）
            work_dir_name = work_dir_path.name
            evidence_name = f"{work_dir_name}-作業証跡.xlsx"
            target_file = work_dir_path / "証跡" / evidence_name
            shutil.copy2(evidence_template, target_file)

    def _copy_work_templates(self, work_dir_path: Path, cloud: str, work_type: str):
        """作業内容に応じたテンプレートファイルをコピー"""
        # 作業内容に応じたテンプレートファイルを取得
        work_templates = self.config_manager.get_procedure_templates(
            cloud, work_type)

        if not work_templates:
            return

        # 手順書ディレクトリにコピー
        for template_path in work_templates:
            if Path(template_path).exists():
                template_name = Path(template_path).name
                target_file = work_dir_path / "手順書" / template_name
                shutil.copy2(template_path, target_file)

    def validate_inputs(
        self,
        change_number: str,
        cloud: str,
        work_type: str,
        work_date: str,
        system_name: str,
        parent_directory: str
    ) -> List[str]:
        """入力値の検証を行い、エラーメッセージのリストを返す"""
        errors = []

        # 変更番号の検証
        if not change_number or not change_number.strip():
            errors.append("変更番号は必須です")
        elif not change_number.startswith("CHG"):
            errors.append("変更番号は'CHG'で始まる必要があります")

        # 対象クラウドの検証
        valid_clouds = ["AWS", "Azure", "AWS-Azure"]
        if cloud not in valid_clouds:
            errors.append(
                f"対象クラウドは以下のいずれかである必要があります: {', '.join(valid_clouds)}")

        # 作業内容の検証
        if not work_type or not work_type.strip():
            errors.append("作業内容は必須です")

        # 作業日の検証
        if not work_date or not work_date.strip():
            errors.append("作業日は必須です")

        # システム名の検証
        if not system_name or not system_name.strip():
            errors.append("変更対象システム名は必須です")

        # 親ディレクトリの検証
        if not parent_directory or not parent_directory.strip():
            errors.append("親ディレクトリのパスは必須です")
        elif not Path(parent_directory).exists():
            errors.append("指定された親ディレクトリが存在しません")
        elif not Path(parent_directory).is_dir():
            errors.append("指定されたパスはディレクトリではありません")

        return errors
