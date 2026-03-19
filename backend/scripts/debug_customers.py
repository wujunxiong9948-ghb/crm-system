#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
import json

app = create_app()

with app.test_client() as client:
    # 登录
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
    
    # 测试customers
    print("=== /api/v1/customers ===")
    resp = client.get('/api/v1/customers', headers=headers)
    data = resp.get_json()
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
