"""
数据库模型优化 - 解决数据冗余和字段定义问题
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class BaseModel(db.Model):
    """基础模型类 - 所有模型继承"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result


class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    # 基本信息
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    
    # 角色和部门
    role = db.Column(db.String(20), default='user', nullable=False, index=True)
    department = db.Column(db.String(50))
    position = db.Column(db.String(50))
    
    # 状态
    status = db.Column(db.String(20), default='active', nullable=False, index=True)
    last_login = db.Column(db.DateTime)
    
    # 关联
    customers = db.relationship('Customer', backref='assigned_user', lazy='dynamic',
                                foreign_keys='Customer.assigned_to_id')
    opportunities = db.relationship('Opportunity', backref='assigned_user', lazy='dynamic',
                                   foreign_keys='Opportunity.assigned_to_id')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        data = super().to_dict()
        data.pop('password_hash', None)  # 不返回密码
        return data


class Customer(BaseModel):
    """客户模型 - 优化后"""
    __tablename__ = 'customers'
    
    # 基本信息
    name = db.Column(db.String(100), nullable=False, index=True)
    company = db.Column(db.String(200), index=True)
    phone = db.Column(db.String(20), index=True)
    email = db.Column(db.String(100), index=True)
    address = db.Column(db.Text)  # 改为Text类型
    
    # 分类信息
    industry = db.Column(db.String(50), index=True)
    customer_type = db.Column(db.String(20), default='潜在客户', nullable=False, index=True)
    source = db.Column(db.String(50))
    
    # 状态
    status = db.Column(db.String(20), default='活跃', nullable=False, index=True)
    
    # 负责人 - 使用外键关联
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    # 备注 - 使用Text类型
    notes = db.Column(db.Text)
    
    # 关联
    opportunities = db.relationship('Opportunity', backref='customer', lazy='dynamic',
                                   cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='customer', lazy='dynamic',
                            cascade='all, delete-orphan')
    contacts = db.relationship('Contact', backref='customer', lazy='dynamic',
                              cascade='all, delete-orphan')
    
    # 冗余字段（用于列表展示，减少JOIN）
    _opportunity_count = db.Column('opportunity_count', db.Integer, default=0)
    _order_count = db.Column('order_count', db.Integer, default=0)
    _last_contact_date = db.Column('last_contact_date', db.DateTime)
    
    @property
    def opportunity_count(self):
        """销售机会数量"""
        return self.opportunities.count()
    
    @property
    def order_count(self):
        """订单数量"""
        return self.orders.count()
    
    @property
    def assigned_to(self):
        """负责人用户名"""
        return self.assigned_user.username if self.assigned_user else None
    
    def update_stats(self):
        """更新统计字段"""
        self._opportunity_count = self.opportunities.count()
        self._order_count = self.orders.count()
        last_contact = self.contacts.order_by(Contact.contact_date.desc()).first()
        if last_contact:
            self._last_contact_date = last_contact.contact_date


