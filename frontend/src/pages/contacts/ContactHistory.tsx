import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  Button,
  Input,
  Select,
  DatePicker,
  Space,
  Card,
  Tag,
  Modal,
  Form,
  message,
  Popconfirm,
  Row,
  Col,
  Statistic,
  Avatar,
  Tooltip,
  Badge,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  PhoneOutlined,
  MailOutlined,
  UserOutlined,
  MessageOutlined,
  CalendarOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import { apiService } from '@/services/api';
import { usePermission, PERMISSION_CODES } from '@/utils/permission';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { TextArea } = Input;
const { Option } = Select;

// 联系类型配置
const CONTACT_TYPES = [
  { value: '电话', icon: <PhoneOutlined />, color: 'blue' },
  { value: '邮件', icon: <MailOutlined />, color: 'green' },
  { value: '拜访', icon: <UserOutlined />, color: 'orange' },
  { value: '微信', icon: <MessageOutlined />, color: 'cyan' },
  { value: '展会', icon: <CalendarOutlined />, color: 'purple' },
  { value: '其他', icon: <MessageOutlined />, color: 'default' },
];

// 状态颜色配置
const STATUS_COLORS: Record<string, string> = {
  '待处理': 'warning',
  '进行中': 'processing',
  '已完成': 'success',
  '已取消': 'default',
};

interface Contact {
  id: number;
  customer_id: number;
  customer_name: string;
  customer_company: string;
  contact_type: string;
  subject: string;
  content: string;
  contact_date: string;
  follow_up_date: string;
  assigned_to: string;
  status: string;
  created_at: string;
}

interface Customer {
  id: number;
  name: string;
  company: string;
}

