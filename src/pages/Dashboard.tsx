import React from 'react';
import { Row, Col, Card, Statistic, Table, Progress, Space, Typography } from 'antd';
import {
  UserOutlined,
  ShoppingCartOutlined,
  DollarOutlined,
  RiseOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const { Title, Text } = Typography;

// 模拟数据
const salesData = [
  { month: '1月', sales: 4000, orders: 24 },
  { month: '2月', sales: 3000, orders: 13 },
  { month: '3月', sales: 2000, orders: 98 },
  { month: '4月', sales: 2780, orders: 39 },
  { month: '5月', sales: 1890, orders: 48 },
  { month: '6月', sales: 2390, orders: 38 },
  { month: '7月', sales: 3490, orders: 43 },
];

const customerData = [
  { name: '潜在客户', value: 40, color: '#1890ff' },
  { name: '现有客户', value: 30, color: '#52c41a' },
  { name: 'VIP客户', value: 20, color: '#faad14' },
  { name: '流失客户', value: 10, color: '#ff4d4f' },
];

const opportunityData = [
  { stage: '初步接触', count: 12, color: '#8c8c8c' },
  { stage: '需求分析', count: 8, color: '#1890ff' },
  { stage: '方案报价', count: 6, color: '#52c41a' },
  { stage: '谈判', count: 4, color: '#faad14' },
  { stage: '成交', count: 3, color: '#722ed1' },
  { stage: '丢失', count: 2, color: '#ff4d4f' },
];

const recentActivities = [
  {
    key: '1',
    type: '任务',
    title: '跟进张三的需求',
    customer: '张三',
    dueDate: '2026-03-15',
    priority: '高',
    status: '待处理',
  },
  {
    key: '2',
    type: '提醒',
    title: '发送产品报价',
    customer: '李四',
    dueDate: '2026-03-16',
    priority: '中',
    status: '进行中',
  },
  {
    key: '3',
    type: '通知',
    title: '新客户注册',
    customer: '王五',
    dueDate: '2026-03-14',
    priority: '低',
    status: '已完成',
  },
  {
    key: '4',
    type: '任务',
    title: '准备展会材料',
    customer: '赵六',
    dueDate: '2026-03-18',
    priority: '中',
    status: '待处理',
  },
];

const activityColumns = [
  {
    title: '类型',
    dataIndex: 'type',
    key: 'type',
    render: (type: string) => {
      const colors: Record<string, string> = {
        任务: '#1890ff',
        提醒: '#faad14',
        通知: '#52c41a',
      };
      return <Text style={{ color: colors[type] || '#8c8c8c' }}>{type}</Text>;
    },
  },
  {
    title: '标题',
    dataIndex: 'title',
    key: 'title',
  },
  {
    title: '客户',
    dataIndex: 'customer',
    key: 'customer',
  },
  {
    title: '截止日期',
    dataIndex: 'dueDate',
    key: 'dueDate',
  },
  {
    title: '优先级',
    dataIndex: 'priority',
    key: 'priority',
    render: (priority: string) => {
      const colors: Record<string, string> = {
        高: '#ff4d4f',
        中: '#faad14',
        低: '#52c41a',
      };
      return <Text style={{ color: colors[priority] || '#8c8c8c' }}>{priority}</Text>;
    },
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    render: (status: string) => {
      const colors: Record<string, string> = {
        待处理: '#8c8c8c',
        进行中: '#1890ff',
        已完成: '#52c41a',
      };
      return <Text style={{ color: colors[status] || '#8c8c8c' }}>{status}</Text>;
    },
  },
];

const Dashboard: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      {/* 标题 */}
      <Title level={2}>仪表盘</Title>
      <Text type="secondary">欢迎回来，这里是您的业务概览</Text>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总客户数"
              value={156}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <Progress percent={12} size="small" status="active" />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              本月新增 12 个客户
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="进行中机会"
              value={24}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Progress percent={68} size="small" status="active" />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              预计成交金额 ¥156,800
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="本月订单"
              value={42}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
            <Progress percent={85} size="small" status="active" />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              已完成 36 个订单
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="本月营收"
              value={128560}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
              suffix="¥"
            />
            <Progress percent={92} size="small" status="active" />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              同比增长 18%
            </Text>
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="销售趋势" extra={<CalendarOutlined />}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="sales"
                  name="销售额(¥)"
                  stroke="#1890ff"
                  activeDot={{ r: 8 }}
                />
                <Line type="monotone" dataKey="orders" name="订单数" stroke="#52c41a" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="客户分布" extra={<UserOutlined />}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={customerData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {customerData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 机会管道和活动提醒 */}
      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="销售机会管道" extra={<RiseOutlined />}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={opportunityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="stage" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" name="机会数量">
                  {opportunityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card
            title="最近活动"
            extra={
              <Space>
                <CheckCircleOutlined style={{ color: '#52c41a' }} />
                <ClockCircleOutlined style={{ color: '#faad14' }} />
                <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
              </Space>
            }
          >
            <Table
              dataSource={recentActivities}
              columns={activityColumns}
              pagination={false}
              size="small"
              scroll={{ y: 240 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 快速操作 */}
      <Card title="快速操作" style={{ marginTop: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={12} sm={6}>
            <Card
              hoverable
              style={{ textAlign: 'center' }}
              onClick={() => (window.location.href = '/customers/new')}
            >
              <UserOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
              <div style={{ marginTop: '8px' }}>新增客户</div>
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card
              hoverable
              style={{ textAlign: 'center' }}
              onClick={() => (window.location.href = '/opportunities/new')}
            >
              <RiseOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
              <div style={{ marginTop: '8px' }}>创建机会</div>
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card
              hoverable
              style={{ textAlign: 'center' }}
              onClick={() => (window.location.href = '/orders/new')}
            >
              <ShoppingCartOutlined style={{ fontSize: '24px', color: '#faad14' }} />
              <div style={{ marginTop: '8px' }}>新建订单</div>
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card
              hoverable
              style={{ textAlign: 'center' }}
              onClick={() => (window.location.href = '/reports/sales')}
            >
              <DollarOutlined style={{ fontSize: '24px', color: '#ff4d4f' }} />
              <div style={{ marginTop: '8px' }}>查看报表</div>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Dashboard;
