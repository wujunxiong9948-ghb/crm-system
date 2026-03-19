#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单管理API模块
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, Customer, Opportunity, Product
from utils.pagination import paginate_query
from utils.validators import validate_required_fields
from datetime import datetime
import json

orders_bp = Blueprint('orders', __name__)


def generate_order_number():
    """生成订单编号: ORD + 年月日 + 4位序号"""
    today = datetime.now().strftime('%Y%m%d')
    prefix = f"ORD{today}"

    # 查询今天最后一个订单号
    last_order = Order.query.filter(
        Order.order_number.like(f"{prefix}%")
    ).order_by(Order.order_number.desc()).first()

    if last_order:
        # 提取序号并加1
        last_seq = int(last_order.order_number[-4:])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    return f"{prefix}{new_seq:04d}"


@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """获取订单列表 - 支持分页、搜索、筛选"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        customer_id = request.args.get('customer_id', type=int)
        opportunity_id = request.args.get('opportunity_id', type=int)
        status = request.args.get('status', '')
        payment_status = request.args.get('payment_status', '')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # 构建查询
        query = Order.query

        # 搜索条件（订单号、客户名称）
        if search:
            query = query.join(Customer).filter(
                db.or_(
                    Order.order_number.contains(search),
                    Customer.name.contains(search),
                    Customer.company.contains(search)
                )
            )

        # 客户筛选
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)

        # 机会筛选
        if opportunity_id:
            query = query.filter(Order.opportunity_id == opportunity_id)

        # 状态筛选
        if status:
            query = query.filter(Order.status == status)

        # 支付状态筛选
        if payment_status:
            query = query.filter(Order.payment_status == payment_status)

        # 排序
        if sort_order == 'desc':
            query = query.order_by(db.desc(getattr(Order, sort_by, Order.created_at)))
        else:
            query = query.order_by(getattr(Order, sort_by, Order.created_at))

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        orders = pagination.items

        # 构建返回数据（包含客户信息）
        data = []
        for order in orders:
            order_dict = order.to_dict()
            # 添加客户信息
            if order.customer:
                order_dict['customer'] = {
                    'id': order.customer.id,
                    'name': order.customer.name,
                    'company': order.customer.company
                }
            # 添加机会信息
            if order.opportunity:
                order_dict['opportunity'] = {
                    'id': order.opportunity.id,
                    'name': order.opportunity.name
                }
            # 添加订单明细
            order_dict['items'] = [item.to_dict() for item in order.items]
            data.append(order_dict)

        return jsonify({
            'success': True,
            'data': data,
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
        return jsonify({'success': False, 'message': f'获取订单列表失败: {str(e)}'}), 500


@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """获取单个订单详情"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'}), 404

        order_dict = order.to_dict()

        # 添加客户信息
        if order.customer:
            order_dict['customer'] = {
                'id': order.customer.id,
                'name': order.customer.name,
                'company': order.customer.company,
                'phone': order.customer.phone,
                'email': order.customer.email
            }

        # 添加机会信息
        if order.opportunity:
            order_dict['opportunity'] = {
                'id': order.opportunity.id,
                'name': order.opportunity.name,
                'hotel_name': order.opportunity.hotel_name
            }

        # 添加订单明细
        order_dict['items'] = [item.to_dict() for item in order.items]

        return jsonify({
            'success': True,
            'data': order_dict
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取订单详情失败: {str(e)}'}), 500


@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """创建新订单"""
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['customer_id']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify({'success': False, 'message': validation_error}), 400

        # 验证客户是否存在
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'success': False, 'message': '客户不存在'}), 400

        # 验证机会是否存在（如果提供了机会ID）
        opportunity_id = data.get('opportunity_id')
        if opportunity_id:
            opportunity = Opportunity.query.get(opportunity_id)
            if not opportunity:
                return jsonify({'success': False, 'message': '销售机会不存在'}), 400

        # 生成订单编号
        order_number = data.get('order_number') or generate_order_number()

        # 检查订单号是否已存在
        existing = Order.query.filter_by(order_number=order_number).first()
        if existing:
            return jsonify({'success': False, 'message': '订单编号已存在'}), 400

        # 解析订单日期
        order_date = data.get('order_date')
        if order_date:
            try:
                order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '订单日期格式不正确，应为 YYYY-MM-DD'}), 400
        else:
            order_date = datetime.now().date()

        # 创建订单
        order = Order(
            order_number=order_number,
            customer_id=data['customer_id'],
            opportunity_id=opportunity_id,
            order_date=order_date,
            total_amount=data.get('total_amount', 0.0),
            currency=data.get('currency', 'CNY'),
            status=data.get('status', '待处理'),
            payment_status=data.get('payment_status', '未支付'),
            shipping_address=data.get('shipping_address', ''),
            notes=data.get('notes', '')
        )

        db.session.add(order)
        db.session.flush()  # 获取order.id

        # 处理订单明细
        items = data.get('items', [])
        total_amount = 0.0

        for item_data in items:
            quantity = item_data.get('quantity', 1)
            unit_price = item_data.get('unit_price', 0.0)
            total_price = quantity * unit_price
            total_amount += total_price

            order_item = OrderItem(
                order_id=order.id,
                product_code=item_data.get('product_code', ''),
                product_name=item_data.get('product_name', ''),
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                specifications=item_data.get('specifications', '')
            )
            db.session.add(order_item)

        # 如果没有传入总金额，使用计算的总金额
        if not data.get('total_amount'):
            order.total_amount = total_amount

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '订单创建成功',
            'data': order.to_dict()
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建订单失败: {str(e)}'}), 500


