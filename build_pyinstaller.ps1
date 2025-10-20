# DirCraft - PyInstaller�r���h�X�N���v�g (PowerShell��)
# ===================================================

Write-Host "DirCraft - PyInstaller�r���h�X�N���v�g" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# ���ϐ��̐ݒ�
$env:PYTHONPATH = $PSScriptRoot
$SCRIPT_NAME = "main.py"

Write-Host "Python�p�X: $env:PYTHONPATH" -ForegroundColor Yellow
Write-Host "�X�N���v�g: $SCRIPT_NAME" -ForegroundColor Yellow

# �����̃r���h�t�@�C�����폜
if (Test-Path "DirCraft.exe") { Remove-Item "DirCraft.exe" -Force }
if (Test-Path "DirCraft_debug.exe") { Remove-Item "DirCraft_debug.exe" -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "DirCraft.spec") { Remove-Item "DirCraft.spec" -Force }
if (Test-Path "DirCraft_debug.spec") { Remove-Item "DirCraft_debug.spec" -Force }

Write-Host "`n1. �{�Ԕł��r���h��..." -ForegroundColor Cyan
python -m PyInstaller --onefile --windowed --icon=DirCraft.ico --name=DirCraft --add-data "config;config" --add-data "templates;templates" $SCRIPT_NAME

if ($LASTEXITCODE -eq 0) {
    Write-Host "�{�Ԕł̃r���h���������܂���: dist\DirCraft.exe" -ForegroundColor Green
    if (Test-Path "dist\DirCraft.exe") {
        Copy-Item "dist\DirCraft.exe" "DirCraft.exe" -Force
        Write-Host "DirCraft.exe�����[�g�f�B���N�g���ɃR�s�[���܂���" -ForegroundColor Green
    }
}
else {
    Write-Host "�{�Ԕł̃r���h�Ɏ��s���܂���" -ForegroundColor Red
    goto error
}

Write-Host "`n2. �f�o�b�O�ł��r���h��..." -ForegroundColor Cyan
python -m PyInstaller --onefile --console --icon=DirCraft.ico --name=DirCraft_debug --add-data "config;config" --add-data "templates;templates" $SCRIPT_NAME

if ($LASTEXITCODE -eq 0) {
    Write-Host "�f�o�b�O�ł̃r���h���������܂���: dist\DirCraft_debug.exe" -ForegroundColor Green
    if (Test-Path "dist\DirCraft_debug.exe") {
        Copy-Item "dist\DirCraft_debug.exe" "DirCraft_debug.exe" -Force
        Write-Host "DirCraft_debug.exe�����[�g�f�B���N�g���ɃR�s�[���܂���" -ForegroundColor Green
    }
}
else {
    Write-Host "�f�o�b�O�ł̃r���h�Ɏ��s���܂���" -ForegroundColor Red
    goto error
}

Write-Host "`n�r���h���������܂����I" -ForegroundColor Green
Write-Host "- �{�Ԕ�: DirCraft.exe" -ForegroundColor White
Write-Host "- �f�o�b�O��: DirCraft_debug.exe" -ForegroundColor White

Write-Host "`n�r���h�t�H���_�̃N���[���A�b�v..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "DirCraft.spec") { Remove-Item "DirCraft.spec" -Force }
if (Test-Path "DirCraft_debug.spec") { Remove-Item "DirCraft_debug.spec" -Force }
Write-Host "�N���[���A�b�v����" -ForegroundColor Green
goto end

:error
Write-Host "`n�G���[���������܂����B�ȉ����m�F���Ă��������F" -ForegroundColor Red
Write-Host "1. PyInstaller���C���X�g�[������Ă��邩" -ForegroundColor Yellow
Write-Host "2. �K�v�Ȉˑ��֌W���C���X�g�[������Ă��邩" -ForegroundColor Yellow
Write-Host "3. �A�C�R���t�@�C�������݂��邩" -ForegroundColor Yellow
Write-Host "4. config/templates�t�H���_�����݂��邩" -ForegroundColor Yellow

:end
Read-Host "`nEnter�L�[�������ďI��"