class Opportunity(BaseModel):
    """销售机会模型 - 优化后（移除冗余字段）"""
    __tablename__ = 'opportunities'
    
    # 关联客户 - 外键索引
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False, index=True)
    hotel_name = db.Column(db.String(200), index=True)
    project_type = db.Column(db.String(50), default='新建酒店', nullable=False)
    
    # 酒店信息
    hotel_star = db.Column(db.String(10))
    room_count = db.Column(db.Integer, default=0)
    
    # 地址信息
    province = db.Column(db.String(50))
    city = db.Column(db.String(50), index=True)
    district = db.Column(db.String(50))
    address = db.Column(db.Text)
    
    # 预算信息 - 使用Decimal避免浮点误差
    renovation_budget = db.Column(db.Numeric(15, 2), default=0)
    furniture_budget = db.Column(db.Numeric(15, 2), default=0)
    expected_value = db.Column(db.Numeric(15, 2), default=0)
    
    # 产品数量
    bed_count = db.Column(db.Integer, default=0)
    nightstand_count = db.Column(db.Integer, default=0)
    wardrobe_count = db.Column(db.Integer, default=0)
    desk_count = db.Column(db.Integer, default=0)
    chair_count = db.Column(db.Integer, default=0)
    sofa_count = db.Column(db.Integer, default=0)
    coffee_table_count = db.Column(db.Integer, default=0)
    tv_cabinet_count = db.Column(db.Integer, default=0)
    other_furniture = db.Column(db.Text)
    
    # 销售阶段
    stage = db.Column(db.String(20), default='初步接触', nullable=False, index=True)
    probability = db.Column(db.Integer, default=10)  # 成交概率
    priority = db.Column(db.String(10), default='中', nullable=False)
    
    # 状态
    status = db.Column(db.String(20), default='进行中', nullable=False, index=True)
    
    # 日期 - 统一使用DateTime
    planned_opening_date = db.Column(db.Date)
    expected_close_date = db.Column(db.Date, index=True)
    next_follow_up_date = db.Column(db.Date)
    
    # 负责人
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    # 竞争信息
    competitors = db.Column(db.Text)
    our_advantage = db.Column(db.Text)
    customer_concern = db.Column(db.Text)
    
    # 决策信息
    decision_maker = db.Column(db.String(100))
    decision_process = db.Column(db.Text)
    
    # 描述
    description = db.Column(db.Text)
    
    # 关键联系人 - 使用JSON字段
    key_contacts = db.Column(db.JSON)
    
    # 跟进记录 - 使用关联表，不存JSON
    follow_up_records = db.relationship('OpportunityFollowUp', backref='opportunity', 
                                        lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def customer_name(self):
        """客户名称 - 通过关系获取"""
        return self.customer.name if self.customer else None
    
    @property
    def assigned_to(self):
        """负责人用户名"""
        return self.assigned_user.username if self.assigned_user else None
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data['customer_name'] = self.customer_name
        data['assigned_to'] = self.assigned_to
        return data


class OpportunityFollowUp(BaseModel):
    """销售机会跟进记录 - 新增表"""
    __tablename__ = 'opportunity_follow_ups'
    
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=False, index=True)
    follow_up_date = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.Text, nullable=False)
    stage_before = db.Column(db.String(20))
    stage_after = db.Column(db.String(20))
    created_by = db.Column(db.String(50))


class Order(BaseModel):
    """订单模型 - 优化后（移除冗余字段）"""
    __tablename__ = 'orders'
    
    # 订单编号 - 唯一索引
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # 关联客户
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    
    # 关联销售机会
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), index=True)
    
    # 金额 - 使用Decimal
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    paid_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # 状态
    status = db.Column(db.String(20), default='待处理', nullable=False, index=True)
    payment_status = db.Column(db.String(20), default='未支付', nullable=False, index=True)
    
    # 日期
    order_date = db.Column(db.DateTime, nullable=False, index=True)
    delivery_date = db.Column(db.Date)
    completion_date = db.Column(db.DateTime)
    
    # 备注
    notes = db.Column(db.Text)
    
    # 关联
    items = db.relationship('OrderItem', backref='order', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    @property
    def customer_name(self):
        """客户名称 - 通过关系获取"""
        return self.customer.name if self.customer else None
    
    @property
    def unpaid_amount(self):
        """未付金额"""
        return float(self.total_amount) - float(self.paid_amount)
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data['customer_name'] = self.customer_name
        data['unpaid_amount'] = self.unpaid_amount
        return data


class OrderItem(BaseModel):
    """订单明细模型 - 优化后（添加产品关联）"""
    __tablename__ = 'order_items'
    
    # 关联订单
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    
    # 关联产品 - 添加外键
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), index=True)
    
    # 产品信息（冗余，用于历史记录）
    product_name = db.Column(db.String(200), nullable=False)
    product_code = db.Column(db.String(50))
    specification = db.Column(db.String(200))
    
    # 数量和价格 - 使用Decimal
    quantity = db.Column(db.Numeric(10, 2), default=1)
    unit_price = db.Column(db.Numeric(15, 2), default=0)
    total_price = db.Column(db.Numeric(15, 2), default=0)
    
    # 备注
    notes = db.Column(db.Text)
    
    # 关联
    product = db.relationship('Product', backref='order_items')
    
    def calculate_total(self):
        """计算总价"""
        self.total_price = float(self.quantity) * float(self.unit_price)


