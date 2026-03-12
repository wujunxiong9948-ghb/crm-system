import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Input,
  Select,
  Space,
  Card,
  Tag,
  Modal,
  message,
  Popconfirm,
  Statistic,
  Row,
  Col,
} from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  ExportOutlined,
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
} from '@ant-design/icons';
import { apiService, apiEndpoints } from '../../services/api';
import type { ColumnsType } from 'antd/es/table';
import CustomerForm from './CustomerForm';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;

interface Customer {
  id: number;
  name: string;
  company: string;
  phone: string;
  email: string;
  address: string;
  industry: string;
  customer_type: string;
  source: string;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

interface CustomerStats {
  total_customers: number;
  recent_customers: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  by_source: Record<string, number>;
}

const CustomerList: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<CustomerStats | null>(null);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    pages: 1,
  });
  const [searchParams, setSearchParams] = useState({
    search: '',
    type: '',
    status: '',
    page: 1,
    per_page: 20,
  });
  const [formVisible, setFormVisible] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);

  // 获取客户列表
  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchParams.search) params.append('search', searchParams.search);
      if (searchParams.type) params.append('type', searchParams.type);
      if (searchParams.status) params.append('status', searchParams.status);
      params.append('page', searchParams.page.toString());
      params.append('per_page', searchParams.per_page.toString());

      const response = await apiService.get(`${apiEndpoints.customers.list}?${params}`);
      // 后端返回的是直接的数据结构，不是包装在ApiResponse中
      setCustomers(response.customers || []);
      setPagination(
        response.pagination || {
          current: 1,
          pageSize: 20,
          total: 0,
          pages: 1,
        }
      );
    } catch (error) {
      message.error('获取客户列表失败');
      console.error('获取客户列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取客户统计
  const fetchStats = async () => {
    try {
      const response = await apiService.get(apiEndpoints.customers.stats);
      // 后端返回的是直接的数据结构
      setStats(
        response || {
          total_customers: 0,
          recent_customers: 0,
          by_type: {},
          by_status: {},
          by_source: {},
        }
      );
    } catch (error) {
      console.error('获取客户统计失败:', error);
    }
  };

  useEffect(() => {
    fetchCustomers();
    fetchStats();
  }, [searchParams]);

  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchParams(prev => ({
      ...prev,
      search: value,
      page: 1,
    }));
  };

  // 处理分页
  const handleTableChange = (pagination: any) => {
    setSearchParams(prev => ({
      ...prev,
      page: pagination.current,
      per_page: pagination.pageSize,
    }));
  };

  // 删除客户
  const handleDelete = async (id: number) => {
    try {
      await apiService.delete(apiEndpoints.customers.delete(id));
      message.success('客户删除成功');
      fetchCustomers();
      fetchStats();
    } catch (error) {
      message.error('删除客户失败');
      console.error('删除客户失败:', error);
    }
  };

  // 编辑客户
  const handleEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setFormVisible(true);
  };

  // 创建客户
  const handleCreate = () => {
    setEditingCustomer(null);
    setFormVisible(true);
  };

  // 表单提交成功
  const handleFormSuccess = () => {
    setFormVisible(false);
    fetchCustomers();
    fetchStats();
  };

  // 导出数据
  const handleExport = () => {
    message.info('导出功能开发中...');
  };

  // 表格列定义
  const columns: ColumnsType<Customer> = [
    {
      title: '客户名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{record.company}</div>
        </div>
      ),
    },
    {
      title: '联系方式',
      dataIndex: 'phone',
      key: 'phone',
      width: 120,
      render: (text, record) => (
        <div>
          <div>
            <PhoneOutlined style={{ marginRight: 4 }} /> {text}
          </div>
          {record.email && (
            <div style={{ fontSize: '12px' }}>
              <MailOutlined style={{ marginRight: 4 }} /> {record.email}
            </div>
          )}
        </div>
      ),
    },
    {
      title: '客户类型',
      dataIndex: 'customer_type',
      key: 'customer_type',
      width: 100,
      render: (type: string) => {
        const colors: Record<string, string> = {
          VIP客户: 'red',
          现有客户: 'blue',
          潜在客户: 'green',
        };
        return <Tag color={colors[type] || 'default'}>{type}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => {
        const colors: Record<string, string> = {
          活跃: 'success',
          休眠: 'warning',
          流失: 'error',
        };
        return <Tag color={colors[status] || 'default'}>{status}</Tag>;
      },
    },
    {
      title: '来源',
      dataIndex: 'source',
      key: 'source',
      width: 80,
      render: (source: string) => <Tag>{source}</Tag>,
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right' as const,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个客户吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />} size="small">
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      {stats && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总客户数"
                value={stats.total_customers}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="30天新增"
                value={stats.recent_customers}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="VIP客户"
                value={stats.by_type['VIP客户'] || 0}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#f5222d' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="活跃客户"
                value={stats.by_status['活跃'] || 0}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 搜索和操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space size="large" style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Search
              placeholder="搜索客户名称、公司、电话..."
              allowClear
              enterButton={<SearchOutlined />}
              onSearch={handleSearch}
              style={{ width: 300 }}
            />
            <Select
              placeholder="客户类型"
              allowClear
              style={{ width: 120 }}
              onChange={value => setSearchParams(prev => ({ ...prev, type: value, page: 1 }))}
            >
              <Option value="潜在客户">潜在客户</Option>
              <Option value="现有客户">现有客户</Option>
              <Option value="VIP客户">VIP客户</Option>
            </Select>
            <Select
              placeholder="客户状态"
              allowClear
              style={{ width: 120 }}
              onChange={value => setSearchParams(prev => ({ ...prev, status: value, page: 1 }))}
            >
              <Option value="活跃">活跃</Option>
              <Option value="休眠">休眠</Option>
              <Option value="流失">流失</Option>
            </Select>
          </Space>

          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => {
                setSearchParams({
                  search: '',
                  type: '',
                  status: '',
                  page: 1,
                  per_page: 20,
                });
              }}
            >
              重置
            </Button>
            <Button icon={<ExportOutlined />} onClick={handleExport}>
              导出
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              新建客户
            </Button>
          </Space>
        </Space>
      </Card>

      {/* 客户表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={customers}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: total => `共 ${total} 条记录`,
          }}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 客户表单模态框 */}
      <Modal
        title={editingCustomer ? '编辑客户' : '新建客户'}
        open={formVisible}
        onCancel={() => setFormVisible(false)}
        footer={null}
        width={800}
        destroyOnClose
      >
        <CustomerForm
          customer={editingCustomer}
          onSuccess={handleFormSuccess}
          onCancel={() => setFormVisible(false)}
        />
      </Modal>
    </div>
  );
};

export default CustomerList;
