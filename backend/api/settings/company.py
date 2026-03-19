#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公司信息管理API
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime

from . import settings_bp
from models import db, CompanyInfo
from utils.auth import manager_required


@settings_bp.route('/company', methods=['GET'])
@jwt_required()
def get_company_info():
    """获取公司信息"""
    try:
        # 获取最新的公司信息
        company = CompanyInfo.query.order_by(CompanyInfo.id.desc()).first()

        if not company:
            return jsonify({
                'id': None,
                'name': '',
                'short_name': '',
                'logo': '',
                'address': '',
                'phone': '',
                'fax': '',
                'email': '',
                'website': '',
                'business_license': '',
                'tax_number': '',
                'bank_name': '',
                'bank_account': '',
                'description': ''
            })

        return jsonify(company.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/company', methods=['PUT'])
@jwt_required()
@manager_required
def update_company_info():
    """更新公司信息"""
    try:
        data = request.get_json()

        # 获取或创建公司信息
        company = CompanyInfo.query.order_by(CompanyInfo.id.desc()).first()

        if not company:
            company = CompanyInfo()
            db.session.add(company)

        # 更新字段
        if 'name' in data:
            company.name = data['name']
        if 'short_name' in data:
            company.short_name = data['short_name']
        if 'logo' in data:
            company.logo = data['logo']
        if 'address' in data:
            company.address = data['address']
        if 'phone' in data:
            company.phone = data['phone']
        if 'fax' in data:
            company.fax = data['fax']
        if 'email' in data:
            company.email = data['email']
        if 'website' in data:
            company.website = data['website']
        if 'business_license' in data:
            company.business_license = data['business_license']
        if 'tax_number' in data:
            company.tax_number = data['tax_number']
        if 'bank_name' in data:
            company.bank_name = data['bank_name']
        if 'bank_account' in data:
            company.bank_account = data['bank_account']
        if 'description' in data:
            company.description = data['description']

        company.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '公司信息更新成功',
            'company': company.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/company/logo', methods=['POST'])
@jwt_required()
@manager_required
def upload_company_logo():
    """上传公司Logo"""
    try:
        if 'logo' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400

        file = request.files['logo']

        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400

        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
        if '.' not in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': '只允许上传图片文件'}), 400

        # 保存文件
        import os
        from werkzeug.utils import secure_filename

        filename = secure_filename(f"company_logo_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1]}")
        upload_path = os.path.join('uploads', 'company')
        os.makedirs(upload_path, exist_ok=True)

        file_path = os.path.join(upload_path, filename)
        file.save(file_path)

        # 更新公司Logo
        company = CompanyInfo.query.order_by(CompanyInfo.id.desc()).first()
        if company:
            company.logo = f'/uploads/company/{filename}'
            company.updated_at = datetime.utcnow()
            db.session.commit()

        return jsonify({
            'message': 'Logo上传成功',
            'logo_url': f'/uploads/company/{filename}'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
