#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户管理API模块 - 带权限控制
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Customer, Contact, User
from datetime import datetime, timedelta
import json

# 导入权限工具
from utils.auth import (
    check_permission, 
    require_any_permission,
    log_operation,
    apply_data_scope,
    check_data_ownership,
    get_user_data_scope,
    Permissions
)

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('', methods=['GET'])
@jwt_required()
@check_permission(Permissions.CUSTOMER_VIEW)
@log_operation('customer', 'view', '查看客户列表')
def get_customers():
    """获取客户列表（带数据权限）"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        customer_type = request.args.get('type', '')
        status = request.args.get('status', '')
        assigned_to = request.args.get('assigned_to', '')

        # 构建查询
        query = Customer.query

        # 应用数据权限范围
        user_id = get_jwt_identity()
        query = apply_data_scope(query, Customer, user_id)

        # 搜索条件
        if search:
            query = query.filter(
                (Customer.name.contains(search)) |
                (Customer.company.contains(search)) |
                (Customer.phone.contains(search)) |
                (Customer.email.contains(search))
            )

        if customer_type:
            query = query.filter(Customer.customer_type == customer_type)

        if status:
            query = query.filter(Customer.status == status)
        
        # 负责人筛选（管理员可以筛选，普通用户只能看到自己的）
        if assigned_to:
            scope = get_user_data_scope(user_id)
            if scope['type'] == 'all' or scope['type'] == 'department':
                query = query.filter(Customer.assigned_to == assigned_to)

        # 分页查询
        pagination = query.order_by(Customer.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        customers = pagination.items

        # 构建响应
        result = {
            'customers': [customer.to_dict() for customer in customers],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
@check_permission(Permissions.CUSTOMER_VIEW)
@log_operation('customer', 'view', '查看客户详情')
def get_customer(customer_id):
    """获取单个客户详情"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # 数据权限检查 - 确保用户只能查看自己有权限的数据
        user_id = get_jwt_identity()
        if not check_data_ownership(customer, user_id):
            # 检查是否是部门数据
            scope = get_user_data_scope(user_id)
            if scope['type'] == 'department' and hasattr(customer, 'assigned_to'):
                user = User.query.get(user_id)
                assigned_user = User.query.filter_by(username=customer.assigned_to).first()
                if not assigned_user or assigned_user.department != scope['department']:
                    return jsonify({'error': '无权查看此客户'}), 403
            elif scope['type'] == 'self':
                return jsonify({'error': '无权查看此客户'}), 403

        # 获取相关数据
        contacts = Contact.query.filter_by(customer_id=customer_id).order_by(Contact.created_at.desc()).limit(10).all()

        result = customer.to_dict()
        result['recent_contacts'] = [contact.to_dict() for contact in contacts]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('', methods=['POST'])
