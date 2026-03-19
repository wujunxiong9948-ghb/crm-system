#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务参数字典管理API
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_
from datetime import datetime

from . import settings_bp
from models import db, Dictionary
from utils.auth import manager_required
from utils.pagination import paginate
from utils.validators import validate_required


@settings_bp.route('/dictionaries', methods=['GET'])
@jwt_required()
def get_dictionaries():
    """获取字典列表"""
    try:
        # 查询参数
        dict_type = request.args.get('type', '')
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', '')

        query = Dictionary.query

        # 类型筛选
        if dict_type:
            query = query.filter(Dictionary.type == dict_type)

        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    Dictionary.name.contains(keyword),
                    Dictionary.code.contains(keyword),
                    Dictionary.value.contains(keyword)
                )
            )

        # 状态筛选
        if status:
            query = query.filter(Dictionary.status == status)

        # 排序
        query = query.order_by(Dictionary.type, Dictionary.sort_order, Dictionary.created_at.desc())

        # 分页
        result = paginate(query, request)
        result['items'] = [d.to_dict() for d in result['items']]

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/dictionaries/types', methods=['GET'])
@jwt_required()
def get_dictionary_types():
    """获取字典类型列表"""
    try:
        types = db.session.query(Dictionary.type).distinct().all()
        return jsonify([t[0] for t in types])

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/dictionaries/by-type', methods=['GET'])
@jwt_required()
def get_dictionaries_by_type():
    """按类型获取字典（用于下拉选择）"""
    try:
        # 获取所有启用的字典
        dictionaries = Dictionary.query.filter_by(status='active').order_by(
            Dictionary.type, Dictionary.sort_order
        ).all()

        # 按类型分组
        result = {}
        for d in dictionaries:
            if d.type not in result:
                result[d.type] = []
            result[d.type].append({
                'id': d.id,
                'code': d.code,
                'name': d.name,
                'value': d.value
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/dictionaries/<int:dict_id>', methods=['GET'])
@jwt_required()
def get_dictionary(dict_id):
    """获取字典详情"""
    try:
        dictionary = Dictionary.query.get_or_404(dict_id)
        return jsonify(dictionary.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/dictionaries', methods=['POST'])
@jwt_required()
@manager_required
def create_dictionary():
    """创建字典"""
    try:
        data = request.get_json()

        # 验证必填字段
        errors = validate_required(data, ['type', 'code', 'name'])
        if errors:
            return jsonify({'error': '缺少必填字段', 'details': errors}), 400

        # 检查同类型下代码是否已存在
        existing = Dictionary.query.filter_by(
            type=data['type'],
            code=data['code']
        ).first()

        if existing:
            return jsonify({'error': '该类型下字典代码已存在'}), 400

        # 创建字典
        dictionary = Dictionary(
            type=data['type'],
            code=data['code'],
            name=data['name'],
            value=data.get('value'),
            sort_order=data.get('sort_order', 0),
            description=data.get('description'),
            status=data.get('status', 'active'),
            is_system=False
        )

        db.session.add(dictionary)
        db.session.commit()

        return jsonify({
            'message': '字典创建成功',
            'dictionary': dictionary.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/dictionaries/<int:dict_id>', methods=['PUT'])
@jwt_required()
@manager_required
def update_dictionary(dict_id):
    """更新字典"""
    try:
        dictionary = Dictionary.query.get_or_404(dict_id)
        data = request.get_json()

        # 系统内置字典不能修改类型和代码
        if dictionary.is_system:
            if 'type' in data or 'code' in data:
                return jsonify({'error': '系统内置字典不能修改类型和代码'}), 400

        # 检查同类型下代码是否冲突
        if 'code' in data and 'type' in data:
            existing = Dictionary.query.filter_by(
                type=data['type'],
                code=data['code']
            ).first()
            if existing and existing.id != dict_id:
                return jsonify({'error': '该类型下字典代码已存在'}), 400

        # 更新字段
        if 'type' in data:
            dictionary.type = data['type']
        if 'code' in data:
            dictionary.code = data['code']
        if 'name' in data:
            dictionary.name = data['name']
        if 'value' in data:
            dictionary.value = data['value']
        if 'sort_order' in data:
            dictionary.sort_order = data['sort_order']
        if 'description' in data:
            dictionary.description = data['description']
        if 'status' in data:
            dictionary.status = data['status']

        dictionary.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '字典更新成功',
            'dictionary': dictionary.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/dictionaries/<int:dict_id>', methods=['DELETE'])
@jwt_required()
@manager_required
def delete_dictionary(dict_id):
    """删除字典"""
    try:
        dictionary = Dictionary.query.get_or_404(dict_id)

        # 系统内置字典不能删除
        if dictionary.is_system:
            return jsonify({'error': '系统内置字典不能删除'}), 400

        db.session.delete(dictionary)
        db.session.commit()

        return jsonify({'message': '字典删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/dictionaries/batch', methods=['POST'])
@jwt_required()
@manager_required
def batch_create_dictionaries():
    """批量创建字典（用于初始化）"""
    try:
        data = request.get_json()
        items = data.get('items', [])

        created = []
        errors = []

        for item in items:
            try:
                # 检查是否已存在
                existing = Dictionary.query.filter_by(
                    type=item['type'],
                    code=item['code']
                ).first()

                if existing:
                    errors.append(f"{item['type']}.{item['code']} 已存在")
                    continue

                dictionary = Dictionary(
                    type=item['type'],
                    code=item['code'],
                    name=item['name'],
                    value=item.get('value'),
                    sort_order=item.get('sort_order', 0),
                    description=item.get('description'),
                    status=item.get('status', 'active'),
                    is_system=item.get('is_system', False)
                )

                db.session.add(dictionary)
                created.append(item)

            except Exception as e:
                errors.append(f"{item.get('type', '')}.{item.get('code', '')}: {str(e)}")

        db.session.commit()

        return jsonify({
            'message': f'成功创建 {len(created)} 个字典',
            'created': created,
            'errors': errors
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
