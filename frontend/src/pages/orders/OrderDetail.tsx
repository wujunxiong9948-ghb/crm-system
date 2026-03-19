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
  Typography,
  Divider,
  Popconfirm,
  Empty,
  Table,
  Steps,
  Timeline,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  CarOutlined,
  ToolOutlined,
  CloseCircleOutlined,
  PrinterOutlined,
  DollarOutlined,
} from '@ant-design/icons';
import { apiService } from '@/services/api';
import { usePermission, PERMISSION_CODES } from '@/utils/permission';
import { Order, OrderItem } from '@/types';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Step } = Steps;

const OrderDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { hasPermissionCode } = usePermission();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  // 获取订单详情
  const fetchOrderDetail = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const response = await apiService.get(`/orders/${id}`);
      if (response.success) {
        setOrder(response.data);
      } else {
        message.error(response.message || '获取订单详情失败');
      }
    } catch (error) {
      console.error('获取订单详情失败:', error);
      message.error('获取订单详情失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrderDetail();
  }, [id]);

  // 删除订单
  const handleDelete = async () => {
    if (!id) return;
    try {
      const response = await apiService.delete(`/orders/${id}`);
      if (response.success) {
        message.success('订单删除成功');
        navigate('/orders');
      } else {
        message.error(response.message || '删除失败');
      }
    } catch (error) {
      console.error('删除订单失败:', error);
      message.error('删除订单失败');
    }
  };

  // 更新订单状态
  const handleUpdateStatus = async (status: string) => {
    if (!id) return;
    setUpdating(true);
    try {
      const response = await apiService.put(`/orders/${id}/status`, { status });
      if (response.success) {
        message.success('订单状态更新成功');
        fetchOrderDetail();
      } else {
        message.error(response.message || '更新失败');
      }
    } catch (error) {
      console.error('更新订单状态失败:', error);
      message.error('更新订单状态失败');
    } finally {
      setUpdating(false);
    }
  };

  // 更新支付状态
  const handleUpdatePaymentStatus = async (paymentStatus: string) => {
    if (!id) return;
    setUpdating(true);
    try {
      const response = await apiService.put(`/orders/${id}/payment`, { payment_status: paymentStatus });
      if (response.success) {
        message.success('支付状态更新成功');
        fetchOrderDetail();
      } else {
        message.error(response.message || '更新失败');
      }
    } catch (error) {
      console.error('更新支付状态失败:', error);
      message.error('更新支付状态失败');
    } finally {
      setUpdating(false);
    }
  };

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
      '待处理': { color: 'default', icon: <FileTextOutlined />, text: '待处理' },
      '生产中': { color: 'processing', icon: <ToolOutlined />, text: '生产中' },
      '已发货': { color: 'warning', icon: <CarOutlined />, text: '已发货' },
      '已完成': { color: 'success', icon: <CheckCircleOutlined />, text: '已完成' },
      '已取消': { color: 'error', icon: <CloseCircleOutlined />, text: '已取消' },
    };
    const config = statusMap[status] || { color: 'default', icon: null, text: status };
    return (
      <Tag color={config.color} icon={config.icon} className="text-base px-3 py-1">
        {config.text}
      </Tag>
    );
  };

  // 获取支付状态标签
  const getPaymentStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      '未支付': { color: 'error', text: '未支付' },
      '部分支付': { color: 'warning', text: '部分支付' },
      '已支付': { color: 'success', text: '已支付' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 获取当前步骤
  const getCurrentStep = (status: string) => {
    const stepMap: Record<string, number> = {
      '待处理': 0,
      '生产中': 1,
      '已发货': 2,
      '已完成': 3,
      '已取消': -1,
    };
    return stepMap[status] ?? 0;
  };

  // 订单明细表格列
  const itemColumns: ColumnsType<OrderItem> = [
    {
      title: '序号',
      key: 'index',
      width: 60,
      align: 'center',
      render: (_, __, index) => index + 1,
    },
    {
      title: '产品编码',
      dataIndex: 'product_code',
      key: 'product_code',
      width: 120,
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 200,
    },
    {
      title: '规格',
      dataIndex: 'specifications',
      key: 'specifications',
      render: (spec: string) => spec || '-',
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
      align: 'right',
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 120,
      align: 'right',
      render: (price: number) => price ? `¥${price.toFixed(2)}` : '-',
    },
    {
      title: '总价',
      dataIndex: 'total_price',
      key: 'total_price',
      width: 120,
      align: 'right',
      render: (price: number) => <Text strong>{price ? `¥${price.toFixed(2)}` : '-'}</Text>,
    },
  ];

  if (loading) {
    return (
      <div className="p-6 flex justify-center items-center min-h-96">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (!order) {
    return (
      <div className="p-6">
        <Empty description="订单不存在或已被删除" />
        <div className="text-center mt-4">
          <Button onClick={() => navigate('/orders')} icon={<ArrowLeftOutlined />}>
            返回订单列表
          </Button>
        </div>
      </div>
    );
  }

  const currentStep = getCurrentStep(order.status);

  return (
    <div className="p-6">
      {/* 页面标题和操作按钮 */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/orders')}
            className="mb-4"
          >
            返回列表
          </Button>
          <div className="flex items-center gap-4">
            <Title level={2} className="!mb-0">
              订单 {order.order_number}
            </Title>
            {getStatusTag(order.status)}
          </div>
          <Text type="secondary">
            创建时间：{order.created_at ? new Date(order.created_at).toLocaleString('zh-CN') : '-'}
          </Text>
        </div>
        <Space>
          <Button icon={<PrinterOutlined />}>打印订单</Button>
          {hasPermissionCode(PERMISSION_CODES.ORDER_UPDATE) && (
            <Button
              icon={<EditOutlined />}
              onClick={() => navigate(`/orders/${id}/edit`)}
            >
              编辑
            </Button>
          )}
          {hasPermissionCode(PERMISSION_CODES.ORDER_DELETE) && (
            <Popconfirm
              title="确认删除"
              description="确定要删除这个订单吗？此操作不可恢复。"
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

      {/* 订单状态流程 */}
      {order.status !== '已取消' && (
        <Card className="mb-6">
          <Steps current={currentStep} status="process">
            <Step title="待处理" icon={<FileTextOutlined />} description="订单已创建" />
            <Step title="生产中" icon={<ToolOutlined />} description="安排生产" />
            <Step title="已发货" icon={<CarOutlined />} description="物流配送" />
            <Step title="已完成" icon={<CheckCircleOutlined />} description="订单完成" />
          </Steps>
        </Card>
      )}

      <Row gutter={24}>
        {/* 左侧：订单信息 */}
        <Col xs={24} lg={16}>
          {/* 客户信息 */}
          <Card title="客户信息" className="mb-6">
            <Descriptions column={2} bordered>
              <Descriptions.Item label="客户名称">
                {order.customer?.name || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="公司名称">
                {order.customer?.company || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="联系电话">
                {order.customer?.phone || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="电子邮箱">
                {order.customer?.email || '-'}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 订单明细 */}
          <Card title="订单明细" className="mb-6">
            <Table
              columns={itemColumns}
              dataSource={order.items || []}
              rowKey="id"
              pagination={false}
              bordered
              summary={() => (
                <Table.Summary.Row>
                  <Table.Summary.Cell index={0} colSpan={6} align="right">
                    <Text strong>订单总金额：</Text>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={1} align="right">
                    <Text strong className="text-lg text-red-500">
                      ¥{order.total_amount?.toFixed(2) || '0.00'}
                    </Text>
                  </Table.Summary.Cell>
                </Table.Summary.Row>
              )}
            />
          </Card>

          {/* 配送信息 */}
          <Card title="配送信息" className="mb-6">
            <Descriptions column={1} bordered>
              <Descriptions.Item label="送货地址">
                {order.shipping_address || '未设置'}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 备注 */}
          <Card title="订单备注">
            <div className="min-h-24 p-4 bg-gray-50 rounded">
              {order.notes ? (
                <Text>{order.notes}</Text>
              ) : (
                <Text type="secondary">暂无备注</Text>
              )}
            </div>
          </Card>
        </Col>

        {/* 右侧：订单状态和操作 */}
        <Col xs={24} lg={8}>
          {/* 订单金额 */}
          <Card title="订单金额" className="mb-6">
            <div className="text-center py-4">
              <Text type="secondary">订单总金额</Text>
              <div className="text-3xl font-bold text-red-500 mt-2">
                ¥{order.total_amount?.toFixed(2) || '0.00'}
              </div>
              <div className="mt-4">
                <Text>货币：{order.currency || 'CNY'}</Text>
              </div>
            </div>
            <Divider />
            <div className="flex justify-between items-center">
              <Text>支付状态</Text>
              {getPaymentStatusTag(order.payment_status)}
            </div>
          </Card>

          {/* 状态操作 */}
          <Card title="订单操作" className="mb-6">
            <Spin spinning={updating}>
              {hasPermissionCode(PERMISSION_CODES.ORDER_UPDATE) ? (
                <Space direction="vertical" style={{ width: '100%' }}>
                  {/* 订单状态操作 */}
                  {order.status === '待处理' && (
                    <Button
                      type="primary"
                      block
                      icon={<ToolOutlined />}
                      onClick={() => handleUpdateStatus('生产中')}
                    >
                      开始生产
                    </Button>
                  )}
                  {order.status === '生产中' && (
                    <Button
                      type="primary"
                      block
                      icon={<CarOutlined />}
                      onClick={() => handleUpdateStatus('已发货')}
                    >
                      标记发货
                    </Button>
                  )}
                  {order.status === '已发货' && (
                    <Button
                      type="primary"
                      block
                      icon={<CheckCircleOutlined />}
                      onClick={() => handleUpdateStatus('已完成')}
                    >
                      确认完成
                    </Button>
                  )}
                  {(order.status === '待处理' || order.status === '生产中') && (
                    <Button
                      danger
                      block
                      icon={<CloseCircleOutlined />}
                      onClick={() => handleUpdateStatus('已取消')}
                    >
                      取消订单
                    </Button>
                  )}

                  <Divider style={{ margin: '12px 0' }} />

                  {/* 支付状态操作 */}
                  <Text strong>支付状态</Text>
                  {order.payment_status !== '已支付' && (
                    <Button
                      block
                      icon={<DollarOutlined />}
                      onClick={() => handleUpdatePaymentStatus('已支付')}
                    >
                      标记已支付
                    </Button>
                  )}
                  {order.payment_status === '未支付' && (
                    <Button
                      block
                      onClick={() => handleUpdatePaymentStatus('部分支付')}
                    >
                      标记部分支付
                    </Button>
                  )}
                </Space>
              ) : (
                <div className="text-center text-gray-500 py-4">
                  <Text type="secondary">您没有权限操作订单状态</Text>
                </div>
              )}
            </Spin>
          </Card>

          {/* 关联信息 */}
          <Card title="关联信息">
            <Descriptions column={1}>
              <Descriptions.Item label="销售机会">
                {order.opportunity ? (
                  <a onClick={() => navigate(`/opportunities/${order.opportunity_id}`)}>
                    {order.opportunity.name}
                  </a>
                ) : (
                  '-'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="酒店名称">
                {order.opportunity?.hotel_name || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="订单日期">
                {order.order_date || '-'}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default OrderDetail;