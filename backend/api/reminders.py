"""
提醒系统API
"""
from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging

from models import db, Reminder
from utils.api_utils import api_success, api_error

logger = logging.getLogger(__name__)

reminders_bp = Blueprint('reminders', __name__)

reminders_bp = Blueprint('reminders', __name__)

class ReminderListView(MethodView):
    """提醒列表视图"""
    decorators = [jwt_required()]
    
    def get(self):
        """获取提醒列表"""
        try:
            user_id = get_jwt_identity()
            
            # 筛选参数
            status = request.args.get('status', 'pending')
            reminder_type = request.args.get('type')
            
            query = Reminder.query.filter_by(user_id=user_id)
            
            if status:
                query = query.filter(Reminder.status == status)
            if reminder_type:
                query = query.filter(Reminder.reminder_type == reminder_type)
            
            # 按提醒时间排序
            reminders = query.order_by(Reminder.remind_at.asc()).all()
            
            return api_success(data={
                'items': [r.to_dict() for r in reminders],
                'total': len(reminders)
            })
        except Exception as e:
            logger.error(f"获取提醒列表失败: {e}")
            return api_error(message='获取提醒列表失败', code=500)
    
    def post(self):
        """创建提醒"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            reminder = Reminder(
                user_id=user_id,
                reminder_type=data.get('reminder_type'),
                related_type=data.get('related_type'),
                related_id=data.get('related_id'),
                title=data.get('title'),
                content=data.get('content'),
                remind_at=datetime.fromisoformat(data.get('remind_at')),
                status='pending'
            )
            
            db.session.add(reminder)
            db.session.commit()
            
            return api_success(data=reminder.to_dict(), message='提醒创建成功')
        except Exception as e:
            logger.error(f"创建提醒失败: {e}")
            db.session.rollback()
            return api_error(message='创建提醒失败', code=500)

class ReminderDetailView(MethodView):
    """提醒详情视图"""
    decorators = [jwt_required()]
    
    def put(self, reminder_id):
        """更新提醒"""
        try:
            user_id = get_jwt_identity()
            reminder = Reminder.query.filter_by(id=reminder_id, user_id=user_id).first()
            
            if not reminder:
                return api_error(message='提醒不存在', code=404)
            
            data = request.get_json()
            
            if 'status' in data:
                reminder.status = data['status']
            if 'remind_at' in data:
                reminder.remind_at = datetime.fromisoformat(data['remind_at'])
            if 'title' in data:
                reminder.title = data['title']
            if 'content' in data:
                reminder.content = data['content']
            
            db.session.commit()
            return api_success(data=reminder.to_dict(), message='提醒更新成功')
        except Exception as e:
            logger.error(f"更新提醒失败: {e}")
            db.session.rollback()
            return api_error(message='更新提醒失败', code=500)
    
    def delete(self, reminder_id):
        """删除提醒"""
        try:
            user_id = get_jwt_identity()
            reminder = Reminder.query.filter_by(id=reminder_id, user_id=user_id).first()
            
            if not reminder:
                return api_error(message='提醒不存在', code=404)
            
            db.session.delete(reminder)
            db.session.commit()
            
            return api_success(message='提醒删除成功')
        except Exception as e:
            logger.error(f"删除提醒失败: {e}")
            db.session.rollback()
            return api_error(message='删除提醒失败', code=500)

class ReminderStatsView(MethodView):
    """提醒统计视图"""
    decorators = [jwt_required()]
    
    def get(self):
        """获取提醒统计"""
        try:
            user_id = get_jwt_identity()
            
            # 待处理提醒数
            pending_count = Reminder.query.filter_by(
                user_id=user_id, status='pending'
            ).count()
            
            # 今日到期提醒
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            today_count = Reminder.query.filter(
                Reminder.user_id == user_id,
                Reminder.status == 'pending',
                Reminder.remind_at >= today,
                Reminder.remind_at < tomorrow
            ).count()
            
            # 已逾期提醒
            overdue_count = Reminder.query.filter(
                Reminder.user_id == user_id,
                Reminder.status == 'pending',
                Reminder.remind_at < datetime.now()
            ).count()
            
            return api_success(data={
                'pending': pending_count,
                'today': today_count,
                'overdue': overdue_count
            })
        except Exception as e:
            logger.error(f"获取提醒统计失败: {e}")
            return api_error(message='获取统计失败', code=500)

# 注册路由
reminders_bp.add_url_rule('/', view_func=ReminderListView.as_view('reminder_list'))
reminders_bp.add_url_rule('/stats', view_func=ReminderStatsView.as_view('reminder_stats'))
reminders_bp.add_url_rule('/<int:reminder_id>', view_func=ReminderDetailView.as_view('reminder_detail'))
