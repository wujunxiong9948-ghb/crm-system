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
  Progress,
  Tooltip,
  Badge,
} from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  ExportOutlined,
  EyeOutlined,
  RiseOutlined,
  DollarOutlined,
  HomeOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiService, apiEndpoints } from '../../services/api';
import type { ColumnsType } from 'antd/es/table';
import OpportunityForm from './OpportunityForm';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;

// 酒店家具项目销售机会
interface Opportunity {
  id: number;
  name: string;
  hotel_name: string;
  project_address: string;
  project_type: string;
  star_rating?: string;
  room_count: number;
  planned_opening_date?: string;
  expected_close_date?: string;
  expected_value: number;
  furniture_budget?: number;
  renovation_budget?: number;
  stage: string;
  probability: number;
  status: string;
  priority: string;
  assigned_to?: string;
  assigned_to_name?: string;
  customer_id: number;
  customer_name?: string;
  next_follow_up_date?: string;
  created_at: string;
  updated_at: string;
}

interface OpportunityStats {
  total_count: number;
  total_value: number;
  by_stage: Record<string, number>;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  this_month_new: number;
  this_month_value: number;
}

interface OpportunityListResponse {
  opportunities: Opportunity[];
  pagination: {
    current: number;
    pageSize: number;
    total: number;
    pages: number;
  };
}

