@echo off
echo ========================================
echo   CRM系统前端启动脚本
echo ========================================
echo.

REM 设置当前目录为脚本所在目录
cd /d "%~dp0"

REM 进入frontend目录
cd frontend

echo 正在启动CRM前端React应用...
echo 应用将在 http://localhost:3000 启动
echo.

REM 检查是否已安装依赖
if not exist "node_modules" (
    echo 正在安装前端依赖...
    call npm install
    echo 依赖安装完成！
)

echo 启动前端开发服务器...
call npm start

echo.
echo 前端服务已停止
pause