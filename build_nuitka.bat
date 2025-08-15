@echo off
echo DirCraft - Nuitka�r���h�X�N���v�g
echo =================================

REM ���ϐ��̐ݒ�
set PYTHONPATH=%~dp0
set SCRIPT_NAME=main.py

echo Python�p�X: %PYTHONPATH%
echo �X�N���v�g: %SCRIPT_NAME%

REM �����̃r���h�t�@�C�����폜
if exist "DirCraft.exe" del "DirCraft.exe"
if exist "DirCraft_debug.exe" del "DirCraft_debug.exe"
if exist "main.exe" del "main.exe"
if exist "main.dist" rmdir /s /q "main.dist"
if exist "main.build" rmdir /s /q "main.build"

echo.
echo 1. �{�Ԕł��r���h��...
python -m nuitka --standalone --onefile --windows-console-mode=disable --windows-icon-from-ico=DirCraft.ico --output-filename=DirCraft.exe %SCRIPT_NAME%

if %ERRORLEVEL% EQU 0 (
    echo �{�Ԕł̃r���h���������܂���: DirCraft.exe
) else (
    echo �{�Ԕł̃r���h�Ɏ��s���܂���
    goto :error
)

echo.
echo 2. �f�o�b�O�ł��r���h��...
python -m nuitka --standalone --onefile --windows-console-mode=force --windows-icon-from-ico=DirCraft.ico --output-filename=DirCraft_debug.exe --enable-plugin=tk-inter --show-progress %SCRIPT_NAME%

if %ERRORLEVEL% EQU 0 (
    echo �f�o�b�O�ł̃r���h���������܂���: DirCraft_debug.exe
) else (
    echo �f�o�b�O�ł̃r���h�Ɏ��s���܂���
    goto :error
)

echo.
echo �r���h���������܂����I
echo - �{�Ԕ�: DirCraft.exe
echo - �f�o�b�O��: DirCraft_debug.exe
goto :end

:error
echo.
echo �G���[���������܂����B�ȉ����m�F���Ă��������F
echo 1. Nuitka���C���X�g�[������Ă��邩
echo 2. �K�v�Ȉˑ��֌W���C���X�g�[������Ă��邩
echo 3. �A�C�R���t�@�C�������݂��邩

:end
pause
