import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Row,
  Col,
  Statistic,
  Progress,
  Timeline,
  List,
  Avatar,
  Divider,
  message,
  Popconfirm,
  Modal,
  Form,
  Input,
  DatePicker,
  Select,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  PhoneOutlined,
  MailOutlined,
  HomeOutlined,
  DollarOutlined,
  RiseOutlined,
  CalendarOutlined,
  UserOutlined,
  MessageOutlined,
  PlusOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { apiService, apiEndpoints } from '../../services/api';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Option } = Select;

// 酒店家具项目销售机会
interface Opportunity {
  id: number;
  name: string;
  hotel_name: string;
  project_address: string;
  project_type: string;
  star_rating?: string;
  room_count: number;
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
  planned_opening_date?: string;
  expected_close_date?: string;
  expected_value: number;
  furniture_budget?: number;
  renovation_budget?: number;
  stage: string;
  probability: number;
  status: string;
  priority: string;
  assigned_to?: string;
  assigned_to_name?: string;
  customer_id: number;
  customer?: {
    id: number;
    name: string;
    company?: string;
    phone?: string;
    email?: string;
  };
  description?: string;
  notes?: string;
  competitors?: string;
  our_advantage?: string;
  next_follow_up_date?: string;
  last_contact_date?: string;
  created_at: string;
  updated_at: string;
}

// 跟进记录
interface FollowUpRecord {
  id: number;
  opportunity_id: number;
  contact_type: string;
  content: string;
  contact_date: string;
  next_follow_up_date?: string;
  created_by?: string;
  created_at: string;
}

const OpportunityDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(false);
  const [followUpRecords, setFollowUpRecords] = useState<FollowUpRecord[]>([]);
  const [followUpModalVisible, setFollowUpModalVisible] = useState(false);
  const [followUpForm] = Form.useForm();

  // 获取销售机会详情
  const fetchOpportunityDetail = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const response = await apiService.get<Opportunity>(
        apiEndpoints.opportunities.detail(parseInt(id))
      );
      setOpportunity(response);
    } catch (error) {
      message.error('获取项目详情失败');
      console.error('获取项目详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取跟进记录
  const fetchFollowUpRecords = async () => {
    if (!id) return;
    try {
      // 这里应该调用实际的API获取跟进记录
      // 暂时使用模拟数据
      setFollowUpRecords([
        {
          id: 1,
          opportunity_id: parseInt(id),
          contact_type: '电话',
          content: '与客户初步沟通，了解项目需求，客户对产品质量要求较高',
          contact_date: dayjs().subtract(5, 'day').format('YYYY-MM-DD HH:mm'),
          next_follow_up_date: dayjs().add(3, 'day').format('YYYY-MM-DD'),
          created_by: '张三',
          created_at: dayjs().subtract(5, 'day').format('YYYY-MM-DD HH:mm'),
        },
        {
          id: 2,
          opportunity_id: parseInt(id),
          contact_type: '拜访',
          content: '实地考察项目现场，测量房间尺寸，讨论家具风格偏好',
          contact_date: dayjs().subtract(2, 'day').format('YYYY-MM-DD HH:mm'),
          next_follow_up_date: dayjs().add(1, 'day').format('YYYY-MM-DD'),
          created_by: '张三',
          created_at: dayjs().subtract(2, 'day').format('YYYY-MM-DD HH:mm'),
        },
      ]);
    } catch (error) {
      console.error('获取跟进记录失败:', error);
    }
  };

  useEffect(() => {
    fetchOpportunityDetail();
    fetchFollowUpRecords();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // 删除销售机会
  const handleDelete = async () => {
    if (!id) return;
    try {
      await apiService.delete(apiEndpoints.opportunities.delete(parseInt(id)));
      message.success('项目机会删除成功');
      navigate('/opportunities');
    } catch (error) {
      message.error('删除失败');
      console.error('删除失败:', error);
    }
  };

  // 添加跟进记录
  const handleAddFollowUp = async (values: any) => {
    try {
      // 这里应该调用实际的API
      const newRecord: FollowUpRecord = {
        id: Date.now(),
        opportunity_id: parseInt(id || '0'),
        contact_type: values.contact_type,
        content: values.content,
        contact_date: dayjs().format('YYYY-MM-DD HH:mm'),
        next_follow_up_date: values.next_follow_up_date?.format('YYYY-MM-DD'),
        created_by: '当前用户',
        created_at: dayjs().format('YYYY-MM-DD HH:mm'),
      };
      setFollowUpRecords([newRecord, ...followUpRecords]);
      message.success('跟进记录添加成功');
      setFollowUpModalVisible(false);
      followUpForm.resetFields();
    } catch (error) {
      message.error('添加失败');
    }
  };

  // 阶段颜色映射
  const stageColors: Record<string, string> = {
    '初步接触': 'default',
    '需求调研': 'processing',
    '方案设计': 'warning',
    '报价谈判': 'orange',
    '合同签订': 'purple',
    '成交': 'success',
    '丢失': 'error',
  };

  // 状态颜色映射
  const statusColors: Record<string, string> = {
    '进行中': 'blue',
    '已成交': 'success',
    '已丢失': 'error',
    '暂停': 'warning',
  };

  // 优先级颜色映射
  const priorityColors: Record<string, string> = {
    '高': 'red',
    '中': 'orange',
    '低': 'green',
  };

  // 项目类型标签
  const projectTypeColors: Record<string, string> = {
    '新建酒店': 'blue',
    '酒店翻新': 'purple',
    '连锁扩张': 'cyan',
    '其他': 'default',
  };

  if (!opportunity) {
    return (
      <div style={{ padding: 24 }}>
        <Card loading={loading}>
          <div>加载中...</div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      {/* 顶部操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/opportunities')}>
              返回列表
            </Button>
            <span style={{ fontSize: '20px', fontWeight: 'bold' }}>{opportunity.name}</span>
            <Tag color={stageColors[opportunity.stage]}>{opportunity.stage}</Tag>
            <Tag color={statusColors[opportunity.status]}>{opportunity.status}</Tag>
            <Tag color={priorityColors[opportunity.priority]}>{opportunity.priority}优先级</Tag>
          </Space>
          <Space>
            <Button icon={<EditOutlined />} onClick={() => navigate(`/opportunities/${id}/edit`)}>
              编辑
            </Button>
            <Popconfirm
              title="确定要删除这个项目机会吗？"
              description="删除后将无法恢复"
              onConfirm={handleDelete}
              okText="确定"
              cancelText="取消"
            >
              <Button danger icon={<DeleteOutlined />}>
                删除
              </Button>
            </Popconfirm>
          </Space>
        </Space>
      </Card>

      {/* 关键指标 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="预计订单金额"
              value={opportunity.expected_value}
              suffix="万元"
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#f5222d', fontSize: '24px' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="客房数量"
              value={opportunity.room_count}
              suffix="间"
              prefix={<HomeOutlined />}
              valueStyle={{ color: '#1890ff', fontSize: '24px' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ marginBottom: 8, color: 'rgba(0,0,0,0.45)' }}>成交概率</div>
            <Progress
              percent={opportunity.probability}
              strokeColor={opportunity.probability >= 70 ? '#52c41a' : opportunity.probability >= 40 ? '#faad14' : '#ff4d4f'}
              size="default"
              format={(percent) => `${percent}%`}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="距离开业"
              value={opportunity.planned_opening_date ? dayjs(opportunity.planned_opening_date).diff(dayjs(), 'day') : '-'}
              suffix={opportunity.planned_opening_date ? '天' : ''}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: '#722ed1', fontSize: '24px' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* 左侧：项目信息 */}
        <Col span={16}>
          {/* 项目基本信息 */}
          <Card title="项目基本信息" style={{ marginBottom: 16 }}>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="酒店名称">{opportunity.hotel_name}</Descriptions.Item>
              <Descriptions.Item label="项目类型">
                <Tag color={projectTypeColors[opportunity.project_type]}>
                  {opportunity.project_type}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="项目地址" span={2}>
                <HomeOutlined style={{ marginRight: 8 }} />
                {opportunity.project_address}
              </Descriptions.Item>
              <Descriptions.Item label="酒店星级">
                {opportunity.star_rating ? (
                  <span style={{ color: '#faad14' }}>
                    {'★'.repeat(
                      opportunity.star_rating === '经济型'
                        ? 1
                        : opportunity.star_rating === '三星'
                        ? 3
                        : opportunity.star_rating === '四星'
                        ? 4
                        : 5
                    )}
                    {opportunity.star_rating}
                  </span>
                ) : (
                  '-'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="客房数量">{opportunity.room_count} 间</Descriptions.Item>
              <Descriptions.Item label="计划开业时间">
                {opportunity.planned_opening_date
                  ? dayjs(opportunity.planned_opening_date).format('YYYY年MM月DD日')
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="预计成交时间">
                {opportunity.expected_close_date
                  ? dayjs(opportunity.expected_close_date).format('YYYY年MM月DD日')
                  : '-'}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 预算信息 */}
          <Card title="预算信息" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="装修翻新预算"
                  value={opportunity.renovation_budget || 0}
                  suffix="万元"
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="家具采购预算"
                  value={opportunity.furniture_budget || 0}
                  suffix="万元"
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="预计订单金额"
                  value={opportunity.expected_value}
                  suffix="万元"
                  valueStyle={{ color: '#f5222d', fontWeight: 'bold' }}
                />
              </Col>
            </Row>
          </Card>

          {/* 产品数量 */}
          {opportunity.product_quantity && Object.values(opportunity.product_quantity).some(v => v && v > 0) && (
            <Card title="产品数量预估" style={{ marginBottom: 16 }}>
              <Descriptions column={4} size="small">
                {opportunity.product_quantity.beds ? (
                  <Descriptions.Item label="床">{opportunity.product_quantity.beds} 张</Descriptions.Item>
                ) : null}
                {opportunity.product_quantity.nightstands ? (
                  <Descriptions.Item label="床头柜">{opportunity.product_quantity.nightstands} 个</Descriptions.Item>
                ) : null}
                {opportunity.product_quantity.wardrobes ? (
                  <Descriptions.Item label="衣柜">{opportunity.product_quantity.wardrobes} 个</Descriptions.Item>
                ) : null}
                {opportunity.product_quantity.desks ? (
                  <Descriptions.Item label="书桌">{opportunity.product_quantity.desks} 张</Descriptions.Item>
                ) : null}
                {opportunity.product_quantity.chairs ? (
                  <Descriptions.Item label="椅子">{opportunity.product_quantity.chairs} 把</Descriptions.Item>
                ) : null}
                {opportunity.product_quantity.sofas ? (
                  <Descriptions.Item label="沙发">{opportunity.product_quantity.sofas} 套</Descriptions.Item>
                ) : null}
                {opportunity.product_quantity.coffee_tables ? (
                  <Descriptions.Item label="茶几">{opportunity.product_quantity.coffee_tables} 个</Descriptions.Item>
                ) : null}
                {opportunity.product_quantity.tv_cabinets ? (
                  <Descriptions.Item label="电视柜">{opportunity.product_quantity.tv_cabinets} 个</Descriptions.Item>
                ) : null}
              </Descriptions>
            </Card>
          )}

          {/* 销售跟进信息 */}
          <Card title="销售跟进" style={{ marginBottom: 16 }}>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="销售阶段">
                <Tag color={stageColors[opportunity.stage]}>{opportunity.stage}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="成交概率">{opportunity.probability}%</Descriptions.Item>
              <Descriptions.Item label="负责人">{opportunity.assigned_to_name || opportunity.assigned_to || '-'}</Descriptions.Item>
              <Descriptions.Item label="优先级">
                <Tag color={priorityColors[opportunity.priority]}>{opportunity.priority}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="竞争对手" span={2}>
                {opportunity.competitors || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="我司优势" span={2}>
                {opportunity.our_advantage || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="项目描述" span={2}>
                {opportunity.description || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="备注" span={2}>
                {opportunity.notes || '-'}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 跟进记录 */}
          <Card
            title="跟进记录"
            extra={
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setFollowUpModalVisible(true)}>
                添加跟进
              </Button>
            }
          >
            <Timeline mode="left">
              {followUpRecords.map((record) => (
                <Timeline.Item
                  key={record.id}
                  label={dayjs(record.contact_date).format('MM-DD HH:mm')}
                  dot={<MessageOutlined style={{ fontSize: '16px' }} />}
                >
                  <Card size="small" style={{ marginBottom: 8 }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Space>
                        <Tag color="blue">{record.contact_type}</Tag>
                        <span style={{ color: '#999', fontSize: '12px' }}>
                          记录人: {record.created_by}
                        </span>
                      </Space>
                      <div>{record.content}</div>
                      {record.next_follow_up_date && (
                        <div style={{ fontSize: '12px', color: '#faad14' }}>
                          下次跟进: {dayjs(record.next_follow_up_date).format('YYYY-MM-DD')}
                        </div>
                      )}
                    </Space>
                  </Card>
                </Timeline.Item>
              ))}
            </Timeline>
            {followUpRecords.length === 0 && (
              <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                暂无跟进记录
              </div>
            )}
          </Card>
        </Col>

        {/* 右侧：关联信息 */}
        <Col span={8}>
          {/* 客户信息 */}
          <Card title="关联客户" style={{ marginBottom: 16 }}>
            {opportunity.customer ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
                  <Avatar size={64} icon={<UserOutlined />} style={{ marginRight: 16 }} />
                  <div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      {opportunity.customer.name}
                    </div>
                    <div style={{ color: '#666' }}>{opportunity.customer.company || '-'}</div>
                  </div>
                </div>
                <Divider style={{ margin: '12px 0' }} />
                <div>
                  {opportunity.customer.phone && (
                    <div style={{ marginBottom: 8 }}>
                      <PhoneOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                      {opportunity.customer.phone}
                    </div>
                  )}
                  {opportunity.customer.email && (
                    <div>
                      <MailOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                      {opportunity.customer.email}
                    </div>
                  )}
                </div>
                <Divider style={{ margin: '12px 0' }} />
                <Button type="link" block onClick={() => navigate(`/customers/${opportunity.customer_id}`)}>
                  查看客户详情
                </Button>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                暂无客户信息
              </div>
            )}
          </Card>

          {/* 项目时间线 */}
          <Card title="项目时间线" style={{ marginBottom: 16 }}>
            <Timeline>
              <Timeline.Item color="green">
                <div style={{ fontWeight: 'bold' }}>项目创建</div>
                <div style={{ fontSize: '12px', color: '#999' }}>
                  {dayjs(opportunity.created_at).format('YYYY-MM-DD HH:mm')}
                </div>
              </Timeline.Item>
              <Timeline.Item color="blue">
                <div style={{ fontWeight: 'bold' }}>最后更新</div>
                <div style={{ fontSize: '12px', color: '#999' }}>
                  {dayjs(opportunity.updated_at).format('YYYY-MM-DD HH:mm')}
                </div>
              </Timeline.Item>
              {opportunity.next_follow_up_date && (
                <Timeline.Item color="orange" dot={<CalendarOutlined />}>
                  <div style={{ fontWeight: 'bold' }}>下次跟进</div>
                  <div style={{ fontSize: '12px', color: '#999' }}>
                    {dayjs(opportunity.next_follow_up_date).format('YYYY-MM-DD')}
                  </div>
                </Timeline.Item>
              )}
              {opportunity.expected_close_date && (
                <Timeline.Item color="red" dot={<RiseOutlined />}>
                  <div style={{ fontWeight: 'bold' }}>预计成交</div>
                  <div style={{ fontSize: '12px', color: '#999' }}>
                    {dayjs(opportunity.expected_close_date).format('YYYY-MM-DD')}
                  </div>
                </Timeline.Item>
              )}
            </Timeline>
          </Card>

          {/* 快捷操作 */}
          <Card title="快捷操作">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button icon={<PhoneOutlined />} block>
                拨打电话
              </Button>
              <Button icon={<MailOutlined />} block>
                发送邮件
              </Button>
              <Button icon={<FileTextOutlined />} block>
                生成报价单
              </Button>
              <Button icon={<RiseOutlined />} block type="primary">
                推进到下一阶段
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 添加跟进记录模态框 */}
      <Modal
        title="添加跟进记录"
        open={followUpModalVisible}
        onCancel={() => {
          setFollowUpModalVisible(false);
          followUpForm.resetFields();
        }}
        onOk={() => followUpForm.submit()}
      >
        <Form form={followUpForm} layout="vertical" onFinish={handleAddFollowUp}>
          <Form.Item
            name="contact_type"
            label="联系方式"
            rules={[{ required: true, message: '请选择联系方式' }]}
          >
            <Select placeholder="请选择联系方式">
              <Option value="电话">电话</Option>
              <Option value="邮件">邮件</Option>
              <Option value="拜访">拜访</Option>
              <Option value="微信">微信</Option>
              <Option value="其他">其他</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="content"
            label="跟进内容"
            rules={[{ required: true, message: '请输入跟进内容' }]}
          >
            <TextArea rows={4} placeholder="请输入跟进内容" />
          </Form.Item>
          <Form.Item name="next_follow_up_date" label="下次跟进时间">
            <DatePicker style={{ width: '100%' }} placeholder="请选择下次跟进时间" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default OpportunityDetail;
