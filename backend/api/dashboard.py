#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard API - 仪表盘数据接口
基于赫菲斯托斯架构设计实现
"""
from flask import Blueprint, request
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
from models import db, Order, Contact, Customer, Opportunity, User, Reminder, SalesTarget
from utils.api_utils import api_success, api_error
from utils.auth import check_permission, apply_data_scope, get_user_data_scope, Permissions
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/sales-ranking', methods=['GET'])
@jwt_required()
@check_permission(Permissions.REPORT_VIEW)
def get_sales_ranking():
    """销售业绩排行榜"""
    try:
        # 获取参数
        period = request.args.get('period', 'month')  # week/month/quarter/year
        limit = request.args.get('limit', 5, type=int)

        # 计算时间范围
        now = datetime.now()
        if period == 'week':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'quarter':
            quarter = (now.month - 1) // 3
            start_date = now.replace(month=quarter*3+1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return api_error(message='无效的period参数', code=400)

        # 查询订单统计
        query = db.session.query(
            Order.assigned_to,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('order_amount')
        ).filter(
            Order.order_date >= start_date,
            Order.status != '已取消'
        ).group_by(
            Order.assigned_to
        ).order_by(
            desc('order_amount')
        ).limit(limit)

        results = query.all()

        # 构建排行榜数据
        rankings = []
        rank = 1
        for row in results:
            user = User.query.filter_by(username=row.assigned_to).first()
            if user:
                rankings.append({
                    'rank': rank,
                    'user_id': user.id,
                    'user_name': user.full_name or user.username,
                    'avatar': user.avatar,
                    'department': user.department,
                    'order_count': row.order_count or 0,
                    'order_amount': float(row.order_amount) if row.order_amount else 0
                })
                rank += 1

        return api_success(data={
            'period': period,
            'start_date': start_date.isoformat(),
            'rankings': rankings
        })

    except Exception as e:
        logger.error(f"获取销售业绩排行榜失败: {e}")
        return api_error(message='获取排行榜失败', code=500)


@dashboard_bp.route('/followup-ranking', methods=['GET'])
@jwt_required()
@check_permission(Permissions.REPORT_VIEW)
def get_followup_ranking():
    """客户跟进排行榜"""
    try:
        # 获取参数
        period = request.args.get('period', 'month')
        limit = request.args.get('limit', 5, type=int)

        # 计算时间范围
        now = datetime.now()
        if period == 'week':
            start_date = now - timedelta(days=now.weekday())
        elif period == 'month':
            start_date = now.replace(day=1)
        elif period == 'quarter':
            quarter = (now.month - 1) // 3
            start_date = now.replace(month=quarter*3+1, day=1)
        elif period == 'year':
            start_date = now.replace(month=1, day=1)
        else:
            return api_error(message='无效的period参数', code=400)

        # 查询联系记录统计
        query = db.session.query(
            Contact.assigned_to,
            func.count(Contact.id).label('contact_count'),
            func.count(func.distinct(Contact.customer_id)).label('customer_count')
        ).filter(
            Contact.contact_date >= start_date
        ).group_by(
            Contact.assigned_to
        ).order_by(
            desc('contact_count')
        ).limit(limit)

        results = query.all()

        # 构建排行榜数据
        rankings = []
        rank = 1
        for row in results:
            user = User.query.filter_by(username=row.assigned_to).first()
            if user:
                conversion_rate = round((row.customer_count / row.contact_count * 100), 1) if row.contact_count > 0 else 0
                rankings.append({
                    'rank': rank,
                    'user_id': user.id,
                    'user_name': user.full_name or user.username,
                    'avatar': user.avatar,
                    'department': user.department,
                    'contact_count': row.contact_count or 0,
                    'customer_count': row.customer_count or 0,
                    'conversion_rate': conversion_rate
                })
                rank += 1

        return api_success(data={
            'period': period,
            'start_date': start_date.isoformat(),
            'rankings': rankings
        })

    except Exception as e:
        logger.error(f"获取客户跟进排行榜失败: {e}")
        return api_error(message='获取排行榜失败', code=500)


@dashboard_bp.route('/target-completion', methods=['GET'])
@jwt_required()
def get_target_completion():
    """目标完成度"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return api_error(message='用户不存在', code=404)

        # 获取当前月份
        now = datetime.now()
        target_year = now.year
        target_month = now.month

        # 查询月度目标
        target = SalesTarget.query.filter_by(
            user_id=user_id,
            target_type='monthly',
            target_year=target_year,
            target_month=target_month
        ).first()

        target_amount = target.target_amount if target else 500000  # 默认目标50万

        # 计算本月已完成金额
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_amount = db.session.query(
            func.sum(Order.total_amount)
        ).filter(
            Order.assigned_to == user.username,
            Order.order_date >= month_start,
            Order.status != '已取消'
        ).scalar() or 0

        # 计算完成率和剩余
        completion_rate = round((current_amount / target_amount * 100), 1) if target_amount > 0 else 0
        remaining_amount = max(0, target_amount - current_amount)

        # 计算剩余天数
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        remaining_days = (next_month - now).days

        # 获取每日趋势（最近30天）
        daily_trend = []
        for i in range(29, -1, -1):
            date = now - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date.replace(hour=23, minute=59, second=59)

            daily_amount = db.session.query(
                func.sum(Order.total_amount)
            ).filter(
                Order.assigned_to == user.username,
                Order.order_date >= date_start,
                Order.order_date <= date_end,
                Order.status != '已取消'
            ).scalar() or 0

            daily_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'amount': float(daily_amount)
            })

        return api_success(data={
            'target_type': 'monthly',
            'target_year': target_year,
            'target_month': target_month,
            'target_amount': float(target_amount),
            'current_amount': float(current_amount),
            'completion_rate': completion_rate,
            'remaining_amount': float(remaining_amount),
            'remaining_days': remaining_days,
            'trend': daily_trend
        })

    except Exception as e:
        logger.error(f"获取目标完成度失败: {e}")
        return api_error(message='获取目标完成度失败', code=500)


