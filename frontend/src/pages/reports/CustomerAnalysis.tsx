import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, DatePicker, Table, Spin, Alert, Typography, Tag } from 'antd';
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
import {
  UserOutlined,
  UserAddOutlined,
  TeamOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { apiService, apiEndpoints } from '@/services/api';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Title } = Typography;

// 颜色配置
const COLORS = ['#1890ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1', '#13c2c2', '#eb2f96'];

interface CustomerGrowth {
  month: string;
  new_customers: number;
  cumulative_customers: number;
}

interface TypeDistribution {
  type: string;
  count: number;
}

interface CustomerValue {
  customer_id: number;
  customer_name: string;
  company: string;
  order_count: number;
  total_amount: number;
  last_order_date: string;
}

interface ActivityStats {
  active_30d: number;
  active_90d: number;
  total_customers: number;
  new_30d: number;
  inactive_customers: number;
}

interface CustomerAnalysisData {
  growth_trend: CustomerGrowth[];
  type_distribution: TypeDistribution[];
  status_distribution: TypeDistribution[];
  source_distribution: TypeDistribution[];
  value_analysis: CustomerValue[];
  activity_stats: ActivityStats;
  date_range: {
    start_date: string;
    end_date: string;
  };
}

const CustomerAnalysis: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<CustomerAnalysisData | null>(null);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>([
    dayjs().subtract(12, 'month'),
    dayjs(),
  ]);

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = {};
      if (dateRange) {
        params.start_date = dateRange[0].format('YYYY-MM-DD');
        params.end_date = dateRange[1].format('YYYY-MM-DD');
      }

      const response = await apiService.get(apiEndpoints.reports.customers, { params });
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
    loadData();
  }, [dateRange]);

  // 客户价值表格列
  const valueColumns = [
    {
      title: '排名',
      dataIndex: 'index',
      key: 'index',
      width: 60,
      render: (_: any, __: any, index: number) => index + 1,
    },
    {
      title: '客户名称',
      dataIndex: 'customer_name',
      key: 'customer_name',
    },
    {
      title: '公司名称',
      dataIndex: 'company',
      key: 'company',
    },
    {
      title: '订单数',
      dataIndex: 'order_count',
      key: 'order_count',
      align: 'right' as const,
    },
    {
      title: '累计消费',
      dataIndex: 'total_amount',
      key: 'total_amount',
      align: 'right' as const,
      render: (value: number) => `¥${value?.toLocaleString()}`,
    },
    {
      title: '最近下单',
      dataIndex: 'last_order_date',
      key: 'last_order_date',
      render: (value: string) => value ? dayjs(value).format('YYYY-MM-DD') : '-',
    },
  ];

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

  const activity = data?.activity_stats;
  const growthData = data?.growth_trend || [];
  const typeData = data?.type_distribution || [];
  const sourceData = data?.source_distribution || [];
  const valueData = data?.value_analysis || [];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>客户分析</Title>

      {/* 筛选条件 */}
      <Card style={{ marginBottom: 24 }}>
        <span style={{ marginRight: 8 }}>时间范围：</span>
        <RangePicker
          value={dateRange}
          onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
          format="YYYY-MM-DD"
        />
      </Card>

      {/* 活跃度统计 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总客户数"
              value={activity?.total_customers || 0}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="30天活跃客户"
              value={activity?.active_30d || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="30天新增客户"
              value={activity?.new_30d || 0}
              prefix={<UserAddOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="休眠客户"
              value={activity?.inactive_customers || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 客户增长趋势 */}
      <Card title="客户增长趋势" style={{ marginBottom: 24 }}>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={growthData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="new_customers"
              name="新增客户"
              stroke="#1890ff"
              strokeWidth={2}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="cumulative_customers"
              name="累计客户"
              stroke="#52c41a"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      <Row gutter={16}>
        {/* 客户类型分布 */}
        <Col xs={24} lg={8} style={{ marginBottom: 24 }}>
          <Card title="客户类型分布">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={typeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ type, percent }) => `${type} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={70}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="type"
                >
                  {typeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* 客户来源分布 */}
        <Col xs={24} lg={8} style={{ marginBottom: 24 }}>
          <Card title="客户来源分布">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={sourceData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="source" type="category" width={80} />
                <Tooltip />
                <Bar dataKey="count" name="客户数" fill="#1890ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* 客户状态分布 */}
        <Col xs={24} lg={8} style={{ marginBottom: 24 }}>
          <Card title="客户状态分布">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={data?.status_distribution || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ status, percent }) => `${status} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={70}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="status"
                >
                  {(data?.status_distribution || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 客户价值排行 */}
      <Card title="客户价值排行（TOP 20）" style={{ marginBottom: 24 }}>
        <Table
          dataSource={valueData}
          columns={valueColumns}
          pagination={{ pageSize: 10 }}
          size="small"
          rowKey="customer_id"
        />
      </Card>
    </div>
  );
};

export default CustomerAnalysis;
