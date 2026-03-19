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
  Typography,
  DatePicker,
  Form,
} from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  EyeOutlined,
  FilterOutlined,
  DollarOutlined,
  HomeOutlined,
  StarOutlined,
  PhoneOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import { apiService } from '../../services/api';
import { usePermission, PERMISSION_CODES } from '../../utils/permission';
import type { ColumnsType } from 'antd/es/table';
import type {
  Opportunity,
  OpportunityListResponse,
  OpportunityStats,
  FilterOptions,
  OpportunityStage,
  OpportunityStatus,
  Priority,
  ProjectType,
  HotelStar,
} from '../../types/opportunity';
import {
  STAGE_CONFIG,
  PRIORITY_CONFIG,
  STATUS_CONFIG,
  PROJECT_TYPE_CONFIG,
  HOTEL_STAR_CONFIG,
} from '../../types/opportunity';
import OpportunityForm from './OpportunityForm';
import OpportunityDetail from './OpportunityDetail';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;
const { Text } = Typography;
const { RangePicker } = DatePicker;

interface SearchParams {
  keyword: string;
  stage: string;
  status: string;
  priority: string;
  project_type: string;
  hotel_star: string;
  assigned_to: string;
  min_amount?: number;
  max_amount?: number;
  page: number;
  page_size: number;
}

