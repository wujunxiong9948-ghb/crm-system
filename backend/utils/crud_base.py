"""
通用CRUD视图基类 - 提高代码复用性
"""
from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from sqlalchemy import desc
from models import db
from utils.api_utils import (
    APIResponse, 
    DateTimeUtils, 
    PaginationUtils, 
    ValidationUtils,
    api_success, 
    api_error, 
    api_paginated
)
import logging

logger = logging.getLogger(__name__)


class BaseCRUDView(MethodView):
    """
    通用CRUD视图基类
    
    使用方法:
    1. 继承 BaseCRUDView
    2. 设置 model_class 属性
    3. 设置 required_fields 属性
    4. 重写 serialize 方法
    5. (可选)重写 before_create/before_update 方法
    """
    
    # 必须设置的属性
    model_class = None  # SQLAlchemy模型类
    
    # 可选设置
    required_fields = []  # 创建时必填字段
    order_by = '-created_at'  # 默认排序
    soft_delete_field = 'status'  # 软删除字段名
    soft_delete_value = '已删除'  # 软删除值
    
    decorators = [jwt_required()]
    
    def get_query(self):
        """获取基础查询"""
        query = self.model_class.query
        # 软删除过滤
        if hasattr(self.model_class, self.soft_delete_field):
            query = query.filter(
                getattr(self.model_class, self.soft_delete_field) != self.soft_delete_value
            )
        return query
    
    def serialize(self, obj):
        """序列化对象 - 子类必须重写"""
        raise NotImplementedError("子类必须重写 serialize 方法")
    
    def deserialize(self, data, obj=None):
        """反序列化数据到对象 - 子类必须重写"""
        raise NotImplementedError("子类必须重写 deserialize 方法")
    
    def before_create(self, data):
        """创建前处理 - 可重写"""
        return data
    
    def before_update(self, obj, data):
        """更新前处理 - 可重写"""
        return data
    
    def after_create(self, obj):
        """创建后处理 - 可重写"""
        pass
    
    def after_update(self, obj):
        """更新后处理 - 可重写"""
        pass
    
    def get(self, obj_id=None):
        """获取单个或列表"""
        try:
            if obj_id:
                # 获取单个
                obj = self.get_query().get_or_404(obj_id)
                return api_success(data=self.serialize(obj))
            else:
                # 获取列表
                return self.get_list()
        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            return api_error(message='获取数据失败', code=500)
    
    def get_list(self):
        """获取列表 - 可重写以实现自定义筛选"""
        page, per_page = PaginationUtils.get_params(request)
        
        query = self.get_query()
        
        # 应用排序
        if self.order_by.startswith('-'):
            field = getattr(self.model_class, self.order_by[1:])
            query = query.order_by(desc(field))
        else:
            field = getattr(self.model_class, self.order_by)
            query = query.order_by(field)
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [self.serialize(obj) for obj in pagination.items]
        
        return api_paginated(
            items=items,
            total=pagination.total,
            page=page,
            per_page=per_page
        )
    
    def post(self):
        """创建"""
        try:
            data = request.get_json()
            if not data:
                return api_error(message='请求数据不能为空', code=400)
            
            # 验证必填字段
            error_msg = ValidationUtils.required_fields(data, self.required_fields)
            if error_msg:
                return api_error(message=error_msg, code=400)
            
            # 创建前处理
            data = self.before_create(data)
            
            # 创建对象
            obj = self.model_class()
            self.deserialize(data, obj)
            
            db.session.add(obj)
            db.session.commit()
            
            # 创建后处理
            self.after_create(obj)
            
            return api_success(
                data={'id': obj.id},
                message='创建成功',
                code=201
            )
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建失败: {e}")
            return api_error(message='创建失败', code=500)
    
    def put(self, obj_id):
        """更新"""
        try:
            obj = self.get_query().get_or_404(obj_id)
            data = request.get_json()
            
            if not data:
                return api_error(message='请求数据不能为空', code=400)
            
            # 更新前处理
            data = self.before_update(obj, data)
            
            # 更新对象
            self.deserialize(data, obj)
            db.session.commit()
            
            # 更新后处理
            self.after_update(obj)
            
            return api_success(message='更新成功')
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新失败: {e}")
            return api_error(message='更新失败', code=500)
    
    def delete(self, obj_id):
        """删除 (软删除)"""
        try:
            obj = self.get_query().get_or_404(obj_id)
            
            # 如果有软删除字段，执行软删除
            if hasattr(obj, self.soft_delete_field):
                setattr(obj, self.soft_delete_field, self.soft_delete_value)
            else:
                # 否则硬删除
                db.session.delete(obj)
            
            db.session.commit()
            return api_success(message='删除成功')
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除失败: {e}")
            return api_error(message='删除失败', code=500)


class ContactCRUDView(BaseCRUDView):
    """联系记录CRUD示例"""
    
    model_class = None  # 需要在初始化时设置
    required_fields = ['customer_id', 'contact_type', 'subject', 'content']
    order_by = '-contact_date'
    
    def serialize(self, contact):
        """序列化联系记录"""
        from models import Customer
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
    
    def get_list(self):
        """获取列表 - 自定义筛选"""
        from models import Customer
        from sqlalchemy import or_
        
        page, per_page = PaginationUtils.get_params(request)
        
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        contact_type = request.args.get('contact_type')
        status = request.args.get('status')
        customer_id = request.args.get('customer_id', type=int)
        
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
        
        # 排序
        query = query.order_by(desc(self.model_class.contact_date))
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [self.serialize(obj) for obj in pagination.items]
        
        return api_paginated(
            items=items,
            total=pagination.total,
            page=page,
            per_page=per_page
        )
