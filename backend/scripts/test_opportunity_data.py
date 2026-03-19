#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试销售机会API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Opportunity

app = create_app()

with app.app_context():
    # 1. 检查数据库中是否有数据
    count = Opportunity.query.count()
    print(f"数据库中销售机会总数: {count}")
    
    # 2. 查询所有机会
    if count > 0:
        opps = Opportunity.query.limit(5).all()
        print("\n前5条机会:")
        for opp in opps:
            print(f"  - {opp.name} (stage={opp.stage}, status={opp.status})")
    
    # 3. 检查按阶段分组
    from sqlalchemy import func
    stage_counts = db.session.query(Opportunity.stage, func.count(Opportunity.id)).group_by(Opportunity.stage).all()
    print("\n按阶段统计:")
    for stage, count in stage_counts:
        print(f"  - {stage}: {count}")
