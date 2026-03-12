import React, { useState } from 'react';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Card, Form, Input, message, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';
import { apiService, apiEndpoints } from '../services/api';

const { Title } = Typography;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);

    try {
      // 调用后端登录API
      const response = await apiService.post(apiEndpoints.auth.login, {
        username: values.username,
        password: values.password,
      });

      // 存储token和用户信息
      if (response.access_token) {
        apiService.setAuthToken(response.access_token);
        if (response.user) {
          apiService.setCurrentUser(response.user);
        }
        message.success('登录成功！');
        navigate('/dashboard');
      } else {
        message.error('登录失败，请重试');
      }
    } catch (error: any) {
      const errorMsg = error?.response?.data?.error || error?.message || '登录失败，请重试';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card style={{ width: 400, boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2} style={{ marginBottom: 8 }}>
            酒店家具CRM系统
          </Title>
          <Typography.Text type="secondary">欢迎回来，请登录您的账户</Typography.Text>
        </div>

        <Form name="login" initialValues={{ remember: true }} onFinish={onFinish} size="large">
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large">
              登录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Typography.Text type="secondary">
            测试账号: admin/admin123 或 sales1/sales123
          </Typography.Text>
        </div>
      </Card>
    </div>
  );
};

export default Login;
