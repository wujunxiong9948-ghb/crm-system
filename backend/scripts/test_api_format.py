#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 api_paginated vs api_success 的输出格式
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from utils.api_utils import api_success, api_paginated

app = create_app()

# 测试两种返回格式
with app.app_context():
    print("=== api_success 格式 ===")
    resp1 = api_success(data={'items': [1, 2, 3], 'pagination': {'total': 3}})
    print(f"状态码: {resp1[1]}")
    print(f"数据: {resp1[0].get_json()}")
    
    print("\n=== api_paginated 格式 ===")
    resp2 = api_paginated(items=[1, 2, 3], total=3, page=1, per_page=10)
    print(f"状态码: {resp2[1]}")
    print(f"数据: {resp2[0].get_json()}")
