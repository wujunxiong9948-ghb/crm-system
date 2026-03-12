@echo off
echo ========================================
echo   CRM系统后端启动脚本
echo ========================================
echo.

REM 设置当前目录为脚本所在目录
cd /d "%~dp0"

REM 进入backend目录
cd backend

echo 正在启动CRM后端API服务...
echo 服务将在 http://localhost:5000 启动
echo.

REM 设置Python路径并启动应用
echo 正在启动Python后端服务...
echo 请稍等...

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未找到或未添加到PATH环境变量
    echo.
    echo 解决方案:
    echo 1. 确保已安装Python 3.6+
    echo 2. 在安装Python时勾选"Add Python to PATH"
    echo 3. 或者手动添加Python到PATH
    echo.
    echo 临时解决方案:
    echo 1. 打开命令提示符
    echo 2. 手动进入目录: cd C:\Users\Administrator\lobsterai\project\crm\backend
    echo 3. 运行: python run_app.py
    pause
    exit /b 1
)

REM 启动Python应用
python run_app.py

echo.
echo 后端服务已停止
pause