@jwt_required()
@check_permission(Permissions.CUSTOMER_CREATE)
@log_operation('customer', 'create', '创建客户')
def create_customer():
    """创建新客户"""
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'字段 {field} 不能为空'}), 400

        # 获取当前用户
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # 创建客户
        customer = Customer(
            name=data['name'],
            company=data.get('company', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            address=data.get('address', ''),
            industry=data.get('industry', ''),
            customer_type=data.get('customer_type', '潜在客户'),
            source=data.get('source', '其他'),
            status=data.get('status', '活跃'),
            notes=data.get('notes', ''),
            assigned_to=data.get('assigned_to', user.username)  # 默认分配给创建者
        )

        db.session.add(customer)
        db.session.commit()

        return jsonify({
            'message': '客户创建成功',
            'customer': customer.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
@check_permission(Permissions.CUSTOMER_UPDATE)
@log_operation('customer', 'update', '更新客户')
def update_customer(customer_id):
    """更新客户信息"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        # 数据权限检查
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # 非管理员只能修改自己的数据
        if user.role != 'admin':
            if not check_data_ownership(customer, user_id):
                return jsonify({'error': '无权修改此客户'}), 403
        
        # 普通用户不能修改负责人（除非是自己的数据）
        if 'assigned_to' in data and user.role not in ['admin', 'manager']:
            if customer.assigned_to != user.username:
                return jsonify({'error': '无权转移客户归属'}), 403

        # 更新字段
        update_fields = ['name', 'company', 'phone', 'email', 'address',
                        'industry', 'customer_type', 'source', 'status', 'notes', 'assigned_to']

        for field in update_fields:
            if field in data:
                setattr(customer, field, data[field])

        db.session.commit()

        return jsonify({
            'message': '客户更新成功',
            'customer': customer.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
@check_permission(Permissions.CUSTOMER_DELETE)
@log_operation('customer', 'delete', '删除客户')
def delete_customer(customer_id):
    """删除客户"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # 数据权限检查
        user_id = get_jwt_identity()
        if not check_data_ownership(customer, user_id):
            return jsonify({'error': '无权删除此客户'}), 403

        db.session.delete(customer)
        db.session.commit()

        return jsonify({'message': '客户删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>/transfer', methods=['POST'])
@jwt_required()
@check_permission(Permissions.CUSTOMER_UPDATE)
@log_operation('customer', 'transfer', '转移客户归属')
def transfer_customer(customer_id):
    """转移客户归属"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        new_assigned_to = data.get('assigned_to')
        if not new_assigned_to:
            return jsonify({'error': '缺少新负责人参数'}), 400
        
        # 检查新负责人是否存在
        new_user = User.query.filter_by(username=new_assigned_to).first()
        if not new_user:
            return jsonify({'error': '新负责人不存在'}), 400
        
        # 数据权限检查
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # 管理员可以转移任何客户
        if user.role != 'admin':
            # 经理可以转移部门内的客户
            if user.role == 'manager':
                if new_user.department != user.department:
                    return jsonify({'error': '只能转移给同部门成员'}), 403
            else:
                # 普通用户只能转移自己的客户
                if not check_data_ownership(customer, user_id):
                    return jsonify({'error': '无权转移此客户'}), 403
        
        # 记录原负责人
        old_assigned = customer.assigned_to
        
        # 更新负责人
        customer.assigned_to = new_assigned_to
        db.session.commit()

        return jsonify({
            'message': '客户转移成功',
            'customer': customer.to_dict(),
            'from': old_assigned,
            'to': new_assigned_to
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>/contacts', methods=['GET'])
@jwt_required()
@check_permission(Permissions.CUSTOMER_VIEW)
@log_operation('customer', 'view', '查看客户联系记录')
def get_customer_contacts(customer_id):
    """获取客户联系记录"""
    try:
        # 数据权限检查
        customer = Customer.query.get_or_404(customer_id)
        user_id = get_jwt_identity()
        
        if not check_data_ownership(customer, user_id):
            return jsonify({'error': '无权查看此客户'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = Contact.query.filter_by(customer_id=customer_id)
        
        # 应用数据权限
        query = apply_data_scope(query, Contact, user_id)

        pagination = query.order_by(Contact.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        contacts = pagination.items

        result = {
            'contacts': [contact.to_dict() for contact in contacts],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>/contacts', methods=['POST'])
@jwt_required()
@check_permission(Permissions.CUSTOMER_UPDATE)
@log_operation('customer', 'create_contact', '添加客户联系记录')
def create_contact(customer_id):
    """创建联系记录"""
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['contact_type', 'subject', 'content']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'字段 {field} 不能为空'}), 400
        
        # 数据权限检查
        customer = Customer.query.get_or_404(customer_id)
        user_id = get_jwt_identity()
        
        if not check_data_ownership(customer, user_id):
            return jsonify({'error': '无权为此客户添加联系记录'}), 403

        # 创建联系记录
        contact = Contact(
            customer_id=customer_id,
            contact_type=data['contact_type'],
            subject=data['subject'],
            content=data['content'],
            contact_date=data.get('contact_date', datetime.now()),
            follow_up_date=data.get('follow_up_date'),
            assigned_to=data.get('assigned_to', get_jwt_identity()),
            status=data.get('status', '已完成')
        )

        db.session.add(contact)
        db.session.commit()

        return jsonify({
            'message': '联系记录创建成功',
            'contact': contact.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/export', methods=['GET'])
@jwt_required()
@check_permission(Permissions.CUSTOMER_EXPORT)
@log_operation('customer', 'export', '导出客户数据')
def export_customers():
    """导出客户数据"""
    try:
        # 获取筛选条件
        search = request.args.get('search', '')
        customer_type = request.args.get('type', '')
        status = request.args.get('status', '')

        # 构建查询
        query = Customer.query
        
        # 应用数据权限
        user_id = get_jwt_identity()
        query = apply_data_scope(query, Customer, user_id)

        if search:
            query = query.filter(
                (Customer.name.contains(search)) |
                (Customer.company.contains(search))
            )

        if customer_type:
            query = query.filter(Customer.customer_type == customer_type)

        if status:
            query = query.filter(Customer.status == status)

        customers = query.all()

        # 转换为导出格式
        export_data = []
        for customer in customers:
            export_data.append({
                'ID': customer.id,
                '客户名称': customer.name,
                '公司名称': customer.company,
                '电话': customer.phone,
                '邮箱': customer.email,
                '地址': customer.address,
                '行业': customer.industry,
                '客户类型': customer.customer_type,
                '来源': customer.source,
                '状态': customer.status,
                '负责人': customer.assigned_to if hasattr(customer, 'assigned_to') else '',
                '创建时间': customer.created_at.strftime('%Y-%m-%d %H:%M:%S') if customer.created_at else ''
            })

        return jsonify({
            'data': export_data,
            'total': len(export_data),
            'exported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/stats', methods=['GET'])
@jwt_required()
@check_permission(Permissions.REPORT_VIEW)
@log_operation('customer', 'view_stats', '查看客户统计')
def get_customer_stats():
    """获取客户统计信息（带数据权限）"""
    try:
        # 构建查询
        query = Customer.query
        
        # 应用数据权限
        user_id = get_jwt_identity()
        query = apply_data_scope(query, Customer, user_id)

        # 按类型统计
        from sqlalchemy import func
        type_stats = query.with_entities(
            Customer.customer_type,
            func.count(Customer.id)
        ).group_by(Customer.customer_type).all()

        # 按状态统计
        status_stats = query.with_entities(
            Customer.status,
            func.count(Customer.id)
        ).group_by(Customer.status).all()

        # 按来源统计
        source_stats = query.with_entities(
            Customer.source,
            func.count(Customer.id)
        ).group_by(Customer.source).all()

        # 最近30天新增客户
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_customers = query.filter(
            Customer.created_at >= thirty_days_ago
        ).count()

        # 总客户数
        total_customers = query.count()

        result = {
            'total_customers': total_customers,
            'recent_customers': recent_customers,
            'by_type': {item[0]: item[1] for item in type_stats},
            'by_status': {item[0]: item[1] for item in status_stats},
            'by_source': {item[0]: item[1] for item in source_stats}
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
