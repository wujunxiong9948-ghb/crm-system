import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
  Upload,
  Image,
  Typography,
  Spin,
  Divider,
} from 'antd';
import {
  ArrowLeftOutlined,
  SaveOutlined,
  UploadOutlined,
  PictureOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { apiService } from '@/services/api';
import { Product } from '@/types';
import type { UploadFile } from 'antd/es/upload/interface';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// 产品分类选项
const CATEGORY_OPTIONS = [
  '床',
  '床头柜',
  '衣柜',
  '书桌',
  '椅子',
  '沙发',
  '茶几',
  '电视柜',
  '梳妆台',
  '行李架',
  '客房门',
  '浴室柜',
  '其他',
];

// 材质选项
const MATERIAL_OPTIONS = [
  '实木',
  '板材',
  '金属',
  '皮革',
  '布艺',
  '玻璃',
  '大理石',
  '岩板',
  '藤编',
  '其他',
];

interface ProductFormData {
  product_code: string;
  item_id?: string;
  category?: string;
  description?: string;
  material?: string;
  moq?: number;
  unit_price?: number;
  specifications?: string;
  status: '可用' | '停用' | '缺货';
  images?: string[];
}

const ProductForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const isEdit = !!id;

  // 获取产品详情（编辑模式）
  useEffect(() => {
    if (isEdit) {
      fetchProductDetail();
    }
  }, [id]);

  const fetchProductDetail = async () => {
    setLoading(true);
    try {
      const response = await apiService.get(`/products/${id}`);
      if (response.success) {
        const product: Product = response.data;
        form.setFieldsValue({
          product_code: product.product_code,
          item_id: product.item_id,
          category: product.category,
          description: product.description,
          material: product.material,
          moq: product.moq,
          unit_price: product.unit_price,
          specifications: product.specifications,
          status: product.status,
        });

        // 解析图片
        if (product.images) {
          try {
            const images = JSON.parse(product.images);
            if (Array.isArray(images)) {
              setFileList(
                images.map((url, index) => ({
                  uid: `-${index}`,
                  name: `图片${index + 1}`,
                  status: 'done',
                  url,
                }))
              );
            }
          } catch {
            setFileList([
              {
                uid: '-1',
                name: '图片1',
                status: 'done',
                url: product.images,
              },
            ]);
          }
        }
      } else {
        message.error(response.message || '获取产品详情失败');
      }
    } catch (error) {
      console.error('获取产品详情失败:', error);
      message.error('获取产品详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 提交表单
  const handleSubmit = async (values: ProductFormData) => {
    setSaving(true);
    try {
      // 处理图片
      const images = fileList
        .filter((file) => file.status === 'done' && file.url)
        .map((file) => file.url!);

      const data = {
        ...values,
        images,
      };

      let response;
      if (isEdit) {
        response = await apiService.put(`/products/${id}`, data);
      } else {
        response = await apiService.post('/products', data);
      }

      if (response.success) {
        message.success(isEdit ? '产品更新成功' : '产品创建成功');
        navigate('/products');
      } else {
        message.error(response.message || (isEdit ? '更新失败' : '创建失败'));
      }
    } catch (error: any) {
      console.error(isEdit ? '更新产品失败:' : '创建产品失败:', error);
      message.error(error.response?.data?.message || (isEdit ? '更新产品失败' : '创建产品失败'));
    } finally {
      setSaving(false);
    }
  };

  // 处理图片上传
  const handleUpload = (info: any) => {
    let newFileList = [...info.fileList];

    // 限制最多5张图片
    newFileList = newFileList.slice(-5);

    // 处理上传状态
    newFileList = newFileList.map((file) => {
      if (file.response) {
        file.url = file.response.url;
      }
      return file;
    });

    setFileList(newFileList);
  };

  // 处理图片删除
  const handleRemove = (file: UploadFile) => {
    const newFileList = fileList.filter((item) => item.uid !== file.uid);
    setFileList(newFileList);
  };

  // 模拟上传（实际项目中需要接入真实的图片上传服务）
  const customRequest = ({ file, onSuccess }: any) => {
    // 这里模拟上传，实际应该调用上传API
    setTimeout(() => {
      // 创建本地预览URL
      const url = URL.createObjectURL(file);
      onSuccess?.({ url });
    }, 500);
  };

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/products')}
          className="mb-4"
        >
          返回列表
        </Button>
        <Title level={2}>{isEdit ? '编辑产品' : '新增产品'}</Title>
        <Text type="secondary">
          {isEdit ? '修改产品信息' : '填写产品基本信息创建新产品'}
        </Text>
      </div>

      <Spin spinning={loading}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            status: '可用',
            moq: 1,
            unit_price: 0,
          }}
        >
          <Row gutter={24}>
            {/* 左侧：基本信息 */}
            <Col xs={24} lg={16}>
              <Card title="基本信息" className="mb-6">
                <Row gutter={16}>
                  <Col xs={24} md={12}>
                    <Form.Item
                      name="product_code"
                      label="产品编码"
                      rules={[
                        { required: true, message: '请输入产品编码' },
                        { max: 50, message: '产品编码最多50个字符' },
                      ]}
                    >
                      <Input placeholder="例如：BED-001" disabled={isEdit} />
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={12}>
                    <Form.Item
                      name="item_id"
                      label="项目ID"
                      rules={[{ max: 50, message: '项目ID最多50个字符' }]}
                    >
                      <Input placeholder="可选，内部项目编号" />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col xs={24} md={12}>
                    <Form.Item
                      name="category"
                      label="产品分类"
                      rules={[{ required: true, message: '请选择产品分类' }]}
                    >
                      <Select placeholder="选择分类">
                        {CATEGORY_OPTIONS.map((cat) => (
                          <Option key={cat} value={cat}>
                            {cat}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={12}>
                    <Form.Item name="material" label="材质">
                      <Select placeholder="选择材质" allowClear>
                        {MATERIAL_OPTIONS.map((mat) => (
                          <Option key={mat} value={mat}>
                            {mat}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item
                  name="description"
                  label="产品描述"
                  rules={[{ required: true, message: '请输入产品描述' }]}
                >
                  <TextArea
                    rows={4}
                    placeholder="详细描述产品的特点、用途等信息"
                    showCount
                    maxLength={500}
                  />
                </Form.Item>

                <Form.Item name="specifications" label="规格参数">
                  <TextArea
                    rows={4}
                    placeholder="填写产品的详细规格参数，如尺寸、重量、颜色等"
                    showCount
                    maxLength={1000}
                  />
                </Form.Item>
              </Card>

              <Card title="价格与库存">
                <Row gutter={16}>
                  <Col xs={24} md={8}>
                    <Form.Item
                      name="unit_price"
                      label="单价 (¥)"
                      rules={[{ required: true, message: '请输入单价' }]}
                    >
                      <InputNumber
                        style={{ width: '100%' }}
                        min={0}
                        precision={2}
                        placeholder="0.00"
                        formatter={(value) =>
                          value ? `¥ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',') : ''
                        }
                        parser={(value: string | undefined) =>
                          value ? parseFloat(value.replace(/[¥\s,]/g, '')) : 0
                        }
                      />
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={8}>
                    <Form.Item name="moq" label="最小起订量 (MOQ)">
                      <InputNumber
                        style={{ width: '100%' }}
                        min={1}
                        precision={0}
                        placeholder="1"
                      />
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={8}>
                    <Form.Item
                      name="status"
                      label="产品状态"
                      rules={[{ required: true, message: '请选择状态' }]}
                    >
                      <Select>
                        <Option value="可用">可用</Option>
                        <Option value="停用">停用</Option>
                        <Option value="缺货">缺货</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            </Col>

            {/* 右侧：产品图片 */}
            <Col xs={24} lg={8}>
              <Card title="产品图片" className="mb-6">
                <Upload
                  listType="picture-card"
                  fileList={fileList}
                  onChange={handleUpload}
                  onRemove={handleRemove}
                  customRequest={customRequest}
                  multiple
                  maxCount={5}
                >
                  {fileList.length >= 5 ? null : (
                    <div>
                      <UploadOutlined />
                      <div style={{ marginTop: 8 }}>上传图片</div>
                    </div>
                  )}
                </Upload>
                <Text type="secondary" className="block mt-2">
                  最多上传5张图片，建议尺寸800x800像素
                </Text>
              </Card>

              <Card title="操作">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    onClick={() => form.submit()}
                    loading={saving}
                    block
                    size="large"
                  >
                    {isEdit ? '保存修改' : '创建产品'}
                  </Button>
                  <Button
                    onClick={() => navigate('/products')}
                    block
                  >
                    取消
                  </Button>
                </Space>
              </Card>
            </Col>
          </Row>
        </Form>
      </Spin>
    </div>
  );
};

export default ProductForm;