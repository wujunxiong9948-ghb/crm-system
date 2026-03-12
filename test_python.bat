@echo off
echo ========================================
echo   Python环境测试脚本
echo ========================================
echo.

echo 测试Python环境...
echo.

REM 测试Python版本
echo 1. 测试Python版本:
python --version
if %errorlevel% neq 0 (
    echo 错误: Python命令不可用
    echo.
    echo 请检查:
    echo 1. Python是否已安装
    echo 2. Python是否已添加到PATH环境变量
    echo.
    pause
    exit /b 1
)

echo.
echo 2. 测试Python脚本执行:
echo print("Python环境测试成功！") > test_python.py
python test_python.py
del test_python.py

echo.
echo 3. 测试Flask依赖:
python -c "import flask; print('Flask版本:', flask.__version__)"
if %errorlevel% neq 0 (
    echo 警告: Flask未安装，请运行: pip install flask flask-cors flask-jwt-extended flask-bcrypt
)

echo.
echo 4. 测试后端目录:
cd backend
if %errorlevel% neq 0 (
    echo 错误: 无法进入backend目录
    pause
    exit /b 1
)

echo.
echo 5. 测试app.py是否可以导入:
python -c "import sys; sys.path.insert(0, '.'); from app import create_app; print('app.py导入成功！')"
if %errorlevel% neq 0 (
    echo 警告: app.py导入失败，可能需要安装依赖
    echo 请运行: pip install -r requirements.txt
)

echo.
echo ========================================
echo   测试完成！
echo ========================================
echo.
echo 如果所有测试都通过，可以尝试启动后端:
echo python app.py
echo.
pause