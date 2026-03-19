#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试销售机会API - 检查stats和列表返回格式
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

with app.test_client() as client:
    # 1. 登录
    login_resp = client.post('/api/v1/auth/login', 
        json={"username": "admin", "password": "admin123"})
    token_data = login_resp.get_json()
    
    if token_data.get('success') and token_data.get('data'):
        token = token_data['data']['access_token']
    elif token_data.get('access_token'):
        token = token_data['access_token']
    else:
        print(f"登录失败: {token_data}")
        sys.exit(1)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. 测试 stats API
    print("\n=== 测试 /api/v1/opportunities/stats ===")
    resp = client.get('/api/v1/opportunities/stats', headers=headers)
    data = resp.get_json()
    print(f"返回结构: {list(data.keys())}")
    print(f"数据: {data}")
    
    # 3. 测试列表API
    print("\n=== 测试 /api/v1/opportunities?per_page=1000 ===")
    resp = client.get('/api/v1/opportunities?per_page=1000', headers=headers)
    data = resp.get_json()
    print(f"返回结构: {list(data.keys())}")
    
    if 'data' in data and isinstance(data['data'], list):
        print(f"数据是列表，长度: {len(data['data'])}")
        if len(data['data']) > 0:
            print(f"第一条记录字段: {list(data['data'][0].keys())}")
            print(f"customer_name: {data['data'][0].get('customer_name')}")
            print(f"customer_company: {data['data'][0].get('customer_company')}")
