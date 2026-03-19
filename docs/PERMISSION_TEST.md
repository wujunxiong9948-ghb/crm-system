# CRM 权限功能测试文档

## 1. 权限架构

### 1.1 权限模型
- **功能权限**: 控制用户能执行的操作（查看、创建、编辑、删除等）
- **数据权限**: 控制用户能访问的数据范围（全部、部门、个人）
- **操作日志**: 记录所有操作便于审计

### 1.2 角色权限矩阵

| 角色 | 客户管理 | 机会管理 | 订单管理 | 产品管理 | 用户管理 | 报表查看 |
|------|----------|----------|----------|----------|----------|----------|
| 系统管理员 | 全部 | 全部 | 全部 | 全部 | 全部 | 全部 |
| 销售经理 | 部门 | 部门 | 部门 | 查看 | - | 部门 |
| 销售员 | 个人 | 个人 | 个人 | 查看 | - | 个人 |
| 普通用户 | 查看 | 查看 | 查看 | 查看 | - | - |
| 产品管理员 | - | - | - | 全部 | - | - |

## 2. API 权限列表

### 2.1 客户管理 (/api/customers)
| 接口 | 方法 | 所需权限 | 数据权限 |
|------|------|----------|----------|
| 列表 | GET | customer:view | 根据角色过滤 |
| 详情 | GET | customer:view | 个人/部门/全部 |
| 创建 | POST | customer:create | 分配给创建者 |
| 更新 | PUT | customer:update | 仅负责人/管理员 |
| 删除 | DELETE | customer:delete | 仅负责人/管理员 |
| 转移 | POST | customer:update | 经理及以上 |
| 导出 | GET | customer:export | 根据角色过滤 |

### 2.2 机会管理 (/api/opportunities)
| 接口 | 方法 | 所需权限 | 数据权限 |
|------|------|----------|----------|
| 列表 | GET | opportunity:view | 根据角色过滤 |
| 详情 | GET | opportunity:view | 个人/部门/全部 |
| 创建 | POST | opportunity:create | 分配给创建者 |
| 更新 | PUT | opportunity:update | 仅负责人/管理员 |
| 删除 | DELETE | opportunity:delete | 仅负责人/管理员 |
| 转移 | POST | opportunity:transfer | 经理及以上 |
| 管道 | GET | opportunity:view | 根据角色过滤 |
| 导出 | GET | opportunity:export | 根据角色过滤 |

### 2.3 用户管理 (/api/settings/users)
| 接口 | 方法 | 所需权限 | 说明 |
|------|------|----------|------|
| 列表 | GET | user:manage | 仅管理员/经理 |
| 详情 | GET | user:manage | 查看用户权限 |
| 创建 | POST | user:manage | 分配角色 |
| 更新 | PUT | user:manage | 修改角色/权限 |
| 删除 | DELETE | user:manage | 不能删除自己 |
| 重置密码 | POST | user:manage | 生成新密码 |
| 切换状态 | POST | user:manage | 启用/禁用 |
| 我的权限 | GET | 登录即可 | 查看当前用户权限 |

### 2.4 角色管理 (/api/settings/roles)
| 接口 | 方法 | 所需权限 | 说明 |
|------|------|----------|------|
| 列表 | GET | role:manage | 查看角色权限 |
| 详情 | GET | role:manage | 角色权限详情 |
| 创建 | POST | role:manage | 创建新角色 |
| 更新 | PUT | role:manage | 修改权限 |
| 删除 | DELETE | role:manage | 不能删除系统角色 |

## 3. 权限常量定义

