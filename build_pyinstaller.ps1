# DirCraft - PyInstallerビルドスクリプト (PowerShell版)
# ===================================================

Write-Host "DirCraft - PyInstallerビルドスクリプト" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# 環境変数の設定
$env:PYTHONPATH = $PSScriptRoot
$SCRIPT_NAME = "main.py"

Write-Host "Pythonパス: $env:PYTHONPATH" -ForegroundColor Yellow
Write-Host "スクリプト: $SCRIPT_NAME" -ForegroundColor Yellow

# 既存のビルドファイルを削除
if (Test-Path "DirCraft.exe") { Remove-Item "DirCraft.exe" -Force }
if (Test-Path "DirCraft_debug.exe") { Remove-Item "DirCraft_debug.exe" -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "DirCraft.spec") { Remove-Item "DirCraft.spec" -Force }
if (Test-Path "DirCraft_debug.spec") { Remove-Item "DirCraft_debug.spec" -Force }

Write-Host "`n1. 本番版をビルド中..." -ForegroundColor Cyan
python -m PyInstaller --onefile --windowed --icon=DirCraft.ico --name=DirCraft --add-data "config;config" --add-data "templates;templates" --add-data "assets;assets" $SCRIPT_NAME

if ($LASTEXITCODE -eq 0) {
    Write-Host "本番版のビルドが完了しました: dist\DirCraft.exe" -ForegroundColor Green
    if (Test-Path "dist\DirCraft.exe") {
        Copy-Item "dist\DirCraft.exe" "DirCraft.exe" -Force
        Write-Host "DirCraft.exeをルートディレクトリにコピーしました" -ForegroundColor Green
    }
}
else {
    Write-Host "本番版のビルドに失敗しました" -ForegroundColor Red
    goto error
}

Write-Host "`n2. デバッグ版をビルド中..." -ForegroundColor Cyan
python -m PyInstaller --onefile --console --icon=DirCraft.ico --name=DirCraft_debug --add-data "config;config" --add-data "templates;templates" --add-data "assets;assets" $SCRIPT_NAME

if ($LASTEXITCODE -eq 0) {
    Write-Host "デバッグ版のビルドが完了しました: dist\DirCraft_debug.exe" -ForegroundColor Green
    if (Test-Path "dist\DirCraft_debug.exe") {
        Copy-Item "dist\DirCraft_debug.exe" "DirCraft_debug.exe" -Force
        Write-Host "DirCraft_debug.exeをルートディレクトリにコピーしました" -ForegroundColor Green
    }
}
else {
    Write-Host "デバッグ版のビルドに失敗しました" -ForegroundColor Red
    goto error
}

Write-Host "`nビルドが完了しました！" -ForegroundColor Green
Write-Host "- 本番版: DirCraft.exe" -ForegroundColor White
Write-Host "- デバッグ版: DirCraft_debug.exe" -ForegroundColor White

Write-Host "`nビルドフォルダのクリーンアップ..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "DirCraft.spec") { Remove-Item "DirCraft.spec" -Force }
if (Test-Path "DirCraft_debug.spec") { Remove-Item "DirCraft_debug.spec" -Force }
Write-Host "クリーンアップ完了" -ForegroundColor Green
goto end

:error
Write-Host "`nエラーが発生しました。以下を確認してください：" -ForegroundColor Red
Write-Host "1. PyInstallerがインストールされているか" -ForegroundColor Yellow
Write-Host "2. 必要な依存関係がインストールされているか" -ForegroundColor Yellow
Write-Host "3. アイコンファイルが存在するか" -ForegroundColor Yellow
Write-Host "4. config/templatesフォルダが存在するか" -ForegroundColor Yellow

:end
Read-Host "`nEnterキーを押して終了"

