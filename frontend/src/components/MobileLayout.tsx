import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, Avatar, Badge, Drawer, Grid } from 'antd';
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
  BellOutlined,
  HomeOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons';
import { apiService } from '../services/api';

const { Header, Sider, Content } = Layout;
const { useBreakpoint } = Grid;

// 底部导航配置
const bottomNavItems = [
  { key: '/dashboard', icon: <HomeOutlined />, label: '首页' },
  { key: '/customers', icon: <UserOutlined />, label: '客户' },
  { key: '/opportunities', icon: <RiseOutlined />, label: '机会' },
  { key: '/orders', icon: <ShoppingCartOutlined />, label: '订单' },
  { key: '/more', icon: <UnorderedListOutlined />, label: '更多' },
];

// 更多菜单项
const moreMenuItems = [
  { key: '/products', icon: <AppstoreOutlined />, label: '产品目录' },
  { key: '/contacts', icon: <MessageOutlined />, label: '联系记录' },
  { key: '/reports', icon: <BarChartOutlined />, label: '报表分析' },
  { key: '/reminders', icon: <BellOutlined />, label: '提醒中心' },
  { key: '/settings', icon: <SettingOutlined />, label: '系统设置' },
];

interface MobileLayoutProps {
  children: React.ReactNode;
}

const MobileLayout: React.FC<MobileLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const screens = useBreakpoint();
  
  const [userInfo, setUserInfo] = useState<any>(null);
  const [moreDrawerVisible, setMoreDrawerVisible] = useState(false);
  const [reminderCount, setReminderCount] = useState(0);

  // 获取用户信息
  useEffect(() => {
    const user = apiService.getCurrentUser();
    if (user) {
      setUserInfo(user);
    }
    
    // 获取提醒数量
    const fetchReminderCount = async () => {
      try {
        const response = await apiService.get('/reminders/stats');
        if (response?.data) {
          setReminderCount(response.data.pending || 0);
        }
      } catch (e) {
        console.error('获取提醒数量失败:', e);
      }
    };
    fetchReminderCount();
  }, []);

  // 处理底部导航点击
  const handleNavClick = (key: string) => {
    if (key === '/more') {
      setMoreDrawerVisible(true);
    } else {
      navigate(key);
    }
  };

  // 处理更多菜单点击
  const handleMoreMenuClick = (key: string) => {
    setMoreDrawerVisible(false);
    navigate(key);
  };

  // 判断是否显示底部导航
  const showBottomNav = !screens.md;

  // 获取当前选中的导航
  const getActiveKey = () => {
    const path = location.pathname;
    if (path === '/dashboard') return '/dashboard';
    if (path.startsWith('/customers')) return '/customers';
    if (path.startsWith('/opportunities')) return '/opportunities';
    if (path.startsWith('/orders')) return '/orders';
    return '/dashboard';
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 顶部Header - 移动端 */}
      {!screens.md && (
        <Header
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 1000,
            background: '#fff',
            padding: '0 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            height: 56,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <img
              src="/logo.jpg"
              alt="CRM"
              style={{ height: 32, marginRight: 8, borderRadius: 4 }}
            />
            <span style={{ fontSize: 16, fontWeight: 'bold' }}>远臻CRM</span>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Badge count={reminderCount} size="small">
              <Button
                type="text"
                icon={<BellOutlined style={{ fontSize: 20 }} />}
                onClick={() => navigate('/reminders')}
              />
            </Badge>
            <Avatar
              size={32}
              icon={<UserOutlined />}
              src={userInfo?.avatar}
              onClick={() => navigate('/settings/profile')}
              style={{ cursor: 'pointer' }}
            />
          </div>
        </Header>
      )}

      {/* 主内容区域 */}
      <Content
        style={{
          marginTop: !screens.md ? 56 : 0,
          marginBottom: !screens.md ? 64 : 0,
          padding: !screens.md ? 12 : 24,
          background: '#f5f5f5',
          overflow: 'auto',
        }}
      >
        {children}
      </Content>

      {/* 底部导航栏 - 仅移动端显示 */}
      {showBottomNav && (
        <div
          style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            background: '#fff',
            borderTop: '1px solid #e8e8e8',
            display: 'flex',
            justifyContent: 'space-around',
            padding: '8px 0',
            zIndex: 1000,
            height: 64,
          }}
        >
          {bottomNavItems.map((item) => (
            <div
              key={item.key}
              onClick={() => handleNavClick(item.key)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                flex: 1,
                cursor: 'pointer',
                color: getActiveKey() === item.key ? '#1890ff' : '#666',
                fontSize: 12,
                gap: 4,
              }}
            >
              <span style={{ fontSize: 20 }}>{item.icon}</span>
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      )}

      {/* 更多菜单抽屉 */}
      <Drawer
        title="更多功能"
        placement="bottom"
        onClose={() => setMoreDrawerVisible(false)}
        open={moreDrawerVisible}
        height="auto"
        bodyStyle={{ padding: 0 }}
      >
        <Menu
          mode="vertical"
          selectedKeys={[location.pathname]}
          onClick={({ key }) => handleMoreMenuClick(key)}
          items={moreMenuItems.map(item => ({
            key: item.key,
            icon: item.icon,
            label: item.label,
          }))}
        />
      </Drawer>
    </Layout>
  );
};

export default MobileLayout;
