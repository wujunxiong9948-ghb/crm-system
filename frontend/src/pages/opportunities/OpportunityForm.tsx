import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Button,
  Space,
  Divider,
  Card,
  Row,
  Col,
  message,
  Steps,
  Tooltip,
  Tag,
  AutoComplete,
} from 'antd';
import {
  SaveOutlined,
  CloseOutlined,
  PlusOutlined,
  MinusCircleOutlined,
  HomeOutlined,
  DollarOutlined,
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
  TeamOutlined,
  TrophyOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { apiService } from '../../services/api';
import type {
  Opportunity,
  CreateOpportunityRequest,
  KeyContact,
  OpportunityStage,
  ProjectType,
  HotelStar,
  Priority,
  OpportunityStatus,
} from '../../types/opportunity';
import {
  STAGE_CONFIG,
  PRIORITY_CONFIG,
  STATUS_CONFIG,
  PROJECT_TYPE_CONFIG,
} from '../../types/opportunity';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Option } = Select;

interface CustomerOption {
  id: number;
  name: string;
  company?: string;
  phone?: string;
}

interface OpportunityFormProps {
  opportunity?: Opportunity | null;
  initialCustomerId?: number | null;
  onSuccess: () => void;
  onCancel: () => void;
}

const OpportunityForm: React.FC<OpportunityFormProps> = ({
  opportunity,
  initialCustomerId,
  onSuccess,
  onCancel,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [customers, setCustomers] = useState<CustomerOption[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedStage, setSelectedStage] = useState<OpportunityStage>(
    opportunity?.stage || '初步接触'
  );

  const isEditing = !!opportunity;

  // 获取客户列表
  const fetchCustomers = async () => {
    try {
      const response = await apiService.get<any>('/customers', { params: { per_page: 1000 } });
      
      // 处理不同可能的返回格式
      let customersList: CustomerOption[] = [];
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

  useEffect(() => {
    fetchCustomers();
  }, []);

  // 获取当前选中的客户显示名称
  const getCustomerDisplayName = (customerId?: number) => {
    if (!customerId) return '';
    // 先从已加载的客户列表查找
    const customer = customers.find(c => c.id === customerId);
    if (customer) {
      return `${customer.name}${customer.company ? ` (${customer.company})` : ''}`;
    }
    // 如果在编辑模式且客户列表还没加载完，使用opportunity中的客户名
    if (opportunity?.customer_id === customerId) {
      return `${opportunity.customer_name || ''}${opportunity.customer_company ? ` (${opportunity.customer_company})` : ''}`;
    }
    return '';
  };

  // 初始化表单数据
  useEffect(() => {
    if (opportunity) {
      form.setFieldsValue({
        ...opportunity,
        customer_id: opportunity.customer_id,
        planned_opening_date: opportunity.planned_opening_date
          ? dayjs(opportunity.planned_opening_date)
          : null,
        expected_close_date: opportunity.expected_close_date
          ? dayjs(opportunity.expected_close_date)
          : null,
        next_follow_up_date: opportunity.next_follow_up_date
          ? dayjs(opportunity.next_follow_up_date)
          : null,
        key_contacts: opportunity.key_contacts?.length
          ? opportunity.key_contacts
          : [{ name: '', position: '', phone: '', email: '', role: '' }],
      });
      setSelectedStage(opportunity.stage);
    } else {
      // 新建模式
      const defaultValues: any = {
        project_type: '新建酒店',
        stage: '初步接触',
        priority: '中',
        status: '进行中',
        probability: 10,
        renovation_budget: 0,
        furniture_budget: 0,
        expected_value: 0,
        bed_count: 0,
        nightstand_count: 0,
        wardrobe_count: 0,
        desk_count: 0,
        chair_count: 0,
        sofa_count: 0,
        coffee_table_count: 0,
        tv_cabinet_count: 0,
        key_contacts: [{ name: '', position: '', phone: '', email: '', role: '' }],
      };
      
      // 如果从客户详情页传入客户ID，自动填充
      if (initialCustomerId) {
        defaultValues.customer_id = initialCustomerId;
      }
      
      form.setFieldsValue(defaultValues);
    }
  }, [opportunity, initialCustomerId, form]);
  
  // 当客户列表加载完成后，如果是编辑模式，重新设置客户字段以触发正确显示
  useEffect(() => {
    if (isEditing && opportunity && customers.length > 0) {
      const currentCustomerId = form.getFieldValue('customer_id');
      if (currentCustomerId) {
        // 强制重新设置 customer_id 以触发 Select 重新渲染
        form.setFieldValue('customer_id', currentCustomerId);
      }
    }
  }, [customers, isEditing, opportunity, form]);

  // 处理阶段变化
  const handleStageChange = (stage: OpportunityStage) => {
    setSelectedStage(stage);
    const probability = STAGE_CONFIG[stage]?.probability || 10;
    form.setFieldsValue({ probability });
  };

  // 提交表单
  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      // 处理日期字段
      const formattedValues: CreateOpportunityRequest = {
        ...values,
        planned_opening_date: values.planned_opening_date
          ? values.planned_opening_date.format('YYYY-MM-DD')
          : undefined,
        expected_close_date: values.expected_close_date
          ? values.expected_close_date.format('YYYY-MM-DD')
          : undefined,
        next_follow_up_date: values.next_follow_up_date
          ? values.next_follow_up_date.format('YYYY-MM-DD')
          : undefined,
        key_contacts: values.key_contacts?.filter(
          (c: KeyContact) => c.name || c.phone
        ),
      };

      if (isEditing && opportunity) {
        await apiService.put(`/opportunities/${opportunity.id}`, formattedValues);
        message.success('销售机会更新成功');
      } else {
        await apiService.post('/opportunities', formattedValues);
        message.success('销售机会创建成功');
      }
      onSuccess();
    } catch (error: any) {
      message.error(error.message || '操作失败');
      console.error('提交失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 步骤配置
  const steps = [
    { title: '基本信息', icon: <HomeOutlined /> },
    { title: '项目详情', icon: <DollarOutlined /> },
    { title: '产品需求', icon: <TeamOutlined /> },
    { title: '销售信息', icon: <TrophyOutlined /> },
    { title: '竞争决策', icon: <CheckCircleOutlined /> },
  ];

  // 步骤内容
  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <Row gutter={24}>
            <Col span={24}>
              <Form.Item
                name="customer_id"
                label="关联客户"
                rules={[{ required: true, message: '请选择关联客户' }]}
              >
                <Select
                  placeholder="搜索并选择客户"
                  showSearch
                  optionLabelProp="label"
                  filterOption={(input, option) => {
                    const label = option?.label;
                    if (typeof label === 'string') {
                      return label.toLowerCase().includes(input.toLowerCase());
                    }
                    return false;
                  }}
                >
                  {customers.map((customer) => (
                    <Option 
                      key={customer.id} 
                      value={customer.id}
                      label={`${customer.name}${customer.company ? ` (${customer.company})` : ''}`}
                    >
                      {customer.name} {customer.company ? `(${customer.company})` : ''}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item
                name="name"
                label="项目名称"
                rules={[{ required: true, message: '请输入项目名称' }]}
              >
                <Input placeholder="例如：某某酒店家具采购项目" />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="description" label="项目描述">
                <TextArea
                  rows={4}
                  placeholder="详细描述项目背景、需求特点等..."
                />
              </Form.Item>
            </Col>
          </Row>
        );
      case 1:
        return (
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item name="hotel_name" label="酒店名称">
                <Input placeholder="酒店全称" prefix={<HomeOutlined />} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="project_type" label="项目类型">
                <Select placeholder="选择项目类型">
                  <Option value="新建酒店">
                    <Tag color="blue">新建酒店</Tag>
                  </Option>
                  <Option value="酒店翻新">
                    <Tag color="orange">酒店翻新</Tag>
                  </Option>
                  <Option value="连锁扩张">
                    <Tag color="purple">连锁扩张</Tag>
                  </Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="hotel_star" label="酒店星级">
                <Select placeholder="选择星级">
                  <Option value="经济型">经济型</Option>
                  <Option value="三星">三星</Option>
                  <Option value="四星">四星</Option>
                  <Option value="五星">五星</Option>
                  <Option value="超五星">超五星</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="room_count" label="客房数量">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  placeholder="间"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="planned_opening_date" label="计划开业时间">
                <DatePicker style={{ width: '100%' }} placeholder="选择日期" />
              </Form.Item>
            </Col>
            <Divider orientation="left">项目地址</Divider>
            <Col span={8}>
              <Form.Item name="province" label="省份">
                <Input placeholder="省/直辖市" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="city" label="城市">
                <Input placeholder="市" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="district" label="区县">
                <Input placeholder="区/县" />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="address" label="详细地址">
                <TextArea rows={2} placeholder="街道、门牌号等详细地址" />
              </Form.Item>
            </Col>
            <Divider orientation="left">预算信息（万元）</Divider>
            <Col span={8}>
              <Form.Item name="renovation_budget" label="装修翻新预算">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                  prefix="¥"
                  placeholder="万元"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="furniture_budget" label="家具采购预算">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                  prefix="¥"
                  placeholder="万元"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="expected_value"
                label="预计订单金额"
                rules={[{ required: true, message: '请输入预计订单金额' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  precision={2}
                  prefix="¥"
                  placeholder="万元"
                />
              </Form.Item>
            </Col>
          </Row>
        );
      case 2:
        return (
          <Row gutter={24}>
            <Col span={24}>
              <Card title="客房家具数量预估" size="small">
                <Row gutter={16}>
                  <Col span={6}>
                    <Form.Item name="bed_count" label="床">
                      <InputNumber style={{ width: '100%' }} min={0} placeholder="张" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item name="nightstand_count" label="床头柜">
                      <InputNumber style={{ width: '100%' }} min={0} placeholder="个" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item name="wardrobe_count" label="衣柜">
                      <InputNumber style={{ width: '100%' }} min={0} placeholder="个" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item name="desk_count" label="书桌">
                      <InputNumber style={{ width: '100%' }} min={0} placeholder="张" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item name="chair_count" label="椅子">
                      <InputNumber style={{ width: '100%' }} min={0} placeholder="把" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item name="sofa_count" label="沙发">
                      <InputNumber style={{ width: '100%' }} min={0} placeholder="套" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item name="coffee_table_count" label="茶几">
                      <InputNumber style={{ width: '100%' }} min={0} placeholder="个" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item name="tv_cabinet_count" label="电视柜">
                      <InputNumber style={{ width: '100%' }} min={0} placeholder="个" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            </Col>
            <Col span={24} style={{ marginTop: 16 }}>
              <Form.Item name="other_furniture" label="其他家具需求">
                <TextArea
                  rows={4}
                  placeholder="描述其他家具需求，如：大堂沙发、餐厅桌椅、会议室家具等..."
                />
              </Form.Item>
            </Col>
          </Row>
        );
      case 3:
        return (
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                name="stage"
                label="销售阶段"
                rules={[{ required: true, message: '请选择销售阶段' }]}
              >
                <Select
                  placeholder="选择当前销售阶段"
                  onChange={handleStageChange}
                >
                  {Object.entries(STAGE_CONFIG).map(([stage, config]) => (
                    <Option key={stage} value={stage}>
                      <Space>
                        <Tag color={config.color}>{stage}</Tag>
                        <span style={{ color: '#999' }}>{config.probability}%</span>
                      </Space>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="probability"
                label="成交概率"
                rules={[{ required: true, message: '请输入成交概率' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  max={100}
                  formatter={(value) => `${value}%`}
                  parser={(value) => value?.replace('%', '') as any}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="priority" label="优先级">
                <Select placeholder="选择优先级">
                  <Option value="高">
                    <Tag color="red">高优先级</Tag>
                  </Option>
                  <Option value="中">
                    <Tag color="orange">中优先级</Tag>
                  </Option>
                  <Option value="低">
                    <Tag color="blue">低优先级</Tag>
                  </Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="status" label="项目状态">
                <Select placeholder="选择状态">
                  <Option value="进行中">
                    <Tag color="processing">进行中</Tag>
                  </Option>
                  <Option value="已成交">
                    <Tag color="success">已成交</Tag>
                  </Option>
                  <Option value="已丢失">
                    <Tag>已丢失</Tag>
                  </Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="assigned_to" label="负责人">
                <Input placeholder="项目负责人姓名" prefix={<UserOutlined />} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="expected_close_date" label="预计成交时间">
                <DatePicker style={{ width: '100%' }} placeholder="选择日期" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="next_follow_up_date" label="下次跟进时间">
                <DatePicker style={{ width: '100%' }} placeholder="选择日期" />
              </Form.Item>
            </Col>
          </Row>
        );
      case 4:
        return (
          <Row gutter={24}>
            <Col span={24}>
              <Divider orientation="left">竞争信息</Divider>
            </Col>
            <Col span={24}>
              <Form.Item name="competitors" label="竞争对手">
                <TextArea
                  rows={3}
                  placeholder="列出主要竞争对手及其优劣势..."
                />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="our_advantage" label="我司优势">
                <TextArea
                  rows={3}
                  placeholder="描述我司相比竞争对手的优势..."
                />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="customer_concern" label="客户顾虑">
                <TextArea
                  rows={3}
                  placeholder="记录客户的主要顾虑和担忧..."
                />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Divider orientation="left">决策信息</Divider>
            </Col>
            <Col span={12}>
              <Form.Item name="decision_maker" label="决策人">
                <Input placeholder="最终决策人姓名" prefix={<TrophyOutlined />} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="decision_process" label="决策流程">
                <TextArea
                  rows={2}
                  placeholder="描述客户的决策流程和周期..."
                />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item label="关键联系人">
                <Form.List name="key_contacts">
                  {(fields, { add, remove }) => (
                    <>
                      {fields.map(({ key, name, ...restField }) => (
                        <Card
                          key={key}
                          size="small"
                          style={{ marginBottom: 8 }}
                          extra={
                            <Button
                              type="link"
                              danger
                              icon={<MinusCircleOutlined />}
                              onClick={() => remove(name)}
                            >
                              删除
                            </Button>
                          }
                        >
                          <Row gutter={16}>
                            <Col span={6}>
                              <Form.Item
                                {...restField}
                                name={[name, 'name']}
                                rules={[{ required: true, message: '请输入姓名' }]}
                              >
                                <Input placeholder="姓名" prefix={<UserOutlined />} />
                              </Form.Item>
                            </Col>
                            <Col span={6}>
                              <Form.Item {...restField} name={[name, 'position']}>
                                <Input placeholder="职位" />
                              </Form.Item>
                            </Col>
                            <Col span={6}>
                              <Form.Item {...restField} name={[name, 'phone']}>
                                <Input placeholder="电话" prefix={<PhoneOutlined />} />
                              </Form.Item>
                            </Col>
                            <Col span={6}>
                              <Form.Item {...restField} name={[name, 'email']}>
                                <Input placeholder="邮箱" prefix={<MailOutlined />} />
                              </Form.Item>
                            </Col>
                            <Col span={24}>
                              <Form.Item {...restField} name={[name, 'role']}>
                                <Input placeholder="在项目中的角色（如：技术负责人、采购经理等）" />
                              </Form.Item>
                            </Col>
                          </Row>
                        </Card>
                      ))}
                      <Button
                        type="dashed"
                        onClick={() => add()}
                        block
                        icon={<PlusOutlined />}
                      >
                        添加关键联系人
                      </Button>
                    </>
                  )}
                </Form.List>
              </Form.Item>
            </Col>
          </Row>
        );
      default:
        return null;
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={{
        project_type: '新建酒店',
        stage: '初步接触',
        priority: '中',
        status: '进行中',
        probability: 10,
      }}
    >
      <Steps
        current={currentStep}
        onChange={setCurrentStep}
        items={steps}
        style={{ marginBottom: 24 }}
      />

      <Card style={{ minHeight: 400, marginBottom: 24 }}>
        {renderStepContent()}
      </Card>

      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          {currentStep > 0 && (
            <Button onClick={() => setCurrentStep(currentStep - 1)}>
              上一步
            </Button>
          )}
          {currentStep < steps.length - 1 && (
            <Button type="primary" onClick={() => setCurrentStep(currentStep + 1)}>
              下一步
            </Button>
          )}
        </Space>

        <Space>
          <Button icon={<CloseOutlined />} onClick={onCancel}>
            取消
          </Button>
          {currentStep === steps.length - 1 && (
            <Button
              type="primary"
              icon={<SaveOutlined />}
              htmlType="submit"
              loading={loading}
            >
              {isEditing ? '保存修改' : '创建机会'}
            </Button>
          )}
        </Space>
      </div>
    </Form>
  );
};

export default OpportunityForm;
