import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Space,
  message,
  Row,
  Col,
  InputNumber,
  DatePicker,
  Typography,
  Spin,
  Divider,
  Table,
  Popconfirm,
} from 'antd';
import {
  ArrowLeftOutlined,
  SaveOutlined,
  PlusOutlined,
  DeleteOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { apiService } from '@/services/api';
import { Order, Customer, Opportunity, Product } from '@/types';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface OrderFormData {
  customer_id: number;
  opportunity_id?: number;
  order_number?: string;
  order_date: dayjs.Dayjs;
  total_amount?: number;
  currency: string;
  status: string;
  payment_status: string;
  shipping_address?: string;
  notes?: string;
}

interface OrderItemForm {
  id?: number;
  product_code: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  specifications?: string;
}

const OrderForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [items, setItems] = useState<OrderItemForm[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const isEdit = !!id;

  // 从URL参数获取预填数据
  const queryParams = new URLSearchParams(location.search);
  const prefillOpportunityId = queryParams.get('opportunity_id');
  const prefillCustomerId = queryParams.get('customer_id');

  // 获取客户列表
  const fetchCustomers = async () => {
    try {
      const response = await apiService.get<any>('/customers', {
        params: { per_page: 1000 },
      });
      
      // 处理不同可能的返回格式
      let customersList: Customer[] = [];
      if (response && Array.isArray(response.data)) {
        customersList = response.data;
      } else if (response && Array.isArray(response.customers)) {
        customersList = response.customers;
      } else if (response && response.data && Array.isArray(response.data.items)) {
        customersList = response.data.items;
      }
      
      setCustomers(customersList);
    } catch (error) {
      console.error('获取客户列表失败:', error);
    }
  };

  // 获取机会列表
  const fetchOpportunities = async (customerId?: number) => {
    try {
      const params: any = { per_page: 1000 };
      if (customerId) {
        params.customer_id = customerId;
      }
      const response = await apiService.get<any>('/opportunities', { params });
      
      // 处理不同可能的返回格式
      let opportunitiesList: Opportunity[] = [];
      if (response && Array.isArray(response.data)) {
        opportunitiesList = response.data;
      } else if (response && Array.isArray(response.opportunities)) {
        opportunitiesList = response.opportunities;
      } else if (response && response.data && Array.isArray(response.data.items)) {
        opportunitiesList = response.data.items;
      }
      
      setOpportunities(opportunitiesList);
    } catch (error) {
      console.error('获取机会列表失败:', error);
    }
  };

  // 获取产品列表
  const fetchProducts = async () => {
    try {
      const response = await apiService.get<any>('/products', {
        params: { per_page: 1000, status: '可用' },
      });
      
      // 处理不同可能的返回格式
      let productsList: Product[] = [];
      if (response && Array.isArray(response.data)) {
        productsList = response.data;
      } else if (response && Array.isArray(response.products)) {
        productsList = response.products;
      } else if (response && response.data && Array.isArray(response.data.items)) {
        productsList = response.data.items;
      }
      
      setProducts(productsList);
    } catch (error) {
      console.error('获取产品列表失败:', error);
    }
  };

  // 获取订单详情（编辑模式）
  const fetchOrderDetail = async () => {
    setLoading(true);
    try {
      const response = await apiService.get<any>(`/orders/${id}`);
      
      // 处理不同可能的返回格式
      let order: Order | null = null;
      if (response && response.id) {
        order = response;
      } else if (response && response.data) {
        order = response.data;
      }
      
      if (order) {
        form.setFieldsValue({
          customer_id: order.customer_id,
          opportunity_id: order.opportunity_id,
          order_number: order.order_number,
          order_date: order.order_date ? dayjs(order.order_date) : dayjs(),
          total_amount: order.total_amount,
          currency: order.currency || 'CNY',
          status: order.status,
          payment_status: order.payment_status,
          shipping_address: order.shipping_address,
          notes: order.notes,
        });

        // 设置客户和机会
        if (order.customer) {
          setSelectedCustomer(order.customer);
        }
        if (order.opportunity) {
          setSelectedOpportunity(order.opportunity);
        }

        // 设置订单明细
        if (order.items) {
          setItems(
            order.items.map((item) => ({
              id: item.id,
              product_code: item.product_code || '',
              product_name: item.product_name || '',
              quantity: item.quantity || 1,
              unit_price: item.unit_price || 0,
              total_price: item.total_price || 0,
              specifications: item.specifications || '',
            }))
          );
        }
      } else {
        message.error('获取订单详情失败');
      }
    } catch (error) {
      console.error('获取订单详情失败:', error);
      message.error('获取订单详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    fetchCustomers();
    fetchProducts();
    if (isEdit) {
      fetchOrderDetail();
    } else {
      // 新建模式，设置默认值
      form.setFieldsValue({
        order_date: dayjs(),
        currency: 'CNY',
        status: '待处理',
        payment_status: '未支付',
      });

      // 如果有预填的机会ID
      if (prefillOpportunityId) {
        form.setFieldsValue({ opportunity_id: parseInt(prefillOpportunityId) });
        handleOpportunityChange(parseInt(prefillOpportunityId));
      }

      // 如果有预填的客户ID
      if (prefillCustomerId) {
        form.setFieldsValue({ customer_id: parseInt(prefillCustomerId) });
        handleCustomerChange(parseInt(prefillCustomerId));
      }
    }
  }, [id, prefillOpportunityId, prefillCustomerId]);

  // 处理客户选择变化
  const handleCustomerChange = (customerId: number) => {
    const customer = customers.find((c) => c.id === customerId);
    setSelectedCustomer(customer || null);
    form.setFieldsValue({ opportunity_id: undefined });
    fetchOpportunities(customerId);

    // 自动填充送货地址
    if (customer?.address) {
      form.setFieldsValue({ shipping_address: customer.address });
    }
  };

  // 处理机会选择变化
  const handleOpportunityChange = async (opportunityId: number) => {
    const opportunity = opportunities.find((o) => o.id === opportunityId);
    setSelectedOpportunity(opportunity || null);

    if (opportunity) {
      // 自动填充客户
      form.setFieldsValue({ customer_id: opportunity.customer_id });
      const customer = customers.find((c) => c.id === opportunity.customer_id);
      setSelectedCustomer(customer || null);

      // 自动填充送货地址
      if (opportunity.address) {
        form.setFieldsValue({ shipping_address: opportunity.address });
      }

      // 自动填充总金额
      if (opportunity.expected_value) {
        form.setFieldsValue({ total_amount: opportunity.expected_value });
      }

      // 根据机会中的产品数量生成订单明细
      const newItems: OrderItemForm[] = [];
      if (opportunity.bed_count && opportunity.bed_count > 0) {
        newItems.push({
          product_code: 'BED-001',
          product_name: '酒店床',
          quantity: opportunity.bed_count,
          unit_price: 0,
          total_price: 0,
          specifications: '标准酒店床',
        });
      }
      if (opportunity.nightstand_count && opportunity.nightstand_count > 0) {
        newItems.push({
          product_code: 'NS-001',
          product_name: '床头柜',
          quantity: opportunity.nightstand_count,
          unit_price: 0,
          total_price: 0,
          specifications: '标准床头柜',
        });
      }
      if (opportunity.wardrobe_count && opportunity.wardrobe_count > 0) {
        newItems.push({
          product_code: 'WR-001',
          product_name: '衣柜',
          quantity: opportunity.wardrobe_count,
          unit_price: 0,
          total_price: 0,
          specifications: '标准衣柜',
        });
      }
      if (opportunity.desk_count && opportunity.desk_count > 0) {
        newItems.push({
          product_code: 'DK-001',
          product_name: '书桌',
          quantity: opportunity.desk_count,
          unit_price: 0,
          total_price: 0,
          specifications: '标准书桌',
        });
      }
      if (opportunity.chair_count && opportunity.chair_count > 0) {
        newItems.push({
          product_code: 'CH-001',
          product_name: '椅子',
          quantity: opportunity.chair_count,
          unit_price: 0,
          total_price: 0,
          specifications: '标准椅子',
        });
      }
      if (opportunity.sofa_count && opportunity.sofa_count > 0) {
        newItems.push({
          product_code: 'SF-001',
          product_name: '沙发',
          quantity: opportunity.sofa_count,
          unit_price: 0,
          total_price: 0,
          specifications: '标准沙发',
        });
      }
      if (opportunity.coffee_table_count && opportunity.coffee_table_count > 0) {
        newItems.push({
          product_code: 'CT-001',
          product_name: '茶几',
          quantity: opportunity.coffee_table_count,
          unit_price: 0,
          total_price: 0,
          specifications: '标准茶几',
        });
      }
      if (opportunity.tv_cabinet_count && opportunity.tv_cabinet_count > 0) {
        newItems.push({
          product_code: 'TV-001',
          product_name: '电视柜',
          quantity: opportunity.tv_cabinet_count,
          unit_price: 0,
          total_price: 0,
          specifications: '标准电视柜',
        });
      }

      if (newItems.length > 0) {
        setItems(newItems);
      }
    }
  };

  // 添加订单明细
  const handleAddItem = () => {
    setItems([
      ...items,
      {
        product_code: '',
        product_name: '',
        quantity: 1,
        unit_price: 0,
        total_price: 0,
        specifications: '',
      },
    ]);
  };

  // 删除订单明细
  const handleRemoveItem = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    setItems(newItems);
    calculateTotal(newItems);
  };

  // 更新订单明细
  const handleItemChange = (index: number, field: keyof OrderItemForm, value: any) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };

    // 自动计算总价
    if (field === 'quantity' || field === 'unit_price') {
      newItems[index].total_price =
        (newItems[index].quantity || 0) * (newItems[index].unit_price || 0);
    }

    setItems(newItems);
    calculateTotal(newItems);
  };

  // 选择产品
  const handleProductSelect = (index: number, productCode: string) => {
    const product = products.find((p) => p.product_code === productCode);
    if (product) {
      const newItems = [...items];
      newItems[index] = {
        ...newItems[index],
        product_code: product.product_code,
        product_name: product.description || product.product_code,
        unit_price: product.unit_price || 0,
        total_price: (newItems[index].quantity || 1) * (product.unit_price || 0),
        specifications: product.specifications || '',
      };
      setItems(newItems);
      calculateTotal(newItems);
    }
  };

  // 计算订单总金额
  const calculateTotal = (itemList: OrderItemForm[]) => {
    const total = itemList.reduce((sum, item) => sum + (item.total_price || 0), 0);
    form.setFieldsValue({ total_amount: total });
  };

  // 提交表单
  const handleSubmit = async (values: OrderFormData) => {
    setSaving(true);
    try {
      const data = {
        ...values,
        order_date: values.order_date.format('YYYY-MM-DD'),
        items: items.map((item) => ({
          product_code: item.product_code,
          product_name: item.product_name,
          quantity: item.quantity,
          unit_price: item.unit_price,
          total_price: item.total_price,
          specifications: item.specifications,
        })),
      };

      let response;
      if (isEdit) {
        response = await apiService.put(`/orders/${id}`, data);
      } else {
        response = await apiService.post('/orders', data);
      }

      if (response && (response.success || response.id || response.data?.id)) {
        message.success(isEdit ? '订单更新成功' : '订单创建成功');
        navigate('/orders');
      } else {
        message.error(response?.message || (isEdit ? '更新失败' : '创建失败'));
      }
    } catch (error: any) {
      console.error(isEdit ? '更新订单失败:' : '创建订单失败:', error);
      message.error(error.response?.data?.message || (isEdit ? '更新订单失败' : '创建订单失败'));
    } finally {
      setSaving(false);
    }
  };

  // 订单明细表格列
  const itemColumns: ColumnsType<OrderItemForm> = [
    {
      title: '产品',
      key: 'product',
      width: 250,
      render: (_, record, index) => (
        <Select
          style={{ width: '100%' }}
          placeholder="选择产品"
          value={record.product_code || undefined}
          onChange={(value) => handleProductSelect(index, value)}
          showSearch
          optionFilterProp="children"
          allowClear
        >
          {products.map((product) => (
            <Option key={product.product_code} value={product.product_code}>
              {product.product_code} - {product.description}
            </Option>
          ))}
        </Select>
      ),
    },
    {
      title: '产品名称',
      key: 'product_name',
      width: 180,
      render: (_, record, index) => (
        <Input
          value={record.product_name}
          onChange={(e) => handleItemChange(index, 'product_name', e.target.value)}
          placeholder="产品名称"
        />
      ),
    },
    {
      title: '规格',
      key: 'specifications',
      render: (_, record, index) => (
        <Input
          value={record.specifications}
          onChange={(e) => handleItemChange(index, 'specifications', e.target.value)}
          placeholder="规格"
        />
      ),
    },
    {
      title: '数量',
      key: 'quantity',
      width: 100,
      align: 'right',
      render: (_, record, index) => (
        <InputNumber
          min={1}
          value={record.quantity}
          onChange={(value) => handleItemChange(index, 'quantity', value)}
          style={{ width: '100%' }}
        />
      ),
    },
    {
      title: '单价',
      key: 'unit_price',
      width: 120,
      align: 'right',
      render: (_, record, index) => (
        <InputNumber
          min={0}
          precision={2}
          value={record.unit_price}
          onChange={(value) => handleItemChange(index, 'unit_price', value)}
          style={{ width: '100%' }}
          formatter={(value) => (value ? `¥${value}` : '')}
        />
      ),
    },
    {
      title: '总价',
      key: 'total_price',
      width: 120,
      align: 'right',
      render: (_, record) => (
        <Text strong>¥{(record.total_price || 0).toFixed(2)}</Text>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      align: 'center',
      render: (_, __, index) => (
        <Popconfirm
          title="确认删除"
          onConfirm={() => handleRemoveItem(index)}
          okText="删除"
          cancelText="取消"
        >
          <Button type="text" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/orders')}
          className="mb-4"
        >
          返回列表
        </Button>
        <Title level={2}>{isEdit ? '编辑订单' : '新建订单'}</Title>
        <Text type="secondary">
          {isEdit ? '修改订单信息' : '填写订单信息创建新订单'}
        </Text>
      </div>

      <Spin spinning={loading}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={24}>
            {/* 左侧：订单信息 */}
            <Col xs={24} lg={16}>
              <Card title="基本信息" className="mb-6">
                <Row gutter={16}>
                  <Col xs={24} md={12}>
                    <Form.Item
                      name="customer_id"
                      label="客户"
                      rules={[{ required: true, message: '请选择客户' }]}
                    >
                      <Select
                        placeholder="选择客户"
                        showSearch
                        optionFilterProp="children"
                        onChange={handleCustomerChange}
                        filterOption={(input, option: any) => {
                          const children = option?.children;
                          if (typeof children === 'string') {
                            return children.toLowerCase().includes(input.toLowerCase());
                          }
                          return false;
                        }}
                      >
                        {customers.map((customer) => (
                          <Option key={customer.id} value={customer.id}>
                            {customer.name} {customer.company ? `(${customer.company})` : ''}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={12}>
                    <Form.Item name="opportunity_id" label="关联销售机会">
                      <Select
                        placeholder="选择销售机会（可选）"
                        allowClear
                        onChange={handleOpportunityChange}
                        disabled={!selectedCustomer && opportunities.length === 0}
                      >
                        {opportunities.map((opp) => (
                          <Option key={opp.id} value={opp.id}>
                            {opp.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col xs={24} md={12}>
                    <Form.Item
                      name="order_number"
                      label="订单编号"
                      extra="留空将自动生成订单编号"
                    >
                      <Input placeholder="例如：ORD202403130001" disabled={isEdit} />
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={12}>
                    <Form.Item
                      name="order_date"
                      label="订单日期"
                      rules={[{ required: true, message: '请选择订单日期' }]}
                    >
                      <DatePicker style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col xs={24} md={8}>
                    <Form.Item name="status" label="订单状态">
                      <Select>
                        <Option value="待处理">待处理</Option>
                        <Option value="生产中">生产中</Option>
                        <Option value="已发货">已发货</Option>
                        <Option value="已完成">已完成</Option>
                        <Option value="已取消">已取消</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={8}>
                    <Form.Item name="payment_status" label="支付状态">
                      <Select>
                        <Option value="未支付">未支付</Option>
                        <Option value="部分支付">部分支付</Option>
                        <Option value="已支付">已支付</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={8}>
                    <Form.Item name="currency" label="货币">
                      <Select>
                        <Option value="CNY">CNY (人民币)</Option>
                        <Option value="USD">USD (美元)</Option>
                        <Option value="EUR">EUR (欧元)</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item name="shipping_address" label="送货地址">
                  <TextArea
                    rows={2}
                    placeholder="填写送货地址"
                  />
                </Form.Item>

                <Form.Item name="notes" label="订单备注">
                  <TextArea
                    rows={3}
                    placeholder="填写订单备注信息"
                  />
                </Form.Item>
              </Card>

              {/* 订单明细 */}
              <Card
                title="订单明细"
                extra={
                  <Button type="primary" icon={<PlusOutlined />} onClick={handleAddItem}>
                    添加产品
                  </Button>
                }
                className="mb-6"
              >
                <Table
                  columns={itemColumns}
                  dataSource={items}
                  rowKey={(_, index) => index?.toString() || '0'}
                  pagination={false}
                  bordered
                  summary={() => (
                    <Table.Summary.Row>
                      <Table.Summary.Cell index={0} colSpan={5} align="right">
                        <Text strong>订单总金额：</Text>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={1} align="right">
                        <Form.Item name="total_amount" noStyle>
                          <InputNumber
                            readOnly
                            precision={2}
                            formatter={(value) => `¥${value}`}
                            style={{ width: '100%', fontWeight: 'bold', color: '#f5222d' }}
                          />
                        </Form.Item>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={2} />
                    </Table.Summary.Row>
                  )}
                />
                {items.length === 0 && (
                  <div className="text-center py-8 text-gray-400">
                    暂无订单明细，点击"添加产品"按钮添加
                  </div>
                )}
              </Card>
            </Col>

            {/* 右侧：操作 */}
            <Col xs={24} lg={8}>
              <Card title="操作" className="mb-6">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    onClick={() => form.submit()}
                    loading={saving}
                    block
                    size="large"
                  >
                    {isEdit ? '保存修改' : '创建订单'}
                  </Button>
                  <Button onClick={() => navigate('/orders')} block>
                    取消
                  </Button>
                </Space>
              </Card>

              {/* 客户信息预览 */}
              {selectedCustomer && (
                <Card title="客户信息" className="mb-6">
                  <p><Text strong>姓名：</Text>{selectedCustomer.name}</p>
                  {selectedCustomer.company && (
                    <p><Text strong>公司：</Text>{selectedCustomer.company}</p>
                  )}
                  {selectedCustomer.phone && (
                    <p><Text strong>电话：</Text>{selectedCustomer.phone}</p>
                  )}
                  {selectedCustomer.email && (
                    <p><Text strong>邮箱：</Text>{selectedCustomer.email}</p>
                  )}
                </Card>
              )}

              {/* 机会信息预览 */}
              {selectedOpportunity && (
                <Card title="机会信息">
                  <p><Text strong>机会名称：</Text>{selectedOpportunity.name}</p>
                  {selectedOpportunity.hotel_name && (
                    <p><Text strong>酒店名称：</Text>{selectedOpportunity.hotel_name}</p>
                  )}
                  {selectedOpportunity.expected_value && (
                    <p>
                      <Text strong>预计金额：</Text>
                      ¥{selectedOpportunity.expected_value.toFixed(2)}
                    </p>
                  )}
                </Card>
              )}
            </Col>
          </Row>
        </Form>
      </Spin>
    </div>
  );
};

export default OrderForm;