#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
操作日志API
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, desc
from datetime import datetime, timedelta

from . import settings_bp
from models import db, OperationLog, User
from utils.auth import manager_required
from utils.pagination import paginate


@settings_bp.route('/logs', methods=['GET'])
@jwt_required()
@manager_required
def get_logs():
    """获取操作日志列表"""
    try:
        # 查询参数
        keyword = request.args.get('keyword', '')
        action = request.args.get('action', '')
        module = request.args.get('module', '')
        username = request.args.get('username', '')
        status = request.args.get('status', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')

        query = OperationLog.query

        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    OperationLog.description.contains(keyword),
                    OperationLog.ip_address.contains(keyword)
                )
            )

        # 操作类型筛选
        if action:
            query = query.filter(OperationLog.action == action)

        # 模块筛选
        if module:
            query = query.filter(OperationLog.module == module)

        # 用户名筛选
        if username:
            query = query.filter(OperationLog.username.contains(username))

        # 状态筛选
        if status:
            query = query.filter(OperationLog.status == status)

        # 日期范围筛选
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(OperationLog.created_at >= start)
            except ValueError:
                pass

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(OperationLog.created_at < end)
            except ValueError:
                pass

        # 排序
        query = query.order_by(desc(OperationLog.created_at))

        # 分页
        result = paginate(query, request)

        # 转换数据
        items = []
        for log in result['items']:
            log_dict = log.to_dict()
            # 截断请求和响应数据（避免数据过大）
            if log_dict.get('request_data') and len(str(log_dict['request_data'])) > 500:
                log_dict['request_data'] = str(log_dict['request_data'])[:500] + '...'
            if log_dict.get('response_data') and len(str(log_dict['response_data'])) > 500:
                log_dict['response_data'] = str(log_dict['response_data'])[:500] + '...'
            items.append(log_dict)

        result['items'] = items
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/logs/<int:log_id>', methods=['GET'])
@jwt_required()
@manager_required
def get_log(log_id):
    """获取日志详情"""
    try:
        log = OperationLog.query.get_or_404(log_id)
        return jsonify(log.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/logs/actions', methods=['GET'])
@jwt_required()
def get_log_actions():
    """获取操作类型列表"""
    try:
        actions = db.session.query(OperationLog.action).distinct().all()
        return jsonify([a[0] for a in actions if a[0]])

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/logs/modules', methods=['GET'])
@jwt_required()
def get_log_modules():
    """获取模块列表"""
    try:
        modules = db.session.query(OperationLog.module).distinct().all()
        return jsonify([m[0] for m in modules if m[0]])

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/logs/clear', methods=['POST'])
@jwt_required()
@manager_required
def clear_logs():
    """清理日志"""
    try:
        data = request.get_json()
        days = data.get('days', 90)  # 默认保留90天

        # 计算截止日期
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # 删除旧日志
        deleted = OperationLog.query.filter(OperationLog.created_at < cutoff_date).delete()
        db.session.commit()

        return jsonify({
            'message': f'已清理 {deleted} 条日志',
            'deleted_count': deleted,
            'retention_days': days
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/logs/export', methods=['GET'])
@jwt_required()
@manager_required
def export_logs():
    """导出日志"""
    try:
        # 查询参数
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')

        query = OperationLog.query

        # 日期范围筛选
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(OperationLog.created_at >= start)
            except ValueError:
                pass

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(OperationLog.created_at < end)
            except ValueError:
                pass

        # 限制导出数量
        logs = query.order_by(desc(OperationLog.created_at)).limit(10000).all()

        # 生成CSV
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow(['ID', '用户名', '操作', '模块', '描述', 'IP地址', '状态', '时间'])

        # 写入数据
        for log in logs:
            writer.writerow([
                log.id,
                log.username,
                log.action,
                log.module,
                log.description,
                log.ip_address,
                log.status,
                log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else ''
            ])

        output.seek(0)

        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=operation_logs_{datetime.now().strftime("%Y%m%d")}.csv'
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
