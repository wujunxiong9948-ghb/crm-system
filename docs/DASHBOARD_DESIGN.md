# Dashboard增强 - 架构设计文档
# 设计人: 赫菲斯托斯 (系统架构师)
# 日期: 2026-03-20
# 版本: v1.0

## 1. 需求概述

Dashboard增强包含以下功能模块：
1. 销售业绩排行榜
2. 客户跟进排行榜
3. 月度目标完成度
4. 待办聚合面板

## 2. 数据模型设计

### 2.1 销售目标表 (SalesTarget)

```sql
CREATE TABLE sales_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,              -- 用户ID
    target_type VARCHAR(20) NOT NULL,       -- 目标类型: monthly/quarterly/yearly
    target_year INTEGER NOT NULL,           -- 目标年份
    target_month INTEGER,                   -- 目标月份 (月度目标时使用)
    target_quarter INTEGER,                 -- 目标季度 (季度目标时使用)
    target_amount DECIMAL(15,2) NOT NULL,   -- 目标金额
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_sales_targets_user ON sales_targets(user_id);
CREATE INDEX idx_sales_targets_period ON sales_targets(target_year, target_month, target_quarter);
```

### 2.2 Dashboard统计视图

不需要新建表，基于现有表进行统计：
- Order表 - 计算销售额、订单数
- Contact表 - 计算跟进次数
- Customer表 - 计算客户数
- Opportunity表 - 计算销售机会
- Reminder表 - 获取待办提醒

## 3. API接口设计

### 3.1 销售业绩排行榜

**Endpoint**: `GET /api/v1/dashboard/sales-ranking`

**Request Parameters**:
```json
{
  "period": "month",      // 周期: week/month/quarter/year
  "limit": 5              // 返回条数，默认5
}
```

**Response**:
```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "period": "month",
    "rankings": [
      {
        "rank": 1,
        "user_id": 2,
        "user_name": "张三",
        "avatar": "...",
        "department": "销售一部",
        "order_count": 15,
        "order_amount": 258000.00,
        "completion_rate": 86.0
      }
    ]
  },
  "timestamp": "2026-03-20T12:00:00Z",
  "request_id": "abc123"
}
```

### 3.2 客户跟进排行榜

**Endpoint**: `GET /api/v1/dashboard/followup-ranking`

**Request Parameters**:
```json
{
  "period": "month",
  "limit": 5
}
```

**Response**:
```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "period": "month",
    "rankings": [
      {
        "rank": 1,
        "user_id": 2,
        "user_name": "张三",
        "contact_count": 45,
        "customer_count": 12,
        "conversion_rate": 26.7
      }
    ]
  }
}
```

### 3.3 目标完成度

**Endpoint**: `GET /api/v1/dashboard/target-completion`

**Request Parameters**:
```json
{
  "target_type": "month",   // month/quarter/year
  "year": 2026,
  "month": 3                // 月度时必填
}
```

**Response**:
```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "target_type": "month",
    "target_year": 2026,
    "target_month": 3,
    "target_amount": 500000.00,
    "current_amount": 320000.00,
    "completion_rate": 64.0,
    "remaining_amount": 180000.00,
    "remaining_days": 10,
    "trend": [
      {"date": "2026-03-01", "amount": 12000},
      {"date": "2026-03-02", "amount": 25000}
    ]
  }
}
```

### 3.4 待办聚合

**Endpoint**: `GET /api/v1/dashboard/todos`

**Response**:
```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "total_count": 15,
    "categories": {
      "reminders": {
        "count": 5,
        "items": [
          {
            "id": 1,
            "type": "reminder",
            "title": "跟进李总",
            "customer_name": "李总",
            "due_time": "2026-03-20T14:00:00Z",
            "priority": "high"
          }
        ]
      },
      "pending_contacts": {
        "count": 3,
        "items": [...]
      },
      "pending_orders": {
        "count": 7,
        "items": [...]
      }
    }
  }
}
```

## 4. 数据权限设计

所有Dashboard API需考虑数据权限：

1. **管理员(admin)**: 查看全公司数据
2. **经理(manager)**: 查看本部门数据 + 个人数据
3. **销售员(sales)**: 仅查看个人数据

权限控制通过 `apply_data_scope()` 函数实现。

## 5. 性能优化

1. **缓存策略**: 排行榜数据缓存5分钟
2. **数据库索引**: 确保Order、Contact表的时间字段有索引
3. **分页**: 排行榜默认返回前5名
4. **异步加载**: Dashboard各模块独立加载，避免阻塞

## 6. 前端组件设计

### 6.1 组件结构

```
Dashboard/
├── index.tsx                    # 主页面
├── components/
│   ├── SalesRankingCard.tsx     # 销售业绩排行
│   ├── FollowupRankingCard.tsx  # 客户跟进排行
│   ├── TargetProgressCard.tsx   # 目标完成度
│   └── TodoPanel.tsx            # 待办聚合面板
├── hooks/
│   └── useDashboardData.ts      # 数据获取Hook
└── api.ts                       # API接口
```

### 6.2 状态管理

使用React Query缓存Dashboard数据：
- 排行榜数据: staleTime: 5分钟
- 目标完成度: staleTime: 1分钟
- 待办数据: staleTime: 30秒

## 7. 开发任务分解

### 后端任务
1. [ ] 创建SalesTarget表模型
2. [ ] 实现销售业绩排行榜API
3. [ ] 实现客户跟进排行榜API
4. [ ] 实现目标完成度API
5. [ ] 实现待办聚合API
6. [ ] 添加数据权限控制
7. [ ] 编写单元测试

### 前端任务
1. [ ] 创建Dashboard API服务
2. [ ] 实现SalesRankingCard组件
3. [ ] 实现FollowupRankingCard组件
4. [ ] 实现TargetProgressCard组件
5. [ ] 实现TodoPanel组件
6. [ ] 集成到Dashboard页面
7. [ ] 添加加载状态和错误处理

---
**设计完成，可进入开发阶段**
