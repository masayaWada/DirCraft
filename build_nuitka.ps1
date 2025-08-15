# DirCraft - Nuitkaビルドスクリプト (PowerShell版)
# ================================================

Write-Host "DirCraft - Nuitkaビルドスクリプト" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# 環境変数の設定
$env:PYTHONPATH = $PSScriptRoot
$SCRIPT_NAME = "main.py"

Write-Host "Pythonパス: $env:PYTHONPATH" -ForegroundColor Yellow
Write-Host "スクリプト: $SCRIPT_NAME" -ForegroundColor Yellow

# 既存のビルドファイルを削除
if (Test-Path "DirCraft.exe") { Remove-Item "DirCraft.exe" -Force }
if (Test-Path "DirCraft_debug.exe") { Remove-Item "DirCraft_debug.exe" -Force }
if (Test-Path "main.exe") { Remove-Item "main.exe" -Force }
if (Test-Path "main.dist") { Remove-Item "main.dist" -Recurse -Force }
if (Test-Path "main.build") { Remove-Item "main.build" -Recurse -Force }

Write-Host "`n1. 本番版をビルド中..." -ForegroundColor Cyan
$result1 = python -m nuitka --standalone --onefile --windows-console-mode=hide --windows-icon-from-ico=DirCraft.ico --output-filename=DirCraft.exe $SCRIPT_NAME

if ($LASTEXITCODE -eq 0) {
    Write-Host "本番版のビルドが完了しました: DirCraft.exe" -ForegroundColor Green
} else {
    Write-Host "本番版のビルドに失敗しました" -ForegroundColor Red
    goto error
}

Write-Host "`n2. デバッグ版をビルド中..." -ForegroundColor Cyan
$result2 = python -m nuitka --standalone --onefile --windows-console-mode=force --windows-icon-from-ico=DirCraft.ico --output-filename=DirCraft_debug.exe --enable-plugin=tk-inter --show-progress $SCRIPT_NAME

if ($LASTEXITCODE -eq 0) {
    Write-Host "デバッグ版のビルドが完了しました: DirCraft_debug.exe" -ForegroundColor Green
} else {
    Write-Host "デバッグ版のビルドに失敗しました" -ForegroundColor Red
    goto error
}

Write-Host "`nビルドが完了しました！" -ForegroundColor Green
Write-Host "- 本番版: DirCraft.exe" -ForegroundColor White
Write-Host "- デバッグ版: DirCraft_debug.exe" -ForegroundColor White
goto end

error:
Write-Host "`nエラーが発生しました。以下を確認してください：" -ForegroundColor Red
Write-Host "1. Nuitkaがインストールされているか" -ForegroundColor Yellow
Write-Host "2. 必要な依存関係がインストールされているか" -ForegroundColor Yellow
Write-Host "3. アイコンファイルが存在するか" -ForegroundColor Yellow

end:
Read-Host "`nEnterキーを押して終了"
