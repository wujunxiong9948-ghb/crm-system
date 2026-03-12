#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统数据库模型
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import re

db = SQLAlchemy()

class BaseModel(db.Model):
    """基础模型类"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        """将模型转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

class Customer(BaseModel):
    """客户模型"""
    __tablename__ = 'customers'

    name = Column(String(100), nullable=False)
    company = Column(String(200))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    industry = Column(String(100))
    customer_type = Column(String(20), default='潜在客户')  # 潜在客户, 现有客户, VIP客户
    source = Column(String(20), default='其他')  # 展会, 推荐, 网站, 电话, 其他
    status = Column(String(10), default='活跃')  # 活跃, 休眠, 流失
    notes = Column(Text)

    # 关系
    opportunities = relationship('Opportunity', back_populates='customer', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='customer', cascade='all, delete-orphan')
    contacts = relationship('Contact', back_populates='customer', cascade='all, delete-orphan')

    @validates('email')
    def validate_email(self, key, email):
        """验证邮箱格式"""
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('邮箱格式不正确')
        return email

    @validates('phone')
    def validate_phone(self, key, phone):
        """验证手机号格式"""
        if phone and not re.match(r'^1[3-9]\d{9}$', phone):
            raise ValueError('手机号格式不正确')
        return phone

class Opportunity(BaseModel):
    """销售机会模型"""
    __tablename__ = 'opportunities'

    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    product_category = Column(String(100))
    expected_value = Column(Float, default=0.0)
    probability = Column(Integer, default=0)  # 0-100%
    stage = Column(String(20), default='初步接触')  # 初步接触, 需求分析, 方案报价, 谈判, 成交, 丢失
    expected_close_date = Column(Date)
    assigned_to = Column(String(100))
    status = Column(String(10), default='进行中')  # 进行中, 已成交, 已丢失

    # 关系
    customer = relationship('Customer', back_populates='opportunities')
    orders = relationship('Order', back_populates='opportunity', cascade='all, delete-orphan')

    @validates('probability')
    def validate_probability(self, key, probability):
        """验证概率值"""
        if not 0 <= probability <= 100:
            raise ValueError('概率值必须在0-100之间')
        return probability

    @validates('expected_value')
    def validate_expected_value(self, key, value):
        """验证预期价值"""
        if value < 0:
            raise ValueError('预期价值不能为负数')
        return value

class Order(BaseModel):
    """订单模型"""
    __tablename__ = 'orders'

    opportunity_id = Column(Integer, ForeignKey('opportunities.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)
    order_date = Column(Date, default=func.current_date())
    total_amount = Column(Float, default=0.0)
    currency = Column(String(10), default='CNY')
    status = Column(String(20), default='待处理')  # 待处理, 生产中, 已发货, 已完成, 已取消
    payment_status = Column(String(20), default='未支付')  # 未支付, 部分支付, 已支付
    shipping_address = Column(Text)
    notes = Column(Text)

    # 关系
    opportunity = relationship('Opportunity', back_populates='orders')
    customer = relationship('Customer', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

    @validates('total_amount')
    def validate_total_amount(self, key, amount):
        """验证总金额"""
        if amount < 0:
            raise ValueError('总金额不能为负数')
        return amount

class OrderItem(BaseModel):
    """订单明细模型"""
    __tablename__ = 'order_items'

    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_code = Column(String(50))
    product_name = Column(String(200))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    specifications = Column(Text)

    # 关系
    order = relationship('Order', back_populates='items')

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        """验证数量"""
        if quantity <= 0:
            raise ValueError('数量必须大于0')
        return quantity

    @validates('unit_price')
    def validate_unit_price(self, key, price):
        """验证单价"""
        if price < 0:
            raise ValueError('单价不能为负数')
        return price

class Contact(BaseModel):
    """联系记录模型"""
    __tablename__ = 'contacts'

    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    contact_type = Column(String(20), default='电话')  # 电话, 邮件, 拜访, 展会, 微信, 其他
    subject = Column(String(200))
    content = Column(Text)
    contact_date = Column(DateTime, default=func.now())
    follow_up_date = Column(Date)
    assigned_to = Column(String(100))
    status = Column(String(10), default='已完成')  # 待处理, 进行中, 已完成, 已取消

    # 关系
    customer = relationship('Customer', back_populates='contacts')

class Product(BaseModel):
    """产品模型"""
    __tablename__ = 'products'

    item_id = Column(String(50))
    category = Column(String(100))
    product_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    material = Column(String(100))
    moq = Column(Float, default=0.0)  # 最小起订量
    unit_price = Column(Float, default=0.0)
    specifications = Column(Text)
    images = Column(Text)  # JSON数组存储图片路径
    status = Column(String(10), default='可用')  # 可用, 停用, 缺货

    @validates('moq')
    def validate_moq(self, key, moq):
        """验证最小起订量"""
        if moq < 0:
            raise ValueError('最小起订量不能为负数')
        return moq

    @validates('unit_price')
    def validate_unit_price(self, key, price):
        """验证单价"""
        if price < 0:
            raise ValueError('单价不能为负数')
        return price

class Activity(BaseModel):
    """活动提醒模型"""
    __tablename__ = 'activities'

    type = Column(String(10), default='任务')  # 提醒, 通知, 任务
    title = Column(String(200), nullable=False)
    description = Column(Text)
    related_id = Column(Integer)
    related_type = Column(String(20))  # customer, opportunity, order
    due_date = Column(Date)
    priority = Column(String(10), default='中')  # 高, 中, 低
    assigned_to = Column(String(100))
    status = Column(String(10), default='待处理')  # 待处理, 进行中, 已完成, 已取消

class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'

    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    email = Column(String(100))
    role = Column(String(20), default='user')  # admin, manager, sales, user
    status = Column(String(10), default='active')  # active, inactive
    last_login = Column(DateTime)

    @validates('email')
    def validate_email(self, key, email):
        """验证邮箱格式"""
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('邮箱格式不正确')
        return email

    @validates('role')
    def validate_role(self, key, role):
        """验证角色"""
        valid_roles = ['admin', 'manager', 'sales', 'user']
        if role not in valid_roles:
            raise ValueError(f'角色必须是以下之一: {", ".join(valid_roles)}')
        return role

class SystemSetting(BaseModel):
    """系统设置模型"""
    __tablename__ = 'system_settings'

    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Text)
    description = Column(Text)

class NotificationLog(BaseModel):
    """通知日志模型"""
    __tablename__ = 'notification_logs'

    notification_type = Column(String(20), default='system')  # qq, email, sms, system
    title = Column(String(200))
    content = Column(Text)
    recipient = Column(String(200))
    status = Column(String(20), default='pending')  # pending, sent, failed, read
    error_message = Column(Text)
    sent_at = Column(DateTime)

# 创建所有表
def create_tables():
    """创建所有数据库表"""
    db.create_all()
    print("数据库表创建完成")

# 初始化数据库
def init_db():
    """初始化数据库"""
    try:
        from database.init_database import create_database
        create_database()
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise

if __name__ == '__main__':
    # 测试数据库连接和表创建
    from app import app
    with app.app_context():
        create_tables()
        print("✅ 数据库模型测试完成")