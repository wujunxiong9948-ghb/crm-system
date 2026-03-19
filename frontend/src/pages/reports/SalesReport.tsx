import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, DatePicker, Select, Table, Spin, Alert, Space, Typography } from 'antd';
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
  DollarOutlined,
  ShoppingCartOutlined,
  RiseOutlined,
  FallOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { apiService, apiEndpoints } from '@/services/api';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Title } = Typography;

// 颜色配置
const COLORS = ['#1890ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1', '#13c2c2', '#eb2f96'];

interface SalesTrend {
  period: string;
  order_count: number;
  total_amount: number;
  avg_amount: number;
}

interface PerformanceSummary {
  total_orders: number;
  total_amount: number;
  avg_order_value: number;
  previous_period_amount: number;
  growth_rate: number;
}

interface SalesRanking {
  sales_person: string;
  order_count: number;
  total_amount: number;
}

interface StatusDistribution {
  status: string;
  count: number;
  amount: number;
}

interface SalesReportData {
  sales_trend: SalesTrend[];
  performance_summary: PerformanceSummary;
  sales_ranking: SalesRanking[];
  order_status_distribution: StatusDistribution[];
  payment_status_distribution: StatusDistribution[];
  date_range: {
    start_date: string;
    end_date: string;
  };
}

const SalesReport: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SalesReportData | null>(null);
  const [groupBy, setGroupBy] = useState('month');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>([
    dayjs().subtract(6, 'month'),
    dayjs(),
  ]);

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = { group_by: groupBy };
      if (dateRange) {
        params.start_date = dateRange[0].format('YYYY-MM-DD');
        params.end_date = dateRange[1].format('YYYY-MM-DD');
      }

      const response = await apiService.get(apiEndpoints.reports.sales, { params });
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
  }, [groupBy, dateRange]);

  // 销售排行表格列
  const rankingColumns = [
    {
      title: '排名',
      dataIndex: 'index',
      key: 'index',
      width: 80,
      render: (_: any, __: any, index: number) => index + 1,
    },
    {
      title: '销售人员',
      dataIndex: 'sales_person',
      key: 'sales_person',
    },
    {
      title: '订单数',
      dataIndex: 'order_count',
      key: 'order_count',
      align: 'right' as const,
    },
    {
      title: '销售金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      align: 'right' as const,
      render: (value: number) => `¥${value?.toLocaleString()}`,
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

  const summary = data?.performance_summary;
  const trendData = data?.sales_trend || [];
  const rankingData = data?.sales_ranking || [];
  const statusData = data?.order_status_distribution || [];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>销售报表</Title>

      {/* 筛选条件 */}
      <Card style={{ marginBottom: 24 }}>
        <Space size="large">
          <span>时间范围：</span>
          <RangePicker
            value={dateRange}
            onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
            format="YYYY-MM-DD"
          />
          <span>分组方式：</span>
          <Select value={groupBy} onChange={setGroupBy} style={{ width: 120 }}>
            <Option value="month">按月</Option>
            <Option value="quarter">按季度</Option>
            <Option value="year">按年</Option>
          </Select>
        </Space>
      </Card>

      {/* 业绩汇总 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总订单数"
              value={summary?.total_orders || 0}
              prefix={<ShoppingCartOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总销售额"
              value={summary?.total_amount || 0}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均订单金额"
              value={summary?.avg_order_value || 0}
              precision={2}
              prefix="¥"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="环比增长率"
              value={summary?.growth_rate || 0}
              precision={2}
              suffix="%"
              prefix={summary && summary.growth_rate >= 0 ? <RiseOutlined /> : <FallOutlined />}
              valueStyle={{ color: summary && summary.growth_rate >= 0 ? '#52c41a' : '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 销售趋势图 */}
      <Card title="销售趋势" style={{ marginBottom: 24 }}>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="total_amount"
              name="销售金额"
              stroke="#1890ff"
              strokeWidth={2}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="order_count"
              name="订单数"
              stroke="#52c41a"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      <Row gutter={16}>
        {/* 销售人员排行 */}
        <Col xs={24} lg={12} style={{ marginBottom: 24 }}>
          <Card title="销售人员业绩排行" extra={<TeamOutlined />}>
            <Table
              dataSource={rankingData}
              columns={rankingColumns}
              pagination={false}
              size="small"
              rowKey={(record, index) => `${record.sales_person}-${index}`}
            />
          </Card>
        </Col>

        {/* 订单状态分布 */}
        <Col xs={24} lg={12} style={{ marginBottom: 24 }}>
          <Card title="订单状态分布">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ status, percent }) => `${status} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="status"
                >
                  {statusData.map((entry, index) => (
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
    </div>
  );
};

export default SalesReport;
