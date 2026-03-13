import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';

import Layout from './components/Layout';
import LoadingSpinner from './components/LoadingSpinner';

// 懒加载页面组件
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Login = React.lazy(() => import('./pages/Login'));
const NotFound = React.lazy(() => import('./pages/NotFound'));
const CustomerList = React.lazy(() => import('./pages/customers/CustomerList'));
const OpportunityList = React.lazy(() => import('./pages/opportunities/OpportunityList'));
const OpportunityDetail = React.lazy(() => import('./pages/opportunities/OpportunityDetail'));

// 设置dayjs本地化
dayjs.locale('zh-cn');

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
              <Route path=":id" element={<div>客户详情（开发中）</div>} />
              <Route path="new" element={<div>新建客户（开发中）</div>} />
            </Route>

            {/* 销售机会 */}
            <Route path="opportunities">
              <Route index element={<OpportunityList />} />
              <Route path=":id" element={<OpportunityDetail />} />
              <Route path="new" element={<OpportunityList />} />
            </Route>

            {/* 订单管理 */}
            <Route path="orders">
              <Route index element={<div style={{ padding: 24 }}>订单管理页面（开发中）</div>} />
              <Route path=":id" element={<div>订单详情（开发中）</div>} />
              <Route path="new" element={<div>新建订单（开发中）</div>} />
            </Route>

            {/* 产品目录 */}
            <Route path="products">
              <Route index element={<div style={{ padding: 24 }}>产品目录页面（开发中）</div>} />
              <Route path=":code" element={<div>产品详情（开发中）</div>} />
            </Route>

            {/* 联系记录 */}
            <Route path="contacts">
              <Route index element={<div style={{ padding: 24 }}>联系记录页面（开发中）</div>} />
              <Route path="calendar" element={<div>日历视图（开发中）</div>} />
            </Route>

            {/* 报表分析 */}
            <Route path="reports">
              <Route index element={<Navigate to="/reports/sales" replace />} />
              <Route path="sales" element={<div style={{ padding: 24 }}>销售报表（开发中）</div>} />
              <Route path="customers" element={<div>客户分析（开发中）</div>} />
              <Route path="products" element={<div>产品分析（开发中）</div>} />
            </Route>

            {/* 系统设置 */}
            <Route path="settings">
              <Route index element={<Navigate to="/settings/profile" replace />} />
              <Route
                path="profile"
                element={<div style={{ padding: 24 }}>个人设置（开发中）</div>}
              />
              <Route path="notifications" element={<div>通知设置（开发中）</div>} />
              <Route path="system" element={<div>系统设置（开发中）</div>} />
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
