import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Layout as AntLayout,
  Menu,
  Button,
  Avatar,
  Dropdown,
  Space,
  Typography,
  Breadcrumb,
  theme,
} from 'antd';
import type { MenuProps } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  UserOutlined,
  RiseOutlined,
  ShoppingCartOutlined,
  AppstoreOutlined,
  MessageOutlined,
  BarChartOutlined,
  SettingOutlined,
  LogoutOutlined,
  UserSwitchOutlined,
  BellOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content, Footer } = AntLayout;
const { Title } = Typography;

type MenuItem = Required<MenuProps>['items'][number];

// 菜单配置
const menuItems: MenuItem[] = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘',
  },
  {
    key: '/customers',
    icon: <UserOutlined />,
    label: '客户管理',
  },
  {
    key: '/opportunities',
    icon: <RiseOutlined />,
    label: '销售机会',
    children: [
      { key: '/opportunities', label: '机会列表' },
      { key: '/opportunities/new', label: '创建机会' },
      { key: '/opportunities/pipeline', label: '机会管道' },
    ],
  },
  {
    key: '/orders',
    icon: <ShoppingCartOutlined />,
    label: '订单管理',
    children: [
      { key: '/orders', label: '订单列表' },
      { key: '/orders/new', label: '新建订单' },
    ],
  },
  {
    key: '/products',
    icon: <AppstoreOutlined />,
    label: '产品目录',
  },
  {
    key: '/contacts',
    icon: <MessageOutlined />,
    label: '联系记录',
    children: [
      { key: '/contacts', label: '联系历史' },
      { key: '/contacts/calendar', label: '日历视图' },
    ],
  },
  {
    key: '/reports',
    icon: <BarChartOutlined />,
    label: '报表分析',
    children: [
      { key: '/reports/sales', label: '销售报表' },
      { key: '/reports/customers', label: '客户分析' },
      { key: '/reports/products', label: '产品分析' },
    ],
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: '系统设置',
    children: [
      { key: '/settings/profile', label: '个人设置' },
      { key: '/settings/notifications', label: '通知设置' },
      { key: '/settings/system', label: '系统配置' },
    ],
  },
];

// 用户菜单
const userMenuItems = [
  {
    key: 'profile',
    icon: <UserSwitchOutlined />,
    label: '个人资料',
  },
  {
    key: 'notifications',
    icon: <BellOutlined />,
    label: '通知中心',
  },
  {
    key: 'help',
    icon: <QuestionCircleOutlined />,
    label: '帮助中心',
  },
  {
    type: 'divider' as const,
  },
  {
    key: 'logout',
    icon: <LogoutOutlined />,
    label: '退出登录',
    danger: true,
  },
];

// 面包屑映射
const breadcrumbNameMap: Record<string, string> = {
  '/dashboard': '仪表盘',
  '/customers': '客户管理',
  '/customers/new': '新增客户',
  '/opportunities': '销售机会',
  '/opportunities/new': '创建机会',
  '/opportunities/pipeline': '机会管道',
  '/orders': '订单管理',
  '/orders/new': '新建订单',
  '/products': '产品目录',
  '/contacts': '联系记录',
  '/contacts/calendar': '日历视图',
  '/reports': '报表分析',
  '/reports/sales': '销售报表',
  '/reports/customers': '客户分析',
  '/reports/products': '产品分析',
  '/settings': '系统设置',
  '/settings/profile': '个人设置',
  '/settings/notifications': '通知设置',
  '/settings/system': '系统配置',
};

