import React, { useState, useEffect, useMemo } from 'react';
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
  message,
  Modal,
  Grid,
} from 'antd';
import { apiService, apiEndpoints } from '../services/api';
import { createPermissionChecker, PermissionChecker } from '../utils/permission';
import MobileLayout from './MobileLayout';
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
  ClockCircleOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content, Footer } = AntLayout;
const { Title } = Typography;
const { useBreakpoint } = Grid;

// 菜单配置
const menuItems = [
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
    key: '/reminders',
    icon: <ClockCircleOutlined />,
    label: '提醒中心',
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: '系统设置',
    children: [
      { key: '/settings/profile', label: '个人设置' },
      { key: '/settings/notifications', label: '通知设置' },
      { key: '/settings/users', label: '用户管理' },
      { key: '/settings/roles', label: '角色权限' },
      { key: '/settings/company', label: '公司信息' },
      { key: '/settings/dictionary', label: '业务参数' },
      { key: '/settings/logs', label: '操作日志' },
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
  '/reminders': '提醒中心',
  '/settings': '系统设置',
  '/settings/profile': '个人设置',
  '/settings/notifications': '通知设置',
  '/settings/users': '用户管理',
  '/settings/roles': '角色权限',
  '/settings/company': '公司信息',
  '/settings/dictionary': '业务参数',
  '/settings/logs': '操作日志',
};

// 用户信息接口
interface UserInfo {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: string;
  avatar?: string;
}

const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 创建权限检查器
  const permissionChecker = useMemo(() => {
    return createPermissionChecker(userInfo?.role);
  }, [userInfo?.role]);

  // 根据权限过滤菜单
  const filteredMenuItems = useMemo(() => {
    return permissionChecker.filterMenuItems(menuItems);
  }, [permissionChecker]);

  // 检查当前路由权限
  useEffect(() => {
    if (userInfo && !permissionChecker.hasPermission(location.pathname)) {
      // 显示无权限提示
      Modal.error({
        title: '无权限访问',
        content: `您的角色 [${permissionChecker.getRoleDisplayName()}] 没有权限访问此页面`,
        okText: '返回首页',
        onOk: () => {
          navigate('/dashboard');
        },
      });
    }
  }, [location.pathname, userInfo, permissionChecker, navigate]);

  // 获取用户信息
  useEffect(() => {
    const fetchUserInfo = async () => {
      // 先尝试从 localStorage 获取用户信息
      const cachedUser = apiService.getCurrentUser();
      if (cachedUser) {
        setUserInfo(cachedUser);
      }

      // 如果没有token，跳转到登录页
      if (!apiService.isAuthenticated()) {
        navigate('/login');
        return;
      }

      // 从API获取最新用户信息（包含头像）
      try {
        const data = await apiService.get<{ user: UserInfo }>(apiEndpoints.auth.profile);
        if (data && data.user) {
          setUserInfo(data.user);
          // 更新本地缓存
          apiService.setCurrentUser(data.user);
        }
      } catch (error: any) {
        if (error.response?.status === 401) {
          // Token过期，清除并跳转
          apiService.clearAuthToken();
          navigate('/login');
        } else {
          console.error('获取用户信息失败:', error);
          // 使用缓存数据，不显示错误
        }
      }
    };

    fetchUserInfo();

    // 监听个人信息更新事件
    const handleProfileUpdate = (event: CustomEvent) => {
      const updatedUser = event.detail?.user || event.detail;
      if (updatedUser) {
        setUserInfo(updatedUser);
        apiService.setCurrentUser(updatedUser);
      } else {
        // 如果没有数据，重新获取
        fetchUserInfo();
      }
    };

    window.addEventListener('userProfileUpdated', handleProfileUpdate as EventListener);

    return () => {
      window.removeEventListener('userProfileUpdated', handleProfileUpdate as EventListener);
    };
  }, [navigate]);

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
  const handleMenuClick = (e: any) => {
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
    const findMenuItem = (items: any[], currentPath: string) => {
      for (const item of items) {
        if (item.key === currentPath) {
          selectedKeys.push(item.key);
          return true;
        }
        if (item.children) {
          if (findMenuItem(item.children, currentPath)) {
            selectedKeys.push(item.key);
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

  // 响应式断点
  const screens = useBreakpoint();
  const isMobile = !screens.md;

  // 移动端使用MobileLayout
  if (isMobile) {
    return (
      <MobileLayout>
        <Outlet />
      </MobileLayout>
    );
  }

  // PC端使用完整Layout
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
            padding: '0 16px',
          }}
        >
          {collapsed ? (
            <img
              src="/logo.jpg"
              alt="Logo"
              style={{
                height: '40px',
                width: '40px',
                objectFit: 'contain',
                borderRadius: '4px',
              }}
            />
          ) : (
            <img
              src="/logo.jpg"
              alt="远臻CRM"
              style={{
                height: '48px',
                maxWidth: '100%',
                objectFit: 'contain',
              }}
            />
          )}
        </div>

        {/* 菜单 */}
        <Menu
          mode="inline"
          selectedKeys={getSelectedKeys()}
          defaultOpenKeys={getOpenKeys()}
          items={filteredMenuItems}
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
                {userInfo?.avatar ? (
                  <Avatar
                    size="default"
                    src={userInfo.avatar}
                    style={{ backgroundColor: '#1890ff' }}
                  />
                ) : (
                  <Avatar
                    size="default"
                    icon={<UserOutlined />}
                    style={{ backgroundColor: '#1890ff' }}
                  />
                )}
                <div style={{ minWidth: '80px', lineHeight: '1.4' }}>
                  <div style={{ fontWeight: 500, whiteSpace: 'nowrap', height: '20px', color: '#262626' }}>
                    {userInfo?.full_name || userInfo?.username || '加载中...'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#8c8c8c', whiteSpace: 'nowrap', height: '18px' }}>
                    {userInfo?.email || ''}
                  </div>
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
            <p>CRM系统 © 2026</p>
            <p style={{ fontSize: '12px', marginTop: '4px' }}>
              版本 1.0.0 | 技术支持: wilson 18867006194
            </p>
          </div>
        </Footer>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;
