"""
联系记录API - 使用通用CRUD基类重构
"""
from flask import Blueprint, request
from sqlalchemy import or_, desc
from datetime import datetime, timedelta
from models import Contact, Customer
from utils.api_utils import (
    api_success, api_error,
    DateTimeUtils, PaginationUtils
)
from utils.crud_base import BaseCRUDView
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
contacts_bp = Blueprint('contacts', __name__)


class ContactView(BaseCRUDView):
    """联系记录CRUD视图"""
    
    model_class = Contact
    required_fields = ['customer_id', 'contact_type', 'subject', 'content']
    order_by = '-contact_date'
    soft_delete_field = 'status'
    soft_delete_value = '已删除'
    
    def serialize(self, contact):
        """序列化联系记录"""
        customer = Customer.query.get(contact.customer_id)
        return {
            'id': contact.id,
            'customer_id': contact.customer_id,
            'customer_name': customer.name if customer else '',
            'customer_company': customer.company if customer else '',
            'contact_type': contact.contact_type,
            'subject': contact.subject,
            'content': contact.content,
            'contact_date': DateTimeUtils.format_datetime(contact.contact_date),
            'follow_up_date': DateTimeUtils.format_date(contact.follow_up_date),
            'assigned_to': contact.assigned_to,
            'status': contact.status,
            'created_at': DateTimeUtils.format_datetime(contact.created_at),
        }
    
    def deserialize(self, data, contact):
        """反序列化联系记录"""
        if 'customer_id' in data:
            contact.customer_id = data['customer_id']
        if 'contact_type' in data:
            contact.contact_type = data['contact_type']
        if 'subject' in data:
            contact.subject = data['subject']
        if 'content' in data:
            contact.content = data['content']
        if 'assigned_to' in data:
            contact.assigned_to = data['assigned_to']
        if 'status' in data:
            contact.status = data['status']
        if 'contact_date' in data:
            contact.contact_date = DateTimeUtils.parse_datetime(data['contact_date'])
        if 'follow_up_date' in data:
            contact.follow_up_date = DateTimeUtils.parse_date(data['follow_up_date'])
        return contact
    
    def before_create(self, data):
        """创建前处理 - 设置默认负责人"""
        if not data.get('assigned_to'):
            from flask_jwt_extended import get_jwt_identity
            user = Customer.query.get(int(get_jwt_identity()))
            if user:
                data['assigned_to'] = user.username
        return data
    
    def get_list(self):
        """获取列表 - 自定义筛选和统计"""
        page, per_page = PaginationUtils.get_params(request)
        
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        contact_type = request.args.get('contact_type')
        status = request.args.get('status')
        customer_id = request.args.get('customer_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = self.get_query().join(Customer)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    Customer.name.contains(keyword),
                    Customer.company.contains(keyword),
                    self.model_class.subject.contains(keyword),
                    self.model_class.content.contains(keyword)
                )
            )
        
        # 类型筛选
        if contact_type:
            query = query.filter(self.model_class.contact_type == contact_type)
        
        # 状态筛选
        if status:
            query = query.filter(self.model_class.status == status)
        
        # 客户筛选
        if customer_id:
            query = query.filter(self.model_class.customer_id == customer_id)
        
        # 日期范围筛选
        if start_date:
            query = query.filter(self.model_class.contact_date >= start_date)
        if end_date:
            query = query.filter(self.model_class.contact_date <= end_date)
        
        # 排序
        query = query.order_by(desc(self.model_class.contact_date))
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [self.serialize(obj) for obj in pagination.items]
        
        # 统计数据
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        total = self.get_query().count()
        today_count = self.get_query().filter(
            self.model_class.contact_date >= today_start,
            self.model_class.contact_date < today_end
        ).count()
        pending_count = self.get_query().filter(self.model_class.status == '待处理').count()
        completed_count = self.get_query().filter(self.model_class.status == '已完成').count()
        
        return api_success(data={
            'items': items,
            'pagination': {
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            },
            'stats': {
                'total': total,
                'today': today_count,
                'pending': pending_count,
                'completed': completed_count
            }
        })


# 注册路由
contact_view = ContactView.as_view('contact_view')
contacts_bp.add_url_rule('', defaults={'obj_id': None}, view_func=contact_view, methods=['GET'])
contacts_bp.add_url_rule('', view_func=contact_view, methods=['POST'])
contacts_bp.add_url_rule('/<int:obj_id>', view_func=contact_view, methods=['GET', 'PUT', 'DELETE'])
