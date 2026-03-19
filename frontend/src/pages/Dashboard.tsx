import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Table, Progress, Space, Typography, Spin, Alert } from 'antd';
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
import { apiService, apiEndpoints } from '@/services/api';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

// 颜色配置
const COLORS = ['#1890ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1', '#13c2c2'];

interface DashboardData {
  today: {
    orders: number;
    amount: number;
  };
  this_month: {
    orders: number;
    amount: number;
    new_customers: number;
  };
  customers: {
    total: number;
    new_this_month: number;
  };
  opportunities: {
    total: number;
    active: number;
    total_expected: number;
  };
  pending_orders: number;
  week_trend: {
    date: string;
    amount: number;
  }[];
  opportunity_stages: {
    stage: string;
    count: number;
    expected_value: number;
  }[];
}

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

// 模拟活动数据（实际应从API获取）
const recentActivities = [
  {
    key: '1',
    type: '任务',
    title: '跟进锦江酒店的需求',
    customer: '张经理',
    dueDate: dayjs().add(2, 'day').format('YYYY-MM-DD'),
    priority: '高',
    status: '待处理',
  },
  {
    key: '2',
    type: '提醒',
    title: '发送产品报价',
    customer: '李总',
    dueDate: dayjs().add(1, 'day').format('YYYY-MM-DD'),
    priority: '中',
    status: '进行中',
  },
  {
    key: '3',
    type: '通知',
    title: '新客户注册',
    customer: '王经理',
    dueDate: dayjs().format('YYYY-MM-DD'),
    priority: '低',
    status: '已完成',
  },
  {
    key: '4',
    type: '任务',
    title: '准备展会材料',
    customer: '赵总',
    dueDate: dayjs().add(3, 'day').format('YYYY-MM-DD'),
    priority: '中',
    status: '待处理',
  },
];

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DashboardData | null>(null);

  // 加载仪表盘数据
  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.get(apiEndpoints.reports.dashboard);
      if (response.success) {
        setData(response.data);
      } else {
        setError(response.message || '加载数据失败');
      }
    } catch (err: any) {
      setError(err.message || '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 24 }}>
        <Alert message="错误" description={error} type="error" showIcon />
      </div>
    );
  }

  // 准备图表数据
  const weekTrendData = data?.week_trend?.map(item => ({
    date: dayjs(item.date).format('MM-DD'),
    amount: item.amount,
  })) || [];

  const opportunityChartData = data?.opportunity_stages?.map(item => ({
    stage: item.stage,
    count: item.count,
    value: item.expected_value,
  })) || [];

  // 客户分布数据（从客户分析API获取，这里使用模拟分布）
  const customerDistribution = [
    { name: '潜在客户', value: 35, color: '#1890ff' },
    { name: '现有客户', value: 40, color: '#52c41a' },
    { name: 'VIP客户', value: 15, color: '#faad14' },
    { name: '流失客户', value: 10, color: '#ff4d4f' },
  ];

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
              value={data?.customers?.total || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <Progress 
              percent={Math.min((data?.customers?.new_this_month || 0) * 5, 100)} 
              size="small" 
              status="active" 
            />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              本月新增 {data?.customers?.new_this_month || 0} 个客户
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="进行中机会"
              value={data?.opportunities?.active || 0}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Progress percent={68} size="small" status="active" />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              预计成交金额 ¥{(data?.opportunities?.total_expected || 0).toLocaleString()}
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="本月订单"
              value={data?.this_month?.orders || 0}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
            <Progress percent={85} size="small" status="active" />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              待处理 {data?.pending_orders || 0} 个订单
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="本月营收"
              value={data?.this_month?.amount || 0}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
              suffix="¥"
            />
            <Progress percent={92} size="small" status="active" />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              今日营收 ¥{(data?.today?.amount || 0).toLocaleString()}
            </Text>
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="本周销售趋势" extra={<CalendarOutlined />}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={weekTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value: number) => `¥${value?.toLocaleString()}`} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="amount"
                  name="销售额(¥)"
                  stroke="#1890ff"
                  activeDot={{ r: 8 }}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="客户分布" extra={<UserOutlined />}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={customerDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {customerDistribution.map((entry, index) => (
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
              <BarChart data={opportunityChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="stage" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" name="机会数量">
                  {opportunityChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
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
              onClick={() => (window.location.href = '/customers')}
            >
              <UserOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
              <div style={{ marginTop: '8px' }}>新增客户</div>
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card
              hoverable
              style={{ textAlign: 'center' }}
              onClick={() => (window.location.href = '/opportunities')}
            >
              <RiseOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
              <div style={{ marginTop: '8px' }}>创建机会</div>
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card
              hoverable
              style={{ textAlign: 'center' }}
              onClick={() => (window.location.href = '/orders')}
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
