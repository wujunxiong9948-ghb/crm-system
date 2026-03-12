#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统数据库初始化脚本
创建所有必要的数据库表结构
"""

import sqlite3
import os
from datetime import datetime

def create_database():
    """创建CRM数据库"""

    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), '..', 'crm.db')

    print(f"正在创建数据库: {db_path}")

    # 连接数据库（如果不存在则创建）
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 启用外键约束
    cursor.execute("PRAGMA foreign_keys = ON")

    # 1. 创建customers表 - 客户信息
    print("创建 customers 表...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        company TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        industry TEXT,
        customer_type TEXT CHECK(customer_type IN ('潜在客户', '现有客户', 'VIP客户')),
        source TEXT CHECK(source IN ('展会', '推荐', '网站', '电话', '其他')),
        status TEXT DEFAULT '活跃' CHECK(status IN ('活跃', '休眠', '流失')),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. 创建opportunities表 - 销售机会
    print("创建 opportunities 表...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        description TEXT,
        product_category TEXT,
        expected_value REAL CHECK(expected_value >= 0),
        probability INTEGER CHECK(probability BETWEEN 0 AND 100),
        stage TEXT CHECK(stage IN ('初步接触', '需求分析', '方案报价', '谈判', '成交', '丢失')),
        expected_close_date DATE,
        assigned_to TEXT,
        status TEXT DEFAULT '进行中' CHECK(status IN ('进行中', '已成交', '已丢失')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. 创建orders表 - 订单管理
    print("创建 orders 表...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opportunity_id INTEGER REFERENCES opportunities(id),
        customer_id INTEGER REFERENCES customers(id),
        order_number TEXT UNIQUE NOT NULL,
        order_date DATE DEFAULT CURRENT_DATE,
        total_amount REAL CHECK(total_amount >= 0),
        currency TEXT DEFAULT 'CNY',
        status TEXT CHECK(status IN ('待处理', '生产中', '已发货', '已完成', '已取消')),
        payment_status TEXT CHECK(payment_status IN ('未支付', '部分支付', '已支付')),
        shipping_address TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 4. 创建order_items表 - 订单明细
    print("创建 order_items 表...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
        product_code TEXT,
        product_name TEXT,
        quantity INTEGER CHECK(quantity > 0),
        unit_price REAL CHECK(unit_price >= 0),
        total_price REAL CHECK(total_price >= 0),
        specifications TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 5. 创建contacts表 - 联系记录
    print("创建 contacts 表...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
        contact_type TEXT CHECK(contact_type IN ('电话', '邮件', '拜访', '展会', '微信', '其他')),
        subject TEXT,
        content TEXT,
        contact_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        follow_up_date DATE,
        assigned_to TEXT,
        status TEXT DEFAULT '已完成' CHECK(status IN ('待处理', '进行中', '已完成', '已取消')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. 创建products表 - 产品目录
    print("创建 products 表...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT,
        category TEXT,
        product_code TEXT UNIQUE,
        description TEXT,
        material TEXT,
        moq REAL CHECK(moq >= 0),
        unit_price REAL CHECK(unit_price >= 0),
        specifications TEXT,
        images TEXT, -- JSON数组存储图片路径
        status TEXT DEFAULT '可用' CHECK(status IN ('可用', '停用', '缺货')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 7. 创建activities表 - 活动提醒
    print("创建 activities 表...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT CHECK(type IN ('提醒', '通知', '任务')),
        title TEXT NOT NULL,
        description TEXT,
        related_id INTEGER,
        related_type TEXT CHECK(related_type IN ('customer', 'opportunity', 'order')),
        due_date DATE,
        priority TEXT CHECK(priority IN ('高', '中', '低')),
        assigned_to TEXT,
        status TEXT DEFAULT '待处理' CHECK(status IN ('待处理', '进行中', '已完成', '已取消')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 8. 创建users表 - 系统用户
    print("创建 users 表...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        email TEXT,
        role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'manager', 'sales', 'user')),
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 9. 创建system_settings表 - 系统设置
    print("创建 system_settings 表...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 10. 创建notification_logs表 - 通知日志
    print("创建 notification_logs 表...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notification_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        notification_type TEXT CHECK(notification_type IN ('qq', 'email', 'sms', 'system')),
        title TEXT,
        content TEXT,
        recipient TEXT,
        status TEXT CHECK(status IN ('pending', 'sent', 'failed', 'read')),
        error_message TEXT,
        sent_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 创建索引以提高查询性能
    print("创建索引...")

    # customers表索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_company ON customers(company)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_customer_type ON customers(customer_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status)")

    # opportunities表索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_customer_id ON opportunities(customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_stage ON opportunities(stage)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_expected_close_date ON opportunities(expected_close_date)")

    # orders表索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date)")

    # contacts表索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_customer_id ON contacts(customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_contact_date ON contacts(contact_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_follow_up_date ON contacts(follow_up_date)")

    # products表索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_product_code ON products(product_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_status ON products(status)")

    # activities表索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_due_date ON activities(due_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_status ON activities(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_priority ON activities(priority)")

    # 插入默认系统设置
    print("插入默认系统设置...")
    default_settings = [
        ('system_name', '酒店家具CRM系统', '系统名称'),
        ('company_name', '源臻酒店家具', '公司名称'),
        ('currency', 'CNY', '默认货币'),
        ('timezone', 'Asia/Shanghai', '时区设置'),
        ('date_format', 'YYYY-MM-DD', '日期格式'),
        ('items_per_page', '20', '每页显示条数'),
        ('notification_enabled', 'true', '启用通知'),
        ('backup_enabled', 'true', '启用备份'),
        ('backup_interval', 'daily', '备份频率'),
    ]

    for key, value, description in default_settings:
        cursor.execute("""
        INSERT OR REPLACE INTO system_settings (setting_key, setting_value, description)
        VALUES (?, ?, ?)
        """, (key, value, description))

    # 插入默认管理员用户（密码：admin123）
    print("插入默认管理员用户...")
    cursor.execute("""
    INSERT OR REPLACE INTO users (username, password_hash, full_name, email, role)
    VALUES (?, ?, ?, ?, ?)
    """, ('admin', 'pbkdf2:sha256:260000$abc123$...', '系统管理员', 'admin@example.com', 'admin'))

    # 插入示例数据（用于测试）
    print("插入示例数据...")

    # 示例客户
    cursor.execute("""
    INSERT OR IGNORE INTO customers (name, company, phone, email, customer_type, source, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('张三', '测试公司', '13800138000', 'zhangsan@example.com', '现有客户', '推荐', '活跃'))

    cursor.execute("""
    INSERT OR IGNORE INTO customers (name, company, phone, email, customer_type, source, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('李四', '示例企业', '13900139000', 'lisi@example.com', '潜在客户', '展会', '活跃'))

    # 示例产品
    cursor.execute("""
    INSERT OR IGNORE INTO products (product_code, category, description, material, moq, unit_price)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ('FURN-001', '床', '豪华大床', '实木', 10, 1500.00))

    cursor.execute("""
    INSERT OR IGNORE INTO products (product_code, category, description, material, moq, unit_price)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ('FURN-002', '沙发', '真皮沙发', '真皮', 5, 3000.00))

    # 提交事务
    conn.commit()

    # 验证表创建
    print("\n验证数据库表创建...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    print(f"已创建 {len(tables)} 个表:")
    for table in tables:
        print(f"  - {table[0]}")

    # 统计记录数
    print("\n各表记录统计:")
    for table in ['customers', 'products', 'users', 'system_settings']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} 条记录")

    # 关闭连接
    conn.close()

    print(f"\n✅ 数据库初始化完成！")
    print(f"数据库文件: {db_path}")
    print(f"默认管理员账号: admin / admin123")
    print(f"系统设置已配置完成")

def backup_existing_database():
    """备份现有数据库（如果存在）"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'crm.db')
    backup_path = os.path.join(os.path.dirname(__file__), '..', f'crm_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')

    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"已备份现有数据库到: {backup_path}")
        return True
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("CRM系统数据库初始化工具")
    print("=" * 60)

    try:
        # 备份现有数据库
        backup_existing_database()

        # 创建新数据库
        create_database()

        print("\n" + "=" * 60)
        print("✅ 数据库初始化成功！")
        print("=" * 60)
        print("\n下一步操作:")
        print("1. 运行后端服务器: python app.py")
        print("2. 访问前端应用: http://localhost:3000")
        print("3. 使用管理员账号登录: admin / admin123")

    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()