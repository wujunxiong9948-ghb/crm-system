import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Card,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Popconfirm,
  message,
  Row,
  Col,
  Statistic,
  Typography,
  Tooltip,
  Empty,
  Spin,
  Badge,
  DatePicker,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  FilterOutlined,
  FileTextOutlined,
  DollarOutlined,
  CheckCircleOutlined,
  CarOutlined,
  ToolOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import { usePermission, PERMISSION_CODES } from '@/utils/permission';
import { Order } from '@/types';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import type { FilterValue, SorterResult } from 'antd/es/table/interface';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface OrderStats {
  total: number;
  pending: number;
  producing: number;
  shipped: number;
  completed: number;
  cancelled: number;
  total_amount: number;
  pending_amount: number;
  completed_amount: number;
  month_orders: number;
  month_amount: number;
}

const OrderList: React.FC = () => {
  const navigate = useNavigate();
  const { hasPermissionCode } = usePermission();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<OrderStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  // 搜索和筛选状态
  const [searchText, setSearchText] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [selectedPaymentStatus, setSelectedPaymentStatus] = useState<string>('');

  // 分页状态
  const [pagination, setPagination] = useState<TablePaginationConfig>({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total) => `共 ${total} 条记录`,
  });

  // 获取订单列表
  const fetchOrders = useCallback(async (
    page = 1,
    pageSize = 20,
    search = '',
    status = '',
    paymentStatus = ''
  ) => {
    setLoading(true);
    try {
      const response = await apiService.get('/orders', {
        params: {
          page,
          per_page: pageSize,
          search,
          status,
          payment_status: paymentStatus,
          sort_by: 'created_at',
          sort_order: 'desc',
        },
      });

      if (response.success) {
        setOrders(response.data || []);
        setPagination(prev => ({
          ...prev,
          current: page,
          pageSize,
          total: response.pagination?.total || 0,
        }));
      } else {
        message.error(response.message || '获取订单列表失败');
      }
    } catch (error) {
      console.error('获取订单列表失败:', error);
      message.error('获取订单列表失败');
    } finally {
      setLoading(false);
    }
  }, []);

  // 获取统计数据
  const fetchStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const response = await apiService.get('/orders/stats/summary');
      if (response.success) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('获取统计数据失败:', error);
    } finally {
      setStatsLoading(false);
    }
  }, []);

  // 初始加载
  useEffect(() => {
    fetchOrders();
    fetchStats();
  }, [fetchOrders, fetchStats]);

  // 处理搜索
  const handleSearch = () => {
    fetchOrders(1, pagination.pageSize || 20, searchText, selectedStatus, selectedPaymentStatus);
  };

  // 处理重置
  const handleReset = () => {
    setSearchText('');
    setSelectedStatus('');
    setSelectedPaymentStatus('');
    fetchOrders(1, 20, '', '', '');
  };

  // 处理表格变化
  const handleTableChange = (
    newPagination: TablePaginationConfig,
    filters: Record<string, FilterValue | null>,
    sorter: SorterResult<Order> | SorterResult<Order>[]
  ) => {
    fetchOrders(
      newPagination.current || 1,
      newPagination.pageSize || 20,
      searchText,
      selectedStatus,
      selectedPaymentStatus
    );
  };

  // 删除订单
  const handleDelete = async (id: number) => {
    try {
      const response = await apiService.delete(`/orders/${id}`);
      if (response.success) {
        message.success('订单删除成功');
        fetchOrders(
          pagination.current || 1,
          pagination.pageSize || 20,
          searchText,
          selectedStatus,
          selectedPaymentStatus
        );
        fetchStats();
      } else {
        message.error(response.message || '删除失败');
      }
    } catch (error) {
      console.error('删除订单失败:', error);
      message.error('删除订单失败');
    }
  };

  // 更新订单状态
  const handleUpdateStatus = async (id: number, status: string) => {
    try {
      const response = await apiService.put(`/orders/${id}/status`, { status });
      if (response.success) {
        message.success('订单状态更新成功');
        fetchOrders(
          pagination.current || 1,
          pagination.pageSize || 20,
          searchText,
          selectedStatus,
          selectedPaymentStatus
        );
        fetchStats();
      } else {
        message.error(response.message || '更新失败');
      }
    } catch (error) {
      console.error('更新订单状态失败:', error);
      message.error('更新订单状态失败');
    }
  };

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
      '待处理': { color: 'default', icon: <FileTextOutlined />, text: '待处理' },
      '生产中': { color: 'processing', icon: <ToolOutlined />, text: '生产中' },
      '已发货': { color: 'warning', icon: <CarOutlined />, text: '已发货' },
      '已完成': { color: 'success', icon: <CheckCircleOutlined />, text: '已完成' },
      '已取消': { color: 'error', icon: <DeleteOutlined />, text: '已取消' },
    };
    const config = statusMap[status] || { color: 'default', icon: null, text: status };
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  // 获取支付状态标签
  const getPaymentStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      '未支付': { color: 'error', text: '未支付' },
      '部分支付': { color: 'warning', text: '部分支付' },
      '已支付': { color: 'success', text: '已支付' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 表格列定义
  const columns: ColumnsType<Order> = [
    {
      title: '订单编号',
      dataIndex: 'order_number',
      key: 'order_number',
      width: 150,
      render: (code: string, record: Order) => (
        <a onClick={() => navigate(`/orders/${record.id}`)} className="font-medium">
          {code}
        </a>
      ),
    },
    {
      title: '客户',
      key: 'customer',
      width: 180,
      render: (_, record: Order) => (
        <div>
          <div 
            className="font-medium cursor-pointer text-blue-600 hover:text-blue-800"
            onClick={() => record.customer?.id && navigate(`/customers/${record.customer.id}`)}
          >
            {record.customer?.name || '-'}
          </div>
          <div className="text-gray-500 text-sm">{record.customer?.company || ''}</div>
        </div>
      ),
    },
    {
      title: '关联机会',
      key: 'opportunity',
      width: 150,
      render: (_, record: Order) => (
        record.opportunity ? (
          <a onClick={() => navigate(`/opportunities/${record.opportunity_id}`)}>
            {record.opportunity.name}
          </a>
        ) : (
          '-'
        )
      ),
    },
    {
      title: '订单金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 120,
      align: 'right',
      render: (amount: number) => (
        <Text strong>{amount ? `¥${amount.toFixed(2)}` : '-'}</Text>
      ),
    },
    {
      title: '订单状态',
      dataIndex: 'status',
      key: 'status',
      width: 110,
      align: 'center',
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '支付状态',
      dataIndex: 'payment_status',
      key: 'payment_status',
      width: 100,
      align: 'center',
      render: (status: string) => getPaymentStatusTag(status),
    },
    {
      title: '订单日期',
      dataIndex: 'order_date',
      key: 'order_date',
      width: 120,
      render: (date: string) => date || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (date: string) => date ? new Date(date).toLocaleString('zh-CN') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record: Order) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/orders/${record.id}`)}
            />
          </Tooltip>
          {hasPermissionCode(PERMISSION_CODES.ORDER_UPDATE) && (
            <Tooltip title="编辑">
              <Button
                type="text"
                icon={<EditOutlined />}
                onClick={() => navigate(`/orders/${record.id}/edit`)}
              />
            </Tooltip>
          )}
          {record.status === '待处理' && hasPermissionCode(PERMISSION_CODES.ORDER_UPDATE) && (
            <Tooltip title="开始生产">
              <Button
                type="text"
                icon={<ToolOutlined />}
                onClick={() => handleUpdateStatus(record.id, '生产中')}
              />
            </Tooltip>
          )}
          {record.status === '生产中' && hasPermissionCode(PERMISSION_CODES.ORDER_UPDATE) && (
            <Tooltip title="标记发货">
              <Button
                type="text"
                icon={<CarOutlined />}
                onClick={() => handleUpdateStatus(record.id, '已发货')}
              />
            </Tooltip>
          )}
          {hasPermissionCode(PERMISSION_CODES.ORDER_DELETE) && (
            <Popconfirm
              title="确认删除"
              description="确定要删除这个订单吗？此操作不可恢复。"
              onConfirm={() => handleDelete(record.id)}
              okText="删除"
              cancelText="取消"
              okButtonProps={{ danger: true }}
            >
              <Tooltip title="删除">
                <Button type="text" danger icon={<DeleteOutlined />} />
              </Tooltip>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <Title level={2}>订单管理</Title>
        <Text type="secondary">管理客户订单，跟踪订单状态和交付进度</Text>
      </div>

      {/* 统计卡片 */}
      <Spin spinning={statsLoading}>
        <Row gutter={16} className="mb-6">
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="订单总数"
                value={stats?.total || 0}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="本月订单"
                value={stats?.month_orders || 0}
                suffix={`¥${(stats?.month_amount || 0).toFixed(0)}`}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="待处理订单"
                value={stats?.pending || 0}
                suffix={`+${stats?.producing || 0}生产中`}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="已完成金额"
                value={stats?.completed_amount || 0}
                precision={2}
                prefix="¥"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        </Row>
      </Spin>

      {/* 搜索和筛选 */}
      <Card className="mb-6">
        <Row gutter={16} align="middle">
          <Col xs={24} sm={12} md={6} lg={6}>
            <Input
              placeholder="搜索订单号、客户名称..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={5} lg={5}>
            <Select
              placeholder="订单状态"
              style={{ width: '100%' }}
              value={selectedStatus || undefined}
              onChange={setSelectedStatus}
              allowClear
            >
              <Option value="待处理">待处理</Option>
              <Option value="生产中">生产中</Option>
              <Option value="已发货">已发货</Option>
              <Option value="已完成">已完成</Option>
              <Option value="已取消">已取消</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={5} lg={5}>
            <Select
              placeholder="支付状态"
              style={{ width: '100%' }}
              value={selectedPaymentStatus || undefined}
              onChange={setSelectedPaymentStatus}
              allowClear
            >
              <Option value="未支付">未支付</Option>
              <Option value="部分支付">部分支付</Option>
              <Option value="已支付">已支付</Option>
            </Select>
          </Col>
          <Col xs={24} sm={24} md={8} lg={8}>
            <Space>
              <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                搜索
              </Button>
              <Button icon={<ReloadOutlined />} onClick={handleReset}>
                重置
              </Button>
              {hasPermissionCode(PERMISSION_CODES.ORDER_CREATE) && (
                <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/orders/new')}>
                  新建订单
                </Button>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 订单列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={orders}
          rowKey="id"
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 1400 }}
          locale={{
            emptyText: (
              <Empty
                description="暂无订单数据"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            ),
          }}
        />
      </Card>
    </div>
  );
};

export default OrderList;