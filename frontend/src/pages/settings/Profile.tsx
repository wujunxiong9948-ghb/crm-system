import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  message,
  Row,
  Col,
  Upload,
  Avatar,
  Divider,
  Tabs,
  Select,
} from 'antd';
import type { UploadRequestOption } from 'rc-upload/lib/interface';
import {
  UserOutlined,
  UploadOutlined,
  LockOutlined,
  SaveOutlined,
  SafetyOutlined,
  GlobalOutlined,
  MailOutlined,
  PhoneOutlined,
  IdcardOutlined,
} from '@ant-design/icons';
import { profileApi, apiService, apiEndpoints } from '../../services/api';

const { TabPane } = Tabs;
const { Option } = Select;

interface UserProfile {
  id: number;
  username: string;
  full_name: string;
  email: string;
  phone: string;
  avatar: string;
  department: string;
  position: string;
  theme: string;
  language: string;
  timezone: string;
  date_format: string;
  role: string;
  roles: { id: number; name: string; code: string }[];
}

const Profile: React.FC = () => {
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState('');
  const [activeTab, setActiveTab] = useState('basic');

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const data = await profileApi.getProfile();
      form.setFieldsValue(data);
      setAvatarUrl(data.avatar || '');
    } catch (error) {
      message.error('获取个人信息失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleSave = async (values: any) => {
    setSaving(true);
    try {
      const result = await profileApi.updateProfile(values);
      message.success('个人信息保存成功');
      // 派发事件通知 Layout 组件刷新用户信息
      window.dispatchEvent(new CustomEvent('userProfileUpdated', { detail: result }));
    } catch (error: any) {
      message.error(error.response?.data?.error || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (values: any) => {
    setPasswordSaving(true);
    try {
      await profileApi.changePassword(values);
      message.success('密码修改成功');
      passwordForm.resetFields();
    } catch (error: any) {
      message.error(error.response?.data?.error || '修改失败');
    } finally {
      setPasswordSaving(false);
    }
  };

  const handleAvatarUpload = async (options: UploadRequestOption) => {
    const { file, onSuccess, onError, onProgress } = options;

    try {
      const result = await apiService.uploadFile(
        apiEndpoints.settings.uploadAvatar,
        file as File,
        (progress) => {
          onProgress?.({ percent: progress });
        },
        'avatar'
      );

      message.success('头像上传成功');
      const avatarUrl = (result as any).avatar_url || (result as any).url || (result as any).data?.avatar_url;
      if (avatarUrl) {
        setAvatarUrl(avatarUrl);
        form.setFieldsValue({ avatar: avatarUrl });
      }
      onSuccess?.(result);
    } catch (error: any) {
      message.error(error.response?.data?.error || '头像上传失败');
      onError?.(error);
    }
  };

  return (
    <Card loading={loading}>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane
          tab={
            <span>
              <UserOutlined /> 基本信息
            </span>
          }
          key="basic"
        >
          <Form form={form} layout="vertical" onFinish={handleSave} style={{ maxWidth: 800 }}>
            <Row gutter={24}>
              <Col span={16}>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      name="full_name"
                      label="姓名"
                      rules={[{ required: true, message: '请输入姓名' }]}
                    >
                      <Input prefix={<IdcardOutlined />} placeholder="请输入姓名" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item name="username" label="用户名">
                      <Input disabled prefix={<UserOutlined />} />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item name="email" label="邮箱">
                      <Input prefix={<MailOutlined />} placeholder="请输入邮箱" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item name="phone" label="手机号">
                      <Input prefix={<PhoneOutlined />} placeholder="请输入手机号" />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item name="department" label="部门">
                      <Input placeholder="请输入部门" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item name="position" label="职位">
                      <Input placeholder="请输入职位" />
                    </Form.Item>
                  </Col>
                </Row>
              </Col>

              <Col span={8}>
                <Form.Item name="avatar" label="头像">
                  <div style={{ textAlign: 'center' }}>
                    <Avatar
                      size={100}
                      src={avatarUrl}
                      icon={<UserOutlined />}
                      style={{ marginBottom: 16, backgroundColor: '#1890ff' }}
                    />
                    <Upload
                      name="avatar"
                      customRequest={handleAvatarUpload}
                      showUploadList={false}
                      accept="image/*"
                    >
                      <Button icon={<UploadOutlined />}>更换头像</Button>
                    </Upload>
                  </div>
                </Form.Item>
              </Col>
            </Row>

            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={saving}>
                保存修改
              </Button>
            </Form.Item>
          </Form>
        </TabPane>

        <TabPane
          tab={
            <span>
              <SafetyOutlined /> 修改密码
            </span>
          }
          key="password"
        >
          <Form
            form={passwordForm}
            layout="vertical"
            onFinish={handleChangePassword}
            style={{ maxWidth: 400 }}
          >
            <Form.Item
              name="old_password"
              label="原密码"
              rules={[{ required: true, message: '请输入原密码' }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="请输入原密码" />
            </Form.Item>

            <Form.Item
              name="new_password"
              label="新密码"
              rules={[
                { required: true, message: '请输入新密码' },
                { min: 6, message: '密码长度至少6位' },
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="请输入新密码" />
            </Form.Item>

            <Form.Item
              name="confirm_password"
              label="确认新密码"
              rules={[
                { required: true, message: '请确认新密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('new_password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'));
                  },
                }),
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="请确认新密码" />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={passwordSaving}
              >
                修改密码
              </Button>
            </Form.Item>
          </Form>
        </TabPane>

        <TabPane
          tab={
            <span>
              <GlobalOutlined /> 偏好设置
            </span>
          }
          key="preference"
        >
          <Form form={form} layout="vertical" onFinish={handleSave} style={{ maxWidth: 400 }}>
            <Form.Item name="theme" label="主题" initialValue="light">
              <Select>
                <Option value="light">浅色主题</Option>
                <Option value="dark">深色主题</Option>
              </Select>
            </Form.Item>

            <Form.Item name="language" label="语言" initialValue="zh-CN">
              <Select>
                <Option value="zh-CN">简体中文</Option>
                <Option value="en-US">English</Option>
              </Select>
            </Form.Item>

            <Form.Item name="timezone" label="时区" initialValue="Asia/Shanghai">
              <Select>
                <Option value="Asia/Shanghai">北京时间 (Asia/Shanghai)</Option>
                <Option value="Asia/Hong_Kong">香港时间 (Asia/Hong_Kong)</Option>
                <Option value="Asia/Tokyo">东京时间 (Asia/Tokyo)</Option>
                <Option value="America/New_York">纽约时间 (America/New_York)</Option>
              </Select>
            </Form.Item>

            <Form.Item name="date_format" label="日期格式" initialValue="YYYY-MM-DD">
              <Select>
                <Option value="YYYY-MM-DD">YYYY-MM-DD</Option>
                <Option value="YYYY/MM/DD">YYYY/MM/DD</Option>
                <Option value="DD/MM/YYYY">DD/MM/YYYY</Option>
                <Option value="MM/DD/YYYY">MM/DD/YYYY</Option>
              </Select>
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={saving}>
                保存设置
              </Button>
            </Form.Item>
          </Form>
        </TabPane>
      </Tabs>
    </Card>
  );
};

export default Profile;
