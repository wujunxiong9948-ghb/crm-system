import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Button,
  Row,
  Col,
  Card,
  Divider,
  message,
  Space,
  Slider,
  Cascader,
} from 'antd';
import { SaveOutlined, CloseOutlined } from '@ant-design/icons';
import { apiService, apiEndpoints } from '../../services/api';
import dayjs from 'dayjs';

const { Option } = Select;
const { TextArea } = Input;

// 中国省市区数据（简化版，实际项目中可以从后端获取或使用完整数据）
const regionData = [
  {
    value: '广东省',
    label: '广东省',
    children: [
      { value: '广州市', label: '广州市', children: [{ value: '天河区', label: '天河区' }, { value: '越秀区', label: '越秀区' }, { value: '海珠区', label: '海珠区' }, { value: '番禺区', label: '番禺区' }] },
      { value: '深圳市', label: '深圳市', children: [{ value: '福田区', label: '福田区' }, { value: '南山区', label: '南山区' }, { value: '罗湖区', label: '罗湖区' }, { value: '宝安区', label: '宝安区' }] },
      { value: '佛山市', label: '佛山市', children: [{ value: '禅城区', label: '禅城区' }, { value: '南海区', label: '南海区' }, { value: '顺德区', label: '顺德区' }] },
      { value: '东莞市', label: '东莞市', children: [{ value: '莞城区', label: '莞城区' }, { value: '南城区', label: '南城区' }] },
    ],
  },
  {
    value: '浙江省',
    label: '浙江省',
    children: [
      { value: '杭州市', label: '杭州市', children: [{ value: '西湖区', label: '西湖区' }, { value: '上城区', label: '上城区' }, { value: '滨江区', label: '滨江区' }] },
      { value: '宁波市', label: '宁波市', children: [{ value: '海曙区', label: '海曙区' }, { value: '江北区', label: '江北区' }] },
    ],
  },
  {
    value: '江苏省',
    label: '江苏省',
    children: [
      { value: '南京市', label: '南京市', children: [{ value: '玄武区', label: '玄武区' }, { value: '秦淮区', label: '秦淮区' }, { value: '鼓楼区', label: '鼓楼区' }] },
      { value: '苏州市', label: '苏州市', children: [{ value: '姑苏区', label: '姑苏区' }, { value: '工业园区', label: '工业园区' }] },
    ],
  },
  {
    value: '北京市',
    label: '北京市',
    children: [
      { value: '北京市', label: '北京市', children: [{ value: '朝阳区', label: '朝阳区' }, { value: '海淀区', label: '海淀区' }, { value: '东城区', label: '东城区' }, { value: '西城区', label: '西城区' }] },
    ],
  },
  {
    value: '上海市',
    label: '上海市',
    children: [
      { value: '上海市', label: '上海市', children: [{ value: '黄浦区', label: '黄浦区' }, { value: '静安区', label: '静安区' }, { value: '浦东新区', label: '浦东新区' }, { value: '徐汇区', label: '徐汇区' }] },
    ],
  },
];

interface Customer {
  id: number;
  name: string;
  company: string;
}

interface OpportunityFormProps {
  opportunity?: {
    id?: number;
    name?: string;
    hotel_name?: string;
    project_address?: string;
    project_type?: string;
    star_rating?: string;
    room_count?: number;
    planned_opening_date?: string;
    expected_close_date?: string;
    expected_value?: number;
    furniture_budget?: number;
    renovation_budget?: number;
    stage?: string;
    probability?: number;
    status?: string;
    priority?: string;
    assigned_to?: string;
    customer_id?: number;
    description?: string;
    notes?: string;
    next_follow_up_date?: string;
    competitors?: string;
    our_advantage?: string;
    product_quantity?: {
      beds?: number;
      nightstands?: number;
      wardrobes?: number;
      desks?: number;
      chairs?: number;
      sofas?: number;
      coffee_tables?: number;
      tv_cabinets?: number;
      other?: number;
    };
  } | null;
  onSuccess: () => void;
  onCancel: () => void;
}