const OpportunityList: React.FC = () => {
  const navigate = useNavigate();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<OpportunityStats | null>(null);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    pages: 1,
  });
  const [searchParams, setSearchParams] = useState({
    search: '',
    stage: '',
    status: '',
    priority: '',
    project_type: '',
    page: 1,
    per_page: 20,
  });
  const [formVisible, setFormVisible] = useState(false);
  const [editingOpportunity, setEditingOpportunity] = useState<Opportunity | null>(null);

  // 获取销售机会列表
  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchParams.search) params.append('search', searchParams.search);
      if (searchParams.stage) params.append('stage', searchParams.stage);
      if (searchParams.status) params.append('status', searchParams.status);
      if (searchParams.priority) params.append('priority', searchParams.priority);
      if (searchParams.project_type) params.append('project_type', searchParams.project_type);
      params.append('page', searchParams.page.toString());
      params.append('per_page', searchParams.per_page.toString());

      const response = await apiService.get<OpportunityListResponse>(
        `${apiEndpoints.opportunities.list}?${params}`
      );
      setOpportunities(response.opportunities || []);
      setPagination(
        response.pagination || {
          current: 1,
          pageSize: 20,
          total: 0,
          pages: 1,
        }
      );
    } catch (error) {
      message.error('获取销售机会列表失败');
      console.error('获取销售机会列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取统计数据
  const fetchStats = async () => {
    try {
      const response = await apiService.get<OpportunityStats>(apiEndpoints.opportunities.stats);
      setStats(response);
    } catch (error) {
      console.error('获取统计数据失败:', error);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      await fetchOpportunities();
      await fetchStats();
    };
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
  const handleTableChange = (pagination: { current?: number; pageSize?: number }) => {
    setSearchParams(prev => ({
      ...prev,
      page: pagination.current || 1,
      per_page: pagination.pageSize || 20,
    }));
  };

  // 删除销售机会
  const handleDelete = async (id: number) => {
    try {
      await apiService.delete(apiEndpoints.opportunities.delete(id));
      message.success('销售机会删除成功');
      fetchOpportunities();
      fetchStats();
    } catch (error) {
      message.error('删除销售机会失败');
      console.error('删除销售机会失败:', error);
    }
  };

  // 编辑销售机会
  const handleEdit = (opportunity: Opportunity) => {
    setEditingOpportunity(opportunity);
    setFormVisible(true);
  };

  // 查看详情
  const handleView = (id: number) => {
    navigate(`/opportunities/${id}`);
  };

  // 创建销售机会
  const handleCreate = () => {
    setEditingOpportunity(null);
    setFormVisible(true);
  };

  // 表单提交成功
  const handleFormSuccess = () => {
    setFormVisible(false);
    fetchOpportunities();
    fetchStats();
  };

  // 导出数据
  const handleExport = () => {
    message.info('导出功能开发中...');
  };

  // 阶段颜色映射
  const stageColors: Record<string, string> = {
    '初步接触': 'default',
    '需求调研': 'processing',
    '方案设计': 'warning',
    '报价谈判': 'orange',
    '合同签订': 'purple',
    '成交': 'success',
    '丢失': 'error',
  };

  // 状态颜色映射
  const statusColors: Record<string, string> = {
    '进行中': 'blue',
    '已成交': 'success',
    '已丢失': 'error',
    '暂停': 'warning',
  };

  // 优先级颜色映射
  const priorityColors: Record<string, string> = {
    '高': 'red',
    '中': 'orange',
    '低': 'green',
  };

  // 项目类型标签
  const projectTypeColors: Record<string, string> = {
    '新建酒店': 'blue',
    '酒店翻新': 'purple',
    '连锁扩张': 'cyan',
    '其他': 'default',
  };

  // 表格列定义
  const columns: ColumnsType<Opportunity> = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      fixed: 'left',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#666', marginTop: 4 }}>
            <HomeOutlined style={{ marginRight: 4 }} />
            {record.hotel_name}
          </div>
          <div style={{ fontSize: '12px', color: '#999' }}>
            {record.project_address}
          </div>
        </div>
      ),
    },
    {
      title: '项目类型',
      dataIndex: 'project_type',
      key: 'project_type',
      width: 100,
      render: (type: string) => (
        <Tag color={projectTypeColors[type] || 'default'}>{type}</Tag>
      ),
    },
    {
      title: '项目规模',
      key: 'scale',
      width: 120,
      render: (_, record) => (
        <div>
          <div><Tag color="blue">{record.room_count} 间客房</Tag></div>
          {record.star_rating && (
            <div style={{ fontSize: '12px', color: '#faad14', marginTop: 4 }}>
              {'★'.repeat(record.star_rating === '经济型' ? 1 : record.star_rating === '三星' ? 3 : record.star_rating === '四星' ? 4 : 5)}
              {record.star_rating}
            </div>
          )}
        </div>
      ),
    },
    {
      title: '时间节点',
      key: 'dates',
      width: 140,
      render: (_, record) => (
        <div style={{ fontSize: '12px' }}>
          {record.planned_opening_date && (
            <div>
              <CalendarOutlined style={{ marginRight: 4, color: '#1890ff' }} />
              开业: {dayjs(record.planned_opening_date).format('MM-DD')}
            </div>
          )}
          {record.expected_close_date && (
            <div style={{ marginTop: 4 }}>
              <RiseOutlined style={{ marginRight: 4, color: '#52c41a' }} />
              成交: {dayjs(record.expected_close_date).format('MM-DD')}
            </div>
          )}
        </div>
      ),
    },
    {
      title: '预算/金额',
      key: 'budget',
      width: 140,
      align: 'right',
      render: (_, record) => (
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontWeight: 'bold', color: '#f5222d', fontSize: '14px' }}>
            <DollarOutlined style={{ marginRight: 4 }} />
            {record.expected_value}万
          </div>
          {record.furniture_budget && (
            <div style={{ fontSize: '12px', color: '#666' }}>
              家具: {record.furniture_budget}万
            </div>
          )}
          {record.renovation_budget && (
            <div style={{ fontSize: '12px', color: '#999' }}>
              装修: {record.renovation_budget}万
            </div>
          )}
        </div>
      ),
    },
    {
      title: '销售阶段',
      dataIndex: 'stage',
      key: 'stage',
      width: 120,
      render: (stage: string, record) => (
        <div>
          <Tag color={stageColors[stage] || 'default'}>{stage}</Tag>
          <div style={{ marginTop: 8 }}>
            <Tooltip title={`成交概率: ${record.probability}%`}>
              <Progress
                percent={record.probability}
                size="small"
                strokeColor={record.probability >= 70 ? '#52c41a' : record.probability >= 40 ? '#faad14' : '#ff4d4f'}
                showInfo={false}
              />
            </Tooltip>
          </div>
        </div>
      ),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: string) => (
        <Badge
          color={priorityColors[priority] || 'default'}
          text={<span style={{ color: priorityColors[priority] }}>{priority}</span>}
        />
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => (
        <Tag color={statusColors[status] || 'default'}>{status}</Tag>
      ),
    },
    {
      title: '负责人',
      dataIndex: 'assigned_to_name',
      key: 'assigned_to_name',
      width: 100,
      render: (name: string) => name || '-',
    },
    {
      title: '下次跟进',
      dataIndex: 'next_follow_up_date',
      key: 'next_follow_up_date',
      width: 110,
      render: (date: string) => {
        if (!date) return '-';
        const days = dayjs(date).diff(dayjs(), 'day');
        const color = days < 0 ? 'red' : days === 0 ? 'orange' : days <= 3 ? 'blue' : 'green';
        return (
          <Tag color={color}>
            {days < 0 ? `逾期${Math.abs(days)}天` : days === 0 ? '今天' : `${days}天后`}
          </Tag>
        );
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record.id)}
            size="small"
          >
            详情
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个项目机会吗？"
            description="删除后将无法恢复"
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
          <Col span={4}>
            <Card>
              <Statistic
                title="项目总数"
                value={stats.total_count}
                prefix={<RiseOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={5}>
            <Card>
              <Statistic
                title="预计总金额"
                value={stats.total_value}
                suffix="万"
                prefix={<DollarOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={5}>
            <Card>
              <Statistic
                title="本月新增"
                value={stats.this_month_new}
                suffix={`个 / ${stats.this_month_value}万`}
                prefix={<RiseOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
          <Col span={5}>
            <Card>
              <Statistic
                title="进行中项目"
                value={stats.by_status['进行中'] || 0}
                prefix={<HomeOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </Col>
          <Col span={5}>
            <Card>
              <Statistic
                title="高优先级"
                value={stats.by_priority['高'] || 0}
                prefix={<RiseOutlined />}
                valueStyle={{ color: '#f5222d' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 搜索和操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space size="middle" style={{ width: '100%', flexWrap: 'wrap' }}>
          <Search
            placeholder="搜索项目名称、酒店名称、地址..."
            allowClear
            enterButton={<SearchOutlined />}
            onSearch={handleSearch}
            style={{ width: 280 }}
          />
          <Select
            placeholder="销售阶段"
            allowClear
            style={{ width: 120 }}
            onChange={value => setSearchParams(prev => ({ ...prev, stage: value, page: 1 }))}
          >
            <Option value="初步接触">初步接触</Option>
            <Option value="需求调研">需求调研</Option>
            <Option value="方案设计">方案设计</Option>
            <Option value="报价谈判">报价谈判</Option>
            <Option value="合同签订">合同签订</Option>
            <Option value="成交">成交</Option>
          </Select>
          <Select
            placeholder="项目类型"
            allowClear
            style={{ width: 120 }}
            onChange={value => setSearchParams(prev => ({ ...prev, project_type: value, page: 1 }))}
          >
            <Option value="新建酒店">新建酒店</Option>
            <Option value="酒店翻新">酒店翻新</Option>
            <Option value="连锁扩张">连锁扩张</Option>
            <Option value="其他">其他</Option>
          </Select>
          <Select
            placeholder="优先级"
            allowClear
            style={{ width: 100 }}
            onChange={value => setSearchParams(prev => ({ ...prev, priority: value, page: 1 }))}
          >
            <Option value="高">高</Option>
            <Option value="中">中</Option>
            <Option value="低">低</Option>
          </Select>
          <Select
            placeholder="状态"
            allowClear
            style={{ width: 100 }}
            onChange={value => setSearchParams(prev => ({ ...prev, status: value, page: 1 }))}
          >
            <Option value="进行中">进行中</Option>
            <Option value="已成交">已成交</Option>
            <Option value="已丢失">已丢失</Option>
            <Option value="暂停">暂停</Option>
          </Select>

          <Space style={{ marginLeft: 'auto' }}>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => {
                setSearchParams({
                  search: '',
                  stage: '',
                  status: '',
                  priority: '',
                  project_type: '',
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
              新建项目机会
            </Button>
          </Space>
        </Space>
      </Card>

      {/* 销售机会表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={opportunities}
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
          scroll={{ x: 1400 }}
        />
      </Card>

      {/* 表单模态框 */}
      <Modal
        title={editingOpportunity ? '编辑项目机会' : '新建项目机会'}
        open={formVisible}
        onCancel={() => setFormVisible(false)}
        footer={null}
        width={900}
        destroyOnClose
      >
        <OpportunityForm
          opportunity={editingOpportunity}
          onSuccess={handleFormSuccess}
          onCancel={() => setFormVisible(false)}
        />
      </Modal>
    </div>
  );
};

export default OpportunityList;
