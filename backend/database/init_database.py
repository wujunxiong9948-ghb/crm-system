#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""

import os
import sys
from datetime import datetime
from flask_bcrypt import Bcrypt

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User, Customer, Product, SystemSetting
from app import create_app

bcrypt = Bcrypt()

def create_database():
    """创建数据库并初始化数据"""
    app = create_app()

    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建完成")

        # 初始化数据
        init_users()
        init_system_settings()
        init_sample_data()

        print("✅ 数据库初始化完成")

def init_users():
    """初始化用户数据"""
    # 检查是否已有用户
    if User.query.first():
        print("⚠️  用户数据已存在，跳过初始化")
        return

    # 创建管理员用户
    admin_user = User(
        username='admin',
        password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
        full_name='系统管理员',
        email='admin@example.com',
        role='admin',
        status='active'
    )

    # 创建销售用户
    sales_user = User(
        username='sales',
        password_hash=bcrypt.generate_password_hash('sales123').decode('utf-8'),
        full_name='销售专员',
        email='sales@example.com',
        role='sales',
        status='active'
    )

    db.session.add(admin_user)
    db.session.add(sales_user)
    db.session.commit()

    print("✅ 用户数据初始化完成")

def init_system_settings():
    """初始化系统设置"""
    # 检查是否已有设置
    if SystemSetting.query.first():
        print("⚠️  系统设置已存在，跳过初始化")
        return

    settings = [
        SystemSetting(
            setting_key='company_name',
            setting_value='酒店家具CRM系统',
            description='公司名称'
        ),
        SystemSetting(
            setting_key='company_address',
            setting_value='上海市浦东新区',
            description='公司地址'
        ),
        SystemSetting(
            setting_key='company_phone',
            setting_value='400-123-4567',
            description='公司电话'
        ),
        SystemSetting(
            setting_key='default_currency',
            setting_value='CNY',
            description='默认货币'
        ),
        SystemSetting(
            setting_key='notification_enabled',
            setting_value='true',
            description='是否启用通知'
        ),
        SystemSetting(
            setting_key='qq_notification_enabled',
            setting_value='true',
            description='是否启用QQ通知'
        ),
        SystemSetting(
            setting_key='auto_backup_enabled',
            setting_value='true',
            description='是否启用自动备份'
        ),
        SystemSetting(
            setting_key='backup_interval_days',
            setting_value='7',
            description='备份间隔天数'
        )
    ]

    for setting in settings:
        db.session.add(setting)

    db.session.commit()

    print("✅ 系统设置初始化完成")

def init_sample_data():
    """初始化示例数据"""
    # 检查是否已有客户数据
    if Customer.query.first():
        print("⚠️  示例数据已存在，跳过初始化")
        return

    # 创建示例客户
    customers = [
        Customer(
            name='张先生',
            company='上海大酒店',
            phone='13800138001',
            email='zhang@shanghai-hotel.com',
            address='上海市黄浦区南京东路',
            industry='酒店',
            customer_type='VIP客户',
            source='展会',
            status='活跃',
            notes='重要客户，需要重点关注'
        ),
        Customer(
            name='李女士',
            company='北京国际酒店',
            phone='13900139001',
            email='li@beijing-hotel.com',
            address='北京市朝阳区建国门外大街',
            industry='酒店',
            customer_type='现有客户',
            source='推荐',
            status='活跃',
            notes='长期合作客户'
        ),
        Customer(
            name='王总',
            company='广州白云酒店',
            phone='13700137001',
            email='wang@guangzhou-hotel.com',
            address='广州市白云区机场路',
            industry='酒店',
            customer_type='潜在客户',
            source='网站',
            status='活跃',
            notes='新客户，需要跟进'
        )
    ]

    for customer in customers:
        db.session.add(customer)

    # 创建示例产品
    products = [
        Product(
            item_id='FURN-001',
            category='客房家具',
            product_code='BED-KING-001',
            description='豪华大床（2.0米）',
            material='实木+真皮',
            moq=10,
            unit_price=5800.00,
            specifications='尺寸：2000×1800×600mm\n材质：进口实木框架，意大利真皮包覆\n颜色：深棕色、浅棕色可选',
            status='可用'
        ),
        Product(
            item_id='FURN-002',
            category='餐厅家具',
            product_code='TABLE-ROUND-001',
            description='圆形餐桌（1.5米）',
            material='大理石+实木',
            moq=5,
            unit_price=3200.00,
            specifications='尺寸：直径1500mm，高度750mm\n材质：天然大理石桌面，实木桌腿\n颜色：白色大理石，胡桃木色',
            status='可用'
        ),
        Product(
            item_id='FURN-003',
            category='办公家具',
            product_code='CHAIR-EXEC-001',
            description='总裁办公椅',
            material='真皮+铝合金',
            moq=1,
            unit_price=4500.00,
            specifications='尺寸：650×650×1200mm\n材质：意大利进口真皮，铝合金框架\n功能：可调节高度、靠背角度',
            status='可用'
        )
    ]

    for product in products:
        db.session.add(product)

    db.session.commit()

    print("✅ 示例数据初始化完成")

if __name__ == '__main__':
    create_database()