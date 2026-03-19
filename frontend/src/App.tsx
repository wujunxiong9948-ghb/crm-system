import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import './styles/mobile.css';

import Layout from './components/Layout';
import LoadingSpinner from './components/LoadingSpinner';
import { PermissionGuard } from './components/PermissionGuard';

// 懒加载页面组件
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Login = React.lazy(() => import('./pages/Login'));
const NotFound = React.lazy(() => import('./pages/NotFound'));
const CustomerList = React.lazy(() => import('./pages/customers/CustomerList'));
const CustomerDetail = React.lazy(() => import('./pages/customers/CustomerDetail'));
const OpportunityList = React.lazy(() => import('./pages/opportunities/OpportunityList'));
const OpportunityDetail = React.lazy(() => import('./pages/opportunities/OpportunityDetail'));
const OpportunityPipeline = React.lazy(() => import('./pages/opportunities/OpportunityPipeline'));

// 产品管理页面
const ProductList = React.lazy(() => import('./pages/products/ProductList'));
const ProductDetail = React.lazy(() => import('./pages/products/ProductDetail'));
const ProductForm = React.lazy(() => import('./pages/products/ProductForm'));

// 订单管理页面
const OrderList = React.lazy(() => import('./pages/orders/OrderList'));
const OrderDetail = React.lazy(() => import('./pages/orders/OrderDetail'));
const OrderForm = React.lazy(() => import('./pages/orders/OrderForm'));

// 系统设置页面
const Profile = React.lazy(() => import('./pages/settings/Profile'));
const NotificationSettings = React.lazy(() => import('./pages/settings/NotificationSettings'));
const UserList = React.lazy(() => import('./pages/settings/UserList'));
const RoleList = React.lazy(() => import('./pages/settings/RoleList'));
const CompanyInfo = React.lazy(() => import('./pages/settings/CompanyInfo'));
const Dictionary = React.lazy(() => import('./pages/settings/Dictionary'));
const OperationLog = React.lazy(() => import('./pages/settings/OperationLog'));

// 联系记录页面
const ContactHistory = React.lazy(() => import('./pages/contacts/ContactHistory'));
const ContactCalendar = React.lazy(() => import('./pages/contacts/ContactCalendar'));

// 报表分析页面
const SalesReport = React.lazy(() => import('./pages/reports/SalesReport'));
const CustomerAnalysis = React.lazy(() => import('./pages/reports/CustomerAnalysis'));
const ProductAnalysis = React.lazy(() => import('./pages/reports/ProductAnalysis'));

// 提醒中心页面
const ReminderList = React.lazy(() => import('./pages/reminders/ReminderList'));

// 设置dayjs本地化
dayjs.locale('zh-cn');

// 强制刷新缓存

// 自定义主题配置
const theme = {
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',
    borderRadius: 6,
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  components: {
    Layout: {
      headerBg: '#001529',
      headerColor: '#fff',
      siderBg: '#fff',
      triggerBg: '#001529',
      triggerColor: '#fff',
    },
    Menu: {
      itemBg: 'transparent',
      itemHoverBg: '#f5f5f5',
      itemSelectedBg: '#e6f7ff',
      itemSelectedColor: '#1890ff',
    },
    Table: {
      headerBg: '#fafafa',
      headerColor: 'rgba(0, 0, 0, 0.85)',
      rowHoverBg: '#fafafa',
    },
    Card: {
      borderRadiusLG: 8,
      boxShadowTertiary:
        '0 1px 2px -2px rgba(0, 0, 0, 0.16), 0 3px 6px 0 rgba(0, 0, 0, 0.12), 0 5px 12px 4px rgba(0, 0, 0, 0.09)',
    },
  },
};

const App: React.FC = () => {
  // 这里可以添加认证检查逻辑
  const isAuthenticated = true; // 临时设置为true

  return (
    <ConfigProvider locale={zhCN} theme={theme}>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          {/* 登录页面 */}
          <Route path="/login" element={<Login />} />

          {/* 主应用路由 */}
          <Route path="/" element={isAuthenticated ? <Layout /> : <Navigate to="/login" replace />}>
            {/* 默认重定向到仪表盘 */}
            <Route index element={<Navigate to="/dashboard" replace />} />

            {/* 仪表盘 */}
            <Route path="dashboard" element={<Dashboard />} />

            {/* 客户管理 */}
            <Route path="customers">
              <Route index element={<CustomerList />} />
              <Route path=":id" element={<CustomerDetail />} />
              <Route path="new" element={<div>新建客户（开发中）</div>} />
            </Route>

            {/* 销售机会 */}
            <Route path="opportunities">
              <Route index element={<OpportunityList />} />
              <Route path="pipeline" element={<OpportunityPipeline />} />
              <Route path=":id" element={<OpportunityDetail />} />
              <Route path="new" element={<div>新建机会（开发中）</div>} />
            </Route>

            {/* 订单管理 */}
            <Route path="orders">
              <Route index element={<OrderList />} />
              <Route path=":id" element={<OrderDetail />} />
              <Route path=":id/edit" element={<OrderForm />} />
              <Route path="new" element={<OrderForm />} />
            </Route>

            {/* 产品目录 */}
            <Route path="products">
              <Route index element={<ProductList />} />
              <Route path=":id" element={<ProductDetail />} />
              <Route path=":id/edit" element={<ProductForm />} />
              <Route path="new" element={<ProductForm />} />
            </Route>

            {/* 联系记录 */}
            <Route path="contacts">
              <Route index element={<ContactHistory />} />
              <Route path="calendar" element={<ContactCalendar />} />
            </Route>

            {/* 报表分析 */}
            <Route path="reports">
              <Route index element={<Navigate to="/reports/sales" replace />} />
              <Route path="sales" element={<SalesReport />} />
              <Route path="customers" element={<CustomerAnalysis />} />
              <Route path="products" element={<ProductAnalysis />} />
            </Route>

            {/* 提醒中心 */}
            <Route path="reminders" element={<ReminderList />} />

            {/* 系统设置 */}
            <Route path="settings">
              <Route index element={<Navigate to="/settings/profile" replace />} />
              <Route path="profile" element={<Profile />} />
              <Route path="notifications" element={<NotificationSettings />} />
              <Route path="users" element={
                <PermissionGuard requiredRole={['admin']}>
                  <UserList />
                </PermissionGuard>
              } />
              <Route path="roles" element={
                <PermissionGuard requiredRole={['admin']}>
                  <RoleList />
                </PermissionGuard>
              } />
              <Route path="company" element={
                <PermissionGuard requiredRole={['admin', 'manager']}>
                  <CompanyInfo />
                </PermissionGuard>
              } />
              <Route path="dictionary" element={
                <PermissionGuard requiredRole={['admin', 'manager']}>
                  <Dictionary />
                </PermissionGuard>
              } />
              <Route path="logs" element={
                <PermissionGuard requiredRole={['admin']}>
                  <OperationLog />
                </PermissionGuard>
              } />
            </Route>

            {/* 404页面 */}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </Suspense>
    </ConfigProvider>
  );
};

export default App;
