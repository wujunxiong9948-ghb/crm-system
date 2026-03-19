import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Button,
  Space,
  Tag,
  message,
  Spin,
  Row,
  Col,
  Tabs,
  Table,
  Timeline,
  Typography,
  Divider,
  Popconfirm,
  Empty,
  Badge,
  Modal,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  PhoneOutlined,
  MailOutlined,
  EnvironmentOutlined,
  BuildOutlined,
  UserOutlined,
  RiseOutlined,
  ShoppingCartOutlined,
  MessageOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { apiService, apiEndpoints } from '@/services/api';
import { usePermission, PERMISSION_CODES } from '@/utils/permission';
import OpportunityForm from '@/pages/opportunities/OpportunityForm';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

// 客户类型颜色映射
const customerTypeColors: Record<string, string> = {
  'VIP客户': 'red',
  '现有客户': 'blue',
  '潜在客户': 'green',
};

// 客户状态颜色映射
const statusColors: Record<string, string> = {
  '活跃': 'success',
  '休眠': 'warning',
  '流失': 'error',
};

// 机会阶段颜色映射
const stageColors: Record<string, string> = {
  '初步接触': 'default',
  '需求分析': 'processing',
  '方案报价': 'warning',
  '谈判': 'error',
  '成交': 'success',
  '丢失': 'default',
};

// 订单状态颜色映射
const orderStatusColors: Record<string, string> = {
  '待处理': 'default',
  '生产中': 'processing',
  '已发货': 'warning',
  '已完成': 'success',
  '已取消': 'error',
};

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
  assigned_to: string;
  created_at: string;
  updated_at: string;
}

interface Opportunity {
  id: number;
  name: string;
  stage: string;
  expected_value: number;
  probability: number;
  status: string;
  created_at: string;
}

interface Order {
  id: number;
  order_number: string;
  total_amount: number;
  status: string;
  payment_status: string;
  order_date: string;
}

interface Contact {
  id: number;
  contact_type: string;
  subject: string;
  content: string;
  contact_date: string;
  status: string;
}

const CustomerDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { hasPermissionCode } = usePermission();
  
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // 销售机会弹窗状态
  const [opportunityModalVisible, setOpportunityModalVisible] = useState(false);

  // 获取客户详情
  const fetchCustomerDetail = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      const response = await apiService.get(`${apiEndpoints.customers.list}/${id}`);
      setCustomer(response.customer || response);
    } catch (error) {
      message.error('获取客户详情失败');
      console.error('获取客户详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取客户关联数据
  const fetchRelatedData = async () => {
    if (!id) return;
    
    try {
      // 获取销售机会
      const oppResponse = await apiService.get(`${apiEndpoints.opportunities.list}?customer_id=${id}`);
      const oppData = oppResponse.opportunities || oppResponse.data || [];
      setOpportunities(Array.isArray(oppData) ? oppData : []);
      
      // 获取订单
      const orderResponse = await apiService.get(`${apiEndpoints.orders.list}?customer_id=${id}`);
      const orderData = orderResponse.orders || orderResponse.data || [];
      setOrders(Array.isArray(orderData) ? orderData : []);
      
      // 获取联系记录
      const contactResponse = await apiService.get(`/contacts?customer_id=${id}`);
      const contactData = contactResponse.contacts || contactResponse.data || [];
      setContacts(Array.isArray(contactData) ? contactData : []);
    } catch (error) {
      console.error('获取关联数据失败:', error);
    }
  };

  useEffect(() => {
    fetchCustomerDetail();
    fetchRelatedData();
  }, [id]);

  // 删除客户
  const handleDelete = async () => {
    if (!id) return;
    
    try {
      await apiService.delete(apiEndpoints.customers.delete(Number(id)));
      message.success('客户删除成功');
      navigate('/customers');
    } catch (error) {
      message.error('删除客户失败');
      console.error('删除客户失败:', error);
    }
  };

  // 编辑客户
  const handleEdit = () => {
    navigate(`/customers/${id}/edit`);
  };

  // 新建销售机会 - 打开弹窗
  const handleNewOpportunity = () => {
    setOpportunityModalVisible(true);
  };

  // 销售机会创建成功回调
  const handleOpportunitySuccess = () => {
    setOpportunityModalVisible(false);
    message.success('销售机会创建成功');
    // 刷新销售机会列表
    fetchRelatedData();
    // 切换到销售机会标签页
    setActiveTab('opportunities');
  };

  // 新建订单
  const handleNewOrder = () => {
    navigate('/orders/new', { state: { customerId: id } });
  };

  // 新建联系记录
  const handleNewContact = () => {
    message.info('联系记录功能开发中...');
  };

  // 销售机会列定义
  const opportunityColumns = [
    {
      title: '机会名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Opportunity) => (
        <a onClick={() => navigate(`/opportunities/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: '阶段',
      dataIndex: 'stage',
      key: 'stage',
      render: (stage: string) => <Tag color={stageColors[stage]}>{stage}</Tag>,
    },
    {
      title: '预计金额',
      dataIndex: 'expected_value',
      key: 'expected_value',
      render: (value: number) => `¥${value?.toLocaleString() || 0}`,
    },
    {
      title: '成交概率',
      dataIndex: 'probability',
      key: 'probability',
      render: (value: number) => `${value || 0}%`,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
  ];

  // 订单列定义
  const orderColumns = [
    {
      title: '订单编号',
      dataIndex: 'order_number',
      key: 'order_number',
      render: (text: string, record: Order) => (
        <a onClick={() => navigate(`/orders/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: '订单金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (value: number) => `¥${value?.toLocaleString() || 0}`,
    },
    {
      title: '订单状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => <Tag color={orderStatusColors[status]}>{status}</Tag>,
    },
    {
      title: '支付状态',
      dataIndex: 'payment_status',
      key: 'payment_status',
      render: (status: string) => <Tag>{status}</Tag>,
    },
    {
      title: '订单日期',
      dataIndex: 'order_date',
      key: 'order_date',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
  ];

  // 联系记录列定义
  const contactColumns = [
    {
      title: '联系类型',
      dataIndex: 'contact_type',
      key: 'contact_type',
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: '主题',
      dataIndex: 'subject',
      key: 'subject',
    },
    {
      title: '内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
    },
    {
      title: '联系时间',
      dataIndex: 'contact_date',
      key: 'contact_date',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => <Tag>{status}</Tag>,
    },
  ];

  if (loading) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!customer) {
    return (
      <div style={{ padding: 24 }}>
        <Empty description="客户不存在或已被删除" />
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Button onClick={() => navigate('/customers')} icon={<ArrowLeftOutlined />}>
            返回客户列表
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      {/* 顶部操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/customers')}>
              返回
            </Button>
            <Title level={4} style={{ margin: 0 }}>
              {customer.name}
              <Tag 
                color={customerTypeColors[customer.customer_type]} 
                style={{ marginLeft: 8 }}
              >
                {customer.customer_type}
              </Tag>
              <Tag color={statusColors[customer.status]}>{customer.status}</Tag>
            </Title>
          </Space>
          <Space>
            {hasPermissionCode(PERMISSION_CODES.CUSTOMER_UPDATE) && (
              <Button icon={<EditOutlined />} onClick={handleEdit}>
                编辑
              </Button>
            )}
            {hasPermissionCode(PERMISSION_CODES.CUSTOMER_DELETE) && (
              <Popconfirm
                title="确定要删除这个客户吗？"
                description="删除后将无法恢复，相关的销售机会和订单也将被删除。"
                onConfirm={handleDelete}
                okText="确定"
                cancelText="取消"
                okButtonProps={{ danger: true }}
              >
                <Button danger icon={<DeleteOutlined />}>
                  删除
                </Button>
              </Popconfirm>
            )}
          </Space>
        </Space>
      </Card>

      {/* 标签页内容 */}
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        {/* 概览标签 */}
        <TabPane 
          tab={<span><UserOutlined /> 概览</span>} 
          key="overview"
        >
          <Row gutter={16}>
            {/* 左侧：客户基本信息 */}
            <Col span={16}>
              <Card title="基本信息" style={{ marginBottom: 16 }}>
                <Descriptions column={2} bordered>
                  <Descriptions.Item label="客户名称">{customer.name}</Descriptions.Item>
                  <Descriptions.Item label="公司名称">{customer.company || '-'}</Descriptions.Item>
                  <Descriptions.Item label="客户类型">
                    <Tag color={customerTypeColors[customer.customer_type]}>
                      {customer.customer_type}
                    </Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="客户状态">
                    <Tag color={statusColors[customer.status]}>{customer.status}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="行业">{customer.industry || '-'}</Descriptions.Item>
                  <Descriptions.Item label="来源">{customer.source}</Descriptions.Item>
                  <Descriptions.Item label="负责人">{customer.assigned_to || '-'}</Descriptions.Item>
                  <Descriptions.Item label="创建时间">
                    {dayjs(customer.created_at).format('YYYY-MM-DD HH:mm')}
                  </Descriptions.Item>
                </Descriptions>
              </Card>

              <Card title="联系信息" style={{ marginBottom: 16 }}>
                <Descriptions column={1} bordered>
                  <Descriptions.Item 
                    label={<><PhoneOutlined /> 电话</>}
                  >
                    {customer.phone || '-'}
                  </Descriptions.Item>
                  <Descriptions.Item 
                    label={<><MailOutlined /> 邮箱</>}
                  >
                    {customer.email || '-'}
                  </Descriptions.Item>
                  <Descriptions.Item 
                    label={<><EnvironmentOutlined /> 地址</>}
                  >
                    {customer.address || '-'}
                  </Descriptions.Item>
                </Descriptions>
              </Card>

              {customer.notes && (
                <Card title="备注">
                  <Text>{customer.notes}</Text>
                </Card>
              )}
            </Col>

            {/* 右侧：统计信息 */}
            <Col span={8}>
              <Card title="客户统计" style={{ marginBottom: 16 }}>
                <Row gutter={[0, 16]}>
                  <Col span={24}>
                    <Badge count={opportunities.length} showZero>
                      <Card size="small">
                        <RiseOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                        <div style={{ marginTop: 8 }}>销售机会</div>
                      </Card>
                    </Badge>
                  </Col>
                  <Col span={24}>
                    <Badge count={orders.length} showZero>
                      <Card size="small">
                        <ShoppingCartOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                        <div style={{ marginTop: 8 }}>订单数量</div>
                      </Card>
                    </Badge>
                  </Col>
                  <Col span={24}>
                    <Badge count={contacts.length} showZero>
                      <Card size="small">
                        <MessageOutlined style={{ fontSize: 24, color: '#fa8c16' }} />
                        <div style={{ marginTop: 8 }}>联系记录</div>
                      </Card>
                    </Badge>
                  </Col>
                </Row>
              </Card>

              <Card title="快捷操作">
                <Space direction="vertical" style={{ width: '100%' }}>
                  {hasPermissionCode(PERMISSION_CODES.OPPORTUNITY_CREATE) && (
                    <Button 
                      type="primary" 
                      icon={<PlusOutlined />} 
                      block
                      onClick={(e) => {
                        e.stopPropagation();
                        handleNewOpportunity();
                      }}
                    >
                      新建销售机会
                    </Button>
                  )}
                  {hasPermissionCode(PERMISSION_CODES.ORDER_CREATE) && (
                    <Button 
                      icon={<PlusOutlined />} 
                      block
                      onClick={(e) => {
                        e.stopPropagation();
                        handleNewOrder();
                      }}
                    >
                      新建订单
                    </Button>
                  )}
                  <Button 
                    icon={<PlusOutlined />} 
                    block
                    onClick={(e) => {
                      e.stopPropagation();
                      handleNewContact();
                    }}
                  >
                    添加联系记录
                  </Button>
                </Space>
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* 销售机会标签 */}
        <TabPane 
          tab={
            <span>
              <RiseOutlined /> 
              销售机会 
              <Tag style={{ marginLeft: 4 }}>{opportunities.length}</Tag>
            </span>
          } 
          key="opportunities"
        >
          <Card>
            <div style={{ marginBottom: 16 }}>
              {hasPermissionCode(PERMISSION_CODES.OPPORTUNITY_CREATE) && (
                <Button type="primary" icon={<PlusOutlined />} onClick={handleNewOpportunity}>
                  新建销售机会
                </Button>
              )}
            </div>
            <Table 
              columns={opportunityColumns} 
              dataSource={opportunities}
              rowKey="id"
              pagination={false}
              locale={{ emptyText: '暂无销售机会' }}
            />
          </Card>
        </TabPane>

        {/* 订单标签 */}
        <TabPane 
          tab={
            <span>
              <ShoppingCartOutlined /> 
              订单 
              <Tag style={{ marginLeft: 4 }}>{orders.length}</Tag>
            </span>
          } 
          key="orders"
        >
          <Card>
            <div style={{ marginBottom: 16 }}>
              {hasPermissionCode(PERMISSION_CODES.ORDER_CREATE) && (
                <Button type="primary" icon={<PlusOutlined />} onClick={handleNewOrder}>
                  新建订单
                </Button>
              )}
            </div>
            <Table 
              columns={orderColumns} 
              dataSource={orders}
              rowKey="id"
              pagination={false}
              locale={{ emptyText: '暂无订单' }}
            />
          </Card>
        </TabPane>

        {/* 联系记录标签 */}
        <TabPane 
          tab={
            <span>
              <MessageOutlined /> 
              联系记录 
              <Tag style={{ marginLeft: 4 }}>{contacts.length}</Tag>
            </span>
          } 
          key="contacts"
        >
          <Card>
            <div style={{ marginBottom: 16 }}>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleNewContact}>
                添加联系记录
              </Button>
            </div>
            <Table 
              columns={contactColumns} 
              dataSource={contacts}
              rowKey="id"
              pagination={false}
              locale={{ emptyText: '暂无联系记录' }}
            />
          </Card>
        </TabPane>

        {/* 时间线标签 */}
        <TabPane 
          tab={<span><BuildOutlined /> 动态</span>} 
          key="timeline"
        >
          <Card>
            <Timeline mode="left">
              <Timeline.Item label={dayjs(customer.created_at).format('YYYY-MM-DD HH:mm')}>
                客户创建
              </Timeline.Item>
              {opportunities.map(opp => (
                <Timeline.Item 
                  key={opp.id}
                  label={dayjs(opp.created_at).format('YYYY-MM-DD HH:mm')}
                >
                  创建销售机会：<a onClick={() => navigate(`/opportunities/${opp.id}`)}>{opp.name}</a>
                </Timeline.Item>
              ))}
              {orders.map(order => (
                <Timeline.Item 
                  key={order.id}
                  label={dayjs(order.order_date).format('YYYY-MM-DD')}
                >
                  创建订单：<a onClick={() => navigate(`/orders/${order.id}`)}>{order.order_number}</a>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </TabPane>
      </Tabs>

      {/* 新建销售机会弹窗 */}
      <Modal
        title="新建销售机会"
        open={opportunityModalVisible}
        onCancel={() => setOpportunityModalVisible(false)}
        footer={null}
        width={900}
        destroyOnClose
      >
        {customer && (
          <OpportunityForm
            initialCustomerId={customer.id}
            onSuccess={handleOpportunitySuccess}
            onCancel={() => setOpportunityModalVisible(false)}
          />
        )}
      </Modal>
    </div>
  );
};

export default CustomerDetail;
