#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统启动脚本 - 修复导入问题
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"当前工作目录: {os.getcwd()}")
print(f"脚本所在目录: {current_dir}")
print(f"Python路径已更新")

try:
    # 尝试导入配置
    from config import settings
    print("配置导入成功!")

    # 导入并启动应用
    from app import create_app, app

    if __name__ == '__main__':
        # 启动开发服务器
        print("=" * 60)
        print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
        print("=" * 60)
        print(f"运行模式: {'开发' if settings.DEBUG else '生产'}")
        print(f"数据库: {settings.DATABASE_URL}")
        print(f"日志级别: {settings.LOG_LEVEL}")
        print(f"API前缀: {settings.API_PREFIX}/{settings.API_VERSION}")
        print("=" * 60)

        app.run(
            host='0.0.0.0',
            port=5000,
            debug=settings.DEBUG,
            threaded=True
        )

except ImportError as e:
    print(f"导入错误: {e}")
    print("\n可能的原因:")
    print("1. 依赖未安装 - 运行: pip install -r requirements.txt")
    print("2. 文件缺失 - 确保所有Python文件都在backend目录中")
    print("3. Python路径问题 - 当前目录:", current_dir)
    print("\n当前目录内容:")
    for file in os.listdir(current_dir):
        print(f"  - {file}")
    input("\n按Enter键退出...")
except Exception as e:
    print(f"启动错误: {e}")
    import traceback
    traceback.print_exc()
    input("\n按Enter键退出...")