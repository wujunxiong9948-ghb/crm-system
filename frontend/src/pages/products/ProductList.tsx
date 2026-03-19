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
  Image,
  Empty,
  Spin,
  Badge,
  Divider,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  FilterOutlined,
  ImportOutlined,
  ExportOutlined,
  PictureOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import { usePermission, PERMISSION_CODES } from '@/utils/permission';
import { Product } from '@/types';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import type { FilterValue, SorterResult } from 'antd/es/table/interface';

const { Title, Text } = Typography;
const { Option } = Select;

interface ProductStats {
  total: number;
  available: number;
  out_of_stock: number;
  disabled: number;
  by_category: { category: string; count: number }[];
}

const ProductList: React.FC = () => {
  const navigate = useNavigate();
  const { hasPermissionCode } = usePermission();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<ProductStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [categories, setCategories] = useState<string[]>([]);

  // 搜索和筛选状态
  const [searchText, setSearchText] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  // 分页状态
  const [pagination, setPagination] = useState<TablePaginationConfig>({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total) => `共 ${total} 条记录`,
  });

  // 获取产品列表
  const fetchProducts = useCallback(async (
    page = 1,
    pageSize = 20,
    search = '',
    category = '',
    status = ''
  ) => {
    setLoading(true);
    try {
      const response = await apiService.get('/products', {
        params: {
          page,
          per_page: pageSize,
          search,
          category,
          status,
          sort_by: 'created_at',
          sort_order: 'desc',
        },
      });

      if (response.success) {
        setProducts(response.data || []);
        setPagination(prev => ({
          ...prev,
          current: page,
          pageSize,
          total: response.pagination?.total || 0,
        }));
      } else {
        message.error(response.message || '获取产品列表失败');
      }
    } catch (error) {
      console.error('获取产品列表失败:', error);
      message.error('获取产品列表失败');
    } finally {
      setLoading(false);
    }
  }, []);

  // 获取统计数据
  const fetchStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const response = await apiService.get('/products/stats/summary');
      if (response.success) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('获取统计数据失败:', error);
    } finally {
      setStatsLoading(false);
    }
  }, []);

  // 获取分类列表
  const fetchCategories = useCallback(async () => {
    try {
      const response = await apiService.get('/products/categories');
      if (response.success) {
        setCategories(response.data || []);
      }
    } catch (error) {
      console.error('获取分类列表失败:', error);
    }
  }, []);

  // 初始加载
  useEffect(() => {
    fetchProducts();
    fetchStats();
    fetchCategories();
  }, [fetchProducts, fetchStats, fetchCategories]);

  // 处理搜索
  const handleSearch = () => {
    fetchProducts(1, pagination.pageSize || 20, searchText, selectedCategory, selectedStatus);
  };

  // 处理重置
  const handleReset = () => {
    setSearchText('');
    setSelectedCategory('');
    setSelectedStatus('');
    fetchProducts(1, 20, '', '', '');
  };

  // 处理表格变化（分页、排序、筛选）
  const handleTableChange = (
    newPagination: TablePaginationConfig,
    filters: Record<string, FilterValue | null>,
    sorter: SorterResult<Product> | SorterResult<Product>[]
  ) => {
    fetchProducts(
      newPagination.current || 1,
      newPagination.pageSize || 20,
      searchText,
      selectedCategory,
      selectedStatus
    );
  };

  // 删除产品
  const handleDelete = async (id: number) => {
    try {
      const response = await apiService.delete(`/products/${id}`);
      if (response.success) {
        message.success('产品删除成功');
        fetchProducts(
          pagination.current || 1,
          pagination.pageSize || 20,
          searchText,
          selectedCategory,
          selectedStatus
        );
        fetchStats();
      } else {
        message.error(response.message || '删除失败');
      }
    } catch (error) {
      console.error('删除产品失败:', error);
      message.error('删除产品失败');
    }
  };

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      '可用': { color: 'success', text: '可用' },
      '停用': { color: 'default', text: '停用' },
      '缺货': { color: 'error', text: '缺货' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 表格列定义
  const columns: ColumnsType<Product> = [
    {
      title: '产品图片',
      dataIndex: 'images',
      key: 'images',
      width: 80,
      align: 'center',
      render: (images: string) => {
        if (!images) {
          return (
            <div className="w-12 h-12 bg-gray-100 rounded flex items-center justify-center">
              <PictureOutlined className="text-gray-400" />
            </div>
          );
        }
        try {
          const imageList = JSON.parse(images);
          const firstImage = Array.isArray(imageList) ? imageList[0] : images;
          return (
            <Image
              src={firstImage}
              alt="产品图片"
              className="w-12 h-12 object-cover rounded"
              preview={false}
            />
          );
        } catch {
          return (
            <div className="w-12 h-12 bg-gray-100 rounded flex items-center justify-center">
              <PictureOutlined className="text-gray-400" />
            </div>
          );
        }
      },
    },
    {
      title: '产品编码',
      dataIndex: 'product_code',
      key: 'product_code',
      width: 120,
      render: (code: string, record: Product) => (
        <a onClick={() => navigate(`/products/${record.id}`)} className="font-medium">
          {code}
        </a>
      ),
    },
    {
      title: '产品描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (desc: string) => desc || '-',
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category: string) => category || '-',
    },
    {
      title: '材质',
      dataIndex: 'material',
      key: 'material',
      width: 100,
      render: (material: string) => material || '-',
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 100,
      align: 'right',
      render: (price: number) => (
        <Text strong>{price ? `¥${price.toFixed(2)}` : '-'}</Text>
      ),
    },
    {
      title: 'MOQ',
      dataIndex: 'moq',
      key: 'moq',
      width: 80,
      align: 'right',
      render: (moq: number) => moq || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      align: 'center',
      render: (status: string) => getStatusTag(status),
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
      width: 150,
      fixed: 'right',
      render: (_, record: Product) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/products/${record.id}`)}
            />
          </Tooltip>
          {hasPermissionCode(PERMISSION_CODES.PRODUCT_UPDATE) && (
            <Tooltip title="编辑">
              <Button
                type="text"
                icon={<EditOutlined />}
                onClick={() => navigate(`/products/${record.id}/edit`)}
              />
            </Tooltip>
          )}
          {hasPermissionCode(PERMISSION_CODES.PRODUCT_DELETE) && (
            <Popconfirm
              title="确认删除"
              description="确定要删除这个产品吗？此操作不可恢复。"
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
        <Title level={2}>产品管理</Title>
        <Text type="secondary">管理酒店家具产品目录，包括产品信息、价格和库存状态</Text>
      </div>

      {/* 统计卡片 */}
      <Spin spinning={statsLoading}>
        <Row gutter={16} className="mb-6">
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="产品总数"
                value={stats?.total || 0}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="可用产品"
                value={stats?.available || 0}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="缺货产品"
                value={stats?.out_of_stock || 0}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="停用产品"
                value={stats?.disabled || 0}
                valueStyle={{ color: '#d9d9d9' }}
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
              placeholder="搜索产品编码、描述、材质..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={5} lg={5}>
            <Select
              placeholder="选择分类"
              style={{ width: '100%' }}
              value={selectedCategory || undefined}
              onChange={setSelectedCategory}
              allowClear
            >
              {categories.map((cat) => (
                <Option key={cat} value={cat}>{cat}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={5} lg={5}>
            <Select
              placeholder="选择状态"
              style={{ width: '100%' }}
              value={selectedStatus || undefined}
              onChange={setSelectedStatus}
              allowClear
            >
              <Option value="可用">可用</Option>
              <Option value="停用">停用</Option>
              <Option value="缺货">缺货</Option>
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
              {hasPermissionCode(PERMISSION_CODES.PRODUCT_CREATE) && (
                <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/products/new')}>
                  新增产品
                </Button>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 产品列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={products}
          rowKey="id"
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
          locale={{
            emptyText: (
              <Empty
                description="暂无产品数据"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            ),
          }}
        />
      </Card>
    </div>
  );
};

export default ProductList;