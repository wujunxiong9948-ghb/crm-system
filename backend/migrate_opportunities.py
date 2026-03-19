#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
销售机会表结构迁移脚本
添加酒店家具项目专用字段
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db
from sqlalchemy import text

def migrate_opportunities_table():
    """迁移 opportunities 表，添加新字段"""

    with app.app_context():
        # 获取数据库连接
        conn = db.engine.connect()

        # 新字段列表 (字段名, 类型, 默认值)
        new_columns = [
            ('hotel_name', 'VARCHAR(200)', None),
            ('project_type', 'VARCHAR(20)', "'新建酒店'"),
            ('hotel_star', 'VARCHAR(10)', None),
            ('room_count', 'INTEGER', None),
            ('province', 'VARCHAR(50)', None),
            ('city', 'VARCHAR(50)', None),
            ('district', 'VARCHAR(50)', None),
            ('planned_opening_date', 'DATE', None),
            ('next_follow_up_date', 'DATE', None),
            ('renovation_budget', 'FLOAT', 0.0),
            ('furniture_budget', 'FLOAT', 0.0),
            ('bed_count', 'INTEGER', 0),
            ('nightstand_count', 'INTEGER', 0),
            ('wardrobe_count', 'INTEGER', 0),
            ('desk_count', 'INTEGER', 0),
            ('chair_count', 'INTEGER', 0),
            ('sofa_count', 'INTEGER', 0),
            ('coffee_table_count', 'INTEGER', 0),
            ('tv_cabinet_count', 'INTEGER', 0),
            ('other_furniture', 'TEXT', None),
            ('priority', 'VARCHAR(10)', "'中'"),
            ('competitors', 'TEXT', None),
            ('our_advantage', 'TEXT', None),
            ('customer_concern', 'TEXT', None),
            ('decision_maker', 'VARCHAR(100)', None),
            ('decision_process', 'TEXT', None),
            ('key_contacts', 'TEXT', None),
            ('follow_up_records', 'TEXT', None),
        ]

        print("=" * 60)
        print("开始迁移 opportunities 表...")
        print("=" * 60)

        # 检查现有字段
        result = conn.execute(text("PRAGMA table_info(opportunities)"))
        existing_columns = {row[1] for row in result.fetchall()}
        print(f"\n现有字段数: {len(existing_columns)}")

        added_count = 0
        skipped_count = 0

        for col_name, col_type, default in new_columns:
            if col_name in existing_columns:
                print(f"  ⚠️  字段已存在，跳过: {col_name}")
                skipped_count += 1
                continue

            # 构建 ALTER TABLE 语句
            if default is not None:
                sql = f"ALTER TABLE opportunities ADD COLUMN {col_name} {col_type} DEFAULT {default}"
            else:
                sql = f"ALTER TABLE opportunities ADD COLUMN {col_name} {col_type}"

            try:
                conn.execute(text(sql))
                print(f"  ✅ 添加字段: {col_name} ({col_type})")
                added_count += 1
            except Exception as e:
                print(f"  ❌ 添加失败: {col_name} - {e}")

        conn.commit()
        conn.close()

        print("\n" + "=" * 60)
        print("迁移完成!")
        print(f"  新增字段: {added_count}")
        print(f"  跳过字段: {skipped_count}")
        print("=" * 60)

        # 验证迁移结果
        conn = db.engine.connect()
        result = conn.execute(text("PRAGMA table_info(opportunities)"))
        all_columns = [row[1] for row in result.fetchall()]
        conn.close()

        print(f"\n当前表字段总数: {len(all_columns)}")
        print("\n新字段列表:")
        for col in new_columns:
            status = "✅" if col[0] in all_columns else "❌"
            print(f"  {status} {col[0]}")

if __name__ == '__main__':
    migrate_opportunities_table()
