"""
提醒任务调度 - 自动创建跟进提醒、订单到期提醒
"""
from datetime import datetime, timedelta
from models import db
from models.reminder import Reminder
from models.customer import Customer
from models.opportunity import Opportunity
from models.order import Order
import logging

logger = logging.getLogger(__name__)

def check_follow_up_reminders():
    """检查需要跟进的客户，自动创建提醒"""
    try:
        # 找出最近7天没有联系记录的客户
        from models.contact import Contact
        
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        # 查询活跃客户（7天内无联系）
        customers = db.session.query(Customer).filter(
            Customer.status == '活跃',
            ~db.session.query(Contact).filter(
                Contact.customer_id == Customer.id,
                Contact.contact_date >= seven_days_ago.date()
            ).exists()
        ).all()
        
        for customer in customers:
            # 检查是否已存在待处理的跟进提醒
            existing = Reminder.query.filter_by(
                related_type='customer',
                related_id=customer.id,
                reminder_type='follow_up',
                status='pending'
            ).first()
            
            if not existing:
                # 创建跟进提醒
                reminder = Reminder(
                    user_id=customer.assigned_to_id if hasattr(customer, 'assigned_to_id') else 1,
                    reminder_type='follow_up',
                    related_type='customer',
                    related_id=customer.id,
                    title=f'跟进客户：{customer.name}',
                    content=f'客户 {customer.name} ({customer.company}) 已7天未联系，建议跟进',
                    remind_at=datetime.now() + timedelta(hours=1),  # 1小时后提醒
                    status='pending'
                )
                db.session.add(reminder)
        
        db.session.commit()
        logger.info(f"创建了 {len(customers)} 个跟进提醒")
        
    except Exception as e:
        logger.error(f"检查跟进提醒失败: {e}")
        db.session.rollback()

def check_order_expiry_reminders():
    """检查即将到期的订单，创建提醒"""
    try:
        # 查询30天内到期的质保/服务订单
        thirty_days_later = datetime.now() + timedelta(days=30)
        
        orders = Order.query.filter(
            Order.status == '已完成',
            Order.warranty_end_date <= thirty_days_later.date(),
            Order.warranty_end_date >= datetime.now().date()
        ).all()
        
        for order in orders:
            # 检查是否已存在待处理的到期提醒
            existing = Reminder.query.filter_by(
                related_type='order',
                related_id=order.id,
                reminder_type='order_expiry',
                status='pending'
            ).first()
            
            if not existing:
                days_until = (order.warranty_end_date - datetime.now().date()).days
                
                reminder = Reminder(
                    user_id=order.assigned_to_id if hasattr(order, 'assigned_to_id') else 1,
                    reminder_type='order_expiry',
                    related_type='order',
                    related_id=order.id,
                    title=f'订单即将到期：{order.order_number}',
                    content=f'订单 {order.order_number} 的质保/服务将在{days_until}天后到期，建议联系客户续费或维护',
                    remind_at=datetime.now() + timedelta(days=1),  # 明天提醒
                    status='pending'
                )
                db.session.add(reminder)
        
        db.session.commit()
        logger.info(f"创建了 {len(orders)} 个订单到期提醒")
        
    except Exception as e:
        logger.error(f"检查订单到期提醒失败: {e}")
        db.session.rollback()

def run_reminder_checks():
    """运行所有提醒检查"""
    logger.info("开始运行提醒检查任务...")
    check_follow_up_reminders()
    check_order_expiry_reminders()
    logger.info("提醒检查任务完成")
