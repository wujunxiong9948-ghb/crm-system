# 🚀 CRM系统快速启动指南

## 📁 系统位置
```
C:\Users\Administrator\lobsterai\project\crm\
```

## 🎯 快速启动方式

### **方式1：使用启动脚本（推荐）**
1. 进入CRM目录：
   ```bash
   cd C:\Users\Administrator\lobsterai\project\crm
   ```

2. 运行启动脚本：
   ```bash
   start_crm.bat
   ```

3. 选择启动选项：
   - 选项1：启动后端API服务
   - 选项2：启动前端React应用
   - 选项3：同时启动前后端
   - 选项4：查看使用说明

### **方式2：手动启动**
#### **启动后端API服务**
```bash
cd crm/backend
python -c "import sys; sys.path.insert(0, '.'); from app import create_app; app = create_app(); app.run(debug=True, host='0.0.0.0', port=5000)"
```
或者双击运行：`start_backend.bat`

#### **启动前端React应用**
```bash
cd crm/frontend
npm start
```
或者双击运行：`start_frontend.bat`

## 🌐 访问地址
- **前端界面**：http://localhost:3000
- **后端API**：http://localhost:5000

## 🔐 登录信息
- **管理员账号**：`admin` / `admin123`
- **销售员账号**：`sales1` / `sales123`

## 📊 系统功能
✅ **客户管理** - 客户信息、跟进记录
✅ **销售管理** - 销售机会、报价单
✅ **产品管理** - 产品目录、库存
✅ **订单管理** - 订单跟踪、发货
✅ **报表分析** - 销售业绩、客户分析
✅ **QQ通知** - 已集成QQ机器人通知功能

## 🛠 技术架构
- **前端**：React + TypeScript + Ant Design
- **后端**：Flask + SQLAlchemy + JWT
- **数据库**：SQLite（无需额外安装）
- **通知系统**：QQ机器人集成

## 🔧 依赖安装
系统依赖已自动安装完成：
- ✅ 后端Python依赖已安装
- ✅ 前端Node.js依赖已安装

## 🚨 常见问题

### 1. **"python不是内部或外部命令"错误**
**问题原因**：Python未添加到系统PATH环境变量
**解决方案**：
```bash
# 方法1：使用简单启动脚本
cd C:\Users\Administrator\lobsterai\project\crm
start_simple.bat

# 方法2：手动启动
# 打开命令提示符，分别执行：
# 启动后端：
cd C:\Users\Administrator\lobsterai\project\crm\backend
python run_app.py

# 启动前端：
cd C:\Users\Administrator\lobsterai\project\crm\frontend
npm start
```

### 2. **找不到crm/frontend目录**
**解决方案**：
```bash
# 确保在正确的位置
cd C:\Users\Administrator\lobsterai\project\crm
# 然后进入frontend
cd frontend
```

### 3. **后端启动失败**
**解决方案**：
```bash
cd crm/backend
# 重新安装依赖
pip install -r requirements.txt
# 使用修复后的启动脚本
python run_app.py
```

### 4. **前端启动失败**
**解决方案**：
```bash
cd crm/frontend
# 重新安装依赖
npm install
# 启动开发服务器
npm start
```

### 5. **端口被占用**
**解决方案**：
- 检查是否有其他程序占用3000或5000端口
- 或者修改配置文件中的端口号

## 📞 技术支持
- **技术支持**：山鸡（你的AI助理）
- **联系方式**：通过LobsterAI直接对话
- **响应时间**：24/7随时待命

## 🎉 开始使用
1. 启动后端服务
2. 启动前端服务
3. 访问 http://localhost:3000
4. 使用测试账号登录
5. 开始管理你的酒店家具客户！

---

**提示**：系统已针对酒店家具行业优化，包含完整的销售流程跟踪和QQ通知功能。首次登录后建议立即修改默认密码。