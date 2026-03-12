# 🏨 酒店家具CRM系统

## 📋 系统概述
专业的客户关系管理系统，专为酒店家具行业设计，包含客户管理、销售跟踪、订单管理、产品管理等功能。

## 🚀 快速启动

### 方法一：使用启动脚本（推荐）
1. 双击运行 `start_crm.bat`
2. 按照脚本提示操作

### 方法二：手动启动

#### 1. 启动后端API服务
```bash
cd backend
pip install -r requirements.txt
python app.py
```
后端将在 `http://localhost:5000` 启动

#### 2. 启动前端React应用
```bash
cd frontend
npm install
npm start
```
前端将在 `http://localhost:3000` 启动

## 🌐 访问地址
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000
- **API文档**: http://localhost:5000/api/docs (启动后访问)

## 🔐 默认登录账号
- **管理员**:
  - 用户名: `admin`
  - 密码: `admin123`
- **销售员**:
  - 用户名: `sales1`
  - 密码: `sales123`

## 📊 系统功能模块

### 1. 客户管理
- 客户信息录入与查询
- 客户分类与标签管理
- 跟进记录管理
- 客户来源分析

### 2. 销售管理
- 销售机会跟踪
- 报价单管理
- 合同管理
- 销售漏斗分析

### 3. 产品管理
- 产品目录管理
- 库存管理
- 价格管理
- 产品图片管理

### 4. 订单管理
- 订单创建与跟踪
- 发货管理
- 收款管理
- 订单统计

### 5. 报表分析
- 销售业绩报表
- 客户分析报表
- 产品销量报表
- 月度/季度/年度报表

## 🔧 技术栈

### 后端 (Flask)
- Python 3.8+
- Flask + Flask-RESTful
- SQLAlchemy (ORM)
- SQLite数据库
- JWT身份验证

### 前端 (React)
- React 18
- TypeScript
- Ant Design UI组件库
- React Router
- Axios HTTP客户端

## 📁 项目结构
```
crm/
├── backend/           # 后端API服务
│   ├── app.py        # 主应用文件
│   ├── config.py     # 配置文件
│   ├── models.py     # 数据模型
│   ├── requirements.txt # Python依赖
│   └── services/     # 业务逻辑服务
├── frontend/         # 前端React应用
│   ├── public/       # 静态资源
│   ├── src/          # 源代码
│   └── package.json  # Node.js依赖
├── database/         # 数据库相关
├── uploads/          # 文件上传目录
├── logs/             # 日志文件
├── crm.db            # SQLite数据库
└── start_crm.bat     # 启动脚本
```

## ⚙️ 环境配置

### 1. 数据库配置
系统默认使用SQLite数据库，文件位于 `crm.db`
如需使用其他数据库，修改 `backend/config.py` 中的 `DATABASE_URL`

### 2. 邮件通知配置
如需启用邮件通知，在 `backend/config.py` 中配置SMTP设置

### 3. QQ通知配置
系统已集成QQ通知功能，配置位于项目根目录的 `qq_config.json`

## 🔄 数据导入
系统支持从Excel导入客户和产品数据：
1. 准备Excel文件（.xlsx格式）
2. 使用数据导入功能
3. 模板文件可在 `database/templates/` 中找到

## 🛠️ 开发指南

### 添加新API端点
1. 在 `backend/routes/` 创建新路由文件
2. 在 `backend/app.py` 中注册路由
3. 在前端 `frontend/src/api/` 中添加对应的API调用

### 添加新页面
1. 在 `frontend/src/pages/` 创建新页面组件
2. 在 `frontend/src/routes/` 中添加路由配置
3. 更新侧边栏菜单（如果需要）

## 📞 技术支持
- 系统问题：联系系统管理员
- 功能需求：提交需求文档
- Bug报告：提供详细的重现步骤

## 📝 更新日志

### v1.0.0 (2026-03-11)
- ✅ 初始版本发布
- ✅ 客户管理模块
- ✅ 销售管理模块
- ✅ 产品管理模块
- ✅ 订单管理模块
- ✅ 基础报表功能
- ✅ QQ通知集成
- ✅ 数据导入导出

---

**注意**: 首次使用前请修改默认密码，确保系统安全。