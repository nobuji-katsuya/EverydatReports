@echo off
REM =====================================================
REM 作業履歴日報ファイル自動生成スクリプト
REM フォルダ構成：作業履歴\YYYY\MM\YYYY-MM-DD.md
REM テンプレート：作業履歴\template\daily_template.md
REM 使用方法：
REM   newlog.bat            → 今日の日付でファイル作成
REM   newlog.bat YYYY-MM-DD → 指定日付でファイル作成
REM =====================================================

setlocal enabledelayedexpansion

REM === 日付取得 ===
if "%1"=="" (
    for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set DATESTR=%%a
) else (
    set DATESTR=%1
)

for /f "tokens=1-3 delims=-" %%a in ("%DATESTR%") do (
    set YYYY=%%a
    set MM=%%b
    set DD=%%c
)
set TODAY=%YYYY%-%MM%-%DD%
REM 曜日取得（PowerShell利用）
for /f %%w in ('powershell -Command "(Get-Date \"%TODAY%\").ToString(\"ddd\")"') do set WEEKDAY=%%w


set TARGET_DIR=%YYYY%\%MM%
set TARGET_FILE=%TARGET_DIR%\%YYYY%-%MM%-%DD%.md
set TEMPLATE_FILE=template\daily_template.md

REM === フォルダ作成 ===
if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%"
)

REM === テンプレートからコピー ===
if exist "%TARGET_FILE%" (
    echo 既に今日のファイルは存在します：%TARGET_FILE%
) else (
    if exist "%TEMPLATE_FILE%" (
        copy "%TEMPLATE_FILE%" "%TARGET_FILE%" >nul
        REM === プレースホルダ置換 ===
        powershell -Command ^
          "$content = Get-Content '%TARGET_FILE%' -Encoding UTF8; $content = $content -replace '\{\{date:YYYY-MM-DD（ddd）\}\}', '%TODAY%（%WEEKDAY%）'; $content | Set-Content '%TARGET_FILE%' -Encoding UTF8"
        echo 新しい作業履歴を作成しました：%TARGET_FILE%
    ) else (
        echo テンプレートファイルが見つかりません：%TEMPLATE_FILE%
    )
)

endlocal
pause
