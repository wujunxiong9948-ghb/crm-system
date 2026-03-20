import React from 'react';
import { Card, Tabs, Badge, List, Typography, Tag, Empty, Spin } from 'antd';
import { 
  BellOutlined, 
  CustomerServiceOutlined, 
  ShoppingCartOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi, TodoItem } from '@/services/dashboardApi';
import dayjs from 'dayjs';
import './TodoPanel.less';

const { Text } = Typography;
const { TabPane } = Tabs;

export const TodoPanel: React.FC = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['todos'],
    queryFn: () => dashboardApi.getTodos(),
    staleTime: 30 * 1000, // 30秒缓存
    refetchInterval: 60 * 1000, // 每分钟自动刷新
  });

  if (isLoading) {
    return <Card loading={true} title="待办事项" />;
  }

  const categories = data?.categories || {
    reminders: { count: 0, items: [] },
    pending_contacts: { count: 0, items: [] },
    pending_orders: { count: 0, items: [] }
  };

  const totalCount = data?.total_count || 0;

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'red';
      case 'normal': return 'blue';
      case 'low': return 'green';
      default: return 'default';
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'high': return '紧急';
      case 'normal': return '普通';
      case 'low': return '低';
      default: return '普通';
    }
  };

  const renderTodoItem = (item: TodoItem) => {
    return (
      <List.Item className="todo-item">
        <div className="todo-content">
          <div className="todo-title-row">
            <Text strong className="todo-title">{item.title}</Text>
            <Tag color={getPriorityColor(item.priority)} size="small">
              {getPriorityText(item.priority)}
            </Tag>
          </div>
          <div className="todo-meta">
            {item.customer_name && (
              <Text type="secondary" className="customer-name">
                客户: {item.customer_name}
              </Text>
            )}
            {item.due_time && (
              <Text type="secondary" className="due-time">
                <ClockCircleOutlined /> {dayjs(item.due_time).format('HH:mm')}
              </Text>
            )}
          </div>
        </div>
      </List.Item>
    );
  };

  const renderEmpty = () => (
    <Empty 
      image={Empty.PRESENTED_IMAGE_SIMPLE} 
      description="暂无待办事项"
    />
  );

  return (
    <Card 
      title={
        <span>
          <BellOutlined /> 待办事项
          {totalCount > 0 && <Badge count={totalCount} style={{ marginLeft: 8 }} />}
        </span>
      }
      className="todo-panel"
    >
      <Tabs defaultActiveKey="reminders">
        <TabPane 
          tab={
            <span>
              <BellOutlined /> 今日提醒
              {categories.reminders.count > 0 && (
                <Badge count={categories.reminders.count} style={{ marginLeft: 4 }} />
              )}
            </span>
          } 
          key="reminders"
        >
          {categories.reminders.items.length > 0 ? (
            <List
              dataSource={categories.reminders.items}
              renderItem={renderTodoItem}
              size="small"
            />
          ) : renderEmpty()}
        </TabPane>

        <TabPane 
          tab={
            <span>
              <CustomerServiceOutlined /> 待跟进
              {categories.pending_contacts.count > 0 && (
                <Badge count={categories.pending_contacts.count} style={{ marginLeft: 4 }} />
              )}
            </span>
          } 
          key="contacts"
        >
          {categories.pending_contacts.items.length > 0 ? (
            <List
              dataSource={categories.pending_contacts.items}
              renderItem={renderTodoItem}
              size="small"
            />
          ) : renderEmpty()}
        </TabPane>

        <TabPane 
          tab={
            <span>
              <ShoppingCartOutlined /> 待处理订单
              {categories.pending_orders.count > 0 && (
                <Badge count={categories.pending_orders.count} style={{ marginLeft: 4 }} />
              )}
            </span>
          } 
          key="orders"
        >
          {categories.pending_orders.items.length > 0 ? (
            <List
              dataSource={categories.pending_orders.items}
              renderItem={renderTodoItem}
              size="small"
            />
          ) : renderEmpty()}
        </TabPane>
      </Tabs>
    </Card>
  );
};
