"""
产品管理API - 使用通用CRUD基类重构
"""
from flask import Blueprint, request
from sqlalchemy import or_, desc
from models import Product, User, db
from utils.api_utils import (
    api_success, api_error,
    DateTimeUtils, PaginationUtils
)
from utils.crud_base import BaseCRUDView
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.auth import check_permission, log_operation, Permissions
import logging

logger = logging.getLogger(__name__)

products_bp = Blueprint('products', __name__)


class ProductView(BaseCRUDView):
    """产品CRUD视图"""
    
    model_class = Product
    required_fields = ['name', 'code']
    order_by = '-created_at'
    soft_delete_field = 'status'
    soft_delete_value = '已删除'
    
    decorators = [jwt_required(), check_permission(Permissions.PRODUCT_VIEW)]
    
    def serialize(self, product):
        """序列化产品"""
        return {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'category': product.category,
            'specification': product.specification,
            'unit': product.unit,
            'price': product.price,
            'cost': product.cost,
            'description': product.description,
            'material': product.material,
            'color': product.color,
            'size': product.size,
            'weight': product.weight,
            'warranty': product.warranty,
            'stock': product.stock,
            'status': product.status,
            'images': product.images.split(',') if product.images else [],
            'created_at': DateTimeUtils.format_datetime(product.created_at),
            'updated_at': DateTimeUtils.format_datetime(product.updated_at),
        }
    
    def deserialize(self, data, product):
        """反序列化产品"""
        fields = [
            'code', 'name', 'category', 'specification', 'unit',
            'price', 'cost', 'description', 'material', 'color',
            'size', 'weight', 'warranty', 'stock', 'status'
        ]
        for field in fields:
            if field in data:
                setattr(product, field, data[field])
        
        # 图片字段特殊处理
        if 'images' in data:
            if isinstance(data['images'], list):
                product.images = ','.join(data['images'])
            else:
                product.images = data['images']
        
        return product
    
    def after_create(self, product):
        """创建后处理"""
        log_operation('product', 'create', f'创建产品: {product.name}')
    
    def after_update(self, product):
        """更新后处理"""
        log_operation('product', 'update', f'更新产品: {product.name}')
    
    def get_list(self):
        """获取列表 - 自定义筛选"""
        page, per_page = PaginationUtils.get_params(request)
        
        # 查询参数
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        status = request.args.get('status', '')
        
        query = self.get_query()
        
        # 搜索条件
        if search:
            query = query.filter(
                or_(
                    self.model_class.name.contains(search),
                    self.model_class.code.contains(search),
                    self.model_class.category.contains(search)
                )
            )
        
        # 类型筛选
        if category:
            query = query.filter(self.model_class.category == category)
        
        # 状态筛选
        if status:
            query = query.filter(self.model_class.status == status)
        
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


# 产品分类列表API
@products_bp.route('/categories', methods=['GET'])
@jwt_required()
@check_permission(Permissions.PRODUCT_VIEW)
def get_categories():
    """获取产品分类列表"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        return api_success(data={
            'categories': [c[0] for c in categories if c[0]]
        })
    except Exception as e:
        logger.error(f"获取产品分类失败: {e}")
        return api_error(message='获取分类失败', code=500)


# 产品统计API
@products_bp.route('/stats', methods=['GET'])
@jwt_required()
@check_permission(Permissions.PRODUCT_VIEW)
def get_product_stats():
    """获取产品统计"""
    try:
        # 总产品数
        total = Product.query.filter(Product.status != '已删除').count()
        
        # 按分类统计
        categories = db.session.query(
            Product.category,
            db.func.count(Product.id)
        ).filter(Product.status != '已删除').group_by(Product.category).all()
        
        return api_success(data={
            'total': total,
            'by_category': {cat: count for cat, count in categories if cat}
        })
    except Exception as e:
        logger.error(f"获取产品统计失败: {e}")
        return api_error(message='获取统计失败', code=500)


# 注册路由
product_view = ProductView.as_view('product_view')
products_bp.add_url_rule('', defaults={'obj_id': None}, view_func=product_view, methods=['GET'])
products_bp.add_url_rule('', view_func=product_view, methods=['POST'])
products_bp.add_url_rule('/<int:obj_id>', view_func=product_view, methods=['GET', 'PUT', 'DELETE'])
