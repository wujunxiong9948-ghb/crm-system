#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试销售机会API - 直接查看返回数据结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

# 模拟API请求
with app.test_client() as client:
    # 1. 先登录获取token
    login_resp = client.post('/api/v1/auth/login', 
        json={"username": "admin", "password": "admin123"})
    print("登录响应:", login_resp.status_code)
    
    if login_resp.status_code == 200:
        token_data = login_resp.get_json()
        # 处理两种响应格式
        if token_data.get('success') and token_data.get('data'):
            token = token_data['data']['access_token']
        elif token_data.get('access_token'):
            token = token_data['access_token']
        else:
            print(f"登录失败: {token_data}")
            sys.exit(1)
            
        headers = {'Authorization': f'Bearer {token}'}
        
        # 2. 调用销售机会列表API
        print("\n=== 测试 /api/v1/opportunities?per_page=1000 ===")
        resp = client.get('/api/v1/opportunities?per_page=1000', headers=headers)
        print(f"状态码: {resp.status_code}")
        
        data = resp.get_json()
        print(f"响应结构: {list(data.keys())}")
        print(f"success: {data.get('success')}")
        
        if data.get('success') and data.get('data'):
            response_data = data['data']
            print(f"data结构: {list(response_data.keys())}")
            
            if 'items' in response_data:
                items = response_data['items']
                print(f"\n返回条目数: {len(items)}")
                
                if len(items) > 0:
                    print(f"\n第一条数据:")
                    first = items[0]
                    print(f"  - id: {first.get('id')}")
                    print(f"  - name: {first.get('name')}")
                    print(f"  - stage: {first.get('stage')}")
                    print(f"  - status: {first.get('status')}")
                    print(f"  - customer_name: {first.get('customer_name')}")
                    
                    # 统计各阶段数量
                    stage_count = {}
                    for item in items:
                        stage = item.get('stage', '未知')
                        stage_count[stage] = stage_count.get(stage, 0) + 1
                    
                    print(f"\n各阶段统计:")
                    for stage, count in stage_count.items():
                        print(f"  - {stage}: {count}")
                else:
                    print("\n警告: 返回空数组!")
                    print(f"pagination: {response_data.get('pagination')}")
            elif 'opportunities' in response_data:
                print(f"\n使用'opportunities'字段，数量: {len(response_data['opportunities'])}")
            else:
                print(f"\n未知数据结构: {response_data}")
        else:
            print(f"\n错误响应: {data}")
    else:
        print(f"登录请求失败: {login_resp.status_code}")
        print(login_resp.data)
