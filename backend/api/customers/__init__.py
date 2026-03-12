#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户管理API模块
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Customer, Contact
from datetime import datetime, timedelta
import json

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    """获取客户列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        customer_type = request.args.get('type', '')
        status = request.args.get('status', '')

        # 构建查询
        query = Customer.query

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
def get_customer(customer_id):
    """获取单个客户详情"""
    try:
        customer = Customer.query.get_or_404(customer_id)

        # 获取相关数据
        contacts = Contact.query.filter_by(customer_id=customer_id).order_by(Contact.created_at.desc()).limit(10).all()

        result = customer.to_dict()
        result['recent_contacts'] = [contact.to_dict() for contact in contacts]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    """创建新客户"""
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'字段 {field} 不能为空'}), 400

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
            notes=data.get('notes', '')
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
def update_customer(customer_id):
    """更新客户信息"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()

        # 更新字段
        update_fields = ['name', 'company', 'phone', 'email', 'address',
                        'industry', 'customer_type', 'source', 'status', 'notes']

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
def delete_customer(customer_id):
    """删除客户"""
    try:
        customer = Customer.query.get_or_404(customer_id)

        db.session.delete(customer)
        db.session.commit()

        return jsonify({'message': '客户删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<int:customer_id>/contacts', methods=['GET'])
@jwt_required()
def get_customer_contacts(customer_id):
    """获取客户联系记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = Contact.query.filter_by(customer_id=customer_id)

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
def create_contact(customer_id):
    """创建联系记录"""
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['contact_type', 'subject', 'content']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'字段 {field} 不能为空'}), 400

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

@customers_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_customer_stats():
    """获取客户统计信息"""
    try:
        # 按类型统计
        type_stats = db.session.query(
            Customer.customer_type,
            db.func.count(Customer.id)
        ).group_by(Customer.customer_type).all()

        # 按状态统计
        status_stats = db.session.query(
            Customer.status,
            db.func.count(Customer.id)
        ).group_by(Customer.status).all()

        # 按来源统计
        source_stats = db.session.query(
            Customer.source,
            db.func.count(Customer.id)
        ).group_by(Customer.source).all()

        # 最近30天新增客户
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_customers = Customer.query.filter(
            Customer.created_at >= thirty_days_ago
        ).count()

        # 总客户数
        total_customers = Customer.query.count()

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