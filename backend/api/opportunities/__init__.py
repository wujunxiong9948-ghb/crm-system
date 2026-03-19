#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
销售机会管理API模块 - 酒店家具项目专用（带权限控制）
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Opportunity, Customer, User
from sqlalchemy import or_, and_, desc
from datetime import datetime, date
import json

# 导入权限工具
from utils.auth import (
    check_permission, 
    log_operation,
    apply_data_scope,
    check_data_ownership,
    get_user_data_scope,
    Permissions
)

opportunities_bp = Blueprint('opportunities', __name__)


# 阶段与概率映射
STAGE_PROBABILITY_MAP = {
    '初步接触': 10,
    '需求分析': 25,
    '方案报价': 50,
    '谈判': 75,
    '成交': 100,
    '丢失': 0
}


def parse_date(date_str):
    """解析日期字符串"""
    if not date_str:
        return None
    try:
        if isinstance(date_str, str):
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        return date_str
    except:
        return None


def validate_opportunity_data(data, is_update=False):
    """验证机会数据"""
    errors = {}

    if not is_update:
        if not data.get('customer_id'):
            errors['customer_id'] = '客户ID不能为空'
        if not data.get('name'):
            errors['name'] = '项目名称不能为空'

    # 验证概率值
    probability = data.get('probability')
    if probability is not None:
        try:
            prob = int(probability)
            if not 0 <= prob <= 100:
                errors['probability'] = '概率值必须在0-100之间'
        except:
            errors['probability'] = '概率值必须是数字'

    # 验证预算
    for field in ['renovation_budget', 'furniture_budget', 'expected_value']:
        value = data.get(field)
        if value is not None:
            try:
                val = float(value)
                if val < 0:
                    errors[field] = '金额不能为负数'
            except:
                errors[field] = '金额必须是数字'

    # 验证数量
    for field in ['room_count', 'bed_count', 'nightstand_count', 'wardrobe_count',
                  'desk_count', 'chair_count', 'sofa_count', 'coffee_table_count', 'tv_cabinet_count']:
        value = data.get(field)
        if value is not None:
            try:
                val = int(value)
                if val < 0:
                    errors[field] = '数量不能为负数'
            except:
                errors[field] = '数量必须是整数'

    return errors


