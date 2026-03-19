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
  Image,
  Typography,
  Divider,
  Popconfirm,
  Empty,
  Carousel,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  PictureOutlined,
  FileTextOutlined,
  DollarOutlined,
  TagsOutlined,
  BoxPlotOutlined,
} from '@ant-design/icons';
import { apiService } from '@/services/api';
import { usePermission, PERMISSION_CODES } from '@/utils/permission';
import { Product } from '@/types';

const { Title, Text } = Typography;

const ProductDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { hasPermissionCode } = usePermission();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [images, setImages] = useState<string[]>([]);

  // 获取产品详情
  const fetchProductDetail = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const response = await apiService.get(`/products/${id}`);
      if (response.success) {
        setProduct(response.data);
        // 解析图片
        if (response.data.images) {
          try {
            const parsedImages = JSON.parse(response.data.images);
            setImages(Array.isArray(parsedImages) ? parsedImages : [response.data.images]);
          } catch {
            setImages([response.data.images]);
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

  useEffect(() => {
    fetchProductDetail();
  }, [id]);

  // 删除产品
  const handleDelete = async () => {
    if (!id) return;
    try {
      const response = await apiService.delete(`/products/${id}`);
      if (response.success) {
        message.success('产品删除成功');
        navigate('/products');
      } else {
        message.error(response.message || '删除失败');
      }
    } catch (error) {
      console.error('删除产品失败:', error);
      message.error('删除产品失败');
    }
  };

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      '可用': { color: 'success', text: '可用' },
      '停用': { color: 'default', text: '停用' },
      '缺货': { color: 'error', text: '缺货' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  if (loading) {
    return (
      <div className="p-6 flex justify-center items-center min-h-96">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="p-6">
        <Empty description="产品不存在或已被删除" />
        <div className="text-center mt-4">
          <Button onClick={() => navigate('/products')} icon={<ArrowLeftOutlined />}>
            返回产品列表
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* 页面标题和操作按钮 */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/products')}
            className="mb-4"
          >
            返回列表
          </Button>
          <Title level={2} className="!mb-0">
            {product.product_code}
          </Title>
          <Text type="secondary">{product.description || '暂无描述'}</Text>
        </div>
        <Space>
          {hasPermissionCode(PERMISSION_CODES.PRODUCT_UPDATE) && (
            <Button
              icon={<EditOutlined />}
              onClick={() => navigate(`/products/${id}/edit`)}
            >
              编辑
            </Button>
          )}
          {hasPermissionCode(PERMISSION_CODES.PRODUCT_DELETE) && (
            <Popconfirm
              title="确认删除"
              description="确定要删除这个产品吗？此操作不可恢复。"
              onConfirm={handleDelete}
              okText="删除"
              cancelText="取消"
              okButtonProps={{ danger: true }}
            >
              <Button danger icon={<DeleteOutlined />}>
                删除
              </Button>
            </Popconfirm>
          )}
        </Space>
      </div>

      <Row gutter={24}>
        {/* 左侧：产品图片 */}
        <Col xs={24} lg={8}>
          <Card title="产品图片" className="mb-6">
            {images.length > 0 ? (
              <Carousel autoplay={images.length > 1}>
                {images.map((img, index) => (
                  <div key={index} className="bg-gray-100 flex items-center justify-center">
                    <Image
                      src={img}
                      alt={`产品图片 ${index + 1}`}
                      className="max-h-80 object-contain"
                      fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
                    />
                  </div>
                ))}
              </Carousel>
            ) : (
              <div className="h-64 bg-gray-100 rounded flex flex-col items-center justify-center">
                <PictureOutlined className="text-4xl text-gray-400 mb-2" />
                <Text type="secondary">暂无产品图片</Text>
              </div>
            )}
          </Card>

          {/* 价格信息 */}
          <Card title="价格信息" className="mb-6">
            <Descriptions column={1} bordered>
              <Descriptions.Item label="单价">
                <Text strong className="text-lg text-red-500">
                  {product.unit_price ? `¥${product.unit_price.toFixed(2)}` : '未设置'}
                </Text>
              </Descriptions.Item>
              <Descriptions.Item label="最小起订量 (MOQ)">
                {product.moq || 0} 件
              </Descriptions.Item>
              <Descriptions.Item label="货币">
                CNY (人民币)
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 右侧：产品详情 */}
        <Col xs={24} lg={16}>
          <Card title="基本信息" className="mb-6">
            <Descriptions column={2} bordered>
              <Descriptions.Item label="产品编码">
                {product.product_code}
              </Descriptions.Item>
              <Descriptions.Item label="项目ID">
                {product.item_id || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="产品分类">
                <Tag icon={<TagsOutlined />}>
                  {product.category || '未分类'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="材质">
                {product.material || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                {getStatusTag(product.status)}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {product.created_at
                  ? new Date(product.created_at).toLocaleString('zh-CN')
                  : '-'}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          <Card title="产品描述" className="mb-6">
            <div className="min-h-24 p-4 bg-gray-50 rounded">
              {product.description ? (
                <Text>{product.description}</Text>
              ) : (
                <Text type="secondary">暂无产品描述</Text>
              )}
            </div>
          </Card>

          <Card title="规格参数" className="mb-6">
            <div className="min-h-24 p-4 bg-gray-50 rounded">
              {product.specifications ? (
                <Text style={{ whiteSpace: 'pre-wrap' }}>{product.specifications}</Text>
              ) : (
                <Text type="secondary">暂无规格参数</Text>
              )}
            </div>
          </Card>

          <Card title="系统信息">
            <Descriptions column={2} bordered>
              <Descriptions.Item label="产品ID">{product.id}</Descriptions.Item>
              <Descriptions.Item label="更新时间">
                {product.updated_at
                  ? new Date(product.updated_at).toLocaleString('zh-CN')
                  : '-'}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ProductDetail;