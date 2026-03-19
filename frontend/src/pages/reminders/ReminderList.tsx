import React, { useState, useEffect } from 'react';
import { Card, List, Tag, Button, Space, Badge, Typography, Tabs, Empty, message, Popconfirm } from 'antd';
import { BellOutlined, CheckOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { apiService } from '@/services/api';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface Reminder {
  id: number;
  reminder_type: string;
  related_type: string;
  related_id: number;
  title: string;
  content: string;
  remind_at: string;
  status: 'pending' | 'sent' | 'dismissed';
}

const ReminderList: React.FC = () => {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [stats, setStats] = useState({ pending: 0, today: 0, overdue: 0 });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('pending');

  // 获取提醒列表
  const fetchReminders = async (status?: string) => {
    setLoading(true);
    try {
      const response = await apiService.get('/reminders', {
        params: { status }
      });
      
      if (response && response.data) {
        setReminders(response.data.items || []);
      }
    } catch (error) {
      console.error('获取提醒失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取统计
  const fetchStats = async () => {
    try {
      const response = await apiService.get('/reminders/stats');
      if (response && response.data) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('获取统计失败:', error);
    }
  };

  // 标记为已完成
  const handleComplete = async (id: number) => {
    try {
      await apiService.put(`/reminders/${id}`, { status: 'dismissed' });
      message.success('已标记为完成');
      fetchReminders(activeTab === 'all' ? undefined : activeTab);
      fetchStats();
    } catch (error) {
      message.error('操作失败');
    }
  };

  // 删除提醒
  const handleDelete = async (id: number) => {
    try {
      await apiService.delete(`/reminders/${id}`);
      message.success('删除成功');
      fetchReminders(activeTab === 'all' ? undefined : activeTab);
      fetchStats();
    } catch (error) {
      message.error('删除失败');
    }
  };

  useEffect(() => {
    fetchReminders('pending');
    fetchStats();
  }, []);

  const handleTabChange = (key: string) => {
    setActiveTab(key);
    fetchReminders(key === 'all' ? undefined : key);
  };

  // 获取提醒类型标签
  const getTypeTag = (type: string) => {
    const typeMap: Record<string, { color: string; text: string }> = {
      follow_up: { color: 'blue', text: '跟进提醒' },
      order_expiry: { color: 'orange', text: '订单到期' }
    };
    const config = typeMap[type] || { color: 'default', text: type };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      pending: { color: 'warning', text: '待处理' },
      sent: { color: 'processing', text: '已发送' },
      dismissed: { color: 'success', text: '已完成' }
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>
        <BellOutlined /> 提醒中心
        <Badge count={stats.pending} style={{ marginLeft: 16 }} />
      </Title>

      {/* 统计卡片 */}
      <Space size="large" style={{ marginBottom: 24 }}>
        <Card>
          <Badge count={stats.pending} showZero>
            <Text strong>待处理</Text>
          </Badge>
        </Card>
        <Card>
          <Badge count={stats.today} showZero style={{ backgroundColor: '#52c41a' }}>
            <Text strong>今日</Text>
          </Badge>
        </Card>
        <Card>
          <Badge count={stats.overdue} showZero style={{ backgroundColor: '#ff4d4f' }}>
            <Text strong>已逾期</Text>
          </Badge>
        </Card>
        <Button icon={<ReloadOutlined />} onClick={() => { fetchReminders(activeTab); fetchStats(); }}>
          刷新
        </Button>
      </Space>

      {/* 提醒列表 */}
      <Card>
        <Tabs activeKey={activeTab} onChange={handleTabChange}>
          <TabPane tab="待处理" key="pending">
            <ReminderListContent 
              reminders={reminders} 
              loading={loading}
              onComplete={handleComplete}
              onDelete={handleDelete}
              getTypeTag={getTypeTag}
              getStatusTag={getStatusTag}
            />
          </TabPane>
          <TabPane tab="全部" key="all">
            <ReminderListContent 
              reminders={reminders} 
              loading={loading}
              onComplete={handleComplete}
              onDelete={handleDelete}
              getTypeTag={getTypeTag}
              getStatusTag={getStatusTag}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

// 提醒列表内容组件
interface ReminderListContentProps {
  reminders: Reminder[];
  loading: boolean;
  onComplete: (id: number) => void;
  onDelete: (id: number) => void;
  getTypeTag: (type: string) => React.ReactNode;
  getStatusTag: (status: string) => React.ReactNode;
}

const ReminderListContent: React.FC<ReminderListContentProps> = ({
  reminders,
  loading,
  onComplete,
  onDelete,
  getTypeTag,
  getStatusTag
}) => {
  if (reminders.length === 0) {
    return <Empty description="暂无提醒" />;
  }

  return (
    <List
      loading={loading}
      dataSource={reminders}
      renderItem={(item) => (
        <List.Item
          actions={[
            item.status === 'pending' && (
              <Button 
                type="primary" 
                icon={<CheckOutlined />} 
                size="small"
                onClick={() => onComplete(item.id)}
              >
                完成
              </Button>
            ),
            <Popconfirm
              title="确认删除"
              onConfirm={() => onDelete(item.id)}
            >
              <Button icon={<DeleteOutlined />} size="small" danger>
                删除
              </Button>
            </Popconfirm>
          ]}
        >
          <List.Item.Meta
            title={
              <Space>
                {getTypeTag(item.reminder_type)}
                <Text strong>{item.title}</Text>
                {getStatusTag(item.status)}
              </Space>
            }
            description={
              <div>
                <Text type="secondary">{item.content}</Text>
                <div style={{ marginTop: 8 }}>
                  <Text type="secondary">
                    提醒时间：{dayjs(item.remind_at).format('YYYY-MM-DD HH:mm')}
                  </Text>
                </div>
              </div>
            }
          />
        </List.Item>
      )}
    />
  );
};

export default ReminderList;
