#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建reminders表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()

with app.app_context():
    print("正在创建数据库表...")
    db.create_all()
    print("✅ 数据库表创建完成！")
    
    # 验证表是否创建成功
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'reminders' in tables:
        print("✅ reminders表已成功创建！")
    else:
        print("❌ reminders表未找到")
        print(f"现有表: {tables}")