@dashboard_bp.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    """待办聚合"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return api_error(message='用户不存在', code=404)

        # 1. 获取今日提醒
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59)

        reminders = Reminder.query.filter(
            Reminder.user_id == user_id,
            Reminder.remind_at >= today_start,
            Reminder.remind_at <= today_end,
            Reminder.status == 'pending'
        ).order_by(Reminder.remind_at).limit(5).all()

        reminder_items = [{
            'id': r.id,
            'type': 'reminder',
            'title': r.title,
            'content': r.content,
            'related_type': r.related_type,
            'related_id': r.related_id,
            'due_time': r.remind_at.isoformat() if r.remind_at else None,
            'priority': 'high' if r.reminder_type == 'order_expiry' else 'normal'
        } for r in reminders]

        # 2. 获取待跟进客户（7天内未联系）
        seven_days_ago = datetime.now() - timedelta(days=7)
        pending_customers = Customer.query.filter(
            Customer.assigned_to == user.username,
            or_(
                Customer.updated_at < seven_days_ago,
                Customer.updated_at == None
            )
        ).limit(5).all()

        customer_items = [{
            'id': c.id,
            'type': 'customer',
            'title': f'跟进客户: {c.name}',
            'customer_name': c.name,
            'customer_company': c.company,
            'last_contact': c.updated_at.isoformat() if c.updated_at else None,
            'priority': 'normal'
        } for c in pending_customers]

        # 3. 获取待处理订单（待处理状态）
        pending_orders = Order.query.filter(
            Order.assigned_to == user.username,
            Order.status == '待处理'
        ).order_by(Order.created_at.desc()).limit(5).all()

        order_items = [{
            'id': o.id,
            'type': 'order',
            'title': f'处理订单: {o.order_number}',
            'order_number': o.order_number,
            'customer_id': o.customer_id,
            'total_amount': float(o.total_amount) if o.total_amount else 0,
            'created_at': o.created_at.isoformat() if o.created_at else None,
            'priority': 'high'
        } for o in pending_orders]

        total_count = len(reminder_items) + len(customer_items) + len(order_items)

        return api_success(data={
            'total_count': total_count,
            'categories': {
                'reminders': {
                    'count': len(reminder_items),
                    'items': reminder_items
                },
                'pending_contacts': {
                    'count': len(customer_items),
                    'items': customer_items
                },
                'pending_orders': {
                    'count': len(order_items),
                    'items': order_items
                }
            }
        })

    except Exception as e:
        logger.error(f"获取待办聚合失败: {e}")
        return api_error(message='获取待办失败', code=500)