@orders_bp.route('/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    """更新订单信息"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'}), 404

        data = request.get_json()

        # 更新客户（如果提供）
        if 'customer_id' in data:
            customer = Customer.query.get(data['customer_id'])
            if not customer:
                return jsonify({'success': False, 'message': '客户不存在'}), 400
            order.customer_id = data['customer_id']

        # 更新机会（如果提供）
        if 'opportunity_id' in data:
            if data['opportunity_id']:
                opportunity = Opportunity.query.get(data['opportunity_id'])
                if not opportunity:
                    return jsonify({'success': False, 'message': '销售机会不存在'}), 400
            order.opportunity_id = data['opportunity_id']

        # 更新订单编号（如果提供且不重复）
        if 'order_number' in data and data['order_number'] != order.order_number:
            existing = Order.query.filter_by(order_number=data['order_number']).first()
            if existing:
                return jsonify({'success': False, 'message': '订单编号已存在'}), 400
            order.order_number = data['order_number']

        # 更新订单日期
        if 'order_date' in data:
            try:
                order.order_date = datetime.strptime(data['order_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': '订单日期格式不正确'}), 400

        # 更新其他字段
        if 'total_amount' in data:
            order.total_amount = data['total_amount']
        if 'currency' in data:
            order.currency = data['currency']
        if 'status' in data:
            order.status = data['status']
        if 'payment_status' in data:
            order.payment_status = data['payment_status']
        if 'shipping_address' in data:
            order.shipping_address = data['shipping_address']
        if 'notes' in data:
            order.notes = data['notes']

        # 更新订单明细（如果提供）
        if 'items' in data:
            # 删除原有明细
            OrderItem.query.filter_by(order_id=order.id).delete()

            # 添加新明细
            total_amount = 0.0
            for item_data in data['items']:
                quantity = item_data.get('quantity', 1)
                unit_price = item_data.get('unit_price', 0.0)
                total_price = quantity * unit_price
                total_amount += total_price

                order_item = OrderItem(
                    order_id=order.id,
                    product_code=item_data.get('product_code', ''),
                    product_name=item_data.get('product_name', ''),
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    specifications=item_data.get('specifications', '')
                )
                db.session.add(order_item)

            # 更新订单总金额
            order.total_amount = total_amount

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '订单更新成功',
            'data': order.to_dict()
        }), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新订单失败: {str(e)}'}), 500


@orders_bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    """删除订单"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'}), 404

        db.session.delete(order)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '订单删除成功'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除订单失败: {str(e)}'}), 500


@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """更新订单状态"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'}), 404

        data = request.get_json()
        new_status = data.get('status')

        if not new_status:
            return jsonify({'success': False, 'message': '状态不能为空'}), 400

        valid_statuses = ['待处理', '生产中', '已发货', '已完成', '已取消']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': f'无效的状态，必须是以下之一: {", ".join(valid_statuses)}'}), 400

        order.status = new_status
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '订单状态更新成功',
            'data': order.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新状态失败: {str(e)}'}), 500