const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 获取当前路径的面包屑
  const getBreadcrumbItems = () => {
    const pathSnippets = location.pathname.split('/').filter(i => i);
    const items = [
      {
        title: '首页',
        href: '/dashboard',
      },
    ];

    let currentPath = '';
    for (const snippet of pathSnippets) {
      currentPath += `/${snippet}`;
      if (breadcrumbNameMap[currentPath]) {
        items.push({
          title: breadcrumbNameMap[currentPath],
          href: currentPath,
        });
      }
    }

    return items;
  };

  // 处理菜单点击
  const handleMenuClick = (e: { key: string }) => {
    navigate(e.key);
  };

  // 处理用户菜单点击
  const handleUserMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'logout':
        // 处理退出登录
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        navigate('/login');
        break;
      case 'profile':
        navigate('/settings/profile');
        break;
      case 'notifications':
        navigate('/settings/notifications');
        break;
      case 'help':
        window.open('https://help.example.com', '_blank');
        break;
    }
  };

  // 获取选中的菜单项
  const getSelectedKeys = () => {
    const path = location.pathname;
    const selectedKeys: string[] = [];

    // 查找匹配的菜单项
    const findMenuItem = (items: MenuItem[], currentPath: string) => {
      for (const item of items) {
        if (!item) continue;
        if (item.key === currentPath) {
          selectedKeys.push(item.key as string);
          return true;
        }
        if (item.children) {
          if (findMenuItem(item.children, currentPath)) {
            selectedKeys.push(item.key as string);
            return true;
          }
        }
      }
      return false;
    };

    findMenuItem(menuItems, path);
    return selectedKeys;
  };

  // 获取打开的菜单项
  const getOpenKeys = () => {
    return getSelectedKeys();
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      {/* 侧边栏 */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={240}
        style={{
          background: colorBgContainer,
          borderRight: '1px solid #f0f0f0',
        }}
      >
        {/* Logo区域 */}
        <div
          style={{
            height: '64px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          {collapsed ? (
            <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
              CRM
            </Title>
          ) : (
            <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
              酒店家具CRM
            </Title>
          )}
        </div>

        {/* 菜单 */}
        <Menu
          mode="inline"
          selectedKeys={getSelectedKeys()}
          defaultOpenKeys={getOpenKeys()}
          items={menuItems}
          onClick={handleMenuClick}
          style={{
            borderRight: 0,
            marginTop: '8px',
          }}
        />
      </Sider>

      <AntLayout>
        {/* 顶部导航栏 */}
        <Header
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <Space>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ fontSize: '16px' }}
            />
            <Breadcrumb items={getBreadcrumbItems()} />
          </Space>

          <Space size="large">
            {/* 通知按钮 */}
            <Button
              type="text"
              icon={<BellOutlined />}
              shape="circle"
              onClick={() => navigate('/settings/notifications')}
            />

            {/* 帮助按钮 */}
            <Button
              type="text"
              icon={<QuestionCircleOutlined />}
              shape="circle"
              onClick={() => window.open('https://help.example.com', '_blank')}
            />

            {/* 用户菜单 */}
            <Dropdown
              menu={{
                items: userMenuItems,
                onClick: handleUserMenuClick,
              }}
              placement="bottomRight"
            >
              <Space style={{ cursor: 'pointer' }}>
                <Avatar
                  size="default"
                  icon={<UserOutlined />}
                  style={{ backgroundColor: '#1890ff' }}
                />
                <div>
                  <div style={{ fontWeight: 500 }}>管理员</div>
                  <div style={{ fontSize: '12px', color: '#8c8c8c' }}>admin@example.com</div>
                </div>
              </Space>
            </Dropdown>
          </Space>
        </Header>

        {/* 主要内容区域 */}
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            overflow: 'auto',
          }}
        >
          <Outlet />
        </Content>

        {/* 页脚 */}
        <Footer style={{ textAlign: 'center', padding: '16px 50px' }}>
          <div style={{ color: 'rgba(0, 0, 0, 0.45)' }}>
            <p>酒店家具CRM系统 © 2026 源臻酒店家具</p>
            <p style={{ fontSize: '12px', marginTop: '4px' }}>
              版本 1.0.0 | 技术支持: 400-123-4567
            </p>
          </div>
        </Footer>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;
