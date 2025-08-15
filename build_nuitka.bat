@echo off
echo DirCraft - Nuitkaビルドスクリプト
echo =================================

REM 環境変数の設定
set PYTHONPATH=%~dp0
set SCRIPT_NAME=main.py

echo Pythonパス: %PYTHONPATH%
echo スクリプト: %SCRIPT_NAME%

REM 既存のビルドファイルを削除
if exist "DirCraft.exe" del "DirCraft.exe"
if exist "DirCraft_debug.exe" del "DirCraft_debug.exe"
if exist "main.exe" del "main.exe"
if exist "main.dist" rmdir /s /q "main.dist"
if exist "main.build" rmdir /s /q "main.build"

echo.
echo 1. 本番版をビルド中...
python -m nuitka --standalone --onefile --windows-console-mode=disable --windows-icon-from-ico=DirCraft.ico --output-filename=DirCraft.exe %SCRIPT_NAME%

if %ERRORLEVEL% EQU 0 (
    echo 本番版のビルドが完了しました: DirCraft.exe
) else (
    echo 本番版のビルドに失敗しました
    goto :error
)

echo.
echo 2. デバッグ版をビルド中...
python -m nuitka --standalone --onefile --windows-console-mode=force --windows-icon-from-ico=DirCraft.ico --output-filename=DirCraft_debug.exe --enable-plugin=tk-inter --show-progress %SCRIPT_NAME%

if %ERRORLEVEL% EQU 0 (
    echo デバッグ版のビルドが完了しました: DirCraft_debug.exe
) else (
    echo デバッグ版のビルドに失敗しました
    goto :error
)

echo.
echo ビルドが完了しました！
echo - 本番版: DirCraft.exe
echo - デバッグ版: DirCraft_debug.exe
goto :end

:error
echo.
echo エラーが発生しました。以下を確認してください：
echo 1. Nuitkaがインストールされているか
echo 2. 必要な依存関係がインストールされているか
echo 3. アイコンファイルが存在するか

:end
pause
