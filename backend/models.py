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
    assigned_to = Column(String(100))  # 负责人
    created_by = Column(Integer, ForeignKey('users.id'))  # 创建者

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
    """销售机会模型 - 酒店家具项目专用"""
    __tablename__ = 'opportunities'

    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)

    # 基本信息
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # 酒店项目专用字段
    hotel_name = Column(String(200))  # 酒店名称
    project_type = Column(String(20), default='新建酒店')  # 新建酒店, 酒店翻新, 连锁扩张
    hotel_star = Column(String(10))  # 星级：经济型, 三星, 四星, 五星, 超五星
    room_count = Column(Integer)  # 客房数量

    # 地址信息
    province = Column(String(50))  # 省
    city = Column(String(50))  # 市
    district = Column(String(50))  # 区
    address = Column(Text)  # 详细地址

    # 时间节点
    planned_opening_date = Column(Date)  # 计划开业时间
    expected_close_date = Column(Date)  # 预计成交时间
    next_follow_up_date = Column(Date)  # 下次跟进时间

    # 预算信息（单位：万元）
    renovation_budget = Column(Float, default=0.0)  # 装修翻新预算
    furniture_budget = Column(Float, default=0.0)  # 家具采购预算
    expected_value = Column(Float, default=0.0)  # 预计订单金额

    # 产品数量预估
    bed_count = Column(Integer, default=0)  # 床
    nightstand_count = Column(Integer, default=0)  # 床头柜
    wardrobe_count = Column(Integer, default=0)  # 衣柜
    desk_count = Column(Integer, default=0)  # 书桌
    chair_count = Column(Integer, default=0)  # 椅子
    sofa_count = Column(Integer, default=0)  # 沙发
    coffee_table_count = Column(Integer, default=0)  # 茶几
    tv_cabinet_count = Column(Integer, default=0)  # 电视柜
    other_furniture = Column(Text)  # 其他家具描述

    # 销售信息
    stage = Column(String(20), default='初步接触')  # 初步接触, 需求分析, 方案报价, 谈判, 成交, 丢失
    probability = Column(Integer, default=10)  # 成交概率 0-100%
    priority = Column(String(10), default='中')  # 高, 中, 低
    assigned_to = Column(String(100))  # 负责人
    status = Column(String(10), default='进行中')  # 进行中, 已成交, 已丢失

    # 竞争信息
    competitors = Column(Text)  # 竞争对手
    our_advantage = Column(Text)  # 我司优势
    customer_concern = Column(Text)  # 客户顾虑

    # 决策信息
    decision_maker = Column(String(100))  # 决策人
    decision_process = Column(Text)  # 决策流程
    key_contacts = Column(Text)  # 关键联系人(JSON格式)

    # 跟进记录（JSON格式存储）
    follow_up_records = Column(Text)  # [{date, type, content, result, next_action}]

    # 关系
    customer = relationship('Customer', back_populates='opportunities')
    orders = relationship('Order', back_populates='opportunity', cascade='all, delete-orphan')

    @validates('probability')
    def validate_probability(self, key, probability):
        """验证概率值"""
        if probability is not None and not 0 <= probability <= 100:
            raise ValueError('概率值必须在0-100之间')
        return probability

    @validates('expected_value')
    def validate_expected_value(self, key, value):
        """验证预期价值"""
        if value is not None and value < 0:
            raise ValueError('预期价值不能为负数')
        return value

    @validates('room_count')
    def validate_room_count(self, key, value):
        """验证客房数量"""
        if value is not None and value < 0:
            raise ValueError('客房数量不能为负数')
        return value

    def to_dict(self):
        """将模型转换为字典（包含所有新字段）"""
        result = super().to_dict()

        # 解析JSON字段
        if self.follow_up_records:
            try:
                import json
                result['follow_up_records'] = json.loads(self.follow_up_records)
            except:
                result['follow_up_records'] = []
        else:
            result['follow_up_records'] = []

        if self.key_contacts:
            try:
                import json
                result['key_contacts'] = json.loads(self.key_contacts)
            except:
                result['key_contacts'] = []
        else:
            result['key_contacts'] = []

        return result

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
    assigned_to = Column(String(100))  # 负责人/销售员

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
    phone = Column(String(20))
    avatar = Column(String(500))  # 头像路径
    department = Column(String(100))  # 部门
    position = Column(String(100))  # 职位
    role = Column(String(20), default='user')  # admin, manager, sales, user (保留用于兼容)
    status = Column(String(10), default='active')  # active, inactive
    last_login = Column(DateTime)

    # 个人设置
    theme = Column(String(20), default='light')  # light, dark
    language = Column(String(10), default='zh-CN')
    timezone = Column(String(50), default='Asia/Shanghai')
    date_format = Column(String(20), default='YYYY-MM-DD')

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

class Role(BaseModel):
    """角色模型"""
    __tablename__ = 'roles'

    name = Column(String(50), unique=True, nullable=False)  # 角色名称
    code = Column(String(50), unique=True, nullable=False)  # 角色代码
    description = Column(Text)  # 角色描述
    status = Column(String(10), default='active')  # active, inactive
    is_system = Column(Boolean, default=False)  # 是否系统内置角色

    # 关系
    permissions = relationship('RolePermission', back_populates='role', cascade='all, delete-orphan')
    users = relationship('UserRole', back_populates='role', cascade='all, delete-orphan')

