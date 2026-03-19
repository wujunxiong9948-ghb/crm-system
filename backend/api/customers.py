"""
客户管理API - 使用通用CRUD基类重构
"""
from flask import Blueprint, request
from sqlalchemy import or_, desc
from models import Customer, Contact, User, db
from utils.api_utils import (
    api_success, api_error,
    DateTimeUtils, PaginationUtils
)
from utils.crud_base import BaseCRUDView
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.auth import (
    check_permission,
    log_operation,
    apply_data_scope,
    check_data_ownership,
    get_user_data_scope,
    Permissions
)
import logging

logger = logging.getLogger(__name__)

customers_bp = Blueprint('customers', __name__)


class CustomerView(BaseCRUDView):
    """客户CRUD视图"""
    
    model_class = Customer
    required_fields = ['name']
    order_by = '-created_at'
    soft_delete_field = 'status'
    soft_delete_value = '已删除'
    
    decorators = [jwt_required(), check_permission(Permissions.CUSTOMER_VIEW)]
    
    def get_query(self):
        """获取基础查询 - 应用数据权限"""
        query = super().get_query()
        user_id = get_jwt_identity()
        query = apply_data_scope(query, self.model_class, user_id)
        return query
    
    def serialize(self, customer):
        """序列化客户"""
        return {
            'id': customer.id,
            'name': customer.name,
            'company': customer.company,
            'phone': customer.phone,
            'email': customer.email,
            'address': customer.address,
            'industry': customer.industry,
            'customer_type': customer.customer_type,
            'source': customer.source,
            'status': customer.status,
            'notes': customer.notes,
            'assigned_to': customer.assigned_to,
            'created_at': DateTimeUtils.format_datetime(customer.created_at),
            'updated_at': DateTimeUtils.format_datetime(customer.updated_at),
        }
    
    def deserialize(self, data, customer):
        """反序列化客户"""
        fields = [
            'name', 'company', 'phone', 'email', 'address',
            'industry', 'customer_type', 'source', 'status',
            'notes', 'assigned_to'
        ]
        for field in fields:
            if field in data:
                setattr(customer, field, data[field])
        return customer
    
    def before_create(self, data):
        """创建前处理 - 设置默认负责人"""
        if not data.get('assigned_to'):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user:
                data['assigned_to'] = user.username
        return data
    
    def after_create(self, customer):
        """创建后处理 - 记录日志"""
        log_operation('customer', 'create', f'创建客户: {customer.name}')
    
    def after_update(self, customer):
        """更新后处理 - 记录日志"""
        log_operation('customer', 'update', f'更新客户: {customer.name}')
    
    def get_list(self):
        """获取列表 - 自定义筛选"""
        page, per_page = PaginationUtils.get_params(request)
        
        # 获取查询参数
        search = request.args.get('search', '')
        customer_type = request.args.get('type', '')
        status = request.args.get('status', '')
        assigned_to = request.args.get('assigned_to', '')
        
        query = self.get_query()
        
        # 搜索条件
        if search:
            query = query.filter(
                or_(
                    self.model_class.name.contains(search),
                    self.model_class.company.contains(search),
                    self.model_class.phone.contains(search),
                    self.model_class.email.contains(search)
                )
            )
        
        # 类型筛选
        if customer_type:
            query = query.filter(self.model_class.customer_type == customer_type)
        
        # 状态筛选
        if status:
            query = query.filter(self.model_class.status == status)
        
        # 负责人筛选
        if assigned_to:
            user_id = get_jwt_identity()
            scope = get_user_data_scope(user_id)
            if scope['type'] == 'all' or scope['type'] == 'department':
                query = query.filter(self.model_class.assigned_to == assigned_to)
        
        # 排序和分页
        query = query.order_by(desc(self.model_class.created_at))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [self.serialize(obj) for obj in pagination.items]
        
        return api_success(data={
            'items': items,
            'pagination': {
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        })
    
    def get(self, obj_id=None):
        """获取单个或列表 - 添加权限检查"""
        if obj_id:
            # 获取单个 - 检查数据权限
            obj = self.get_query().get_or_404(obj_id)
            user_id = get_jwt_identity()
            
            if not check_data_ownership(obj, user_id):
                scope = get_user_data_scope(user_id)
                if scope['type'] == 'department':
                    assigned_user = User.query.filter_by(username=obj.assigned_to).first()
                    if not assigned_user or assigned_user.department != scope.get('department'):
                        return api_error(message='无权查看此客户', code=403)
                elif scope['type'] == 'self':
                    return api_error(message='无权查看此客户', code=403)
            
            # 获取关联数据
            result = self.serialize(obj)
            contacts = Contact.query.filter_by(customer_id=obj_id).order_by(desc(Contact.created_at)).limit(10).all()
            result['recent_contacts'] = [c.to_dict() for c in contacts]
            
            return api_success(data=result)
        else:
            return self.get_list()


# 注册路由
customer_view = CustomerView.as_view('customer_view')
customers_bp.add_url_rule('', defaults={'obj_id': None}, view_func=customer_view, methods=['GET'])
customers_bp.add_url_rule('', view_func=customer_view, methods=['POST'])
customers_bp.add_url_rule('/<int:obj_id>', view_func=customer_view, methods=['GET', 'PUT', 'DELETE'])
