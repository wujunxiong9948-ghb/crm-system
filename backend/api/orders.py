"""
订单管理API - 使用通用CRUD基类重构
"""
from flask import Blueprint, request
from sqlalchemy import or_, desc, func
from datetime import datetime, timedelta
from models import Order, OrderItem, Customer, Product, User, db
from utils.api_utils import (
    api_success, api_error,
    DateTimeUtils, PaginationUtils
)
from utils.crud_base import BaseCRUDView
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.auth import check_permission, log_operation, Permissions
import logging

logger = logging.getLogger(__name__)

orders_bp = Blueprint('orders', __name__)


class OrderView(BaseCRUDView):
    """订单CRUD视图"""
    
    model_class = Order
    required_fields = ['customer_id', 'order_number']
    order_by = '-order_date'
    
    decorators = [jwt_required(), check_permission(Permissions.ORDER_VIEW)]
    
    def serialize(self, order):
        """序列化订单"""
        customer = Customer.query.get(order.customer_id)
        return {
            'id': order.id,
            'order_number': order.order_number,
            'customer_id': order.customer_id,
            'customer_name': customer.name if customer else '',
            'customer_company': customer.company if customer else '',
            'total_amount': order.total_amount,
            'status': order.status,
            'payment_status': order.payment_status,
            'order_date': DateTimeUtils.format_datetime(order.order_date),
            'delivery_date': DateTimeUtils.format_date(order.delivery_date),
            'notes': order.notes,
            'created_at': DateTimeUtils.format_datetime(order.created_at),
        }
    
    def deserialize(self, data, order):
        """反序列化订单"""
        fields = [
            'customer_id', 'order_number', 'total_amount',
            'status', 'payment_status', 'notes'
        ]
        for field in fields:
            if field in data:
                setattr(order, field, data[field])
        
        # 日期字段特殊处理
        if 'order_date' in data:
            order.order_date = DateTimeUtils.parse_datetime(data['order_date'])
        if 'delivery_date' in data:
            order.delivery_date = DateTimeUtils.parse_date(data['delivery_date'])
        
        return order
    
    def before_create(self, data):
        """创建前处理"""
        if not data.get('order_date'):
            data['order_date'] = datetime.now().isoformat()
        return data
    
    def after_create(self, order):
        """创建后处理 - 创建订单明细"""
        log_operation('order', 'create', f'创建订单: {order.order_number}')
    
    def get_list(self):
        """获取列表 - 自定义筛选"""
        page, per_page = PaginationUtils.get_params(request)
        
        # 查询参数
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        payment_status = request.args.get('payment_status', '')
        customer_id = request.args.get('customer_id', type=int)
        
        query = self.get_query().join(Customer)
        
        # 搜索条件
        if search:
            query = query.filter(
                or_(
                    self.model_class.order_number.contains(search),
                    Customer.name.contains(search),
                    Customer.company.contains(search)
                )
            )
        
        # 状态筛选
        if status:
            query = query.filter(self.model_class.status == status)
        if payment_status:
            query = query.filter(self.model_class.payment_status == payment_status)
        if customer_id:
            query = query.filter(self.model_class.customer_id == customer_id)
        
        # 排序和分页
        query = query.order_by(desc(self.model_class.order_date))
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
        """获取单个或列表"""
        if obj_id:
            obj = self.get_query().get_or_404(obj_id)
            result = self.serialize(obj)
            
            # 获取订单明细
            items = OrderItem.query.filter_by(order_id=obj_id).all()
            result['items'] = [{
                'id': item.id,
                'product_id': item.product_id,
                'product_name': Product.query.get(item.product_id).name if item.product_id else '',
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price
            } for item in items]
            
            return api_success(data=result)
        else:
            return self.get_list()


# 订单统计API
@orders_bp.route('/stats', methods=['GET'])
@jwt_required()
@check_permission(Permissions.ORDER_VIEW)
def get_order_stats():
    """获取订单统计"""
    try:
        # 总订单数
        total_count = Order.query.count()
        
        # 本月订单
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        month_count = Order.query.filter(Order.order_date >= month_start).count()
        
        # 待处理订单
        pending_count = Order.query.filter(Order.status == '待处理').count()
        
        # 本月金额
        month_amount = db.session.query(func.sum(Order.total_amount)).filter(
            Order.order_date >= month_start
        ).scalar() or 0
        
        return api_success(data={
            'total_count': total_count,
            'month_count': month_count,
            'pending_count': pending_count,
            'month_amount': month_amount
        })
    except Exception as e:
        logger.error(f"获取订单统计失败: {e}")
        return api_error(message='获取统计失败', code=500)


# 注册路由
order_view = OrderView.as_view('order_view')
orders_bp.add_url_rule('', defaults={'obj_id': None}, view_func=order_view, methods=['GET'])
orders_bp.add_url_rule('', view_func=order_view, methods=['POST'])
orders_bp.add_url_rule('/<int:obj_id>', view_func=order_view, methods=['GET', 'PUT', 'DELETE'])