@opportunities_bp.route('', methods=['GET'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_VIEW)
@log_operation('opportunity', 'view', '查看销售机会列表')
def get_opportunities():
    """获取销售机会列表（带数据权限）"""
    try:
        # 查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        keyword = request.args.get('keyword', '')
        stage = request.args.get('stage', '')
        status = request.args.get('status', '')
        priority = request.args.get('priority', '')
        assigned_to = request.args.get('assigned_to', '')
        project_type = request.args.get('project_type', '')
        hotel_star = request.args.get('hotel_star', '')

        # 构建查询
        query = Opportunity.query
        
        # 应用数据权限
        user_id = get_jwt_identity()
        query = apply_data_scope(query, Opportunity, user_id)

        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    Opportunity.name.contains(keyword),
                    Opportunity.hotel_name.contains(keyword),
                    Opportunity.description.contains(keyword)
                )
            )

        # 阶段筛选
        if stage:
            query = query.filter(Opportunity.stage == stage)

        # 状态筛选
        if status:
            query = query.filter(Opportunity.status == status)

        # 优先级筛选
        if priority:
            query = query.filter(Opportunity.priority == priority)

        # 负责人筛选（管理员可以筛选，普通用户只能看到自己的）
        if assigned_to:
            scope = get_user_data_scope(user_id)
            if scope['type'] == 'all' or scope['type'] == 'department':
                query = query.filter(Opportunity.assigned_to == assigned_to)

        # 项目类型筛选
        if project_type:
            query = query.filter(Opportunity.project_type == project_type)

        # 星级筛选
        if hotel_star:
            query = query.filter(Opportunity.hotel_star == hotel_star)

        # 分页查询
        pagination = query.order_by(desc(Opportunity.created_at)).paginate(
            page=page, per_page=page_size, error_out=False
        )

        opportunities = pagination.items

        # 构建响应 - 匹配前端期望的格式
        result = {
            'data': [opp.to_dict() for opp in opportunities],
            'pagination': {
                'current': page,
                'pageSize': page_size,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@opportunities_bp.route('/<int:opportunity_id>', methods=['GET'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_VIEW)
@log_operation('opportunity', 'view', '查看销售机会详情')
def get_opportunity(opportunity_id):
    """获取销售机会详情"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        
        # 数据权限检查
        user_id = get_jwt_identity()
        if not check_data_ownership(opportunity, user_id):
            # 检查是否是部门数据
            scope = get_user_data_scope(user_id)
            if scope['type'] == 'department' and opportunity.assigned_to:
                user = User.query.get(user_id)
                assigned_user = User.query.filter_by(username=opportunity.assigned_to).first()
                if not assigned_user or assigned_user.department != scope['department']:
                    return jsonify({'error': '无权查看此机会'}), 403
            elif scope['type'] == 'self':
                return jsonify({'error': '无权查看此机会'}), 403

        return jsonify(opportunity.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@opportunities_bp.route('', methods=['POST'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_CREATE)
@log_operation('opportunity', 'create', '创建销售机会')
def create_opportunity():
    """创建销售机会"""
    try:
        data = request.get_json()

        # 验证数据
        errors = validate_opportunity_data(data)
        if errors:
            return jsonify({'error': '数据验证失败', 'details': errors}), 400

        # 检查客户是否存在
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': '客户不存在'}), 404
        
        # 数据权限检查 - 只能为自己负责的客户创建机会
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            if hasattr(customer, 'assigned_to') and customer.assigned_to != user.username:
                return jsonify({'error': '只能为自己负责的客户创建机会'}), 403

        # 如果提供了阶段，自动设置概率
        stage = data.get('stage', '初步接触')
        probability = data.get('probability', STAGE_PROBABILITY_MAP.get(stage, 10))

        # 创建机会
        opportunity = Opportunity(
            customer_id=data['customer_id'],
            name=data['name'],
            description=data.get('description', ''),
            
            # 酒店项目信息
            hotel_name=data.get('hotel_name', ''),
            project_type=data.get('project_type', '新建酒店'),
            hotel_star=data.get('hotel_star', ''),
            room_count=data.get('room_count'),
            
            # 地址信息
            province=data.get('province', ''),
            city=data.get('city', ''),
            district=data.get('district', ''),
            address=data.get('address', ''),
            
            # 时间节点
            planned_opening_date=parse_date(data.get('planned_opening_date')),
            expected_close_date=parse_date(data.get('expected_close_date')),
            next_follow_up_date=parse_date(data.get('next_follow_up_date')),
            
            # 预算信息
            renovation_budget=float(data.get('renovation_budget', 0) or 0),
            furniture_budget=float(data.get('furniture_budget', 0) or 0),
            expected_value=float(data.get('expected_value', 0) or 0),
            
            # 产品数量
            bed_count=int(data.get('bed_count', 0) or 0),
            nightstand_count=int(data.get('nightstand_count', 0) or 0),
            wardrobe_count=int(data.get('wardrobe_count', 0) or 0),
            desk_count=int(data.get('desk_count', 0) or 0),
            chair_count=int(data.get('chair_count', 0) or 0),
            sofa_count=int(data.get('sofa_count', 0) or 0),
            coffee_table_count=int(data.get('coffee_table_count', 0) or 0),
            tv_cabinet_count=int(data.get('tv_cabinet_count', 0) or 0),
            other_furniture=data.get('other_furniture', ''),
            
            # 销售信息
            stage=stage,
            probability=int(probability),
            priority=data.get('priority', '中'),
            assigned_to=data.get('assigned_to', user.username),  # 默认分配给创建者
            status=data.get('status', '进行中'),
            
            # 竞争信息
            competitors=data.get('competitors', ''),
            our_advantage=data.get('our_advantage', ''),
            customer_concern=data.get('customer_concern', ''),
            
            # 决策信息
            decision_maker=data.get('decision_maker', ''),
            decision_process=data.get('decision_process', ''),
            key_contacts=json.dumps(data.get('key_contacts', [])) if data.get('key_contacts') else None,
            
            # 跟进记录
            follow_up_records=json.dumps(data.get('follow_up_records', [])) if data.get('follow_up_records') else None
        )

        db.session.add(opportunity)
        db.session.commit()

        return jsonify({
            'message': '销售机会创建成功',
            'opportunity': opportunity.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@opportunities_bp.route('/<int:opportunity_id>', methods=['PUT'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_UPDATE)
@log_operation('opportunity', 'update', '更新销售机会')
def update_opportunity(opportunity_id):
    """更新销售机会"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        data = request.get_json()
        
        # 数据权限检查
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            if not check_data_ownership(opportunity, user_id):
                return jsonify({'error': '无权修改此机会'}), 403
        
        # 普通用户不能修改负责人
        if 'assigned_to' in data and user.role not in ['admin', 'manager']:
            if opportunity.assigned_to != user.username:
                return jsonify({'error': '无权转移机会归属'}), 403

        # 验证数据
        errors = validate_opportunity_data(data, is_update=True)
        if errors:
            return jsonify({'error': '数据验证失败', 'details': errors}), 400

        # 更新字段
        update_fields = [
            'name', 'description', 'hotel_name', 'project_type', 'hotel_star', 'room_count',
            'province', 'city', 'district', 'address',
            'renovation_budget', 'furniture_budget', 'expected_value',
            'bed_count', 'nightstand_count', 'wardrobe_count', 'desk_count', 'chair_count',
            'sofa_count', 'coffee_table_count', 'tv_cabinet_count', 'other_furniture',
            'stage', 'probability', 'priority', 'status', 'assigned_to',
            'competitors', 'our_advantage', 'customer_concern',
            'decision_maker', 'decision_process'
        ]

        for field in update_fields:
            if field in data:
                if field in ['renovation_budget', 'furniture_budget', 'expected_value']:
                    setattr(opportunity, field, float(data[field] or 0))
                elif field in ['bed_count', 'nightstand_count', 'wardrobe_count', 'desk_count',
                               'chair_count', 'sofa_count', 'coffee_table_count', 'tv_cabinet_count', 'room_count']:
                    setattr(opportunity, field, int(data[field] or 0))
                elif field == 'probability':
                    setattr(opportunity, field, int(data[field]))
                else:
                    setattr(opportunity, field, data[field])

        # 更新日期字段
        if 'planned_opening_date' in data:
            opportunity.planned_opening_date = parse_date(data['planned_opening_date'])
        if 'expected_close_date' in data:
            opportunity.expected_close_date = parse_date(data['expected_close_date'])
        if 'next_follow_up_date' in data:
            opportunity.next_follow_up_date = parse_date(data['next_follow_up_date'])

        # 更新JSON字段
        if 'key_contacts' in data:
            opportunity.key_contacts = json.dumps(data['key_contacts'])
        if 'follow_up_records' in data:
            opportunity.follow_up_records = json.dumps(data['follow_up_records'])

        opportunity.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '销售机会更新成功',
            'opportunity': opportunity.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@opportunities_bp.route('/<int:opportunity_id>/status', methods=['PUT'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_UPDATE)
@log_operation('opportunity', 'update_status', '更新机会状态')
def update_opportunity_status(opportunity_id):
    """更新机会状态（成交/丢失）"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        data = request.get_json()
        
        # 数据权限检查
        user_id = get_jwt_identity()
        if not check_data_ownership(opportunity, user_id):
            return jsonify({'error': '无权修改此机会'}), 403

        new_status = data.get('status')
        if new_status not in ['进行中', '已成交', '已丢失']:
            return jsonify({'error': '无效的状态值'}), 400

        opportunity.status = new_status
        
        if new_status == '已成交':
            opportunity.stage = '成交'
            opportunity.probability = 100
        elif new_status == '已丢失':
            opportunity.stage = '丢失'
            opportunity.probability = 0

        opportunity.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': f'机会状态已更新为{new_status}',
            'opportunity': opportunity.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@opportunities_bp.route('/<int:opportunity_id>', methods=['DELETE'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_DELETE)
@log_operation('opportunity', 'delete', '删除销售机会')
def delete_opportunity(opportunity_id):
    """删除销售机会"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        
        # 数据权限检查
        user_id = get_jwt_identity()
        if not check_data_ownership(opportunity, user_id):
            return jsonify({'error': '无权删除此机会'}), 403

        db.session.delete(opportunity)
        db.session.commit()

        return jsonify({'message': '销售机会删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@opportunities_bp.route('/<int:opportunity_id>/transfer', methods=['POST'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_TRANSFER)
@log_operation('opportunity', 'transfer', '转移机会归属')
def transfer_opportunity(opportunity_id):
    """转移机会归属"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
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
        
        # 管理员可以转移任何机会
        if user.role != 'admin':
            # 经理可以转移部门内的机会
            if user.role == 'manager':
                if new_user.department != user.department:
                    return jsonify({'error': '只能转移给同部门成员'}), 403
            else:
                # 普通用户只能转移自己的机会
                if not check_data_ownership(opportunity, user_id):
                    return jsonify({'error': '无权转移此机会'}), 403
        
        # 记录原负责人
        old_assigned = opportunity.assigned_to
        
        # 更新负责人
        opportunity.assigned_to = new_assigned_to
        db.session.commit()

        return jsonify({
            'message': '机会转移成功',
            'opportunity': opportunity.to_dict(),
            'from': old_assigned,
            'to': new_assigned_to
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@opportunities_bp.route('/pipeline', methods=['GET'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_VIEW)
@log_operation('opportunity', 'view_pipeline', '查看销售管道')
def get_pipeline():
    """获取销售管道看板数据"""
    try:
        # 应用数据权限
        user_id = get_jwt_identity()
        query = apply_data_scope(Opportunity.query, Opportunity, user_id)
        
        # 只查询进行中的机会
        query = query.filter(Opportunity.status == '进行中')
        
        opportunities = query.all()

        # 按阶段分组
        stages = ['初步接触', '需求分析', '方案报价', '谈判', '成交', '丢失']
        pipeline = {stage: [] for stage in stages}

        for opp in opportunities:
            stage = opp.stage if opp.stage in stages else '初步接触'
            pipeline[stage].append(opp.to_dict())

        # 计算统计数据
        stats = {
            'total_count': len(opportunities),
            'total_value': sum(opp.expected_value for opp in opportunities),
            'stage_counts': {stage: len(items) for stage, items in pipeline.items()}
        }

        return jsonify({
            'pipeline': pipeline,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@opportunities_bp.route('/stats', methods=['GET'])
@jwt_required()
@check_permission(Permissions.REPORT_VIEW)
@log_operation('opportunity', 'view_stats', '查看机会统计')
def get_opportunity_stats():
    """获取销售机会统计"""
    try:
        from sqlalchemy import func
        
        # 应用数据权限
        user_id = get_jwt_identity()
        query = apply_data_scope(Opportunity.query, Opportunity, user_id)

        # 按阶段统计
        stage_stats = query.with_entities(
            Opportunity.stage,
            func.count(Opportunity.id),
            func.sum(Opportunity.expected_value)
        ).group_by(Opportunity.stage).all()

        # 按状态统计
        status_stats = query.with_entities(
            Opportunity.status,
            func.count(Opportunity.id)
        ).group_by(Opportunity.status).all()

        # 按优先级统计
        priority_stats = query.with_entities(
            Opportunity.priority,
            func.count(Opportunity.id)
        ).group_by(Opportunity.priority).all()

        # 按项目类型统计
        type_stats = query.with_entities(
            Opportunity.project_type,
            func.count(Opportunity.id)
        ).group_by(Opportunity.project_type).all()

        result = {
            'by_stage': [
                {'stage': item[0], 'count': item[1], 'value': float(item[2] or 0)}
                for item in stage_stats
            ],
            'by_status': {item[0]: item[1] for item in status_stats},
            'by_priority': {item[0]: item[1] for item in priority_stats},
            'by_project_type': {item[0]: item[1] for item in type_stats}
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@opportunities_bp.route('/export', methods=['GET'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_EXPORT)
@log_operation('opportunity', 'export', '导出机会数据')
def export_opportunities():
    """导出销售机会数据"""
    try:
        # 应用数据权限
        user_id = get_jwt_identity()
        query = apply_data_scope(Opportunity.query, Opportunity, user_id)
        
        opportunities = query.all()

        # 转换为导出格式
        export_data = []
        for opp in opportunities:
            customer = Customer.query.get(opp.customer_id)
            export_data.append({
                'ID': opp.id,
                '项目名称': opp.name,
                '客户名称': customer.name if customer else '',
                '酒店名称': opp.hotel_name or '',
                '项目类型': opp.project_type,
                '星级': opp.hotel_star or '',
                '客房数': opp.room_count or 0,
                '阶段': opp.stage,
                '概率': f"{opp.probability}%",
                '预计金额': opp.expected_value,
                '家具预算': opp.furniture_budget,
                '装修预算': opp.renovation_budget,
                '负责人': opp.assigned_to or '',
                '状态': opp.status,
                '创建时间': opp.created_at.strftime('%Y-%m-%d %H:%M:%S') if opp.created_at else ''
            })

        return jsonify({
            'data': export_data,
            'total': len(export_data),
            'exported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@opportunities_bp.route('/filters/options', methods=['GET'])
@jwt_required()
def get_filter_options():
    """获取筛选选项"""
    try:
        # 应用数据权限
        user_id = get_jwt_identity()
        query = apply_data_scope(Opportunity.query, Opportunity, user_id)
        
        # 获取所有机会用于提取选项
        opportunities = query.all()

        # 提取唯一的选项值
        hotel_names = list(set([opp.hotel_name for opp in opportunities if opp.hotel_name]))
        stages = list(set([opp.stage for opp in opportunities if opp.stage]))
        statuses = list(set([opp.status for opp in opportunities if opp.status]))
        priorities = list(set([opp.priority for opp in opportunities if opp.priority]))
        project_types = list(set([opp.project_type for opp in opportunities if opp.project_type]))
        assigned_to_list = list(set([opp.assigned_to for opp in opportunities if opp.assigned_to]))

        return jsonify({
            'hotel_names': sorted(hotel_names),
            'stages': sorted(stages),
            'statuses': sorted(statuses),
            'priorities': sorted(priorities),
            'project_types': sorted(project_types),
            'assigned_to': sorted(assigned_to_list)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
