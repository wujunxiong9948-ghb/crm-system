#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品管理API模块
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Product
from utils.pagination import paginate_query
from utils.validators import validate_required_fields
import json

products_bp = Blueprint('products', __name__)


@products_bp.route('', methods=['GET'])
@jwt_required()
def get_products():
    """获取产品列表 - 支持分页、搜索、筛选"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        status = request.args.get('status', '')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # 构建查询
        query = Product.query

        # 搜索条件
        if search:
            query = query.filter(
                db.or_(
                    Product.product_code.contains(search),
                    Product.description.contains(search),
                    Product.material.contains(search)
                )
            )

        # 分类筛选
        if category:
            query = query.filter(Product.category == category)

        # 状态筛选
        if status:
            query = query.filter(Product.status == status)

        # 排序
        if sort_order == 'desc':
            query = query.order_by(db.desc(getattr(Product, sort_by, Product.created_at)))
        else:
            query = query.order_by(getattr(Product, sort_by, Product.created_at))

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items

        return jsonify({
            'success': True,
            'data': [product.to_dict() for product in products],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取产品列表失败: {str(e)}'}), 500


@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """获取单个产品详情"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'message': '产品不存在'}), 404

        return jsonify({
            'success': True,
            'data': product.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取产品详情失败: {str(e)}'}), 500


@products_bp.route('/code/<string:product_code>', methods=['GET'])
@jwt_required()
def get_product_by_code(product_code):
    """通过产品编码获取产品"""
    try:
        product = Product.query.filter_by(product_code=product_code).first()
        if not product:
            return jsonify({'success': False, 'message': '产品不存在'}), 404

        return jsonify({
            'success': True,
            'data': product.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取产品失败: {str(e)}'}), 500


@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """创建新产品"""
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['product_code', 'description', 'category']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify({'success': False, 'message': validation_error}), 400

        # 检查产品编码是否已存在
        existing = Product.query.filter_by(product_code=data['product_code']).first()
        if existing:
            return jsonify({'success': False, 'message': '产品编码已存在'}), 400

        # 处理图片字段
        images = data.get('images', [])
        if isinstance(images, list):
            images = json.dumps(images, ensure_ascii=False)

        # 创建产品
        product = Product(
            item_id=data.get('item_id', ''),
            category=data['category'],
            product_code=data['product_code'],
            description=data['description'],
            material=data.get('material', ''),
            moq=data.get('moq', 0.0),
            unit_price=data.get('unit_price', 0.0),
            specifications=data.get('specifications', ''),
            images=images,
            status=data.get('status', '可用')
        )

        db.session.add(product)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '产品创建成功',
            'data': product.to_dict()
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建产品失败: {str(e)}'}), 500


@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """更新产品信息"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'message': '产品不存在'}), 404

        data = request.get_json()

        # 如果更新产品编码，检查是否与其他产品冲突
        if 'product_code' in data and data['product_code'] != product.product_code:
            existing = Product.query.filter_by(product_code=data['product_code']).first()
            if existing:
                return jsonify({'success': False, 'message': '产品编码已存在'}), 400
            product.product_code = data['product_code']

        # 更新字段
        if 'item_id' in data:
            product.item_id = data['item_id']
        if 'category' in data:
            product.category = data['category']
        if 'description' in data:
            product.description = data['description']
        if 'material' in data:
            product.material = data['material']
        if 'moq' in data:
            product.moq = data['moq']
        if 'unit_price' in data:
            product.unit_price = data['unit_price']
        if 'specifications' in data:
            product.specifications = data['specifications']
        if 'status' in data:
            product.status = data['status']
        if 'images' in data:
            images = data['images']
            if isinstance(images, list):
                images = json.dumps(images, ensure_ascii=False)
            product.images = images

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '产品更新成功',
            'data': product.to_dict()
        }), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新产品失败: {str(e)}'}), 500


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """删除产品"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'message': '产品不存在'}), 404

        db.session.delete(product)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '产品删除成功'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除产品失败: {str(e)}'}), 500


@products_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """获取所有产品分类"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        category_list = [c[0] for c in categories if c[0]]

        return jsonify({
            'success': True,
            'data': category_list
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取分类失败: {str(e)}'}), 500


@products_bp.route('/stats/summary', methods=['GET'])
@jwt_required()
def get_product_stats():
    """获取产品统计信息"""
    try:
        total = Product.query.count()
        available = Product.query.filter_by(status='可用').count()
        out_of_stock = Product.query.filter_by(status='缺货').count()
        disabled = Product.query.filter_by(status='停用').count()

        # 按分类统计
        category_stats = db.session.query(
            Product.category,
            db.func.count(Product.id).label('count')
        ).group_by(Product.category).all()

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'available': available,
                'out_of_stock': out_of_stock,
                'disabled': disabled,
                'by_category': [{'category': c[0], 'count': c[1]} for c in category_stats if c[0]]
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取统计失败: {str(e)}'}), 500


@products_bp.route('/batch', methods=['POST'])
@jwt_required()
def batch_create_products():
    """批量创建产品"""
    try:
        data = request.get_json()
        products_data = data.get('products', [])

        if not products_data:
            return jsonify({'success': False, 'message': '产品数据不能为空'}), 400

        created_count = 0
        errors = []

        for idx, product_data in enumerate(products_data):
            try:
                # 验证必填字段
                if not all(k in product_data for k in ['product_code', 'description', 'category']):
                    errors.append(f'第{idx+1}行: 缺少必填字段')
                    continue

                # 检查产品编码是否已存在
                existing = Product.query.filter_by(product_code=product_data['product_code']).first()
                if existing:
                    errors.append(f'第{idx+1}行: 产品编码 {product_data["product_code"]} 已存在')
                    continue

                # 处理图片
                images = product_data.get('images', [])
                if isinstance(images, list):
                    images = json.dumps(images, ensure_ascii=False)

                # 创建产品
                product = Product(
                    item_id=product_data.get('item_id', ''),
                    category=product_data['category'],
                    product_code=product_data['product_code'],
                    description=product_data['description'],
                    material=product_data.get('material', ''),
                    moq=product_data.get('moq', 0.0),
                    unit_price=product_data.get('unit_price', 0.0),
                    specifications=product_data.get('specifications', ''),
                    images=images,
                    status=product_data.get('status', '可用')
                )

                db.session.add(product)
                created_count += 1

            except Exception as e:
                errors.append(f'第{idx+1}行: {str(e)}')

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'成功创建 {created_count} 个产品',
            'data': {
                'created_count': created_count,
                'errors': errors
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'批量创建失败: {str(e)}'}), 500