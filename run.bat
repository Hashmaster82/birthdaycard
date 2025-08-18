@echo off
setlocal enabledelayedexpansion

REM === Папка проекта (где лежит репозиторий) ===
set REPO_DIR=%~dp0

REM === Проверка, установлен ли git ===
where git >nul 2>nul
if errorlevel 1 (
    echo ❌ Git не найден. Установите Git: https://git-scm.com/download/win
    pause
    exit /b
)

echo 🔄 Обновление проекта с GitHub...
cd /d "%REPO_DIR%"
git pull

REM === Проверка наличия EXE ===
if exist "%REPO_DIR%dist\main.exe" (
    echo 🚀 Запуск собранной программы...
    start "" "%REPO_DIR%dist\main.exe"
) else (
    echo 🚀 Запуск через Python...
    python "%REPO_DIR%main.py"
)

endlocal