class Product(BaseModel):
    """产品模型 - 优化后"""
    __tablename__ = 'products'
    
    # 产品编码
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(50), index=True)
    specification = db.Column(db.String(500))
    unit = db.Column(db.String(20), default='件')
    
    # 价格 - 使用Decimal
    price = db.Column(db.Numeric(15, 2), default=0)
    cost = db.Column(db.Numeric(15, 2), default=0)
    
    # 描述
    description = db.Column(db.Text)
    
    # 属性
    material = db.Column(db.String(100))
    color = db.Column(db.String(50))
    size = db.Column(db.String(100))
    weight = db.Column(db.String(20))
    warranty = db.Column(db.String(50))
    
    # 库存
    stock = db.Column(db.Integer, default=0)
    
    # 状态
    status = db.Column(db.String(20), default='active', nullable=False, index=True)
    
    # 图片 - 使用关联表，不再用逗号分隔
    images = db.relationship('ProductImage', backref='product', lazy='dynamic',
                            cascade='all, delete-orphan')
    
    @property
    def main_image(self):
        """主图"""
        img = self.images.filter_by(is_main=True).first()
        return img.url if img else None
    
    @property
    def image_urls(self):
        """所有图片URL"""
        return [img.url for img in self.images.order_by(ProductImage.sort_order)]
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data['main_image'] = self.main_image
        data['images'] = self.image_urls
        return data


class ProductImage(BaseModel):
    """产品图片 - 新增表"""
    __tablename__ = 'product_images'
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    url = db.Column(db.String(500), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    description = db.Column(db.String(200))


class Contact(BaseModel):
    """联系记录模型 - 优化后"""
    __tablename__ = 'contacts'
    
    # 关联客户
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    
    # 联系信息
    contact_type = db.Column(db.String(20), nullable=False, index=True)  # 电话、邮件、拜访等
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # 改为Text类型
    
    # 日期
    contact_date = db.Column(db.DateTime, nullable=False, index=True)
    follow_up_date = db.Column(db.Date)
    
    # 负责人
    assigned_to = db.Column(db.String(50))
    
    # 状态
    status = db.Column(db.String(20), default='已完成', nullable=False, index=True)
    
    # 关联销售机会
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), index=True)
    
    @property
    def customer_name(self):
        """客户名称"""
        return self.customer.name if self.customer else None


class SystemSetting(BaseModel):
    """系统设置模型"""
    __tablename__ = 'system_settings'
    
    setting_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(20), default='string')  # string, int, float, json, bool
    description = db.Column(db.String(500))
    
    def get_value(self):
        """获取值，根据类型转换"""
        if self.setting_type == 'int':
            return int(self.setting_value) if self.setting_value else 0
        elif self.setting_type == 'float':
            return float(self.setting_value) if self.setting_value else 0.0
        elif self.setting_type == 'json':
            return json.loads(self.setting_value) if self.setting_value else {}
        elif self.setting_type == 'bool':
            return self.setting_value.lower() == 'true' if self.setting_value else False
        return self.setting_value
    
    def set_value(self, value):
        """设置值"""
        if self.setting_type == 'json':
            self.setting_value = json.dumps(value, ensure_ascii=False)
        else:
            self.setting_value = str(value)


class OperationLog(BaseModel):
    """操作日志模型"""
    __tablename__ = 'operation_logs'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    username = db.Column(db.String(50))
    module = db.Column(db.String(50), index=True)  # 模块：customer, order等
    action = db.Column(db.String(50), index=True)  # 操作：create, update等
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data['created_at'] = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        return data


# 数据库初始化函数
def init_database(app):
    """初始化数据库"""
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建默认管理员
        create_default_admin()
        
        # 创建默认系统设置
        create_default_settings()


def create_default_admin():
    """创建默认管理员账号"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            name='管理员',
            email='admin@example.com',
            role='admin',
            status='active'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


def create_default_settings():
    """创建默认系统设置"""
    default_settings = [
        {'key': 'company_name', 'value': '酒店家具有限公司', 'type': 'string'},
        {'key': 'system_title', 'value': 'CRM客户管理系统', 'type': 'string'},
        {'key': 'items_per_page', 'value': '10', 'type': 'int'},
    ]
    
    for setting in default_settings:
        existing = SystemSetting.query.filter_by(setting_key=setting['key']).first()
        if not existing:
            s = SystemSetting(
                setting_key=setting['key'],
                setting_value=setting['value'],
                setting_type=setting['type']
            )
            db.session.add(s)
    
    db.session.commit()
