"""DirectoryCreator.validate_inputs の単体テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.directory_creator import DirectoryCreator  # noqa: E402


def _make_creator() -> DirectoryCreator:
    return DirectoryCreator(MagicMock())


class ValidateInputsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.creator = _make_creator()
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.valid_parent = self._tmp.name

    # --- 正常系 --------------------------------------------------------
    def test_all_valid_returns_empty(self) -> None:
        errors = self.creator.validate_inputs(
            change_number="CHG0001",
            cloud="AWS",
            work_type="IAM改廃",
            work_date="2026-04-23",
            system_name="sysA",
            parent_directory=self.valid_parent,
        )
        self.assertEqual(errors, {})

    def test_each_valid_cloud_accepted(self) -> None:
        for cloud in ("AWS", "Azure", "AWS-Azure"):
            with self.subTest(cloud=cloud):
                errors = self.creator.validate_inputs(
                    "CHG1", cloud, "wt", "2026-04-23", "sys", self.valid_parent
                )
                self.assertNotIn("cloud", errors)

    # --- 変更番号 ------------------------------------------------------
    def test_change_number_required(self) -> None:
        errors = self.creator.validate_inputs(
            "", "AWS", "wt", "2026-04-23", "sys", self.valid_parent
        )
        self.assertIn("change_number", errors)
        self.assertIn("必須", errors["change_number"])

    def test_change_number_whitespace_treated_as_empty(self) -> None:
        errors = self.creator.validate_inputs(
            "   ", "AWS", "wt", "2026-04-23", "sys", self.valid_parent
        )
        self.assertIn("change_number", errors)

    def test_change_number_must_start_with_chg(self) -> None:
        errors = self.creator.validate_inputs(
            "XYZ001", "AWS", "wt", "2026-04-23", "sys", self.valid_parent
        )
        self.assertIn("change_number", errors)
        self.assertIn("CHG", errors["change_number"])

    # --- 対象クラウド -------------------------------------------------
    def test_invalid_cloud(self) -> None:
        errors = self.creator.validate_inputs(
            "CHG1", "GCP", "wt", "2026-04-23", "sys", self.valid_parent
        )
        self.assertIn("cloud", errors)

    def test_empty_cloud(self) -> None:
        errors = self.creator.validate_inputs(
            "CHG1", "", "wt", "2026-04-23", "sys", self.valid_parent
        )
        self.assertIn("cloud", errors)

    # --- 作業内容 / 作業日 / システム名 ------------------------------
    def test_work_type_required(self) -> None:
        errors = self.creator.validate_inputs(
            "CHG1", "AWS", "", "2026-04-23", "sys", self.valid_parent
        )
        self.assertIn("work_type", errors)

    def test_work_date_required(self) -> None:
        errors = self.creator.validate_inputs(
            "CHG1", "AWS", "wt", "", "sys", self.valid_parent
        )
        self.assertIn("work_date", errors)

    def test_system_name_required(self) -> None:
        errors = self.creator.validate_inputs(
            "CHG1", "AWS", "wt", "2026-04-23", "", self.valid_parent
        )
        self.assertIn("system_name", errors)

    # --- 親ディレクトリ -----------------------------------------------
    def test_parent_required(self) -> None:
        errors = self.creator.validate_inputs(
            "CHG1", "AWS", "wt", "2026-04-23", "sys", ""
        )
        self.assertIn("parent_directory", errors)

    def test_parent_must_exist(self) -> None:
        errors = self.creator.validate_inputs(
            "CHG1", "AWS", "wt", "2026-04-23", "sys", "/no/such/path/really"
        )
        self.assertIn("parent_directory", errors)
        self.assertIn("存在しません", errors["parent_directory"])

    def test_parent_must_be_directory(self) -> None:
        file_path = Path(self.valid_parent) / "not_a_dir.txt"
        file_path.write_text("x", encoding="utf-8")
        errors = self.creator.validate_inputs(
            "CHG1", "AWS", "wt", "2026-04-23", "sys", str(file_path)
        )
        self.assertIn("parent_directory", errors)
        self.assertIn("ディレクトリではありません", errors["parent_directory"])

    # --- 複数エラー ----------------------------------------------------
    def test_multiple_errors_reported(self) -> None:
        errors = self.creator.validate_inputs(
            "", "", "", "", "", ""
        )
        expected_keys = {
            "change_number", "cloud", "work_type",
            "work_date", "system_name", "parent_directory",
        }
        self.assertEqual(set(errors.keys()), expected_keys)


if __name__ == "__main__":
    unittest.main()
