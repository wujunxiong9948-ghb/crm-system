#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查用户数据"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User, db

with app.app_context():
    user_count = User.query.count()
    print(f"用户总数: {user_count}")

    if user_count > 0:
        users = User.query.all()
        for u in users:
            print(f"  - {u.username}: {u.full_name} ({u.role})")
    else:
        print("数据库中没有用户，需要创建默认用户")
