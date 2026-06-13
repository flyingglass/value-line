@echo off
chcp 65001 >nul
cd /d %~dp0
echo ========================================
echo  微云下载: 微云 value-line-pdfs -^> data/pdfs
echo  增量同步: 已存在的跳过, 只下载新增/变更
echo ========================================
echo.
.venv\Scripts\python sync_pdfs.py download
echo.
echo === 下载完成 ===
pause
