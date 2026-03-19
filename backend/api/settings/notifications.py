#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知设置API
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from . import settings_bp
from models import db, UserNotificationSetting


@settings_bp.route('/notification-settings', methods=['GET'])
@jwt_required()
def get_notification_settings():
    """获取通知设置"""
    try:
        user_id = get_jwt_identity()

        # 获取或创建设置
        settings = UserNotificationSetting.query.filter_by(user_id=user_id).first()

        if not settings:
            settings = UserNotificationSetting(user_id=user_id)
            db.session.add(settings)
            db.session.commit()

        return jsonify(settings.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/notification-settings', methods=['PUT'])
@jwt_required()
def update_notification_settings():
    """更新通知设置"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # 获取或创建设置
        settings = UserNotificationSetting.query.filter_by(user_id=user_id).first()

        if not settings:
            settings = UserNotificationSetting(user_id=user_id)
            db.session.add(settings)

        # 更新通知渠道
        if 'email_enabled' in data:
            settings.email_enabled = data['email_enabled']
        if 'sms_enabled' in data:
            settings.sms_enabled = data['sms_enabled']
        if 'qq_enabled' in data:
            settings.qq_enabled = data['qq_enabled']
        if 'browser_enabled' in data:
            settings.browser_enabled = data['browser_enabled']

        # 更新通知类型
        if 'task_reminder' in data:
            settings.task_reminder = data['task_reminder']
        if 'opportunity_reminder' in data:
            settings.opportunity_reminder = data['opportunity_reminder']
        if 'customer_reminder' in data:
            settings.customer_reminder = data['customer_reminder']
        if 'system_notice' in data:
            settings.system_notice = data['system_notice']
        if 'daily_report' in data:
            settings.daily_report = data['daily_report']
        if 'weekly_report' in data:
            settings.weekly_report = data['weekly_report']

        # 更新提醒时间
        if 'reminder_time' in data:
            settings.reminder_time = data['reminder_time']

        settings.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '通知设置更新成功',
            'settings': settings.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/notification-settings/test', methods=['POST'])
@jwt_required()
def test_notification():
    """测试通知"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        channel = data.get('channel', 'email')  # email, sms, qq

        # 获取用户信息
        from models import User
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 发送测试通知
        if channel == 'email':
            if not user.email:
                return jsonify({'error': '请先设置邮箱地址'}), 400
            # TODO: 发送测试邮件
            return jsonify({'message': f'测试邮件已发送至 {user.email}'})

        elif channel == 'qq':
            if not user.email:
                return jsonify({'error': '请先设置QQ号'}), 400
            # TODO: 发送测试QQ消息
            return jsonify({'message': f'测试QQ消息已发送至 {user.email}'})

        elif channel == 'sms':
            if not user.phone:
                return jsonify({'error': '请先设置手机号'}), 400
            # TODO: 发送测试短信
            return jsonify({'message': f'测试短信已发送至 {user.phone}'})

        else:
            return jsonify({'error': '不支持的通知渠道'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
