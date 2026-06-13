@echo off
chcp 65001 >nul
cd /d %~dp0
echo ========================================
echo  微云上传: data/pdfs -^> 微云 value-line-pdfs
echo  增量同步: 已存在的跳过, 只传新增/变更
echo ========================================
echo.
.venv\Scripts\python sync_pdfs.py upload
echo.
echo === 上传完成 ===
pause
