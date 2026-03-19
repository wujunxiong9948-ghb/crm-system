"""
生成CRM测试数据脚本
包括：用户、客户、销售机会、订单、联系记录
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from app import create_app
from models import db, User, Customer, Opportunity, Order, OrderItem, Contact, Product
from utils.auth import hash_password

def generate_test_data():
    """生成测试数据"""
    app = create_app()
    
    with app.app_context():
        print("开始生成测试数据...")
        
        # 1. 创建测试用户
        create_test_users()
        
        # 2. 创建客户数据
        create_customers()
        
        # 3. 创建产品数据
        create_products()
        
        # 4. 创建销售机会数据
        create_opportunities()
        
        # 5. 创建订单数据
        create_orders()
        
        # 6. 创建联系记录数据
        create_contacts()
        
        print("\n✅ 测试数据生成完成！")
        print("\n测试账号:")
        print("  - admin / admin123 (管理员)")
        print("  - sales01 / 123456 (销售)")
        print("  - sales02 / 123456 (销售)")

def create_test_users():
    """创建测试用户"""
    print("\n1. 创建测试用户...")
    
    users = [
        {
            'username': 'admin',
            'password': 'admin123',
            'full_name': '系统管理员',
            'email': 'admin@yzcrm.com',
            'role': 'admin',
            'department': '管理部',
            'status': 'active'
        },
        {
            'username': 'sales01',
            'password': '123456',
            'full_name': '张销售',
            'email': 'sales01@yzcrm.com',
            'role': 'sales',
            'department': '销售部',
            'status': 'active'
        },
        {
            'username': 'sales02',
            'password': '123456',
            'full_name': '李销售',
            'email': 'sales02@yzcrm.com',
            'role': 'sales',
            'department': '销售部',
            'status': 'active'
        }
    ]
    
    for user_data in users:
        existing = User.query.filter_by(username=user_data['username']).first()
        if not existing:
            user = User(
                username=user_data['username'],
                password_hash=hash_password(user_data['password']),
                full_name=user_data['full_name'],
                email=user_data['email'],
                role=user_data['role'],
                department=user_data['department'],
                status=user_data['status']
            )
            db.session.add(user)
            print(f"  ✓ 创建用户: {user_data['username']}")
    
    db.session.commit()

def create_customers():
    """创建客户数据"""
    print("\n2. 创建客户数据...")
    
    customers_data = [
        {
            'name': '李经理',
            'company': '华住酒店集团',
            'phone': '13800138001',
            'email': 'li@huazhu.com',
            'address': '上海市浦东新区张江高科技园区',
            'industry': '酒店连锁',
            'customer_type': 'VIP客户',
            'source': '展会',
            'status': '活跃',
            'assigned_to': 'admin',
            'notes': '全国连锁酒店，年采购量约5000万'
        },
        {
            'name': '王总',
            'company': '如家酒店集团',
            'phone': '13900139002',
            'email': 'wang@homeinns.com',
            'address': '北京市朝阳区',
            'industry': '酒店连锁',
            'customer_type': '现有客户',
            'source': '推荐',
            'status': '活跃',
            'assigned_to': 'sales01',
            'notes': '老客户，合作关系良好'
        },
        {
            'name': '陈经理',
            'company': '锦江之星酒店',
            'phone': '13700137003',
            'email': 'chen@jinjiang.com',
            'address': '上海市黄浦区',
            'industry': '酒店连锁',
            'customer_type': '潜在客户',
            'source': '网站',
            'status': '活跃',
            'assigned_to': 'sales01',
            'notes': '正在洽谈中'
        },
        {
            'name': '刘总监',
            'company': '希尔顿酒店管理有限公司',
            'phone': '13600136004',
            'email': 'liu@hilton.com',
            'address': '广州市天河区',
            'industry': '高端酒店',
            'customer_type': '潜在客户',
            'source': '展会',
            'status': '活跃',
            'assigned_to': 'sales02',
            'notes': '高端酒店项目，预算充足'
        },
        {
            'name': '赵经理',
            'company': '七天连锁酒店',
            'phone': '13500135005',
            'email': 'zhao@7daysinn.com',
            'address': '深圳市福田区',
            'industry': '经济型酒店',
            'customer_type': '现有客户',
            'source': '电话',
            'status': '休眠',
            'assigned_to': 'sales02',
            'notes': '需要重新激活'
        }
    ]
    
    for cust_data in customers_data:
        existing = Customer.query.filter_by(phone=cust_data['phone']).first()
        if not existing:
            customer = Customer(**cust_data)
            db.session.add(customer)
            print(f"  ✓ 创建客户: {cust_data['name']} ({cust_data['company']})")
    
    db.session.commit()

def create_products():
    """创建产品数据"""
    print("\n3. 创建产品数据...")
    
    products_data = [
        {
            'code': 'BED-001',
            'name': '标准单人床',
            'category': '床类',
            'specification': '1200*2000mm',
            'unit': '张',
            'price': 2800.00,
            'cost': 1800.00,
            'material': '实木+布艺',
            'stock': 50,
            'status': 'active'
        },
        {
            'code': 'BED-002',
            'name': '豪华双人床',
            'category': '床类',
            'specification': '1800*2000mm',
            'unit': '张',
            'price': 4500.00,
            'cost': 2800.00,
            'material': '实木+真皮',
            'stock': 30,
            'status': 'active'
        },
        {
            'code': 'NS-001',
            'name': '实木床头柜',
            'category': '柜类',
            'specification': '500*400*550mm',
            'unit': '个',
            'price': 680.00,
            'cost': 380.00,
            'material': '橡木',
            'stock': 100,
            'status': 'active'
        },
        {
            'code': 'DESK-001',
            'name': '写字台',
            'category': '桌类',
            'specification': '1200*600*750mm',
            'unit': '张',
            'price': 1200.00,
            'cost': 720.00,
            'material': '实木',
            'stock': 40,
            'status': 'active'
        },
        {
            'code': 'CHAIR-001',
            'name': '办公椅',
            'category': '椅类',
            'specification': '标准',
            'unit': '把',
            'price': 580.00,
            'cost': 320.00,
            'material': '网布+钢架',
            'stock': 80,
            'status': 'active'
        }
    ]
    
    for prod_data in products_data:
        existing = Product.query.filter_by(product_code=prod_data['code']).first()
        if not existing:
            # 将 code 字段映射到 product_code
            prod_data['product_code'] = prod_data.pop('code')
            product = Product(**prod_data)
            db.session.add(product)
            print(f"  ✓ 创建产品: {prod_data['name']}")
    
    db.session.commit()

def create_opportunities():
    """创建销售机会数据"""
    print("\n4. 创建销售机会数据...")
    
    customers = Customer.query.all()
    stages = ['初步接触', '需求分析', '方案报价', '谈判', '成交']
    
    opportunities_data = [
        {
            'name': '华住酒店2026年家具采购项目',
            'hotel_name': '华住旗下全季酒店',
            'project_type': '连锁扩张',
            'hotel_star': '四星',
            'room_count': 200,
            'province': '上海',
            'city': '上海',
            'expected_value': 850000.00,
            'stage': '方案报价',
            'probability': 60,
            'priority': '高',
            'assigned_to': 'sales01',
            'status': '进行中'
        },
        {
            'name': '如家酒店翻新项目',
            'hotel_name': '如家快捷酒店',
            'project_type': '酒店翻新',
            'hotel_star': '经济型',
            'room_count': 120,
            'province': '北京',
            'city': '北京',
            'expected_value': 320000.00,
            'stage': '谈判',
            'probability': 80,
            'priority': '中',
            'assigned_to': 'sales01',
            'status': '进行中'
        },
        {
            'name': '希尔顿新酒店项目',
            'hotel_name': '希尔顿欢朋酒店',
            'project_type': '新建酒店',
            'hotel_star': '五星',
            'room_count': 300,
            'province': '广东',
            'city': '广州',
            'expected_value': 1500000.00,
            'stage': '需求分析',
            'probability': 40,
            'priority': '高',
            'assigned_to': 'sales02',
            'status': '进行中'
        },
        {
            'name': '七天酒店家具更新',
            'hotel_name': '7天连锁酒店',
            'project_type': '酒店翻新',
            'hotel_star': '经济型',
            'room_count': 80,
            'province': '广东',
            'city': '深圳',
            'expected_value': 180000.00,
            'stage': '初步接触',
            'probability': 20,
            'priority': '低',
            'assigned_to': 'sales02',
            'status': '进行中'
        }
    ]
    
    for i, opp_data in enumerate(opportunities_data):
        if i < len(customers):
            opp_data['customer_id'] = customers[i].id
            existing = Opportunity.query.filter_by(name=opp_data['name']).first()
            if not existing:
                opportunity = Opportunity(**opp_data)
                db.session.add(opportunity)
                print(f"  ✓ 创建机会: {opp_data['name']}")
    
    db.session.commit()

def create_orders():
    """创建订单数据"""
    print("\n5. 创建订单数据...")
    
    customers = Customer.query.all()
    
    orders_data = [
        {
            'order_number': 'SO-2026-001',
            'total_amount': 125000.00,
            'status': '已完成',
            'payment_status': '已支付',
            'order_date': datetime.now() - timedelta(days=30),
            'notes': '首批订单，已完成交付'
        },
        {
            'order_number': 'SO-2026-002',
            'total_amount': 86000.00,
            'status': '生产中',
            'payment_status': '部分支付',
            'order_date': datetime.now() - timedelta(days=15),
            'notes': '正在生产，预计下周发货'
        },
        {
            'order_number': 'SO-2026-003',
            'total_amount': 240000.00,
            'status': '待处理',
            'payment_status': '部分支付',
            'order_date': datetime.now() - timedelta(days=5),
            'notes': '大客户订单，需加急处理'
        }
    ]
    
    for i, order_data in enumerate(orders_data):
        if i < len(customers):
            order_data['customer_id'] = customers[i].id
            existing = Order.query.filter_by(order_number=order_data['order_number']).first()
            if not existing:
                order = Order(**order_data)
                db.session.add(order)
                print(f"  ✓ 创建订单: {order_data['order_number']}")
    
    db.session.commit()

def create_contacts():
    """创建联系记录数据"""
    print("\n6. 创建联系记录数据...")
    
    customers = Customer.query.all()
    contact_types = ['电话', '邮件', '拜访', '微信', '展会']
    subjects = [
        '初次接洽，了解需求',
        '发送产品报价',
        '现场拜访洽谈',
        '跟进合同进度',
        '确认交付时间',
        '售后服务回访',
        '新产品推荐',
        '价格协商'
    ]
    
    contents = [
        '与客户进行了深入的沟通，了解了客户的具体需求和预算情况。',
        '已向客户发送详细的产品报价单，等待客户反馈。',
        '前往客户公司进行实地考察，展示了产品样品。',
        '与客户确认了合同条款，预计下周签约。',
        '确认了交付时间表，客户表示满意。',
        '对已交付产品进行回访，客户反馈良好。',
        '向客户推荐了新产品系列，客户表现出浓厚兴趣。',
        '就价格问题进行了深入协商，达成了初步共识。'
    ]
    
    for i in range(20):
        customer = random.choice(customers)
        contact_type = random.choice(contact_types)
        subject = random.choice(subjects)
        content = random.choice(contents)
        
        contact = Contact(
            customer_id=customer.id,
            contact_type=contact_type,
            subject=subject,
            content=content,
            contact_date=datetime.now() - timedelta(days=random.randint(1, 60)),
            assigned_to=random.choice(['sales01', 'sales02']),
            status=random.choice(['已完成', '进行中', '待处理'])
        )
        db.session.add(contact)
    
    db.session.commit()
    print(f"  ✓ 创建联系记录: 20条")

if __name__ == '__main__':
    generate_test_data()
