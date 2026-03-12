-- 迁移: 初始数据库架构
-- 版本: 1
-- 描述: 创建CRM系统所有基础表结构
-- 创建时间: 2026-03-11 17:30:00

BEGIN TRANSACTION;

-- 1. 创建customers表 - 客户信息
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    industry TEXT,
    customer_type TEXT CHECK(customer_type IN ('潜在客户', '现有客户', 'VIP客户')),
    source TEXT CHECK(source IN ('展会', '推荐', '网站', '电话', '其他')),
    status TEXT DEFAULT '活跃' CHECK(status IN ('活跃', '休眠', '流失')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 创建opportunities表 - 销售机会
CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    product_category TEXT,
    expected_value REAL CHECK(expected_value >= 0),
    probability INTEGER CHECK(probability BETWEEN 0 AND 100),
    stage TEXT CHECK(stage IN ('初步接触', '需求分析', '方案报价', '谈判', '成交', '丢失')),
    expected_close_date DATE,
    assigned_to TEXT,
    status TEXT DEFAULT '进行中' CHECK(status IN ('进行中', '已成交', '已丢失')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 创建orders表 - 订单管理
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER REFERENCES opportunities(id),
    customer_id INTEGER REFERENCES customers(id),
    order_number TEXT UNIQUE NOT NULL,
    order_date DATE DEFAULT CURRENT_DATE,
    total_amount REAL CHECK(total_amount >= 0),
    currency TEXT DEFAULT 'CNY',
    status TEXT CHECK(status IN ('待处理', '生产中', '已发货', '已完成', '已取消')),
    payment_status TEXT CHECK(payment_status IN ('未支付', '部分支付', '已支付')),
    shipping_address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 创建order_items表 - 订单明细
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_code TEXT,
    product_name TEXT,
    quantity INTEGER CHECK(quantity > 0),
    unit_price REAL CHECK(unit_price >= 0),
    total_price REAL CHECK(total_price >= 0),
    specifications TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 创建contacts表 - 联系记录
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    contact_type TEXT CHECK(contact_type IN ('电话', '邮件', '拜访', '展会', '微信', '其他')),
    subject TEXT,
    content TEXT,
    contact_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    follow_up_date DATE,
    assigned_to TEXT,
    status TEXT DEFAULT '已完成' CHECK(status IN ('待处理', '进行中', '已完成', '已取消')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 创建products表 - 产品目录
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT,
    category TEXT,
    product_code TEXT UNIQUE,
    description TEXT,
    material TEXT,
    moq REAL CHECK(moq >= 0),
    unit_price REAL CHECK(unit_price >= 0),
    specifications TEXT,
    images TEXT, -- JSON数组存储图片路径
    status TEXT DEFAULT '可用' CHECK(status IN ('可用', '停用', '缺货')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 创建activities表 - 活动提醒
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT CHECK(type IN ('提醒', '通知', '任务')),
    title TEXT NOT NULL,
    description TEXT,
    related_id INTEGER,
    related_type TEXT CHECK(related_type IN ('customer', 'opportunity', 'order')),
    due_date DATE,
    priority TEXT CHECK(priority IN ('高', '中', '低')),
    assigned_to TEXT,
    status TEXT DEFAULT '待处理' CHECK(status IN ('待处理', '进行中', '已完成', '已取消')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 创建users表 - 系统用户
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    email TEXT,
    role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'manager', 'sales', 'user')),
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. 创建system_settings表 - 系统设置
CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. 创建notification_logs表 - 通知日志
CREATE TABLE IF NOT EXISTS notification_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_type TEXT CHECK(notification_type IN ('qq', 'email', 'sms', 'system')),
    title TEXT,
    content TEXT,
    recipient TEXT,
    status TEXT CHECK(status IN ('pending', 'sent', 'failed', 'read')),
    error_message TEXT,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能

-- customers表索引
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);
CREATE INDEX IF NOT EXISTS idx_customers_company ON customers(company);
CREATE INDEX IF NOT EXISTS idx_customers_customer_type ON customers(customer_type);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);

-- opportunities表索引
CREATE INDEX IF NOT EXISTS idx_opportunities_customer_id ON opportunities(customer_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_stage ON opportunities(stage);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opportunities_expected_close_date ON opportunities(expected_close_date);

-- orders表索引
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);

-- contacts表索引
CREATE INDEX IF NOT EXISTS idx_contacts_customer_id ON contacts(customer_id);
CREATE INDEX IF NOT EXISTS idx_contacts_contact_date ON contacts(contact_date);
CREATE INDEX IF NOT EXISTS idx_contacts_follow_up_date ON contacts(follow_up_date);

-- products表索引
CREATE INDEX IF NOT EXISTS idx_products_product_code ON products(product_code);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);

