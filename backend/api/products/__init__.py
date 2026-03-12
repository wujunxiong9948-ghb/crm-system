#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品管理API模块
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Product
import json

products_bp = Blueprint('products', __name__)

@products_bp.route('', methods=['GET'])
@jwt_required()
def get_products():
    """获取产品列表"""
    return jsonify({'message': '产品列表API - 待实现'}), 200

@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """获取单个产品"""
    return jsonify({'message': f'获取产品 {product_id} - 待实现'}), 200

@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """创建新产品"""
    return jsonify({'message': '创建产品 - 待实现'}), 200

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """更新产品信息"""
    return jsonify({'message': f'更新产品 {product_id} - 待实现'}), 200

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """删除产品"""
    return jsonify({'message': f'删除产品 {product_id} - 待实现'}), 200