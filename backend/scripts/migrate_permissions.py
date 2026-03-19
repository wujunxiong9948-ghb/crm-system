#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加权限相关字段
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text


def migrate_customer_table():
    """为客户表添加权限相关字段"""
    print("\n[1] 迁移客户表...")
    
    try:
        # 检查字段是否已存在
        result = db.session.execute(text("PRAGMA table_info(customers)"))
        columns = [row[1] for row in result]
        
        if 'assigned_to' not in columns:
            db.session.execute(text("ALTER TABLE customers ADD COLUMN assigned_to VARCHAR(100)"))
            print("  [+] 添加 assigned_to 字段")
        else:
            print("  [*] assigned_to 字段已存在")
        
        if 'created_by' not in columns:
            db.session.execute(text("ALTER TABLE customers ADD COLUMN created_by INTEGER"))
            print("  [+] 添加 created_by 字段")
        else:
            print("  [*] created_by 字段已存在")
        
        db.session.commit()
        print("  [OK] 客户表迁移完成")
        return True
        
    except Exception as e:
        print(f"  [X] 客户表迁移失败: {e}")
        db.session.rollback()
        return False


def migrate_opportunity_table():
    """为机会表添加权限相关字段"""
    print("\n[2] 迁移机会表...")
    
    try:
        result = db.session.execute(text("PRAGMA table_info(opportunities)"))
        columns = [row[1] for row in result]
        
        if 'created_by' not in columns:
            db.session.execute(text("ALTER TABLE opportunities ADD COLUMN created_by INTEGER"))
            print("  [+] 添加 created_by 字段")
        else:
            print("  [*] created_by 字段已存在")
        
        db.session.commit()
        print("  [OK] 机会表迁移完成")
        return True
        
    except Exception as e:
        print(f"  [X] 机会表迁移失败: {e}")
        db.session.rollback()
        return False


def init_default_data():
    """初始化默认数据"""
    print("\n[3] 初始化默认数据...")
    
    from models import User, Customer
    
    try:
        # 获取 admin 用户
        admin = User.query.filter_by(username='admin').first()
        if admin:
            # 更新现有客户，设置创建者和负责人
            customers = Customer.query.all()
            updated = 0
            for customer in customers:
                if not customer.assigned_to:
                    customer.assigned_to = admin.username
                    updated += 1
                if not customer.created_by:
                    customer.created_by = admin.id
                    updated += 1
            
            db.session.commit()
            print(f"  [+] 更新了 {updated} 个客户的默认负责人")
        
        print("  [OK] 默认数据初始化完成")
        return True
        
    except Exception as e:
        print(f"  [X] 默认数据初始化失败: {e}")
        db.session.rollback()
        return False


def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("数据库迁移 - 权限字段")
        print("=" * 50)
        
        success = True
        success &= migrate_customer_table()
        success &= migrate_opportunity_table()
        success &= init_default_data()
        
        print("\n" + "=" * 50)
        if success:
            print("数据库迁移完成！")
        else:
            print("数据库迁移部分失败，请检查日志")
        print("=" * 50)


if __name__ == '__main__':
    main()
