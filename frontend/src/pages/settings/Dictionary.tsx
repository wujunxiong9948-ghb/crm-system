import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Tag,
  Space,
  Modal,
  Form,
  Select,
  message,
  Popconfirm,
  Row,
  Col,
  Tabs,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { dictionaryApi } from '../../services/api';

const { TabPane } = Tabs;
const { Option } = Select;

interface DictionaryItem {
  id: number;
  type: string;
  code: string;
  name: string;
  value: string;
  sort_order: number;
  description: string;
  status: string;
  is_system: boolean;
}

const defaultTypes = [
  { key: 'customer_level', name: '客户等级', icon: '⭐' },
  { key: 'customer_source', name: '客户来源', icon: '📢' },
  { key: 'customer_type', name: '客户类型', icon: '🏢' },
  { key: 'opportunity_stage', name: '机会阶段', icon: '📊' },
  { key: 'product_category', name: '产品分类', icon: '📦' },
  { key: 'contact_type', name: '联系类型', icon: '📞' },
  { key: 'order_status', name: '订单状态', icon: '📋' },
  { key: 'payment_status', name: '支付状态', icon: '💰' },
];

const Dictionary: React.FC = () => {
  const [dictionaries, setDictionaries] = useState<DictionaryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<DictionaryItem | null>(null);
  const [form] = Form.useForm();
  const [activeType, setActiveType] = useState('customer_level');
  const [searchKeyword, setSearchKeyword] = useState('');

  const fetchDictionaries = async () => {
    setLoading(true);
    try {
      const response = await dictionaryApi.getDictionaries({
        type: activeType,
        keyword: searchKeyword,
      });
      setDictionaries(response.items || []);
    } catch (error) {
      message.error('获取字典列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDictionaries();
  }, [activeType]);

  const handleAdd = () => {
    setEditingItem(null);
    form.resetFields();
    form.setFieldsValue({ type: activeType, status: 'active', sort_order: 0 });
    setModalVisible(true);
  };

  const handleEdit = (record: DictionaryItem) => {
    setEditingItem(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleSave = async (values: any) => {
    try {
      if (editingItem) {
        await dictionaryApi.updateDictionary(editingItem.id, values);
        message.success('字典更新成功');
      } else {
        await dictionaryApi.createDictionary(values);
        message.success('字典创建成功');
      }
      setModalVisible(false);
      fetchDictionaries();
    } catch (error: any) {
      message.error(error.response?.data?.error || '操作失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await dictionaryApi.deleteDictionary(id);
      message.success('字典删除成功');
      fetchDictionaries();
    } catch (error: any) {
      message.error(error.response?.data?.error || '删除失败');
    }
  };

  const handleInitDefaults = async () => {
    Modal.confirm({
      title: '初始化默认字典',
      content: '确定要初始化所有默认业务字典吗？这将添加常用的字典数据。',
      onOk: async () => {
        try {
          const defaultItems = [
            // 客户等级
            { type: 'customer_level', code: 'vip', name: 'VIP客户', value: 'VIP', sort_order: 1 },
            { type: 'customer_level', code: 'a', name: 'A级客户', value: 'A', sort_order: 2 },
            { type: 'customer_level', code: 'b', name: 'B级客户', value: 'B', sort_order: 3 },
            { type: 'customer_level', code: 'c', name: 'C级客户', value: 'C', sort_order: 4 },
            // 客户来源
            {
              type: 'customer_source',
              code: 'exhibition',
              name: '展会',
              value: 'exhibition',
              sort_order: 1,
            },
            {
              type: 'customer_source',
              code: 'referral',
              name: '推荐',
              value: 'referral',
              sort_order: 2,
            },
            {
              type: 'customer_source',
              code: 'website',
              name: '网站',
              value: 'website',
              sort_order: 3,
            },
            { type: 'customer_source', code: 'phone', name: '电话', value: 'phone', sort_order: 4 },
            { type: 'customer_source', code: 'other', name: '其他', value: 'other', sort_order: 5 },
            // 客户类型
            {
              type: 'customer_type',
              code: 'potential',
              name: '潜在客户',
              value: 'potential',
              sort_order: 1,
            },
            {
              type: 'customer_type',
              code: 'existing',
              name: '现有客户',
              value: 'existing',
              sort_order: 2,
            },
            { type: 'customer_type', code: 'vip', name: 'VIP客户', value: 'vip', sort_order: 3 },
            // 机会阶段
            {
              type: 'opportunity_stage',
              code: 'contact',
              name: '初步接触',
              value: '初步接触',
              sort_order: 1,
            },
            {
              type: 'opportunity_stage',
              code: 'analysis',
              name: '需求分析',
              value: '需求分析',
              sort_order: 2,
            },
            {
              type: 'opportunity_stage',
              code: 'quote',
              name: '方案报价',
              value: '方案报价',
              sort_order: 3,
            },
            {
              type: 'opportunity_stage',
              code: 'negotiation',
              name: '谈判',
              value: '谈判',
              sort_order: 4,
            },
            { type: 'opportunity_stage', code: 'won', name: '成交', value: '成交', sort_order: 5 },
            { type: 'opportunity_stage', code: 'lost', name: '丢失', value: '丢失', sort_order: 6 },
          ];

          await dictionaryApi.batchCreateDictionaries({ items: defaultItems });
          message.success('默认字典初始化成功');
          fetchDictionaries();
        } catch (error: any) {
          message.error(error.response?.data?.error || '初始化失败');
        }
      },
    });
  };

  const columns = [
    {
      title: '字典代码',
      dataIndex: 'code',
      width: 120,
    },
    {
      title: '字典名称',
      dataIndex: 'name',
    },
    {
      title: '字典值',
      dataIndex: 'value',
      render: (value: string) => value || '-',
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      width: 80,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === 'active' ? 'success' : 'default'}>
          {status === 'active' ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '系统',
      dataIndex: 'is_system',
      width: 80,
      render: (isSystem: boolean) => (isSystem ? <Tag color="red">系统</Tag> : <Tag>自定义</Tag>),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (record: DictionaryItem) => (
        <Space size="small">
          <Button type="text" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          {!record.is_system && (
            <Popconfirm title="确定要删除该字典吗？" onConfirm={() => handleDelete(record.id)}>
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Card
      title={
        <span>
          <BookOutlined /> 业务参数设置
        </span>
      }
      extra={
        <Space>
          <Button onClick={handleInitDefaults}>初始化默认字典</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增字典
          </Button>
        </Space>
      }
    >
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Input.Search
            placeholder="搜索字典名称、代码"
            value={searchKeyword}
            onChange={e => setSearchKeyword(e.target.value)}
            onSearch={fetchDictionaries}
            enterButton={<SearchOutlined />}
          />
        </Col>
      </Row>

      <Tabs activeKey={activeType} onChange={setActiveType} type="card">
        {defaultTypes.map(type => (
          <TabPane tab={`${type.icon} ${type.name}`} key={type.key} />
        ))}
      </Tabs>

      <Table
        columns={columns}
        dataSource={dictionaries}
        rowKey="id"
        loading={loading}
        pagination={false}
        size="small"
      />

      <Modal
        title={editingItem ? '编辑字典' : '新增字典'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item name="type" label="字典类型" rules={[{ required: true }]}>
            <Select disabled={!!editingItem}>
              {defaultTypes.map(t => (
                <Option key={t.key} value={t.key}>
                  {t.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="code"
            label="字典代码"
            rules={[{ required: true, message: '请输入字典代码' }]}
          >
            <Input disabled={!!editingItem} placeholder="请输入字典代码，如：vip" />
          </Form.Item>

          <Form.Item
            name="name"
            label="字典名称"
            rules={[{ required: true, message: '请输入字典名称' }]}
          >
            <Input placeholder="请输入字典名称" />
          </Form.Item>

          <Form.Item name="value" label="字典值">
            <Input placeholder="请输入字典值（可选）" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="sort_order" label="排序" initialValue={0}>
                <Input type="number" placeholder="排序号" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="status" label="状态" initialValue="active">
                <Select>
                  <Option value="active">启用</Option>
                  <Option value="inactive">禁用</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} placeholder="请输入描述" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default Dictionary;