const OpportunityForm: React.FC<OpportunityFormProps> = ({
  opportunity,
  onSuccess,
  onCancel,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [probability, setProbability] = useState(opportunity?.probability || 30);

  // 获取客户列表
  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        const response = await apiService.get<{ customers: Customer[] }>(
          `${apiEndpoints.customers.list}?per_page=1000`
        );
        setCustomers(response.customers || []);
      } catch (error) {
        console.error('获取客户列表失败:', error);
      }
    };
    fetchCustomers();
  }, []);

  // 设置表单初始值
  useEffect(() => {
    if (opportunity) {
      // 解析地址为省市区
      let addressRegion: string[] = [];
      let detailAddress = opportunity.project_address || '';

      // 尝试匹配省市区
      for (const province of regionData) {
        if (detailAddress.startsWith(province.value)) {
          for (const city of province.children || []) {
            if (detailAddress.includes(city.value)) {
              for (const district of city.children || []) {
                if (detailAddress.includes(district.value)) {
                  addressRegion = [province.value, city.value, district.value];
                  detailAddress = detailAddress.replace(`${province.value}${city.value}${district.value}`, '').trim();
                  break;
                }
              }
              if (addressRegion.length === 0) {
                addressRegion = [province.value, city.value];
                detailAddress = detailAddress.replace(`${province.value}${city.value}`, '').trim();
              }
              break;
            }
          }
          if (addressRegion.length === 0) {
            addressRegion = [province.value];
            detailAddress = detailAddress.replace(province.value, '').trim();
          }
          break;
        }
      }

      form.setFieldsValue({
        ...opportunity,
        address_region: addressRegion,
        detail_address: detailAddress,
        planned_opening_date: opportunity.planned_opening_date ? dayjs(opportunity.planned_opening_date) : null,
        expected_close_date: opportunity.expected_close_date ? dayjs(opportunity.expected_close_date) : null,
        next_follow_up_date: opportunity.next_follow_up_date ? dayjs(opportunity.next_follow_up_date) : null,
        product_quantity: opportunity.product_quantity || {},
      });
      setProbability(opportunity.probability || 30);
    } else {
      form.resetFields();
      form.setFieldsValue({
        stage: '初步接触',
        probability: 30,
        status: '进行中',
        priority: '中',
        project_type: '新建酒店',
        room_count: 100,
        product_quantity: {},
      });
      setProbability(30);
    }
  }, [opportunity, form]);

  // 阶段与概率映射
  const stageProbabilityMap: Record<string, number> = {
    '初步接触': 10,
    '需求调研': 25,
    '方案设计': 40,
    '报价谈判': 60,
    '合同签订': 80,
    '成交': 100,
    '丢失': 0,
  };

  // 处理阶段变化，自动更新概率
  const handleStageChange = (stage: string) => {
    const newProbability = stageProbabilityMap[stage] || 30;
    setProbability(newProbability);
    form.setFieldsValue({ probability: newProbability });
  };

  // 提交表单
  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      // 组装地址
      const region = values.address_region || [];
      const detailAddress = values.detail_address || '';
      const fullAddress = region.join('') + detailAddress;

      const submitData = {
        ...values,
        project_address: fullAddress,
        planned_opening_date: values.planned_opening_date?.format('YYYY-MM-DD'),
        expected_close_date: values.expected_close_date?.format('YYYY-MM-DD'),
        next_follow_up_date: values.next_follow_up_date?.format('YYYY-MM-DD'),
      };

      // 删除前端使用的临时字段
      delete submitData.address_region;
      delete submitData.detail_address;

      if (opportunity?.id) {
        await apiService.put(apiEndpoints.opportunities.update(opportunity.id), submitData);
        message.success('项目机会更新成功');
      } else {
        await apiService.post(apiEndpoints.opportunities.create, submitData);
        message.success('项目机会创建成功');
      }
      onSuccess();
    } catch (error) {
      message.error(opportunity?.id ? '更新失败' : '创建失败');
      console.error('提交失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      autoComplete="off"
    >
      {/* 基本信息 */}
      <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="name"
              label="项目名称"
              rules={[{ required: true, message: '请输入项目名称' }]}
              tooltip="例如：XX酒店家具采购项目"
            >
              <Input placeholder="请输入项目名称" maxLength={100} showCount />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="customer_id"
              label="关联客户"
              rules={[{ required: true, message: '请选择关联客户' }]}
            >
              <Select
                placeholder="请选择客户"
                showSearch
                optionFilterProp="children"
                filterOption={(input, option) =>
                  (option?.children as unknown as string)?.toLowerCase().includes(input.toLowerCase())
                }
              >
                {customers.map(customer => (
                  <Option key={customer.id} value={customer.id}>
                    {customer.name} {customer.company ? `(${customer.company})` : ''}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="hotel_name"
              label="酒店名称"
              rules={[{ required: true, message: '请输入酒店名称' }]}
            >
              <Input placeholder="请输入酒店名称" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="project_type"
              label="项目类型"
              rules={[{ required: true, message: '请选择项目类型' }]}
            >
              <Select placeholder="请选择项目类型">
                <Option value="新建酒店">新建酒店</Option>
                <Option value="酒店翻新">酒店翻新</Option>
                <Option value="连锁扩张">连锁扩张</Option>
                <Option value="其他">其他</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="address_region"
              label="项目地区"
              rules={[{ required: true, message: '请选择项目地区' }]}
            >
              <Cascader
                options={regionData}
                placeholder="请选择省市区"
                showSearch
              />
            </Form.Item>
          </Col>
          <Col span={16}>
            <Form.Item
              name="detail_address"
              label="详细地址"
              rules={[{ required: true, message: '请输入详细地址' }]}
            >
              <Input placeholder="请输入详细街道地址" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="star_rating"
              label="酒店星级"
            >
              <Select placeholder="请选择酒店星级" allowClear>
                <Option value="经济型">经济型</Option>
                <Option value="三星">三星</Option>
                <Option value="四星">四星</Option>
                <Option value="五星">五星</Option>
                <Option value="奢华">奢华</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="room_count"
              label="客房数量"
              rules={[{ required: true, message: '请输入客房数量' }]}
              tooltip="购买套装的客房数量"
            >
              <InputNumber
                min={1}
                max={10000}
                style={{ width: '100%' }}
                placeholder="请输入客房数量"
                addonAfter="间"
              />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="planned_opening_date"
              label="计划开业时间"
            >
              <DatePicker style={{ width: '100%' }} placeholder="请选择计划开业时间" />
            </Form.Item>
          </Col>
        </Row>
      </Card>

      {/* 产品数量 */}
      <Card title="产品数量预估" size="small" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Form.Item name={['product_quantity', 'beds']} label="床">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="数量" />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name={['product_quantity', 'nightstands']} label="床头柜">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="数量" />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name={['product_quantity', 'wardrobes']} label="衣柜">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="数量" />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name={['product_quantity', 'desks']} label="书桌">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="数量" />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={6}>
            <Form.Item name={['product_quantity', 'chairs']} label="椅子">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="数量" />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name={['product_quantity', 'sofas']} label="沙发">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="数量" />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name={['product_quantity', 'coffee_tables']} label="茶几">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="数量" />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item name={['product_quantity', 'tv_cabinets']} label="电视柜">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="数量" />
            </Form.Item>
          </Col>
        </Row>
      </Card>

      {/* 预算信息 */}
      <Card title="预算信息" size="small" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="renovation_budget"
              label="装修翻新预算"
            >
              <InputNumber
                min={0}
                step={10}
                style={{ width: '100%' }}
                placeholder="请输入装修预算"
                addonAfter="万元"
              />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="furniture_budget"
              label="家具采购预算"
            >
              <InputNumber
                min={0}
                step={10}
                style={{ width: '100%' }}
                placeholder="请输入家具预算"
                addonAfter="万元"
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
                min={0}
                step={10}
                style={{ width: '100%' }}
                placeholder="请输入预计金额"
                addonAfter="万元"
              />
            </Form.Item>
          </Col>
        </Row>
      </Card>

      {/* 销售跟进 */}
      <Card title="销售跟进" size="small" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="stage"
              label="销售阶段"
              rules={[{ required: true, message: '请选择销售阶段' }]}
            >
              <Select placeholder="请选择销售阶段" onChange={handleStageChange}>
                <Option value="初步接触">初步接触</Option>
                <Option value="需求调研">需求调研</Option>
                <Option value="方案设计">方案设计</Option>
                <Option value="报价谈判">报价谈判</Option>
                <Option value="合同签订">合同签订</Option>
                <Option value="成交">成交</Option>
                <Option value="丢失">丢失</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="status"
              label="状态"
              rules={[{ required: true, message: '请选择状态' }]}
            >
              <Select placeholder="请选择状态">
                <Option value="进行中">进行中</Option>
                <Option value="已成交">已成交</Option>
                <Option value="已丢失">已丢失</Option>
                <Option value="暂停">暂停</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="priority"
              label="优先级"
              rules={[{ required: true, message: '请选择优先级' }]}
            >
              <Select placeholder="请选择优先级">
                <Option value="高">高</Option>
                <Option value="中">中</Option>
                <Option value="低">低</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="probability"
              label={`成交概率: ${probability}%`}
              rules={[{ required: true, message: '请设置成交概率' }]}
            >
              <Slider
                min={0}
                max={100}
                step={5}
                marks={{ 0: '0%', 25: '25%', 50: '50%', 75: '75%', 100: '100%' }}
                onChange={(value) => setProbability(value)}
              />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item
              name="expected_close_date"
              label="预计成交时间"
            >
              <DatePicker style={{ width: '100%' }} placeholder="请选择预计成交时间" />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item
              name="next_follow_up_date"
              label="下次跟进时间"
            >
              <DatePicker style={{ width: '100%' }} placeholder="请选择下次跟进时间" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="assigned_to"
              label="负责人"
            >
              <Input placeholder="请输入负责人" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="competitors"
              label="竞争对手"
            >
              <Input placeholder="请输入竞争对手信息" />
            </Form.Item>
          </Col>
        </Row>
      </Card>

      {/* 其他信息 */}
      <Card title="其他信息" size="small" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="our_advantage"
              label="我司优势"
            >
              <TextArea rows={3} placeholder="描述我司相对于竞争对手的优势" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="description"
              label="项目描述"
            >
              <TextArea rows={3} placeholder="请输入项目描述" />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item
          name="notes"
          label="备注"
        >
          <TextArea rows={3} placeholder="请输入备注信息" />
        </Form.Item>
      </Card>

      {/* 操作按钮 */}
      <Divider />
      <Form.Item style={{ marginBottom: 0 }}>
        <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
          <Button icon={<CloseOutlined />} onClick={onCancel}>
            取消
          </Button>
          <Button
            type="primary"
            htmlType="submit"
            icon={<SaveOutlined />}
            loading={loading}
          >
            {opportunity?.id ? '保存修改' : '创建项目'}
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default OpportunityForm;