class Permission(BaseModel):
    """权限模型"""
    __tablename__ = 'permissions'

    name = Column(String(100), nullable=False)  # 权限名称
    code = Column(String(100), unique=True, nullable=False)  # 权限代码
    module = Column(String(50), nullable=False)  # 所属模块
    description = Column(Text)
    status = Column(String(10), default='active')

    # 关系
    roles = relationship('RolePermission', back_populates='permission', cascade='all, delete-orphan')

class RolePermission(BaseModel):
    """角色权限关联模型"""
    __tablename__ = 'role_permissions'

    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)

    # 关系
    role = relationship('Role', back_populates='permissions')
    permission = relationship('Permission', back_populates='roles')

class UserRole(BaseModel):
    """用户角色关联模型"""
    __tablename__ = 'user_roles'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)

    # 关系
    user = relationship('User', backref='user_roles')
    role = relationship('Role', back_populates='users')

class OperationLog(BaseModel):
    """操作日志模型"""
    __tablename__ = 'operation_logs'

    user_id = Column(Integer, ForeignKey('users.id'))  # 操作用户
    username = Column(String(50))  # 用户名（冗余存储）
    action = Column(String(50), nullable=False)  # 操作类型：create, update, delete, login, logout, etc.
    module = Column(String(50), nullable=False)  # 操作模块
    description = Column(Text)  # 操作描述
    ip_address = Column(String(50))  # IP地址
    user_agent = Column(Text)  # 浏览器信息
    request_data = Column(Text)  # 请求数据（JSON）
    response_data = Column(Text)  # 响应数据（JSON）
    status = Column(String(20), default='success')  # success, failed
    error_message = Column(Text)  # 错误信息

class CompanyInfo(BaseModel):
    """公司信息模型"""
    __tablename__ = 'company_info'

    name = Column(String(200), nullable=False)  # 公司名称
    short_name = Column(String(100))  # 公司简称
    logo = Column(String(500))  # Logo路径
    address = Column(Text)  # 公司地址
    phone = Column(String(50))  # 联系电话
    fax = Column(String(50))  # 传真
    email = Column(String(100))  # 邮箱
    website = Column(String(200))  # 网站
    business_license = Column(String(100))  # 营业执照号
    tax_number = Column(String(100))  # 税号
    bank_name = Column(String(200))  # 开户银行
    bank_account = Column(String(100))  # 银行账号
    description = Column(Text)  # 公司简介

class Dictionary(BaseModel):
    """业务参数字典模型"""
    __tablename__ = 'dictionaries'

    type = Column(String(50), nullable=False)  # 字典类型：customer_level, opportunity_stage, product_category等
    code = Column(String(50), nullable=False)  # 字典代码
    name = Column(String(100), nullable=False)  # 字典名称
    value = Column(String(200))  # 字典值
    sort_order = Column(Integer, default=0)  # 排序
    description = Column(Text)  # 描述
    status = Column(String(10), default='active')  # active, inactive
    is_system = Column(Boolean, default=False)  # 是否系统内置

    __table_args__ = (
        db.UniqueConstraint('type', 'code', name='uq_dict_type_code'),
    )

class UserNotificationSetting(BaseModel):
    """用户通知设置模型"""
    __tablename__ = 'user_notification_settings'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # 通知类型开关
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    qq_enabled = Column(Boolean, default=True)
    browser_enabled = Column(Boolean, default=True)

    # 各类通知开关
    task_reminder = Column(Boolean, default=True)  # 任务提醒
    opportunity_reminder = Column(Boolean, default=True)  # 机会提醒
    customer_reminder = Column(Boolean, default=True)  # 客户提醒
    system_notice = Column(Boolean, default=True)  # 系统通知
    daily_report = Column(Boolean, default=False)  # 日报
    weekly_report = Column(Boolean, default=False)  # 周报

    # 提醒时间设置
    reminder_time = Column(String(10), default='09:00')  # 每日提醒时间

class Reminder(BaseModel):
    """提醒模型"""
    __tablename__ = 'reminders'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # 提醒类型
    reminder_type = Column(String(50), nullable=False)  # follow_up:跟进提醒, order_expiry:订单到期

    # 关联对象
    related_type = Column(String(50))  # customer, opportunity, order
    related_id = Column(Integer)

    # 提醒内容
    title = Column(String(200), nullable=False)
    content = Column(Text)

    # 提醒时间
    remind_at = Column(DateTime, nullable=False)

    # 状态
    status = Column(String(20), default='pending')  # pending:待提醒, sent:已发送, dismissed:已忽略


class SalesTarget(BaseModel):
    """销售目标模型"""
    __tablename__ = 'sales_targets'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # 目标类型
    target_type = Column(String(20), nullable=False, default='monthly')  # monthly/quarterly/yearly

    # 目标时间
    target_year = Column(Integer, nullable=False)
    target_month = Column(Integer)  # 月度目标时使用 (1-12)
    target_quarter = Column(Integer)  # 季度目标时使用 (1-4)

    # 目标金额
    target_amount = Column(Float, nullable=False, default=0)

    # 备注
    notes = Column(Text)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_type', 'target_year', 'target_month', 'target_quarter', 
                           name='uq_sales_target_period'),
    )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_type': self.target_type,
            'target_year': self.target_year,
            'target_month': self.target_month,
            'target_quarter': self.target_quarter,
            'target_amount': self.target_amount,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

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