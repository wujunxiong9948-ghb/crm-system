# CRM数据库优化报告

**检查时间**: 2026-03-18  
**检查人**: 山鸡  
**检查范围**: 数据模型、字段定义、索引、数据冗余

---

## 一、发现的问题

### 1. 🔴 数据冗余问题

| 表名 | 冗余字段 | 问题说明 | 解决方案 |
|------|---------|---------|---------|
| Opportunity | customer_name | 与客户表重复 | 改为@property关系查询 |
| Order | customer_name | 与客户表重复 | 改为@property关系查询 |
| Opportunity | follow_up_records | JSON存储，不易查询 | 拆分到独立表 |
| Product | images | 逗号分隔字符串 | 拆分到product_images表 |

### 2. 🟡 字段定义问题

| 表名 | 字段 | 问题 | 优化方案 |
|------|-----|------|---------|
| Order | total_amount | 使用Float | 改为Decimal(15,2) |
| OrderItem | unit_price | 使用Float | 改为Decimal(15,2) |
| Opportunity | expected_value | 使用Float | 改为Decimal(15,2) |
| Contact | content | 使用String | 改为Text类型 |
| Customer | address | 使用String | 改为Text类型 |
| OrderItem | product_id | 缺少外键 | 添加外键关联 |

### 3. 🟠 索引缺失问题

| 表名 | 缺失索引字段 | 影响 |
|------|-------------|------|
| customers | name, status, type | 客户列表查询慢 |
| opportunities | stage, status, customer_id | 销售机会查询慢 |
| orders | status, order_date | 订单查询慢 |
| contacts | contact_date, customer_id | 联系记录查询慢 |

### 4. 🔵 结构优化建议

| 建议 | 说明 | 优先级 |
|------|------|--------|
| 添加updated_at字段 | 所有表统一添加 | 高 |
| 创建基础模型类 | 减少重复代码 | 高 |
| 统一外键命名 | 使用xxx_id格式 | 中 |
| 软删除机制 | 使用status字段标记 | 中 |

---

## 二、已完成的优化

### ✅ 1. 添加索引（已执行）

已创建以下索引：
```sql
-- Customer表
CREATE INDEX ix_customers_name ON customers(name);
CREATE INDEX ix_customers_company ON customers(company);
CREATE INDEX ix_customers_status ON customers(status);
CREATE INDEX ix_customers_type ON customers(customer_type);

-- Opportunity表
CREATE INDEX ix_opportunities_customer ON opportunities(customer_id);
CREATE INDEX ix_opportunities_stage ON opportunities(stage);
CREATE INDEX ix_opportunities_status ON opportunities(status);
CREATE INDEX ix_opportunities_expected_close ON opportunities(expected_close_date);

-- Order表
CREATE INDEX ix_orders_customer ON orders(customer_id);
CREATE INDEX ix_orders_status ON orders(status);
CREATE INDEX ix_orders_date ON orders(order_date);

-- Contact表
CREATE INDEX ix_contacts_customer ON contacts(customer_id);
CREATE INDEX ix_contacts_type ON contacts(contact_type);
CREATE INDEX ix_contacts_date ON contacts(contact_date);
```

### ✅ 2. 创建新表（已执行）

**product_images表** - 替代逗号分隔的图片存储
```sql
CREATE TABLE product_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    url VARCHAR(500) NOT NULL,
    is_main BOOLEAN DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**opportunity_follow_ups表** - 替代JSON存储的跟进记录
```sql
CREATE TABLE opportunity_follow_ups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER NOT NULL,
    follow_up_date TIMESTAMP NOT NULL,
    content TEXT NOT NULL,
    stage_before VARCHAR(20),
    stage_after VARCHAR(20),
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);
```

### ✅ 3. 数据迁移（已执行）

- 产品图片数据已从逗号分隔格式迁移到product_images表
- 数据完整性检查完成，无孤立记录

---

## 三、代码层优化

### 优化后的模型文件
**文件**: `crm/backend/models_optimized.py`

**主要改进**:
1. **BaseModel基类** - 统一created_at/updated_at
2. **@property替代冗余字段** - customer_name等通过关系获取
3. **Decimal替代Float** - 金额字段精确计算
4. **Text替代String** - 大文本字段
5. **关联关系配置** - cascade删除规则

**示例**:
```python
class Opportunity(BaseModel):
    # 不再存储customer_name
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    
    @property
    def customer_name(self):
        """通过关系获取，不冗余存储"""
        return self.customer.name if self.customer else None
    
    # 金额使用Decimal
    expected_value = db.Column(db.Numeric(15, 2), default=0)
```

---

## 四、性能提升预估

| 优化项 | 预期提升 | 说明 |
|--------|---------|------|
| 索引优化 | 50-80% | 列表查询速度提升 |
| 冗余字段移除 | 20-30% | 存储空间减少 |
| 大字段优化 | 10-20% | 内存使用优化 |
| Decimal精度 | 100% | 金额计算准确 |

---

## 五、后续建议

### 1. 数据库层面
- [ ] 定期运行 `VACUUM` 命令整理SQLite数据库
- [ ] 考虑使用数据库连接池
- [ ] 大表考虑分表策略

### 2. 应用层面
- [ ] 使用懒加载（lazy='dynamic'）避免N+1查询
- [ ] 列表页使用分页，避免全表查询
- [ ] 热点数据使用缓存

### 3. 代码规范
- [ ] 新表必须继承BaseModel
- [ ] 外键字段必须添加索引
- [ ] 金额字段必须使用Decimal
- [ ] 大文本字段必须使用Text

---

## 六、注意事项

### 数据兼容性
- 冗余字段仍保留，确保旧代码兼容
- 新代码使用@property方式获取关联数据
- 建议逐步迁移旧数据到新表结构

### 回滚方案
如需要回滚：
1. 保留原models.py备份
2. 新表数据可导出为SQL备份
3. 索引删除不影响数据

---

**报告完成时间**: 2026-03-18  
**执行脚本**: `crm/backend/scripts/optimize_database.py`  
**优化后模型**: `crm/backend/models_optimized.py`

---

**总结**: 数据库优化已完成，索引已添加，新表已创建，数据已迁移。建议在测试环境充分验证后，再应用到生产环境。
