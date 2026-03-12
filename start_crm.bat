@echo off
echo ========================================
echo       酒店家具CRM系统启动脚本
echo ========================================
echo.

REM 设置当前目录为脚本所在目录
cd /d "%~dp0"

echo 请选择启动方式:
echo 1. 启动后端API服务 (http://localhost:5000)
echo 2. 启动前端React应用 (http://localhost:3000)
echo 3. 同时启动前后端（需要两个命令窗口）
echo 4. 查看使用说明
echo.
set /p choice="请输入选择 (1-4): "

if "%choice%"=="1" (
    echo 正在启动后端API服务...
    start cmd /k "start_backend.bat"
) else if "%choice%"=="2" (
    echo 正在启动前端React应用...
    start cmd /k "start_frontend.bat"
) else if "%choice%"=="3" (
    echo 正在同时启动前后端...
    echo 请等待3秒...
    start cmd /k "start_backend.bat"
    timeout /t 3 /nobreak >nul
    start cmd /k "start_frontend.bat"
    echo 前后端已启动！
    echo.
    echo 访问地址:
    echo - 前端界面: http://localhost:3000
    echo - 后端API: http://localhost:5000
    echo.
    pause
) else if "%choice%"=="4" (
    echo.
    echo =========== CRM系统使用说明 ===========
    echo.
    echo 系统位置: %cd%
    echo.
    echo 启动方式:
    echo 1. 双击运行 start_backend.bat 启动后端
    echo 2. 双击运行 start_frontend.bat 启动前端
    echo 3. 运行本脚本选择选项3同时启动
    echo.
    echo 访问地址:
    echo - 前端界面: http://localhost:3000
    echo - 后端API: http://localhost:5000
    echo.
    echo 登录信息:
    echo - 管理员: admin / admin123
    echo - 销售员: sales1 / sales123
    echo.
    echo 系统功能:
    echo - 客户管理 - 客户信息、跟进记录
    echo - 销售管理 - 销售机会、报价单
    echo - 产品管理 - 产品目录、库存
    echo - 订单管理 - 订单跟踪、发货
    echo - 报表分析 - 销售业绩、客户分析
    echo - QQ通知 - 已集成QQ机器人通知功能
    echo.
    pause
) else (
    echo 无效选择，请重新运行脚本
    pause
)