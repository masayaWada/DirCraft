# テンプレートファイル

このディレクトリには、DirCraftで使用する雛形ファイルが配置されます。

## ディレクトリ構造

```
templates/
├── common/           # 共通テンプレート
│   ├── required_procedure.xlsx      # 必須手順書
│   ├── work_procedure.xlsx          # 作業手順書
│   ├── evidence.xlsx                # 証跡
│   └── reception_checklist.xlsx     # 受付チェックシート
├── aws/              # AWS用テンプレート
│   ├── iam_procedure.xlsx           # IAM改廃手順書
│   ├── iam_checklist.xlsx           # IAM改廃チェックリスト
│   ├── ec2_procedure.xlsx           # EC2設定変更手順書
│   ├── ec2_config.xlsx              # EC2設定ファイル
│   └── s3_procedure.xlsx            # S3設定変更手順書
├── azure/            # Azure用テンプレート
│   ├── nsg_procedure.xlsx           # NSG改廃手順書
│   ├── nsg_rules.xlsx               # NSGルール設定
│   └── vm_procedure.xlsx            # VM設定変更手順書
└── hybrid/           # ハイブリッド用テンプレート
    ├── hybrid_procedure.xlsx        # ハイブリッド設定変更手順書
    └── network_config.xlsx          # ネットワーク設定
```

## 注意事項

- すべてのテンプレートファイルはExcel形式（.xlsx）である必要があります
- ファイル名は設定ファイル（procedures.json）で指定されているものと一致する必要があります
- テンプレートファイルが存在しない場合、対応するファイルはコピーされません
