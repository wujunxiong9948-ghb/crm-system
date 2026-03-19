#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统测试数据生成脚本
"""

import sys
import os
from datetime import datetime, timedelta
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Customer, Opportunity, Order, OrderItem, Contact, Product, Activity, User
from flask_bcrypt import Bcrypt

def seed_data():
    """生成测试数据"""
    app = create_app()
    bcrypt = Bcrypt()

    with app.app_context():
        print("开始生成测试数据...")

        # 清空现有数据（保留用户）
        print("清空现有数据...")
        Activity.query.delete()
        OrderItem.query.delete()
        Order.query.delete()
        Contact.query.delete()
        Opportunity.query.delete()
        Customer.query.delete()
        Product.query.delete()
        db.session.commit()

        # 1. 创建测试用户
        print("创建测试用户...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                full_name='管理员',
                role='admin',
                department='管理部',
                status='active'
            )
            db.session.add(admin_user)

        sales_user = User.query.filter_by(username='sales01').first()
        if not sales_user:
            sales_user = User(
                username='sales01',
                email='sales01@example.com',
                password_hash=bcrypt.generate_password_hash('sales123').decode('utf-8'),
                full_name='张三',
                role='sales',
                department='销售部',
                status='active'
            )
            db.session.add(sales_user)
        db.session.commit()

        # 2. 创建客户数据
        print("创建客户数据...")
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
                'notes': '全国连锁酒店，年采购量约5000万'
            },
            {
                'name': '王总',
                'company': '如家酒店集团',
                'phone': '13900139002',
                'email': 'wang@homeinns.com',
                'address': '北京市朝阳区建国路88号',
                'industry': '酒店连锁',
                'customer_type': '现有客户',
                'source': '推荐',
                'status': '活跃',
                'notes': '老客户，合作3年，信誉良好'
            },
            {
                'name': '陈经理',
                'company': '锦江之星酒店',
                'phone': '13700137003',
                'email': 'chen@jinjiang.com',
                'address': '上海市黄浦区南京东路100号',
                'industry': '酒店连锁',
                'customer_type': '潜在客户',
                'source': '网站',
                'status': '活跃',
                'notes': '正在洽谈中，有意向采购'
            },
            {
                'name': '刘总监',
                'company': '希尔顿酒店管理有限公司',
                'phone': '13600136004',
                'email': 'liu@hilton.com',
                'address': '广州市天河区珠江新城',
                'industry': '高端酒店',
                'customer_type': '潜在客户',
                'source': '展会',
                'status': '活跃',
                'notes': '五星级酒店项目，预算充足'
            },
            {
                'name': '赵经理',
                'company': '七天连锁酒店',
                'phone': '13500135005',
                'email': 'zhao@7daysinn.com',
                'address': '深圳市南山区科技园',
                'industry': '经济型酒店',
                'customer_type': '现有客户',
                'source': '电话',
                'status': '休眠',
                'notes': '近期无新项目，需跟进'
            }
        ]

        customers = []
        for data in customers_data:
            customer = Customer(**data)
            db.session.add(customer)
            customers.append(customer)
        db.session.commit()

        # 3. 创建销售机会数据
        print("创建销售机会数据...")
        opportunities_data = [
            {
                'customer_id': customers[0].id,
                'name': '华住集团2024年新店家具采购项目',
                'description': '华住集团计划在2024年新开50家酒店，需要采购全套客房家具',
                'hotel_name': '华住旗下全季酒店',
                'project_type': '连锁扩张',
                'hotel_star': '四星',
                'room_count': 2500,
                'province': '上海',
                'city': '上海市',
                'district': '浦东新区',
                'address': '多个地址',
                'planned_opening_date': datetime(2024, 6, 1).date(),
                'expected_close_date': datetime(2024, 4, 15).date(),
                'renovation_budget': 3000.0,
                'furniture_budget': 1500.0,
                'expected_value': 1200.0,
                'bed_count': 2500,
                'nightstand_count': 2500,
                'wardrobe_count': 2500,
                'desk_count': 2500,
                'chair_count': 2500,
                'sofa_count': 500,
                'coffee_table_count': 500,
                'tv_cabinet_count': 2500,
                'stage': '方案报价',
                'probability': 70,
                'priority': '高',
                'assigned_to': '张三',
                'status': '进行中',
                'competitors': '美克美家、宜家',
                'our_advantage': '价格优势，交货期短',
                'customer_concern': '质量稳定性',
                'decision_maker': '李经理',
                'decision_process': '集团采购部审批',
                'key_contacts': json.dumps([{'name': '李经理', 'role': '采购经理', 'phone': '13800138001'}]),
                'follow_up_records': json.dumps([
                    {'date': '2024-03-01', 'type': '电话', 'content': '初步沟通需求', 'result': '有意向', 'next_action': '发送产品资料'},
                    {'date': '2024-03-05', 'type': '拜访', 'content': '现场参观工厂', 'result': '满意', 'next_action': '提供报价'},
                    {'date': '2024-03-10', 'type': '邮件', 'content': '发送详细报价单', 'result': '等待反馈', 'next_action': '跟进反馈'}
                ])
            },
            {
                'customer_id': customers[1].id,
                'name': '如家酒店翻新项目',
                'description': '如家酒店20家门店翻新，更换全部客房家具',
                'hotel_name': '如家快捷酒店',
                'project_type': '酒店翻新',
                'hotel_star': '经济型',
                'room_count': 800,
                'province': '北京',
                'city': '北京市',
                'district': '朝阳区',
                'address': '北京市朝阳区建国路88号',
                'planned_opening_date': datetime(2024, 5, 1).date(),
                'expected_close_date': datetime(2024, 3, 30).date(),
                'renovation_budget': 800.0,
                'furniture_budget': 400.0,
                'expected_value': 350.0,
                'bed_count': 800,
                'nightstand_count': 800,
                'wardrobe_count': 0,
                'desk_count': 800,
                'chair_count': 800,
                'sofa_count': 0,
                'coffee_table_count': 0,
                'tv_cabinet_count': 800,
                'stage': '谈判',
                'probability': 85,
                'priority': '高',
                'assigned_to': '张三',
                'status': '进行中',
                'competitors': '本地家具厂',
                'our_advantage': '老客户关系好，价格优惠',
                'customer_concern': '交货时间',
                'decision_maker': '王总',
                'decision_process': '直接决策',
                'key_contacts': json.dumps([{'name': '王总', 'role': '总经理', 'phone': '13900139002'}]),
                'follow_up_records': json.dumps([
                    {'date': '2024-02-15', 'type': '拜访', 'content': '洽谈翻新项目', 'result': '达成合作意向', 'next_action': '签订合同'},
                    {'date': '2024-02-20', 'type': '电话', 'content': '确认合同细节', 'result': '基本确定', 'next_action': '正式签约'}
                ])
            },
            {
                'customer_id': customers[2].id,
                'name': '锦江之星新店开业项目',
                'description': '锦江之星新开10家门店家具采购',
                'hotel_name': '锦江之星',
                'project_type': '新建酒店',
                'hotel_star': '经济型',
                'room_count': 500,
                'province': '上海',
                'city': '上海市',
                'district': '黄浦区',
                'address': '上海市黄浦区南京东路100号',
                'planned_opening_date': datetime(2024, 8, 1).date(),
                'expected_close_date': datetime(2024, 5, 15).date(),
                'renovation_budget': 500.0,
                'furniture_budget': 250.0,
                'expected_value': 200.0,
                'bed_count': 500,
                'nightstand_count': 500,
                'wardrobe_count': 0,
                'desk_count': 500,
                'chair_count': 500,
                'sofa_count': 0,
                'coffee_table_count': 0,
                'tv_cabinet_count': 500,
                'stage': '需求分析',
                'probability': 40,
                'priority': '中',
                'assigned_to': '张三',
                'status': '进行中',
                'competitors': '未知',
                'our_advantage': '品牌知名度高',
                'customer_concern': '价格',
                'decision_maker': '陈经理',
                'decision_process': '部门审批',
                'key_contacts': json.dumps([{'name': '陈经理', 'role': '采购经理', 'phone': '13700137003'}]),
                'follow_up_records': json.dumps([
                    {'date': '2024-03-08', 'type': '电话', 'content': '初次联系', 'result': '有兴趣', 'next_action': '发送资料'}
                ])
            },
            {
                'customer_id': customers[3].id,
                'name': '希尔顿五星级酒店项目',
                'description': '希尔顿新开五星级酒店全套家具定制',
                'hotel_name': '希尔顿酒店',
                'project_type': '新建酒店',
                'hotel_star': '五星',
                'room_count': 300,
                'province': '广东',
                'city': '广州市',
                'district': '天河区',
                'address': '广州市天河区珠江新城',
                'planned_opening_date': datetime(2024, 12, 1).date(),
                'expected_close_date': datetime(2024, 8, 30).date(),
                'renovation_budget': 5000.0,
                'furniture_budget': 2000.0,
                'expected_value': 1800.0,
                'bed_count': 300,
                'nightstand_count': 300,
                'wardrobe_count': 300,
                'desk_count': 300,
                'chair_count': 600,
                'sofa_count': 300,
                'coffee_table_count': 300,
                'tv_cabinet_count': 300,
                'stage': '初步接触',
                'probability': 20,
                'priority': '高',
                'assigned_to': '张三',
                'status': '进行中',
                'competitors': '国际知名品牌',
                'our_advantage': '定制化能力强',
                'customer_concern': '品牌档次',
                'decision_maker': '刘总监',
                'decision_process': '集团总部审批',
                'key_contacts': json.dumps([{'name': '刘总监', 'role': '项目总监', 'phone': '13600136004'}]),
                'follow_up_records': json.dumps([
                    {'date': '2024-03-12', 'type': '展会', 'content': '展会现场洽谈', 'result': '留下联系方式', 'next_action': '电话跟进'}
                ])
            }
        ]

        opportunities = []
        for data in opportunities_data:
            opp = Opportunity(**data)
            db.session.add(opp)
            opportunities.append(opp)
        db.session.commit()

        # 4. 创建订单数据
        print("创建订单数据...")
        orders_data = [
            {
                'customer_id': customers[1].id,
                'opportunity_id': opportunities[1].id,
                'order_number': 'ORD-202403-001',
                'order_date': datetime(2024, 3, 1).date(),
                'total_amount': 350000.0,
                'currency': 'CNY',
                'status': '生产中',
                'payment_status': '部分支付',
                'shipping_address': '北京市朝阳区建国路88号',
                'notes': '如家酒店翻新项目订单'
            },
            {
                'customer_id': customers[0].id,
                'opportunity_id': opportunities[0].id,
                'order_number': 'ORD-202402-001',
                'order_date': datetime(2024, 2, 15).date(),
                'total_amount': 500000.0,
                'currency': 'CNY',
                'status': '已完成',
                'payment_status': '已支付',
                'shipping_address': '上海市浦东新区张江高科技园区',
                'notes': '华住集团首批试点订单'
            }
        ]

        orders = []
        for data in orders_data:
            order = Order(**data)
            db.session.add(order)
            orders.append(order)
        db.session.commit()

        # 5. 创建订单明细
        print("创建订单明细...")
        order_items_data = [
            # 订单1的明细
            {'order_id': orders[0].id, 'product_code': 'BED-001', 'product_name': '标准双人床', 'quantity': 800, 'unit_price': 280.0, 'total_price': 224000.0, 'specifications': '1.8m×2.0m，实木框架'},
            {'order_id': orders[0].id, 'product_code': 'NS-001', 'product_name': '床头柜', 'quantity': 800, 'unit_price': 120.0, 'total_price': 96000.0, 'specifications': '标准尺寸，带抽屉'},
            {'order_id': orders[0].id, 'product_code': 'DESK-001', 'product_name': '写字台', 'quantity': 800, 'unit_price': 150.0, 'total_price': 120000.0, 'specifications': '带抽屉，简约风格'},
            # 订单2的明细
            {'order_id': orders[1].id, 'product_code': 'BED-002', 'product_name': '豪华大床', 'quantity': 100, 'unit_price': 350.0, 'total_price': 350000.0, 'specifications': '2.0m×2.2m，真皮软包'},
        ]

        for data in order_items_data:
            item = OrderItem(**data)
            db.session.add(item)
        db.session.commit()

        # 6. 创建产品数据
        print("创建产品数据...")
        products_data = [
            {
                'item_id': 'ITEM-001',
                'category': '客房家具',
                'product_code': 'BED-001',
                'description': '标准双人床，适用于经济型酒店',
                'material': '实木框架+板材',
                'moq': 50.0,
                'unit_price': 280.0,
                'specifications': '1.8m×2.0m×1.1m，床板厚度15mm',
                'images': json.dumps(['/images/bed-001-1.jpg', '/images/bed-001-2.jpg']),
                'status': '可用'
            },
            {
                'item_id': 'ITEM-002',
                'category': '客房家具',
                'product_code': 'BED-002',
                'description': '豪华大床，适用于中高端酒店',
                'material': '实木框架+真皮软包',
                'moq': 20.0,
                'unit_price': 350.0,
                'specifications': '2.0m×2.2m×1.2m，床头软包',
                'images': json.dumps(['/images/bed-002-1.jpg']),
                'status': '可用'
            },
            {
                'item_id': 'ITEM-003',
                'category': '客房家具',
                'product_code': 'NS-001',
                'description': '标准床头柜',
                'material': '板材',
                'moq': 100.0,
                'unit_price': 120.0,
                'specifications': '0.5m×0.4m×0.6m，双抽屉',
                'images': json.dumps(['/images/ns-001-1.jpg']),
                'status': '可用'
            },
            {
                'item_id': 'ITEM-004',
                'category': '客房家具',
                'product_code': 'DESK-001',
                'description': '写字台',
                'material': '板材',
                'moq': 50.0,
                'unit_price': 150.0,
                'specifications': '1.2m×0.6m×0.75m，带抽屉',
                'images': json.dumps(['/images/desk-001-1.jpg']),
                'status': '可用'
            },
            {
                'item_id': 'ITEM-005',
                'category': '客房家具',
                'product_code': 'CHAIR-001',
                'description': '写字椅',
                'material': '实木+布艺',
                'moq': 50.0,
                'unit_price': 80.0,
                'specifications': '标准尺寸，软包坐垫',
                'images': json.dumps(['/images/chair-001-1.jpg']),
                'status': '可用'
            },
            {
                'item_id': 'ITEM-006',
                'category': '客房家具',
                'product_code': 'WARDROBE-001',
                'description': '衣柜',
                'material': '板材',
                'moq': 30.0,
                'unit_price': 450.0,
                'specifications': '2.0m×0.6m×2.2m，推拉门',
                'images': json.dumps(['/images/wardrobe-001-1.jpg']),
                'status': '可用'
            },
            {
                'item_id': 'ITEM-007',
                'category': '客厅家具',
                'product_code': 'SOFA-001',
                'description': '双人沙发',
                'material': '实木框架+真皮',
                'moq': 10.0,
                'unit_price': 1200.0,
                'specifications': '1.8m×0.9m×0.85m',
                'images': json.dumps(['/images/sofa-001-1.jpg']),
                'status': '可用'
            },
            {
                'item_id': 'ITEM-008',
                'category': '客厅家具',
                'product_code': 'CT-001',
                'description': '茶几',
                'material': '钢化玻璃+金属',
                'moq': 20.0,
                'unit_price': 280.0,
                'specifications': '1.0m×0.6m×0.45m',
                'images': json.dumps(['/images/ct-001-1.jpg']),
                'status': '可用'
            }
        ]

        for data in products_data:
            product = Product(**data)
            db.session.add(product)
        db.session.commit()

        # 7. 创建联系记录
        print("创建联系记录...")
        contacts_data = [
            {
                'customer_id': customers[0].id,
                'contact_type': '电话',
                'subject': '项目需求沟通',
                'content': '与李经理沟通华住集团2024年采购计划，对方表示有50家新店需要家具',
                'contact_date': datetime(2024, 3, 1, 10, 30),
                'follow_up_date': datetime(2024, 3, 5).date(),
                'assigned_to': '张三',
                'status': '已完成'
            },
            {
                'customer_id': customers[0].id,
                'contact_type': '拜访',
                'subject': '工厂参观',
                'content': '邀请李经理参观工厂生产线，展示产品质量和生产能力',
                'contact_date': datetime(2024, 3, 5, 14, 0),
                'follow_up_date': datetime(2024, 3, 10).date(),
                'assigned_to': '张三',
                'status': '已完成'
            },
            {
                'customer_id': customers[1].id,
                'contact_type': '邮件',
                'subject': '报价单发送',
                'content': '发送如家酒店翻新项目详细报价单',
                'contact_date': datetime(2024, 2, 20, 9, 0),
                'follow_up_date': datetime(2024, 2, 25).date(),
                'assigned_to': '张三',
                'status': '已完成'
            },
            {
                'customer_id': customers[2].id,
                'contact_type': '微信',
                'subject': '初次联系',
                'content': '通过微信添加陈经理，介绍公司产品和服务',
                'contact_date': datetime(2024, 3, 8, 16, 0),
                'follow_up_date': datetime(2024, 3, 12).date(),
                'assigned_to': '张三',
                'status': '进行中'
            }
        ]

        for data in contacts_data:
            contact = Contact(**data)
            db.session.add(contact)
        db.session.commit()

        # 8. 创建活动提醒
        print("创建活动提醒...")
        activities_data = [
            {
                'type': '任务',
                'title': '跟进华住集团报价反馈',
                'description': '联系李经理确认报价单反馈情况',
                'related_id': opportunities[0].id,
                'related_type': 'opportunity',
                'due_date': datetime(2024, 3, 15).date(),
                'priority': '高',
                'assigned_to': '张三',
                'status': '待处理'
            },
            {
                'type': '提醒',
                'title': '如家合同到期提醒',
                'description': '如家酒店翻新项目合同即将到期，需跟进签约',
                'related_id': orders[0].id,
                'related_type': 'order',
                'due_date': datetime(2024, 3, 20).date(),
                'priority': '高',
                'assigned_to': '张三',
                'status': '待处理'
            },
            {
                'type': '任务',
                'title': '希尔顿项目资料准备',
                'description': '准备希尔顿五星级酒店项目的产品资料和案例',
                'related_id': opportunities[3].id,
                'related_type': 'opportunity',
                'due_date': datetime(2024, 3, 18).date(),
                'priority': '中',
                'assigned_to': '张三',
                'status': '进行中'
            },
            {
                'type': '通知',
                'title': '季度销售会议',
                'description': '参加公司季度销售总结会议',
                'due_date': datetime(2024, 3, 25).date(),
                'priority': '中',
                'assigned_to': '张三',
                'status': '待处理'
            }
        ]

        for data in activities_data:
            activity = Activity(**data)
            db.session.add(activity)
        db.session.commit()

        print("\n测试数据生成完成！")
        print(f"- 用户: {User.query.count()} 个")
        print(f"- 客户: {Customer.query.count()} 个")
        print(f"- 销售机会: {Opportunity.query.count()} 个")
        print(f"- 订单: {Order.query.count()} 个")
        print(f"- 订单明细: {OrderItem.query.count()} 条")
        print(f"- 产品: {Product.query.count()} 个")
        print(f"- 联系记录: {Contact.query.count()} 条")
        print(f"- 活动提醒: {Activity.query.count()} 个")

if __name__ == '__main__':
    seed_data()