@orders_bp.route('/<int:order_id>/payment', methods=['PUT'])
@jwt_required()
def update_payment_status(order_id):
    """更新支付状态"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'}), 404

        data = request.get_json()
        new_status = data.get('payment_status')

        if not new_status:
            return jsonify({'success': False, 'message': '支付状态不能为空'}), 400

        valid_statuses = ['未支付', '部分支付', '已支付']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': f'无效的支付状态，必须是以下之一: {", ".join(valid_statuses)}'}), 400

        order.payment_status = new_status
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '支付状态更新成功',
            'data': order.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新支付状态失败: {str(e)}'}), 500


@orders_bp.route('/stats/summary', methods=['GET'])
@jwt_required()
def get_order_stats():
    """获取订单统计信息"""
    try:
        total = Order.query.count()
        pending = Order.query.filter_by(status='待处理').count()
        producing = Order.query.filter_by(status='生产中').count()
        shipped = Order.query.filter_by(status='已发货').count()
        completed = Order.query.filter_by(status='已完成').count()
        cancelled = Order.query.filter_by(status='已取消').count()

        # 金额统计
        total_amount = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
        pending_amount = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.status.in_(['待处理', '生产中'])
        ).scalar() or 0
        completed_amount = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.status == '已完成'
        ).scalar() or 0

        # 本月订单
        from datetime import datetime
        current_month = datetime.now().strftime('%Y-%m')
        month_start = f"{current_month}-01"
        month_orders = Order.query.filter(
            db.func.strftime('%Y-%m', Order.order_date) == current_month
        ).count()
        month_amount = db.session.query(db.func.sum(Order.total_amount)).filter(
            db.func.strftime('%Y-%m', Order.order_date) == current_month
        ).scalar() or 0

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'pending': pending,
                'producing': producing,
                'shipped': shipped,
                'completed': completed,
                'cancelled': cancelled,
                'total_amount': round(total_amount, 2),
                'pending_amount': round(pending_amount, 2),
                'completed_amount': round(completed_amount, 2),
                'month_orders': month_orders,
                'month_amount': round(month_amount, 2)
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取统计失败: {str(e)}'}), 500


@orders_bp.route('/from-opportunity/<int:opportunity_id>', methods=['POST'])
@jwt_required()
def create_order_from_opportunity(opportunity_id):
    """从销售机会创建订单"""
    try:
        opportunity = Opportunity.query.get(opportunity_id)
        if not opportunity:
            return jsonify({'success': False, 'message': '销售机会不存在'}), 404

        # 检查机会是否已成交
        if opportunity.status != '已成交':
            return jsonify({'success': False, 'message': '只有已成交的机会才能创建订单'}), 400

        data = request.get_json() or {}

        # 生成订单编号
        order_number = generate_order_number()

        # 创建订单
        order = Order(
            order_number=order_number,
            customer_id=opportunity.customer_id,
            opportunity_id=opportunity_id,
            order_date=data.get('order_date', datetime.now().date()),
            total_amount=opportunity.expected_value or 0.0,
            currency='CNY',
            status='待处理',
            payment_status='未支付',
            shipping_address=data.get('shipping_address', opportunity.address or ''),
            notes=data.get('notes', f'从机会 [{opportunity.name}] 创建')
        )

        db.session.add(order)
        db.session.flush()

        # 根据机会中的产品数量预估创建订单明细
        items_created = []

        # 床
        if opportunity.bed_count and opportunity.bed_count > 0:
            item = OrderItem(
                order_id=order.id,
                product_code='BED-001',
                product_name='酒店床',
                quantity=opportunity.bed_count,
                unit_price=0,
                total_price=0,
                specifications='标准酒店床'
            )
            db.session.add(item)
            items_created.append('床')

        # 床头柜
        if opportunity.nightstand_count and opportunity.nightstand_count > 0:
            item = OrderItem(
                order_id=order.id,
                product_code='NS-001',
                product_name='床头柜',
                quantity=opportunity.nightstand_count,
                unit_price=0,
                total_price=0,
                specifications='标准床头柜'
            )
            db.session.add(item)
            items_created.append('床头柜')

        # 衣柜
        if opportunity.wardrobe_count and opportunity.wardrobe_count > 0:
            item = OrderItem(
                order_id=order.id,
                product_code='WR-001',
                product_name='衣柜',
                quantity=opportunity.wardrobe_count,
                unit_price=0,
                total_price=0,
                specifications='标准衣柜'
            )
            db.session.add(item)
            items_created.append('衣柜')

        # 书桌
        if opportunity.desk_count and opportunity.desk_count > 0:
            item = OrderItem(
                order_id=order.id,
                product_code='DK-001',
                product_name='书桌',
                quantity=opportunity.desk_count,
                unit_price=0,
                total_price=0,
                specifications='标准书桌'
            )
            db.session.add(item)
            items_created.append('书桌')

        # 椅子
        if opportunity.chair_count and opportunity.chair_count > 0:
            item = OrderItem(
                order_id=order.id,
                product_code='CH-001',
                product_name='椅子',
                quantity=opportunity.chair_count,
                unit_price=0,
                total_price=0,
                specifications='标准椅子'
            )
            db.session.add(item)
            items_created.append('椅子')

        # 沙发
        if opportunity.sofa_count and opportunity.sofa_count > 0:
            item = OrderItem(
                order_id=order.id,
                product_code='SF-001',
                product_name='沙发',
                quantity=opportunity.sofa_count,
                unit_price=0,
                total_price=0,
                specifications='标准沙发'
            )
            db.session.add(item)
            items_created.append('沙发')

        # 茶几
        if opportunity.coffee_table_count and opportunity.coffee_table_count > 0:
            item = OrderItem(
                order_id=order.id,
                product_code='CT-001',
                product_name='茶几',
                quantity=opportunity.coffee_table_count,
                unit_price=0,
                total_price=0,
                specifications='标准茶几'
            )
            db.session.add(item)
            items_created.append('茶几')

        # 电视柜
        if opportunity.tv_cabinet_count and opportunity.tv_cabinet_count > 0:
            item = OrderItem(
                order_id=order.id,
                product_code='TV-001',
                product_name='电视柜',
                quantity=opportunity.tv_cabinet_count,
                unit_price=0,
                total_price=0,
                specifications='标准电视柜'
            )
            db.session.add(item)
            items_created.append('电视柜')

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'订单创建成功，已自动生成 {len(items_created)} 个产品明细',
            'data': order.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建订单失败: {str(e)}'}), 500