const ContactHistory: React.FC = () => {
  const navigate = useNavigate();
  const { hasPermissionCode } = usePermission();
  
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(false);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingContact, setEditingContact] = useState<Contact | null>(null);
  const [form] = Form.useForm();
  
  // 筛选条件
  const [filters, setFilters] = useState({
    keyword: '',
    contact_type: undefined as string | undefined,
    status: undefined as string | undefined,
    customer_id: undefined as number | undefined,
    date_range: null as any,
  });

  // 统计数据
  const [stats, setStats] = useState({
    total: 0,
    today: 0,
    pending: 0,
    completed: 0,
  });

  // 获取联系记录
  const fetchContacts = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filters.keyword) params.keyword = filters.keyword;
      if (filters.contact_type) params.contact_type = filters.contact_type;
      if (filters.status) params.status = filters.status;
      if (filters.customer_id) params.customer_id = filters.customer_id;
      if (filters.date_range) {
        params.start_date = filters.date_range[0]?.format('YYYY-MM-DD');
        params.end_date = filters.date_range[1]?.format('YYYY-MM-DD');
      }

      const response = await apiService.get('/contacts', { params });
      if (response.success) {
        // 处理两种可能的返回格式
        const contactsData = response.data?.contacts || response.data || [];
        setContacts(contactsData);
        setStats({
          total: response.data?.total || contactsData.length || 0,
          today: response.data?.today || 0,
          pending: response.data?.pending || 0,
          completed: response.data?.completed || 0,
        });
      }
    } catch (error) {
      message.error('获取联系记录失败');
      console.error('获取联系记录失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取客户列表
  const fetchCustomers = async () => {
    try {
      const response = await apiService.get('/customers', {
        params: { per_page: 1000 },
      });
      if (response.success) {
        setCustomers(response.data?.customers || []);
      }
    } catch (error) {
      console.error('获取客户列表失败:', error);
    }
  };

  useEffect(() => {
    fetchContacts();
    fetchCustomers();
  }, []);

  // 提交表单
  const handleSubmit = async (values: any) => {
    try {
      const data = {
        ...values,
        contact_date: values.contact_date?.format('YYYY-MM-DD HH:mm:ss'),
        follow_up_date: values.follow_up_date?.format('YYYY-MM-DD'),
      };

      if (editingContact) {
        await apiService.put(`/contacts/${editingContact.id}`, data);
        message.success('联系记录更新成功');
      } else {
        await apiService.post('/contacts', data);
        message.success('联系记录创建成功');
      }
      
      setModalVisible(false);
      setEditingContact(null);
      form.resetFields();
      fetchContacts();
    } catch (error) {
      message.error(editingContact ? '更新失败' : '创建失败');
      console.error('提交失败:', error);
    }
  };

  // 删除记录
  const handleDelete = async (id: number) => {
    try {
      await apiService.delete(`/contacts/${id}`);
      message.success('删除成功');
      fetchContacts();
    } catch (error) {
      message.error('删除失败');
      console.error('删除失败:', error);
    }
  };

  // 打开新建弹窗
  const handleNew = () => {
    setEditingContact(null);
    form.resetFields();
    form.setFieldsValue({
      contact_date: dayjs(),
      status: '已完成',
    });
    setModalVisible(true);
  };

  // 打开编辑弹窗
  const handleEdit = (record: Contact) => {
    setEditingContact(record);
    form.setFieldsValue({
      ...record,
      contact_date: record.contact_date ? dayjs(record.contact_date) : null,
      follow_up_date: record.follow_up_date ? dayjs(record.follow_up_date) : null,
    });
    setModalVisible(true);
  };

  // 获取联系类型图标和颜色
  const getContactTypeConfig = (type: string) => {
    return CONTACT_TYPES.find(t => t.value === type) || CONTACT_TYPES[5];
  };

  // 表格列定义
  const columns = [
    {
      title: '联系时间',
      dataIndex: 'contact_date',
      key: 'contact_date',
      width: 150,
      sorter: (a: Contact, b: Contact) => 
        dayjs(a.contact_date).unix() - dayjs(b.contact_date).unix(),
      render: (date: string) => (
        <Tooltip title={dayjs(date).format('YYYY-MM-DD HH:mm:ss')}>
          <span>{dayjs(date).format('MM-DD HH:mm')}</span>
        </Tooltip>
      ),
    },
    {
      title: '客户',
      key: 'customer',
      width: 180,
      render: (_: any, record: Contact) => (
        <div>
          <div 
            className="font-medium cursor-pointer text-blue-600 hover:text-blue-800"
            onClick={() => navigate(`/customers/${record.customer_id}`)}
          >
            {record.customer_name}
          </div>
          <div className="text-gray-500 text-xs">{record.customer_company}</div>
        </div>
      ),
    },
    {
      title: '联系类型',
      dataIndex: 'contact_type',
      key: 'contact_type',
      width: 100,
      filters: CONTACT_TYPES.map(t => ({ text: t.value, value: t.value })),
      onFilter: (value: any, record: Contact) => record.contact_type === value,
      render: (type: string) => {
        const config = getContactTypeConfig(type);
        return (
          <Tag color={config.color} icon={config.icon}>
            {type}
          </Tag>
        );
      },
    },
    {
      title: '主题',
      dataIndex: 'subject',
      key: 'subject',
      ellipsis: true,
    },
    {
      title: '内容摘要',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (content: string) => content?.substring(0, 50) + (content?.length > 50 ? '...' : ''),
    },
    {
      title: '负责人',
      dataIndex: 'assigned_to',
      key: 'assigned_to',
      width: 100,
      render: (name: string) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <span>{name || '-'}</span>
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      filters: [
        { text: '待处理', value: '待处理' },
        { text: '进行中', value: '进行中' },
        { text: '已完成', value: '已完成' },
        { text: '已取消', value: '已取消' },
      ],
      onFilter: (value: any, record: Contact) => record.status === value,
      render: (status: string) => (
        <Tag color={STATUS_COLORS[status]}>{status}</Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: any, record: Contact) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button 
              type="text" 
              icon={<EyeOutlined />}
              onClick={() => navigate(`/customers/${record.customer_id}`, { 
                state: { activeTab: 'contacts' } 
              })}
            />
          </Tooltip>
          {hasPermissionCode(PERMISSION_CODES.CUSTOMER_UPDATE) && (
            <Tooltip title="编辑">
              <Button 
                type="text" 
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              />
            </Tooltip>
          )}
          {hasPermissionCode(PERMISSION_CODES.CUSTOMER_DELETE) && (
            <Popconfirm
              title="确定删除这条联系记录吗？"
              onConfirm={() => handleDelete(record.id)}
              okText="删除"
              cancelText="取消"
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
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总记录数"
              value={stats.total}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日联系"
              value={stats.today}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待处理"
              value={stats.pending}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completed}
              valueStyle={{ color: '#13c2c2' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选和工具栏 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <Input
              placeholder="搜索客户、主题、内容..."
              prefix={<SearchOutlined />}
              value={filters.keyword}
              onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
              onPressEnter={fetchContacts}
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder="联系类型"
              allowClear
              style={{ width: '100%' }}
              value={filters.contact_type}
              onChange={(value) => setFilters({ ...filters, contact_type: value })}
            >
              {CONTACT_TYPES.map(t => (
                <Option key={t.value} value={t.value}>{t.value}</Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder="状态"
              allowClear
              style={{ width: '100%' }}
              value={filters.status}
              onChange={(value) => setFilters({ ...filters, status: value })}
            >
              <Option value="待处理">待处理</Option>
              <Option value="进行中">进行中</Option>
              <Option value="已完成">已完成</Option>
              <Option value="已取消">已取消</Option>
            </Select>
          </Col>
          <Col span={6}>
            <RangePicker
              style={{ width: '100%' }}
              value={filters.date_range}
              onChange={(dates) => setFilters({ ...filters, date_range: dates })}
            />
          </Col>
          <Col span={4}>
            <Space>
              <Button type="primary" icon={<SearchOutlined />} onClick={fetchContacts}>
                查询
              </Button>
              <Button icon={<ReloadOutlined />} onClick={() => {
                setFilters({
                  keyword: '',
                  contact_type: undefined,
                  status: undefined,
                  customer_id: undefined,
                  date_range: null,
                });
                fetchContacts();
              }}>
                重置
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 数据表格 */}
      <Card
        title={
          <Space>
            <span>联系记录列表</span>
            <Badge count={contacts.length} style={{ backgroundColor: '#1890ff' }} />
          </Space>
        }
        extra={
          hasPermissionCode(PERMISSION_CODES.CUSTOMER_CREATE) && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleNew}>
              新增联系记录
            </Button>
          )
        }
      >
        <Table
          columns={columns}
          dataSource={contacts}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      {/* 新增/编辑弹窗 */}
      <Modal
        title={editingContact ? '编辑联系记录' : '新增联系记录'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingContact(null);
        }}
        footer={null}
        width={700}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{ status: '已完成' }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="customer_id"
                label="关联客户"
                rules={[{ required: true, message: '请选择客户' }]}
              >
                <Select
                  placeholder="选择客户"
                  showSearch
                  optionFilterProp="children"
                >
                  {customers.map(c => (
                    <Option key={c.id} value={c.id}>
                      {c.name} {c.company && `(${c.company})`}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="contact_type"
                label="联系类型"
                rules={[{ required: true, message: '请选择联系类型' }]}
              >
                <Select placeholder="选择联系类型">
                  {CONTACT_TYPES.map(t => (
                    <Option key={t.value} value={t.value}>{t.value}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="contact_date"
                label="联系时间"
                rules={[{ required: true, message: '请选择联系时间' }]}
              >
                <DatePicker 
                  showTime 
                  style={{ width: '100%' }} 
                  format="YYYY-MM-DD HH:mm"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="follow_up_date"
                label="跟进日期"
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="subject"
            label="主题"
            rules={[{ required: true, message: '请输入主题' }]}
          >
            <Input placeholder="输入联系主题" />
          </Form.Item>

          <Form.Item
            name="content"
            label="联系内容"
            rules={[{ required: true, message: '请输入联系内容' }]}
          >
            <TextArea rows={4} placeholder="详细描述联系内容..." />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="assigned_to"
                label="负责人"
              >
                <Input placeholder="负责人姓名" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="status"
                label="状态"
                rules={[{ required: true, message: '请选择状态' }]}
              >
                <Select placeholder="选择状态">
                  <Option value="待处理">待处理</Option>
                  <Option value="进行中">进行中</Option>
                  <Option value="已完成">已完成</Option>
                  <Option value="已取消">已取消</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingContact ? '更新' : '创建'}
              </Button>
              <Button onClick={() => {
                setModalVisible(false);
                setEditingContact(null);
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ContactHistory;
