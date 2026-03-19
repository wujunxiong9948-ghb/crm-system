#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报表模块测试数据生成脚本
生成订单、客户、销售机会等测试数据，用于验证报表统计功能
"""
import sys
import os
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Customer, Order, OrderItem, Opportunity, Product, Contact, User
from flask_bcrypt import Bcrypt

def generate_test_data():
    """生成测试数据"""
    app = create_app()
    bcrypt = Bcrypt(app)
    
    with app.app_context():
        print("=" * 60)
        print("开始生成报表测试数据")
        print("=" * 60)
        
        # 检查是否已有足够数据
        existing_orders = Order.query.count()
        if existing_orders >= 50:
            print(f"✅ 已有 {existing_orders} 条订单数据，跳过生成")
            return
        
        # 1. 确保有测试用户
        create_test_users(bcrypt)
        
        # 2. 生成产品数据
        create_test_products()
        
        # 3. 生成客户数据
        customers = create_test_customers()
        
        # 4. 生成销售机会数据
        opportunities = create_test_opportunities(customers)
        
        # 5. 生成订单数据
        create_test_orders(customers, opportunities)
        
        # 6. 生成联系记录数据
        create_test_contacts(customers)
        
        print("\n" + "=" * 60)
        print("测试数据生成完成！")
        print("=" * 60)
        
        # 统计生成的数据
        stats = {
            'customers': Customer.query.count(),
            'orders': Order.query.count(),
            'opportunities': Opportunity.query.count(),
            'products': Product.query.count(),
            'contacts': Contact.query.count()
        }
        
        print("\n📊 当前数据总量:")
        for key, value in stats.items():
            print(f"  • {key}: {value}")


def create_test_users(bcrypt):
    """创建测试用户"""
    users_data = [
        {'username': 'sales01', 'full_name': '张三', 'role': 'sales'},
        {'username': 'sales02', 'full_name': '李四', 'role': 'sales'},
        {'username': 'sales03', 'full_name': '王五', 'role': 'sales'},
    ]
    
    for user_data in users_data:
        existing = User.query.filter_by(username=user_data['username']).first()
        if not existing:
            user = User(
                username=user_data['username'],
                password_hash=bcrypt.generate_password_hash('sales123').decode('utf-8'),
                full_name=user_data['full_name'],
                role=user_data['role'],
                status='active'
            )
            db.session.add(user)
    
    db.session.commit()
    print("✅ 测试用户创建完成")


def create_test_products():
    """创建测试产品数据"""
    products_data = [
        {'code': 'BED-001', 'name': '标准单人床', 'category': '床类', 'price': 1200},
        {'code': 'BED-002', 'name': '标准双人床', 'category': '床类', 'price': 1800},
        {'code': 'BED-003', 'name': '豪华大床', 'category': '床类', 'price': 3500},
        {'code': 'NS-001', 'name': '简约床头柜', 'category': '床头柜', 'price': 350},
        {'code': 'NS-002', 'name': '实木床头柜', 'category': '床头柜', 'price': 550},
        {'code': 'WR-001', 'name': '双门衣柜', 'category': '衣柜', 'price': 2200},
        {'code': 'WR-002', 'name': '三门衣柜', 'category': '衣柜', 'price': 3200},
        {'code': 'DS-001', 'name': '写字台', 'category': '书桌', 'price': 800},
        {'code': 'DS-002', 'name': '电脑桌', 'category': '书桌', 'price': 650},
        {'code': 'CH-001', 'name': '餐椅', 'category': '椅子', 'price': 280},
        {'code': 'CH-002', 'name': '办公椅', 'category': '椅子', 'price': 450},
        {'code': 'SF-001', 'name': '双人沙发', 'category': '沙发', 'price': 2800},
        {'code': 'SF-002', 'name': '三人沙发', 'category': '沙发', 'price': 3800},
        {'code': 'CT-001', 'name': '茶几', 'category': '茶几', 'price': 580},
        {'code': 'TV-001', 'name': '电视柜', 'category': '电视柜', 'price': 1200},
    ]
    
    for prod_data in products_data:
        existing = Product.query.filter_by(product_code=prod_data['code']).first()
        if not existing:
            product = Product(
                product_code=prod_data['code'],
                item_id=prod_data['code'],
                description=prod_data['name'],
                category=prod_data['category'],
                unit_price=prod_data['price'],
                moq=1,
                status='可用'
            )
            db.session.add(product)
    
    db.session.commit()
    print("✅ 测试产品创建完成")


def create_test_customers():
    """创建测试客户数据"""
    customers_data = [
        {'name': '张经理', 'company': '锦江酒店集团', 'type': '现有客户', 'status': '活跃', 'source': '展会'},
        {'name': '李总', 'company': '如家酒店连锁', 'type': '现有客户', 'status': '活跃', 'source': '推荐'},
        {'name': '王经理', 'company': '华住酒店集团', 'type': 'VIP客户', 'status': '活跃', 'source': '网站'},
        {'name': '赵总', 'company': '格林豪泰酒店', 'type': '现有客户', 'status': '活跃', 'source': '电话'},
        {'name': '刘经理', 'company': '7天连锁酒店', 'type': '潜在客户', 'status': '活跃', 'source': '其他'},
        {'name': '陈总', 'company': '速8酒店中国', 'type': '潜在客户', 'status': '休眠', 'source': '展会'},
        {'name': '杨经理', 'company': '全季酒店', 'type': '现有客户', 'status': '活跃', 'source': '推荐'},
        {'name': '黄总', 'company': '亚朵酒店', 'type': 'VIP客户', 'status': '活跃', 'source': '网站'},
        {'name': '周经理', 'company': '维也纳酒店', 'type': '现有客户', 'status': '活跃', 'source': '电话'},
        {'name': '吴总', 'company': '汉庭酒店', 'type': '潜在客户', 'status': '活跃', 'source': '其他'},
        {'name': '徐经理', 'company': '桔子水晶酒店', 'type': '现有客户', 'status': '流失', 'source': '展会'},
        {'name': '孙总', 'company': '尚客优酒店', 'type': '潜在客户', 'status': '活跃', 'source': '推荐'},
        {'name': '马经理', 'company': '城市便捷酒店', 'type': '现有客户', 'status': '活跃', 'source': '网站'},
        {'name': '朱总', 'company': '麗枫酒店', 'type': 'VIP客户', 'status': '活跃', 'source': '电话'},
        {'name': '胡经理', 'company': '喆啡酒店', 'type': '潜在客户', 'status': '休眠', 'source': '其他'},
    ]
    
    customers = []
    now = datetime.now()
    
    for i, cust_data in enumerate(customers_data):
        existing = Customer.query.filter_by(name=cust_data['name']).first()
        if not existing:
            # 分散创建时间（最近6个月）
            created_at = now - relativedelta(days=random.randint(1, 180))
            
            customer = Customer(
                name=cust_data['name'],
                company=cust_data['company'],
                customer_type=cust_data['type'],
                status=cust_data['status'],
                source=cust_data['source'],
                phone=f'138{random.randint(10000000, 99999999)}',
                email=f"manager{i+1}@example.com",
                industry='酒店行业',
                assigned_to=random.choice(['张三', '李四', '王五']),
                created_at=created_at
            )
            db.session.add(customer)
            db.session.flush()
            customers.append(customer)
        else:
            customers.append(existing)
    
    db.session.commit()
    print(f"✅ 测试客户创建完成（{len(customers)}个）")
    return customers


def create_test_opportunities(customers):
    """创建测试销售机会数据"""
    stages = ['初步接触', '需求分析', '方案报价', '谈判', '成交', '丢失']
    stage_probabilities = {'初步接触': 10, '需求分析': 25, '方案报价': 50, '谈判': 75, '成交': 100, '丢失': 0}
    project_types = ['新建酒店', '酒店翻新', '连锁扩张']
    hotel_stars = ['经济型', '三星', '四星', '五星']
    
    opportunities = []
    now = datetime.now()
    
    for customer in customers:
        # 每个客户1-3个机会
        for _ in range(random.randint(1, 3)):
            stage = random.choice(stages)
            expected_value = random.choice([50, 80, 100, 150, 200, 300, 500])
            
            opportunity = Opportunity(
                customer_id=customer.id,
                name=f"{customer.company}家具采购项目",
                description=f"为{customer.company}提供酒店家具配套方案",
                project_type=random.choice(project_types),
                hotel_star=random.choice(hotel_stars),
                room_count=random.randint(50, 500),
                expected_value=expected_value,
                furniture_budget=expected_value,
                stage=stage,
                probability=stage_probabilities[stage],
                status='已成交' if stage == '成交' else ('已丢失' if stage == '丢失' else '进行中'),
                expected_close_date=(now + relativedelta(days=random.randint(30, 180))).date(),
                assigned_to=customer.assigned_to,
                created_at=now - relativedelta(days=random.randint(1, 120))
            )
            db.session.add(opportunity)
            db.session.flush()
            opportunities.append(opportunity)
    
    db.session.commit()
    print(f"✅ 测试销售机会创建完成（{len(opportunities)}个）")
    return opportunities


def create_test_orders(customers, opportunities):
    """创建测试订单数据"""
    statuses = ['待处理', '生产中', '已发货', '已完成']
    payment_statuses = ['未支付', '部分支付', '已支付']
    
    products = Product.query.all()
    if not products:
        print("❌ 没有产品数据，无法创建订单")
        return
    
    now = datetime.now()
    orders_count = 0
    
    # 生成最近6个月的订单
    for month_offset in range(6):
        month_date = now - relativedelta(months=month_offset)
        
        # 每月5-15个订单
        for _ in range(random.randint(5, 15)):
            customer = random.choice(customers)
            
            # 订单日期在当前月份内随机
            order_date = month_date.replace(day=random.randint(1, 28))
            
            # 创建订单
            order = Order(
                customer_id=customer.id,
                opportunity_id=random.choice([o.id for o in opportunities if o.customer_id == customer.id]) if random.random() > 0.3 else None,
                order_number=f"ORD{order_date.strftime('%Y%m%d')}{random.randint(1000, 9999)}",
                order_date=order_date.date(),
                status=random.choice(statuses),
                payment_status=random.choice(payment_statuses),
                created_at=order_date
            )
            db.session.add(order)
            db.session.flush()
            
            # 创建订单明细（每个订单2-5个产品）
            total_amount = 0
            for _ in range(random.randint(2, 5)):
                product = random.choice(products)
                quantity = random.randint(5, 50)
                unit_price = product.unit_price
                total_price = quantity * unit_price
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_code=product.product_code,
                    product_name=product.description,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                db.session.add(order_item)
                total_amount += total_price
            
            order.total_amount = total_amount
            orders_count += 1
    
    db.session.commit()
    print(f"✅ 测试订单创建完成（{orders_count}个）")


def create_test_contacts(customers):
    """创建测试联系记录数据"""
    contact_types = ['电话', '邮件', '拜访', '展会', '微信', '其他']
    statuses = ['已完成', '进行中', '待处理']
    subjects = [
        '洽谈合作事宜', '产品报价沟通', '参观工厂', '合同细节确认',
        '售后服务跟进', '新项目需求', '付款事宜', '交货期确认',
        '产品推荐', '节日问候'
    ]
    
    now = datetime.now()
    contacts_count = 0
    
    for customer in customers:
        # 每个客户3-8条联系记录
        for _ in range(random.randint(3, 8)):
            contact_date = now - relativedelta(days=random.randint(1, 90))
            
            contact = Contact(
                customer_id=customer.id,
                contact_type=random.choice(contact_types),
                subject=random.choice(subjects),
                content=f"与{customer.name}沟通相关事宜",
                contact_date=contact_date,
                follow_up_date=(contact_date + relativedelta(days=random.randint(3, 14))).date(),
                assigned_to=customer.assigned_to,
                status=random.choice(statuses)
            )
            db.session.add(contact)
            contacts_count += 1
    
    db.session.commit()
    print(f"✅ 测试联系记录创建完成（{contacts_count}条）")


if __name__ == '__main__':
    generate_test_data()
