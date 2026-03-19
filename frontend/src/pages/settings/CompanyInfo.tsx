import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, message, Row, Col, Upload, Avatar } from 'antd';
import {
  SaveOutlined,
  UploadOutlined,
  BankOutlined,
  GlobalOutlined,
  PhoneOutlined,
  MailOutlined,
} from '@ant-design/icons';
import { companyApi } from '../../services/api';

interface CompanyData {
  name: string;
  short_name: string;
  logo: string;
  address: string;
  phone: string;
  fax: string;
  email: string;
  website: string;
  business_license: string;
  tax_number: string;
  bank_name: string;
  bank_account: string;
  description: string;
}

const CompanyInfo: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [logoUrl, setLogoUrl] = useState('');

  const fetchCompanyInfo = async () => {
    setLoading(true);
    try {
      const data = await companyApi.getCompanyInfo();
      form.setFieldsValue(data);
      setLogoUrl(data.logo || '');
    } catch (error) {
      message.error('获取公司信息失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanyInfo();
  }, []);

  const handleSave = async (values: CompanyData) => {
    setSaving(true);
    try {
      await companyApi.updateCompanyInfo(values);
      message.success('公司信息保存成功');
    } catch (error: any) {
      message.error(error.response?.data?.error || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleLogoUpload = async (info: any) => {
    if (info.file.status === 'done') {
      message.success('Logo上传成功');
      setLogoUrl(info.file.response.logo_url);
      form.setFieldsValue({ logo: info.file.response.logo_url });
    } else if (info.file.status === 'error') {
      message.error('Logo上传失败');
    }
  };

  return (
    <Card
      title={
        <span>
          <BankOutlined /> 公司信息设置
        </span>
      }
      loading={loading}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        initialValues={{
          name: '',
          short_name: '',
          logo: '',
          address: '',
          phone: '',
          fax: '',
          email: '',
          website: '',
          business_license: '',
          tax_number: '',
          bank_name: '',
          bank_account: '',
          description: '',
        }}
      >
        <Row gutter={24}>
          <Col span={16}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="name"
                  label="公司全称"
                  rules={[{ required: true, message: '请输入公司全称' }]}
                >
                  <Input placeholder="请输入公司全称" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="short_name" label="公司简称">
                  <Input placeholder="请输入公司简称" />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="phone" label="联系电话">
                  <Input prefix={<PhoneOutlined />} placeholder="请输入联系电话" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="fax" label="传真">
                  <Input placeholder="请输入传真号码" />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="email" label="电子邮箱">
                  <Input prefix={<MailOutlined />} placeholder="请输入电子邮箱" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="website" label="公司网站">
                  <Input prefix={<GlobalOutlined />} placeholder="请输入公司网站" />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item name="address" label="公司地址">
              <Input.TextArea rows={2} placeholder="请输入公司地址" />
            </Form.Item>
          </Col>

          <Col span={8}>
            <Form.Item name="logo" label="公司Logo">
              <div style={{ textAlign: 'center' }}>
                <Avatar
                  size={120}
                  src={logoUrl}
                  icon={<BankOutlined />}
                  shape="square"
                  style={{ marginBottom: 16 }}
                />
                <Upload
                  name="logo"
                  action="/api/v1/settings/company/logo"
                  showUploadList={false}
                  onChange={handleLogoUpload}
                >
                  <Button icon={<UploadOutlined />}>上传Logo</Button>
                </Upload>
                <div style={{ fontSize: 12, color: '#999', marginTop: 8 }}>
                  建议尺寸：200x200像素
                </div>
              </div>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="business_license" label="营业执照号">
              <Input placeholder="请输入营业执照号" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="tax_number" label="纳税人识别号">
              <Input placeholder="请输入纳税人识别号" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="bank_name" label="开户银行">
              <Input placeholder="请输入开户银行" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="bank_account" label="银行账号">
              <Input placeholder="请输入银行账号" />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item name="description" label="公司简介">
          <Input.TextArea rows={4} placeholder="请输入公司简介" />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={saving}>
            保存设置
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default CompanyInfo;
