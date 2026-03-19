import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Switch,
  Button,
  message,
  Divider,
  TimePicker,
  Space,
  Tag,
  Row,
  Col,
  Typography,
} from 'antd';
import {
  BellOutlined,
  MailOutlined,
  MessageOutlined,
  MobileOutlined,
  ChromeOutlined,
  SaveOutlined,
  SendOutlined,
} from '@ant-design/icons';
import { notificationApi } from '../../services/api';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

interface NotificationSettingsData {
  email_enabled: boolean;
  sms_enabled: boolean;
  qq_enabled: boolean;
  browser_enabled: boolean;
  task_reminder: boolean;
  opportunity_reminder: boolean;
  customer_reminder: boolean;
  system_notice: boolean;
  daily_report: boolean;
  weekly_report: boolean;
  reminder_time: string;
}

const NotificationSettings: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const data = await notificationApi.getSettings();
      form.setFieldsValue({
        ...data,
        reminder_time: data.reminder_time
          ? dayjs(data.reminder_time, 'HH:mm')
          : dayjs('09:00', 'HH:mm'),
      });
    } catch (error) {
      message.error('获取通知设置失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async (values: any) => {
    setSaving(true);
    try {
      const data = {
        ...values,
        reminder_time: values.reminder_time ? values.reminder_time.format('HH:mm') : '09:00',
      };
      await notificationApi.updateSettings(data);
      message.success('通知设置保存成功');
    } catch (error: any) {
      message.error(error.response?.data?.error || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleTestNotification = async (channel: string) => {
    try {
      await notificationApi.testNotification(channel);
      message.success(`测试${getChannelName(channel)}已发送，请查收`);
    } catch (error: any) {
      message.error(error.response?.data?.error || '发送失败');
    }
  };

  const getChannelName = (channel: string) => {
    const names: Record<string, string> = {
      email: '邮件',
      sms: '短信',
      qq: 'QQ消息',
    };
    return names[channel] || channel;
  };

  return (
    <Card
      title={
        <span>
          <BellOutlined /> 通知设置
        </span>
      }
      loading={loading}
    >
      <Form form={form} layout="vertical" onFinish={handleSave}>
        {/* 通知渠道 */}
        <Title level={5}>通知渠道</Title>
        <Text type="secondary">选择您希望接收通知的方式</Text>
        <Divider />

        <Row gutter={[48, 24]}>
          <Col span={12}>
            <Form.Item
              name="email_enabled"
              valuePropName="checked"
              label={
                <Space>
                  <MailOutlined />
                  <span>邮件通知</span>
                  <Tag color="blue">推荐</Tag>
                </Space>
              }
            >
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Text type="secondary">接收重要通知、日报周报等邮件提醒</Text>
          </Col>
          <Col span={12}>
            <Form.Item
              name="qq_enabled"
              valuePropName="checked"
              label={
                <Space>
                  <MessageOutlined />
                  <span>QQ通知</span>
                </Space>
              }
            >
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Text type="secondary">通过QQ接收即时消息提醒</Text>
          </Col>
        </Row>

        <Row gutter={[48, 24]}>
          <Col span={12}>
            <Form.Item
              name="browser_enabled"
              valuePropName="checked"
              label={
                <Space>
                  <ChromeOutlined />
                  <span>浏览器通知</span>
                </Space>
              }
            >
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Text type="secondary">在浏览器中接收桌面通知</Text>
          </Col>
          <Col span={12}>
            <Form.Item
              name="sms_enabled"
              valuePropName="checked"
              label={
                <Space>
                  <MobileOutlined />
                  <span>短信通知</span>
                </Space>
              }
            >
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Text type="secondary">接收重要短信提醒（可能产生费用）</Text>
          </Col>
        </Row>

        <Divider />

        {/* 通知类型 */}
        <Title level={5}>通知类型</Title>
        <Text type="secondary">选择您希望接收的通知内容</Text>
        <Divider />

        <Row gutter={[48, 24]}>
          <Col span={12}>
            <Form.Item name="task_reminder" valuePropName="checked" label="任务提醒">
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Text type="secondary">待办任务到期提醒</Text>
          </Col>
          <Col span={12}>
            <Form.Item name="opportunity_reminder" valuePropName="checked" label="机会提醒">
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Text type="secondary">销售机会跟进提醒</Text>
          </Col>
        </Row>

        <Row gutter={[48, 24]}>
          <Col span={12}>
            <Form.Item name="customer_reminder" valuePropName="checked" label="客户提醒">
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Text type="secondary">客户相关动态提醒</Text>
          </Col>
          <Col span={12}>
            <Form.Item name="system_notice" valuePropName="checked" label="系统通知">
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Text type="secondary">系统更新、维护等通知</Text>
          </Col>
        </Row>

        <Row gutter={[48, 24]}>
          <Col span={12}>
            <Form.Item name="daily_report" valuePropName="checked" label="日报">
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Text type="secondary">每日工作总结报告</Text>
          </Col>
          <Col span={12}>
            <Form.Item name="weekly_report" valuePropName="checked" label="周报">
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Text type="secondary">每周工作总结报告</Text>
          </Col>
        </Row>

        <Divider />

        {/* 提醒时间 */}
        <Title level={5}>提醒时间</Title>
        <Form.Item name="reminder_time" label="每日提醒时间">
          <TimePicker format="HH:mm" />
        </Form.Item>
        <Text type="secondary">设置每日接收提醒的时间</Text>

        <Divider />

        {/* 测试通知 */}
        <Title level={5}>测试通知</Title>
        <Space>
          <Button icon={<SendOutlined />} onClick={() => handleTestNotification('email')}>
            测试邮件
          </Button>
          <Button icon={<SendOutlined />} onClick={() => handleTestNotification('qq')}>
            测试QQ
          </Button>
        </Space>

        <Divider />

        <Form.Item>
          <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={saving}>
            保存设置
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default NotificationSettings;