const OpportunityList: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<OpportunityStats | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    totalPages: 1,
  });
  const [searchParams, setSearchParams] = useState<SearchParams>({
    keyword: '',
    stage: '',
    status: '',
    priority: '',
    project_type: '',
    hotel_star: '',
    assigned_to: '',
    page: 1,
    page_size: 10,
  });

  // 获取当前用户权限
  const { hasPermissionCode } = usePermission();
  const [formVisible, setFormVisible] = useState(false);
  const [editingOpportunity, setEditingOpportunity] = useState<Opportunity | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [viewingOpportunity, setViewingOpportunity] = useState<Opportunity | null>(null);

  // 获取销售机会列表
  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {
        page: searchParams.page,
        page_size: searchParams.page_size,
      };
      if (searchParams.keyword) params.keyword = searchParams.keyword;
      if (searchParams.stage) params.stage = searchParams.stage;
      if (searchParams.status) params.status = searchParams.status;
      if (searchParams.priority) params.priority = searchParams.priority;
      if (searchParams.project_type) params.project_type = searchParams.project_type;
      if (searchParams.hotel_star) params.hotel_star = searchParams.hotel_star;
      if (searchParams.assigned_to) params.assigned_to = searchParams.assigned_to;
      if (searchParams.min_amount) params.min_amount = searchParams.min_amount;
      if (searchParams.max_amount) params.max_amount = searchParams.max_amount;

      const response = await apiService.get<OpportunityListResponse>('/opportunities', { params });

      if (response && response.data) {
        // 获取客户信息并合并到机会数据中
        const opportunitiesWithCustomers = await enrichOpportunitiesWithCustomers(response.data || []);
        setOpportunities(opportunitiesWithCustomers);
        setPagination({
          current: response.pagination.current,
          pageSize: response.pagination.pageSize,
          total: response.pagination.total,
          totalPages: response.pagination.pages,
        });
        setStats(response.stats);
      }
    } catch (error) {
      message.error('获取销售机会列表失败');
      console.error('获取销售机会列表失败:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // 获取客户信息并合并到机会数据
  const enrichOpportunitiesWithCustomers = async (opportunities: Opportunity[]) => {
    // 获取所有客户ID
    const customerIds: number[] = [];
    const idSet = new Set<number>();
    opportunities.forEach(o => {
      if (o.customer_id && !idSet.has(o.customer_id)) {
        idSet.add(o.customer_id);
        customerIds.push(o.customer_id);
      }
    });
    
    if (customerIds.length === 0) return opportunities;
    
    try {
      // 批量获取客户信息
      const customerMap: Record<number, {name: string, company: string}> = {};
      
      // 使用现有的客户列表API
      const customersResponse = await apiService.get('/customers', {
        params: { per_page: 1000 }
      });
      
      console.log('Customers API response:', customersResponse);
      
      // 处理不同可能的返回格式
      let customersList: any[] = [];
      if (customersResponse && Array.isArray(customersResponse.data)) {
        customersList = customersResponse.data;
      } else if (customersResponse && Array.isArray(customersResponse.customers)) {
        customersList = customersResponse.customers;
      } else if (customersResponse && customersResponse.data && Array.isArray(customersResponse.data.items)) {
        customersList = customersResponse.data.items;
      }
      
      console.log('Customers list length:', customersList.length);
      
      customersList.forEach((customer: any) => {
        if (customer.id) {
          customerMap[Number(customer.id)] = {
            name: customer.name || '-',
            company: customer.company || '-'
          };
        }
      });
      
      console.log('CustomerMap keys:', Object.keys(customerMap));
      
      // 合并客户信息到机会数据
      return opportunities.map(opp => {
        const customerId = Number(opp.customer_id);
        const customerInfo = customerMap[customerId];
        console.log(`Opportunity ${opp.id} customer_id: ${customerId}, found: ${!!customerInfo}`);
        return {
          ...opp,
          customer_name: customerInfo?.name || '-',
          customer_company: customerInfo?.company || '-'
        };
      });
    } catch (error) {
      console.error('获取客户信息失败:', error);
      return opportunities;
    }
  };

  // 获取筛选选项
  const fetchFilterOptions = async () => {
    try {
      const response = await apiService.get<FilterOptions>('/opportunities/filters/options');
      if (response) {
        setFilterOptions(response);
      }
    } catch (error) {
      console.error('获取筛选选项失败:', error);
    }
  };

  useEffect(() => {
    fetchOpportunities();
    fetchFilterOptions();
  }, [searchParams]);

  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchParams(prev => ({
      ...prev,
      keyword: value,
      page: 1,
    }));
  };

  // 处理分页
  const handleTableChange = (pagination: any) => {
    setSearchParams(prev => ({
      ...prev,
      page: pagination.current,
      page_size: pagination.pageSize,
    }));
  };

  // 删除销售机会
  const handleDelete = async (id: number) => {
    try {
      await apiService.delete(`/opportunities/${id}`);
      message.success('销售机会删除成功');
      fetchOpportunities();
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

  // 创建销售机会
  const handleCreate = () => {
    setEditingOpportunity(null);
    setFormVisible(true);
  };

  // 查看详情
  const handleView = (opportunity: Opportunity) => {
    setViewingOpportunity(opportunity);
    setDetailVisible(true);
  };

  // 表单提交成功
  const handleFormSuccess = () => {
    setFormVisible(false);
    fetchOpportunities();
  };

  // 重置筛选
  const handleReset = () => {
    setSearchParams({
      keyword: '',
      stage: '',
      status: '',
      priority: '',
      project_type: '',
      hotel_star: '',
      assigned_to: '',
      page: 1,
      page_size: 10,
    });
  };

  // 渲染阶段标签
  const renderStageTag = (stage: OpportunityStage) => {
    const config = STAGE_CONFIG[stage];
    return (
      <Tag color={config.color}>
        {stage}
      </Tag>
    );
  };

  // 渲染优先级标签
  const renderPriorityTag = (priority: Priority) => {
    const config = PRIORITY_CONFIG[priority];
    return (
      <Badge
        status={priority === '高' ? 'error' : priority === '中' ? 'warning' : 'default'}
        text={<Text style={{ color: priority === '高' ? '#ff4d4f' : priority === '中' ? '#faad14' : '#1890ff' }}>{priority}</Text>}
      />
    );
  };

  // 渲染状态标签
  const renderStatusTag = (status: OpportunityStatus) => {
    const config = STATUS_CONFIG[status];
    return (
      <Tag color={config.color}>
        {config.label}
      </Tag>
    );
  };

  // 渲染项目类型标签
  const renderProjectTypeTag = (type: ProjectType) => {
    const config = PROJECT_TYPE_CONFIG[type];
    return (
      <Tag color={config.color}>
        {config.label}
      </Tag>
    );
  };

  // 渲染星级
  const renderHotelStar = (star?: HotelStar) => {
    if (!star) return '-';
    const config = HOTEL_STAR_CONFIG[star];
    return (
      <span style={{ color: config.color, fontWeight: 'bold' }}>
        {config.icon}
      </span>
    );
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
          {record.hotel_name && (
            <div style={{ fontSize: '12px', color: '#666' }}>
              <HomeOutlined style={{ marginRight: 4 }} />
              {record.hotel_name}
            </div>
          )}
        </div>
      ),
    },
    {
      title: '客户信息',
      key: 'customer',
      width: 150,
      render: (_, record) => (
        <div>
          {record.customer_name && record.customer_name !== '-' ? (
            <a 
              href={`/customers/${record.customer_id}`}
              style={{ fontWeight: 500 }}
              onClick={(e) => {
                e.stopPropagation();
              }}
            >
              {record.customer_name}
            </a>
          ) : (
            <span style={{ color: '#999' }}>-</span>
          )}
          <div style={{ fontSize: '12px', color: '#666' }}>
            {record.customer_company && record.customer_company !== '-' ? record.customer_company : ''}
          </div>
        </div>
      ),
    },
    {
      title: '项目类型',
      dataIndex: 'project_type',
      key: 'project_type',
      width: 100,
      render: (type: ProjectType) => renderProjectTypeTag(type),
    },
    {
      title: '星级/客房',
      key: 'hotel_info',
      width: 100,
      render: (_, record) => (
        <div>
          <div>{renderHotelStar(record.hotel_star)}</div>
          {record.room_count && (
            <div style={{ fontSize: '12px', color: '#666' }}>
              {record.room_count} 间客房
            </div>
          )}
        </div>
      ),
    },
    {
      title: '项目地点',
      key: 'location',
      width: 120,
      render: (_, record) => (
        <span>
          {record.province || ''}{record.city || ''}{record.district || ''}
          {!record.province && !record.city && '-'}
        </span>
      ),
    },
    {
      title: '预计金额',
      dataIndex: 'expected_value',
      key: 'expected_value',
      width: 120,
      sorter: (a, b) => a.expected_value - b.expected_value,
      render: (value: number) => (
        <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
          ¥{(value || 0).toFixed(2)}万
        </span>
      ),
    },
    {
      title: '销售阶段',
      dataIndex: 'stage',
      key: 'stage',
      width: 100,
      filters: [
        { text: '初步接触', value: '初步接触' },
        { text: '需求分析', value: '需求分析' },
        { text: '方案报价', value: '方案报价' },
        { text: '谈判', value: '谈判' },
        { text: '成交', value: '成交' },
        { text: '丢失', value: '丢失' },
      ],
      onFilter: (value, record) => record.stage === value,
      render: (stage: OpportunityStage) => renderStageTag(stage),
    },
    {
      title: '成交概率',
      dataIndex: 'probability',
      key: 'probability',
      width: 120,
      sorter: (a, b) => a.probability - b.probability,
      render: (probability: number, record) => (
        <Tooltip title={`${probability}%`}>
          <Progress
            percent={probability}
            size="small"
            strokeColor={STAGE_CONFIG[record.stage]?.color}
            format={() => `${probability}%`}
          />
        </Tooltip>
      ),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: Priority) => renderPriorityTag(priority),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      render: (status: OpportunityStatus) => renderStatusTag(status),
    },
    {
      title: '负责人',
      dataIndex: 'assigned_to',
      key: 'assigned_to',
      width: 100,
      render: (assigned: string) => assigned || '未分配',
    },
    {
      title: '下次跟进',
      dataIndex: 'next_follow_up_date',
      key: 'next_follow_up_date',
      width: 110,
      render: (date: string) => {
        if (!date) return '-';
        const days = dayjs(date).diff(dayjs(), 'day');
        const color = days < 0 ? 'red' : days <= 3 ? 'orange' : 'green';
        return (
          <Tooltip title={dayjs(date).format('YYYY-MM-DD')}>
            <span style={{ color }}>
              <CalendarOutlined style={{ marginRight: 4 }} />
              {days < 0 ? `逾期${Math.abs(days)}天` : days === 0 ? '今天' : `${days}天后`}
            </span>
          </Tooltip>
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
            onClick={() => handleView(record)}
            size="small"
          >
            详情
          </Button>
          {hasPermissionCode(PERMISSION_CODES.OPPORTUNITY_UPDATE) && (
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
              size="small"
            >
              编辑
            </Button>
          )}
          {hasPermissionCode(PERMISSION_CODES.OPPORTUNITY_DELETE) && (
            <Popconfirm
              title="确定要删除这个销售机会吗？"
              description="删除后将无法恢复"
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button type="link" danger icon={<DeleteOutlined />} size="small">
                删除
              </Button>
            </Popconfirm>
          )}
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
                title="总机会数"
                value={stats.total_count}
                prefix={<HomeOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic
                title="进行中"
                value={stats.active_count}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic
                title="已成交"
                value={stats.won_count}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic
                title="已丢失"
                value={stats.lost_count}
                valueStyle={{ color: '#8c8c8c' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="预计订单总额"
                value={stats.total_value}
                precision={2}
                prefix={<DollarOutlined />}
                suffix="万元"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 搜索和筛选栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Row gutter={16} align="middle">
            <Col flex="auto">
              <Search
                placeholder="搜索项目名称、酒店名称、描述..."
                allowClear
                enterButton={<><SearchOutlined /> 搜索</>}
                onSearch={handleSearch}
                style={{ width: 350 }}
              />
            </Col>
            <Col>
              <Space>
                <Button icon={<ReloadOutlined />} onClick={handleReset}>
                  重置筛选
                </Button>
                {hasPermissionCode(PERMISSION_CODES.OPPORTUNITY_CREATE) && (
                  <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                    新建销售机会
                  </Button>
                )}
              </Space>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={4}>
              <Select
                placeholder="销售阶段"
                allowClear
                style={{ width: '100%' }}
                value={searchParams.stage || undefined}
                onChange={value => setSearchParams(prev => ({ ...prev, stage: value || '', page: 1 }))}
              >
                <Option value="初步接触">初步接触</Option>
                <Option value="需求分析">需求分析</Option>
                <Option value="方案报价">方案报价</Option>
                <Option value="谈判">谈判</Option>
                <Option value="成交">成交</Option>
                <Option value="丢失">丢失</Option>
              </Select>
            </Col>
            <Col span={4}>
              <Select
                placeholder="项目状态"
                allowClear
                style={{ width: '100%' }}
                value={searchParams.status || undefined}
                onChange={value => setSearchParams(prev => ({ ...prev, status: value || '', page: 1 }))}
              >
                <Option value="进行中">进行中</Option>
                <Option value="已成交">已成交</Option>
                <Option value="已丢失">已丢失</Option>
              </Select>
            </Col>
            <Col span={3}>
              <Select
                placeholder="优先级"
                allowClear
                style={{ width: '100%' }}
                value={searchParams.priority || undefined}
                onChange={value => setSearchParams(prev => ({ ...prev, priority: value || '', page: 1 }))}
              >
                <Option value="高">高</Option>
                <Option value="中">中</Option>
                <Option value="低">低</Option>
              </Select>
            </Col>
            <Col span={4}>
              <Select
                placeholder="项目类型"
                allowClear
                style={{ width: '100%' }}
                value={searchParams.project_type || undefined}
                onChange={value => setSearchParams(prev => ({ ...prev, project_type: value || '', page: 1 }))}
              >
                <Option value="新建酒店">新建酒店</Option>
                <Option value="酒店翻新">酒店翻新</Option>
                <Option value="连锁扩张">连锁扩张</Option>
              </Select>
            </Col>
            <Col span={3}>
              <Select
                placeholder="酒店星级"
                allowClear
                style={{ width: '100%' }}
                value={searchParams.hotel_star || undefined}
                onChange={value => setSearchParams(prev => ({ ...prev, hotel_star: value || '', page: 1 }))}
              >
                <Option value="经济型">经济型</Option>
                <Option value="三星">三星</Option>
                <Option value="四星">四星</Option>
                <Option value="五星">五星</Option>
                <Option value="超五星">超五星</Option>
              </Select>
            </Col>
            <Col span={6}>
              <Select
                placeholder="负责人"
                allowClear
                style={{ width: '100%' }}
                value={searchParams.assigned_to || undefined}
                onChange={value => setSearchParams(prev => ({ ...prev, assigned_to: value || '', page: 1 }))}
              >
                {filterOptions?.assignees?.map(assignee => (
                  <Option key={assignee} value={assignee}>{assignee}</Option>
                ))}
              </Select>
            </Col>
          </Row>
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
          scroll={{ x: 1600 }}
        />
      </Card>

      {/* 新建/编辑表单模态框 */}
      <Modal
        title={editingOpportunity ? '编辑销售机会' : '新建销售机会'}
        open={formVisible}
        onCancel={() => setFormVisible(false)}
        footer={null}
        width={1200}
        destroyOnClose
        style={{ top: 20 }}
      >
        <OpportunityForm
          opportunity={editingOpportunity}
          onSuccess={handleFormSuccess}
          onCancel={() => setFormVisible(false)}
        />
      </Modal>

      {/* 详情查看模态框 */}
      <Modal
        title="销售机会详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            关闭
          </Button>,
          viewingOpportunity && (
            <Button
              key="edit"
              type="primary"
              icon={<EditOutlined />}
              onClick={() => {
                setDetailVisible(false);
                handleEdit(viewingOpportunity);
              }}
            >
              编辑
            </Button>
          ),
        ]}
        width={1000}
        destroyOnClose
      >
        {viewingOpportunity && (
          <OpportunityDetail
            opportunityId={viewingOpportunity.id}
            onEdit={() => {
              setDetailVisible(false);
              handleEdit(viewingOpportunity);
            }}
            onClose={() => setDetailVisible(false)}
          />
        )}
      </Modal>
    </div>
  );
};

export default OpportunityList;
