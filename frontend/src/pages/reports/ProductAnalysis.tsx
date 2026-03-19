import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, DatePicker, Table, Spin, Alert, Typography, Tag } from 'antd';
import {
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
  ShoppingOutlined,
  AppstoreOutlined,
  DollarOutlined,
  InboxOutlined,
} from '@ant-design/icons';
import { apiService, apiEndpoints } from '@/services/api';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Title } = Typography;

// 颜色配置
const COLORS = ['#1890ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1', '#13c2c2', '#eb2f96'];

interface TopProduct {
  product_code: string;
  product_name: string;
  total_quantity: number;
  total_revenue: number;
  order_count: number;
}

interface CategoryStat {
  category: string;
  product_count: number;
  total_quantity: number;
  total_revenue: number;
}

interface InventoryStatus {
  total_products: number;
  status_breakdown: {
    status: string;
    count: number;
    percentage: number;
  }[];
}

interface ProductAnalysisData {
  top_products: TopProduct[];
  category_stats: CategoryStat[];
  inventory_status: InventoryStatus;
  date_range: {
    start_date: string;
    end_date: string;
  };
}

const ProductAnalysis: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ProductAnalysisData | null>(null);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>([
    dayjs().subtract(6, 'month'),
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

      const response = await apiService.get(apiEndpoints.reports.products, { params });
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

  // 热销产品表格列
  const productColumns = [
    {
      title: '排名',
      dataIndex: 'index',
      key: 'index',
      width: 60,
      render: (_: any, __: any, index: number) => index + 1,
    },
    {
      title: '产品编码',
      dataIndex: 'product_code',
      key: 'product_code',
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
    },
    {
      title: '销量',
      dataIndex: 'total_quantity',
      key: 'total_quantity',
      align: 'right' as const,
    },
    {
      title: '销售额',
      dataIndex: 'total_revenue',
      key: 'total_revenue',
      align: 'right' as const,
      render: (value: number) => `¥${value?.toLocaleString()}`,
    },
    {
      title: '订单数',
      dataIndex: 'order_count',
      key: 'order_count',
      align: 'right' as const,
    },
  ];

  // 分类统计表格列
  const categoryColumns = [
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: '产品数',
      dataIndex: 'product_count',
      key: 'product_count',
      align: 'right' as const,
    },
    {
      title: '销量',
      dataIndex: 'total_quantity',
      key: 'total_quantity',
      align: 'right' as const,
    },
    {
      title: '销售额',
      dataIndex: 'total_revenue',
      key: 'total_revenue',
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

  const inventory = data?.inventory_status;
  const topProducts = data?.top_products || [];
  const categoryStats = data?.category_stats || [];
  const statusBreakdown = inventory?.status_breakdown || [];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>产品分析</Title>

      {/* 筛选条件 */}
      <Card style={{ marginBottom: 24 }}>
        <span style={{ marginRight: 8 }}>时间范围：</span>
        <RangePicker
          value={dateRange}
          onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
          format="YYYY-MM-DD"
        />
      </Card>

      {/* 库存概览 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="产品总数"
              value={inventory?.total_products || 0}
              prefix={<AppstoreOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="热销产品数"
              value={topProducts.length}
              prefix={<ShoppingOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="产品分类数"
              value={categoryStats.length}
              prefix={<InboxOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* 热销产品排行 */}
        <Col xs={24} lg={14} style={{ marginBottom: 24 }}>
          <Card title="热销产品排行（TOP 20）">
            <Table
              dataSource={topProducts}
              columns={productColumns}
              pagination={{ pageSize: 10 }}
              size="small"
              rowKey="product_code"
            />
          </Card>
        </Col>

        {/* 产品状态分布 */}
        <Col xs={24} lg={10} style={{ marginBottom: 24 }}>
          <Card title="产品状态分布">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusBreakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ status, percent }) => `${status} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="status"
                >
                  {statusBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>

            {/* 状态详情列表 */}
            <div style={{ marginTop: 16 }}>
              {statusBreakdown.map((item, index) => (
                <div
                  key={item.status}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: '8px 0',
                    borderBottom: index < statusBreakdown.length - 1 ? '1px solid #f0f0f0' : 'none',
                  }}
                >
                  <span>
                    <span
                      style={{
                        display: 'inline-block',
                        width: 12,
                        height: 12,
                        backgroundColor: COLORS[index % COLORS.length],
                        borderRadius: '50%',
                        marginRight: 8,
                      }}
                    />
                    {item.status}
                  </span>
                  <span>
                    {item.count} 个 ({item.percentage}%)
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 分类销售统计 */}
      <Row gutter={16}>
        <Col xs={24} lg={12} style={{ marginBottom: 24 }}>
          <Card title="分类销量统计">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="total_quantity" name="销量" fill="#1890ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        <Col xs={24} lg={12} style={{ marginBottom: 24 }}>
          <Card title="分类销售额统计">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip formatter={(value: number) => `¥${value?.toLocaleString()}`} />
                <Legend />
                <Bar dataKey="total_revenue" name="销售额" fill="#52c41a" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 分类数据表格 */}
      <Card title="分类详细数据">
        <Table
          dataSource={categoryStats}
          columns={categoryColumns}
          pagination={false}
          size="small"
          rowKey="category"
        />
      </Card>
    </div>
  );
};

export default ProductAnalysis;