```python
# 客户管理权限
CUSTOMER_VIEW = 'customer:view'
CUSTOMER_CREATE = 'customer:create'
CUSTOMER_UPDATE = 'customer:update'
CUSTOMER_DELETE = 'customer:delete'
CUSTOMER_EXPORT = 'customer:export'
CUSTOMER_IMPORT = 'customer:import'

# 销售机会权限
OPPORTUNITY_VIEW = 'opportunity:view'
OPPORTUNITY_CREATE = 'opportunity:create'
OPPORTUNITY_UPDATE = 'opportunity:update'
OPPORTUNITY_DELETE = 'opportunity:delete'
OPPORTUNITY_TRANSFER = 'opportunity:transfer'
OPPORTUNITY_EXPORT = 'opportunity:export'

# 订单权限
ORDER_VIEW = 'order:view'
ORDER_CREATE = 'order:create'
ORDER_UPDATE = 'order:update'
ORDER_DELETE = 'order:delete'
ORDER_APPROVE = 'order:approve'
ORDER_EXPORT = 'order:export'

# 产品权限
PRODUCT_VIEW = 'product:view'
PRODUCT_CREATE = 'product:create'
PRODUCT_UPDATE = 'product:update'
PRODUCT_DELETE = 'product:delete'

# 报表权限
REPORT_VIEW = 'report:view'
REPORT_EXPORT = 'report:export'

# 系统管理权限
USER_MANAGE = 'user:manage'
ROLE_MANAGE = 'role:manage'
SETTINGS_MANAGE = 'settings:manage'
LOG_VIEW = 'log:view'
```

## 4. 数据权限规则

### 4.1 管理员 (admin)
- 数据范围: 全部
- 可以查看、修改、删除所有数据
- 可以转移任何数据的归属

### 4.2 销售经理 (manager)
- 数据范围: 同部门
- 可以查看部门内所有数据
- 可以将数据转移给同部门成员
- 不能查看其他部门数据

### 4.3 销售员 (sales)
- 数据范围: 个人
- 只能查看自己负责的数据
- 可以创建数据并分配给自己
- 不能转移数据给他人

### 4.4 普通用户 (user)
- 数据范围: 仅查看
- 只能查看数据，不能创建/修改

## 5. 测试用例

### 5.1 功能权限测试

#### 测试1: 管理员拥有所有权限
```bash
# 登录管理员
POST /api/v1/auth/login
{"username": "admin", "password": "admin123"}

# 验证权限
GET /api/settings/users/me/permissions
# 期望: 返回所有28个权限
```

#### 测试2: 无权限访问被拒绝
```bash
# 使用普通用户token
GET /api/settings/users
# 期望: 403 {error: "没有操作权限", permission: "user:manage"}
```

#### 测试3: 角色权限正确分配
```bash
# 创建销售员用户，分配sales角色
# 验证只能访问个人数据
GET /api/customers
# 期望: 只返回 assigned_to = 该用户的数据
```

### 5.2 数据权限测试

#### 测试4: 数据隔离
```bash
# 创建客户A，分配给user1
# user1 可以查看/编辑客户A
# user2 无法查看客户A (403)
```

#### 测试5: 部门数据共享
```bash
# user1 (销售部) 创建客户
# user2 (销售部) 可以查看该客户
# user3 (其他部) 无法查看该客户
```

#### 测试6: 数据转移
```bash
# manager 可以将客户从user1转移给user2（同部门）
# manager 不能转移到其他部门
# admin 可以转移到任何用户
```

### 5.3 操作日志测试

#### 测试7: 操作被记录
```bash
# 创建客户
POST /api/customers
# 验证 operation_logs 表中有记录
# 包含: user_id, action, module, description, ip_address
```

## 6. 前端适配建议

### 6.1 根据权限显示/隐藏按钮
```javascript
// 检查权限
const hasPermission = (permission) => {
  return userPermissions.includes(permission);
};

// 条件渲染
{hasPermission('customer:create') && (
  <Button>新建客户</Button>
)}
```

### 6.2 根据数据权限禁用操作
```javascript
// 检查是否是自己的数据
const isOwner = (record) => {
  return record.assigned_to === currentUser.username || 
         userRole === 'admin';
};

// 条件禁用
<Button disabled={!isOwner(record)}>编辑</Button>
```

## 7. 已知限制

1. **前端权限**: 当前只做了后端权限控制，前端需要根据权限动态显示/隐藏按钮
2. **数据迁移**: 历史数据需要手动更新 created_by 和 assigned_to 字段
3. **部门权限**: 需要确保用户的 department 字段正确设置

## 8. 后续优化

1. 添加前端权限指令/组件
2. 添加数据权限缓存
3. 添加权限变更实时通知
4. 添加更细粒度的字段级权限
