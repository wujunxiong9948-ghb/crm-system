@echo off
echo ========================================
echo   CRM系统简单启动脚本
echo ========================================
echo.
echo 这个脚本解决了"python不是内部或外部命令"的问题
echo.

REM 设置当前目录为脚本所在目录
cd /d "%~dp0"

echo 请选择启动方式:
echo 1. 启动后端API服务 (http://localhost:5000)
echo 2. 启动前端React应用 (http://localhost:3000)
echo 3. 同时启动前后端（推荐）
echo 4. 退出
echo.
set /p choice="请输入选择 (1-4): "

if "%choice%"=="1" goto start_backend
if "%choice%"=="2" goto start_frontend
if "%choice%"=="3" goto start_both
if "%choice%"=="4" goto exit
echo 无效选择
pause
exit /b

:start_backend
echo.
echo 正在启动后端API服务...
echo 请按照以下步骤操作:
echo.
echo 1. 打开一个新的命令提示符窗口
echo 2. 输入以下命令:
echo    cd C:\Users\Administrator\lobsterai\project\crm\backend
echo    python run_app.py
echo.
echo 3. 按Enter键运行
echo.
echo 后端将在 http://localhost:5000 启动
echo.
pause
exit /b

:start_frontend
echo.
echo 正在启动前端React应用...
echo 请按照以下步骤操作:
echo.
echo 1. 打开一个新的命令提示符窗口
echo 2. 输入以下命令:
echo    cd C:\Users\Administrator\lobsterai\project\crm\frontend
echo    npm start
echo.
echo 3. 按Enter键运行
echo.
echo 前端将在 http://localhost:3000 启动
echo.
pause
exit /b

:start_both
echo.
echo 同时启动前后端服务...
echo.
echo 请按照以下步骤操作:
echo.
echo 步骤1: 启动后端
echo 1. 打开第一个命令提示符窗口
echo 2. 输入以下命令:
echo    cd C:\Users\Administrator\lobsterai\project\crm\backend
echo    python run_app.py
echo 3. 按Enter键运行
echo.
echo 步骤2: 启动前端
echo 1. 打开第二个命令提示符窗口
echo 2. 输入以下命令:
echo    cd C:\Users\Administrator\lobsterai\project\crm\frontend
echo    npm start
echo 3. 按Enter键运行
echo.
echo 访问地址:
echo - 前端界面: http://localhost:3000
echo - 后端API: http://localhost:5000
echo.
echo 登录信息:
echo - 管理员: admin / admin123
echo - 销售员: sales1 / sales123
echo.
pause
exit /b

:exit
echo 退出脚本
pause