-- activities表索引
CREATE INDEX IF NOT EXISTS idx_activities_due_date ON activities(due_date);
CREATE INDEX IF NOT EXISTS idx_activities_status ON activities(status);
CREATE INDEX IF NOT EXISTS idx_activities_priority ON activities(priority);

-- 插入默认系统设置
INSERT OR REPLACE INTO system_settings (setting_key, setting_value, description) VALUES
('system_name', '酒店家具CRM系统', '系统名称'),
('company_name', '源臻酒店家具', '公司名称'),
('currency', 'CNY', '默认货币'),
('timezone', 'Asia/Shanghai', '时区设置'),
('date_format', 'YYYY-MM-DD', '日期格式'),
('items_per_page', '20', '每页显示条数'),
('notification_enabled', 'true', '启用通知'),
('backup_enabled', 'true', '启用备份'),
('backup_interval', 'daily', '备份频率');

-- 插入默认管理员用户（密码：admin123）
-- 注意：实际密码应该使用安全的哈希算法
INSERT OR REPLACE INTO users (username, password_hash, full_name, email, role) VALUES
('admin', 'pbkdf2:sha256:260000$abc123$...', '系统管理员', 'admin@example.com', 'admin');

-- 插入示例数据（用于测试）

-- 示例客户
INSERT OR IGNORE INTO customers (name, company, phone, email, customer_type, source, status) VALUES
('张三', '测试公司', '13800138000', 'zhangsan@example.com', '现有客户', '推荐', '活跃'),
('李四', '示例企业', '13900139000', 'lisi@example.com', '潜在客户', '展会', '活跃'),
('王五', '五星酒店', '13600136000', 'wangwu@example.com', 'VIP客户', '网站', '活跃');

-- 示例产品
INSERT OR IGNORE INTO products (product_code, category, description, material, moq, unit_price) VALUES
('FURN-001', '床', '豪华大床', '实木', 10, 1500.00),
('FURN-002', '沙发', '真皮沙发', '真皮', 5, 3000.00),
('FURN-003', '餐桌', '实木餐桌', '实木', 8, 1200.00),
('FURN-004', '椅子', '会议椅', '金属+皮革', 20, 450.00);

-- 示例销售机会
INSERT OR IGNORE INTO opportunities (customer_id, name, product_category, expected_value, probability, stage, expected_close_date) VALUES
(1, '酒店客房家具采购', '床、沙发', 50000.00, 70, '方案报价', '2026-04-15'),
(2, '会议室家具更新', '会议桌、椅子', 30000.00, 50, '需求分析', '2026-05-20');

-- 示例联系记录
INSERT OR IGNORE INTO contacts (customer_id, contact_type, subject, content, follow_up_date) VALUES
(1, '电话', '初步沟通需求', '客户对酒店家具感兴趣，需要报价', '2026-03-15'),
(2, '邮件', '发送产品目录', '已发送最新产品目录和报价单', '2026-03-20');

-- 示例活动提醒
INSERT OR IGNORE INTO activities (type, title, description, related_type, related_id, due_date, priority) VALUES
('提醒', '跟进张三的需求', '需要提供详细的产品规格和报价', 'customer', 1, '2026-03-15', '高'),
('任务', '准备展会材料', '为下周的家具展会准备宣传材料', 'customer', 2, '2026-03-18', '中');

COMMIT;