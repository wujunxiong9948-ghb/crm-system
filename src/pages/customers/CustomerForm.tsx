import React, { useEffect } from 'react';
import { Form, Input, Select, Button, Space, Row, Col, message } from 'antd';
import { apiService, apiEndpoints } from '../../services/api';

const { TextArea } = Input;
const { Option } = Select;

interface Customer {
  id: number;
  name: string;
  company?: string;
  phone?: string;
  email?: string;
  address?: string;
  industry?: string;
  customer_type?: string;
  source?: string;
  status?: string;
  notes?: string;
}

interface CustomerFormProps {
  customer?: Customer;
  onSuccess: () => void;
  onCancel: () => void;
}

const CustomerForm: React.FC<CustomerFormProps> = ({ customer, onSuccess, onCancel }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (customer) {
      form.setFieldsValue(customer);
    } else {
      form.resetFields();
    }
  }, [customer, form]);

  const handleSubmit = async (values: Record<string, unknown>) => {
    try {
      if (customer) {
        // 更新客户
        await apiService.put(apiEndpoints.customers.update(customer.id), values);
        message.success('客户更新成功');
      } else {
        // 创建客户
        await apiService.post(apiEndpoints.customers.create, values);
        message.success('客户创建成功');
      }
      onSuccess();
    } catch (error: unknown) {
      const err = error as { response?: { data?: { error?: string } } };
      if (err.response?.data?.error) {
        message.error(err.response.data.error);
      } else {
        message.error(customer ? '更新客户失败' : '创建客户失败');
      }
      console.error('表单提交失败:', error);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={{
        customer_type: '潜在客户',
        status: '活跃',
        source: '其他',
      }}
    >
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="name"
            label="客户姓名"
            rules={[{ required: true, message: '请输入客户姓名' }]}
          >
            <Input placeholder="请输入客户姓名" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="company" label="公司名称">
            <Input placeholder="请输入公司名称" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="phone"
            label="联系电话"
            rules={[{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }]}
          >
            <Input placeholder="请输入手机号" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="email"
            label="邮箱"
            rules={[{ type: 'email', message: '请输入正确的邮箱格式' }]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item name="address" label="地址">
        <Input placeholder="请输入地址" />
      </Form.Item>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="industry" label="行业">
            <Select placeholder="请选择行业">
              <Option value="酒店">酒店</Option>
              <Option value="餐饮">餐饮</Option>
              <Option value="办公">办公</Option>
              <Option value="住宅">住宅</Option>
              <Option value="商业">商业</Option>
              <Option value="其他">其他</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item
            name="customer_type"
            label="客户类型"
            rules={[{ required: true, message: '请选择客户类型' }]}
          >
            <Select>
              <Option value="潜在客户">潜在客户</Option>
              <Option value="现有客户">现有客户</Option>
              <Option value="VIP客户">VIP客户</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item name="source" label="客户来源">
            <Select>
              <Option value="展会">展会</Option>
              <Option value="推荐">推荐</Option>
              <Option value="网站">网站</Option>
              <Option value="电话">电话</Option>
              <Option value="微信">微信</Option>
              <Option value="其他">其他</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="status" label="客户状态">
            <Select>
              <Option value="活跃">活跃</Option>
              <Option value="休眠">休眠</Option>
              <Option value="流失">流失</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Form.Item name="notes" label="备注">
        <TextArea rows={4} placeholder="请输入备注信息" maxLength={500} showCount />
      </Form.Item>

      <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
        <Space>
          <Button onClick={onCancel}>取消</Button>
          <Button type="primary" htmlType="submit">
            {customer ? '更新' : '创建'}
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default CustomerForm;
