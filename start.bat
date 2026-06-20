@echo off
chcp 65001 > nul
echo ================================
echo   一线员工薪酬核算系统 v6
echo ================================
echo.

REM 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
python -c "import flask, sqlite3" 2>nul
if %errorlevel% neq 0 (
    echo 📦 安装依赖中...
    pip install flask flask-cors
)

echo 🚀 启动服务器...
echo.
echo    访问地址: <ADDRESS_REMOVED>
echo    按 Ctrl+C 停止服务器
echo.
python app.py
pause
