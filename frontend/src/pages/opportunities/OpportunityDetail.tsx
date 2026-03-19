import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Tag,
  Space,
  Button,
  Timeline,
  Typography,
  Divider,
  Row,
  Col,
  Statistic,
  Progress,
  Table,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  message,
  Empty,
  Avatar,
} from 'antd';
import {
  EditOutlined,
  PlusOutlined,
  HomeOutlined,
  DollarOutlined,
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
  CalendarOutlined,
  EnvironmentOutlined,
  TrophyOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { apiService } from '../../services/api';
import type {
  Opportunity,
  FollowUpRecord,
  KeyContact,
  AddFollowUpRequest,
} from '../../types/opportunity';
import {
  STAGE_CONFIG,
  PRIORITY_CONFIG,
  STATUS_CONFIG,
  PROJECT_TYPE_CONFIG,
  HOTEL_STAR_CONFIG,
} from '../../types/opportunity';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface OpportunityDetailProps {
  opportunityId?: number;
  onEdit?: () => void;
  onClose?: () => void;
}

const OpportunityDetail: React.FC<OpportunityDetailProps> = ({
  opportunityId: propOpportunityId,
  onEdit,
  onClose,
}) => {
  const { id } = useParams<{ id: string }>();
  const opportunityId = propOpportunityId ?? Number(id);
  
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(false);
  const [followUpModalVisible, setFollowUpModalVisible] = useState(false);
  const [followUpForm] = Form.useForm();

  // 获取销售机会详情
  const fetchOpportunityDetail = async () => {
    setLoading(true);
    try {
      const response = await apiService.get<any>(`/opportunities/${opportunityId}`);
      console.log('Opportunity detail response:', response);
      
      // 适配返回格式
      if (response && response.id) {
        // 直接返回对象
        setOpportunity(response as Opportunity);
      } else if (response && response.data && response.data.id) {
        // 包装格式
        setOpportunity(response.data as Opportunity);
      } else {
        console.error('未知详情格式:', response);
      }
    } catch (error) {
      message.error('获取销售机会详情失败');
      console.error('获取详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOpportunityDetail();
  }, [opportunityId]);

  // 添加跟进记录
  const handleAddFollowUp = async (values: any) => {
    try {
      const data: AddFollowUpRequest = {
        type: values.type,
        content: values.content,
        result: values.result,
        next_action: values.next_action,
        next_follow_up_date: values.next_follow_up_date?.format('YYYY-MM-DD'),
      };

      await apiService.post(`/opportunities/${opportunityId}/follow-up`, data);
      message.success('跟进记录添加成功');
      setFollowUpModalVisible(false);
      followUpForm.resetFields();
      fetchOpportunityDetail();
    } catch (error) {
      message.error('添加跟进记录失败');
      console.error('添加失败:', error);
    }
  };

  if (!opportunity) {
    return (
      <Card loading={loading}>
        <Empty description="加载中..." />
      </Card>
    );
  }

  // 渲染阶段进度
  const renderStageProgress = () => {
    const stages = ['初步接触', '需求分析', '方案报价', '谈判', '成交'];
    const currentIndex = stages.indexOf(opportunity.stage);

    return (
      <div style={{ marginBottom: 24 }}>
        <Progress
          percent={opportunity.probability}
          strokeColor={STAGE_CONFIG[opportunity.stage]?.color}
          format={() => `${opportunity.probability}%`}
          style={{ marginBottom: 8 }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          {stages.map((stage, index) => (
            <div
              key={stage}
              style={{
                textAlign: 'center',
                flex: 1,
                color:
                  index <= currentIndex
                    ? STAGE_CONFIG[opportunity.stage]?.color
                    : '#d9d9d9',
                fontWeight: index === currentIndex ? 'bold' : 'normal',
              }}
            >
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor:
                    index <= currentIndex
                      ? STAGE_CONFIG[opportunity.stage]?.color
                      : '#d9d9d9',
                  margin: '0 auto 4px',
                }}
              />
              <Text style={{ fontSize: 12 }}>{stage}</Text>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // 渲染酒店星级
  const renderHotelStar = (star?: string) => {
    if (!star) return '-';
    const config = HOTEL_STAR_CONFIG[star as keyof typeof HOTEL_STAR_CONFIG];
    return (
      <span style={{ color: config?.color || '#666', fontWeight: 'bold' }}>
        {config?.icon || star}
      </span>
    );
  };

  // 跟进记录表格列
  const followUpColumns = [
    {
      title: '时间',
      dataIndex: 'date',
      key: 'date',
      width: 160,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 80,
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: '跟进内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
    },
    {
      title: '结果',
      dataIndex: 'result',
      key: 'result',
      width: 150,
      ellipsis: true,
    },
    {
      title: '下一步行动',
      dataIndex: 'next_action',
      key: 'next_action',
      width: 150,
      ellipsis: true,
    },
  ];

  return (
    <div style={{ padding: '0 0 24px' }}>
      {/* 顶部操作栏 */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 24,
        }}
      >
        <Space>
          <Title level={4} style={{ margin: 0 }}>
            {opportunity.name}
          </Title>
          <Tag color={STAGE_CONFIG[opportunity.stage]?.color}>
            {opportunity.stage}
          </Tag>
          <Tag color={STATUS_CONFIG[opportunity.status]?.color}>
            {STATUS_CONFIG[opportunity.status]?.label}
          </Tag>
        </Space>
        <Space>
          <Button icon={<PlusOutlined />} onClick={() => setFollowUpModalVisible(true)}>
            添加跟进
          </Button>
          {onEdit && (
            <Button type="primary" icon={<EditOutlined />} onClick={onEdit}>
              编辑
            </Button>
          )}
          {onClose && <Button onClick={onClose}>关闭</Button>}
        </Space>
      </div>

      {/* 销售阶段进度 */}
      <Card title="销售进度" style={{ marginBottom: 24 }}>
        {renderStageProgress()}
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="预计订单金额"
              value={opportunity.expected_value}
              precision={2}
              prefix="¥"
              suffix="万"
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="成交概率"
              value={opportunity.probability}
              suffix="%"
              valueStyle={{ color: STAGE_CONFIG[opportunity.stage]?.color }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="优先级"
              value={opportunity.priority}
              valueStyle={{
                color:
                  opportunity.priority === '高'
                    ? '#ff4d4f'
                    : opportunity.priority === '中'
                    ? '#faad14'
                    : '#1890ff',
              }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="负责人"
              value={opportunity.assigned_to || '未分配'}
            />
          </Col>
        </Row>
      </Card>

      <Row gutter={24}>
        {/* 左侧：项目信息 */}
        <Col span={16}>
          {/* 基本信息 */}
          <Card title="基本信息" style={{ marginBottom: 24 }}>
            <Descriptions column={2}>
              <Descriptions.Item label="项目名称">
                {opportunity.name}
              </Descriptions.Item>
              <Descriptions.Item label="关联客户">
                <Space>
                  <Avatar icon={<UserOutlined />} size="small" />
                  <span>{opportunity.customer_name || '-'}</span>
                  {opportunity.customer_company && (
                    <Text type="secondary">({opportunity.customer_company})</Text>
                  )}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="酒店名称">
                <Space>
                  <HomeOutlined />
                  {opportunity.hotel_name || '-'}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="项目类型">
                {opportunity.project_type && (
                  <Tag color={PROJECT_TYPE_CONFIG[opportunity.project_type]?.color}>
                    {opportunity.project_type}
                  </Tag>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="酒店星级">
                {renderHotelStar(opportunity.hotel_star)}
              </Descriptions.Item>
              <Descriptions.Item label="客房数量">
                {opportunity.room_count ? `${opportunity.room_count} 间` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="计划开业时间" span={2}>
                {opportunity.planned_opening_date ? (
                  <Space>
                    <CalendarOutlined />
                    {dayjs(opportunity.planned_opening_date).format('YYYY-MM-DD')}
                  </Space>
                ) : (
                  '-'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="项目地址" span={2}>
                {opportunity.province || opportunity.city || opportunity.district ? (
                  <Space>
                    <EnvironmentOutlined />
                    {opportunity.province}
                    {opportunity.city}
                    {opportunity.district}
                    {opportunity.address && (
                      <Text type="secondary">({opportunity.address})</Text>
                    )}
                  </Space>
                ) : (
                  '-'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="项目描述" span={2}>
                <Paragraph style={{ margin: 0 }}>
                  {opportunity.description || '暂无描述'}
                </Paragraph>
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 预算信息 */}
          <Card title="预算信息" style={{ marginBottom: 24 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="装修翻新预算"
                  value={opportunity.renovation_budget}
                  precision={2}
                  prefix="¥"
                  suffix="万"
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="家具采购预算"
                  value={opportunity.furniture_budget}
                  precision={2}
                  prefix="¥"
                  suffix="万"
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="预计订单金额"
                  value={opportunity.expected_value}
                  precision={2}
                  prefix="¥"
                  suffix="万"
                  valueStyle={{ color: '#52c41a', fontWeight: 'bold' }}
                />
              </Col>
            </Row>
          </Card>

          {/* 产品需求 */}
          <Card title="产品需求预估" style={{ marginBottom: 24 }}>
            <Row gutter={[16, 16]}>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="床" value={opportunity.bed_count} suffix="张" />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="床头柜" value={opportunity.nightstand_count} suffix="个" />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="衣柜" value={opportunity.wardrobe_count} suffix="个" />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="书桌" value={opportunity.desk_count} suffix="张" />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="椅子" value={opportunity.chair_count} suffix="把" />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="沙发" value={opportunity.sofa_count} suffix="套" />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="茶几" value={opportunity.coffee_table_count} suffix="个" />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="电视柜" value={opportunity.tv_cabinet_count} suffix="个" />
                </Card>
              </Col>
            </Row>
            {opportunity.other_furniture && (
              <>
                <Divider />
                <div>
                  <Text strong>其他家具需求：</Text>
                  <Paragraph style={{ marginTop: 8 }}>
                    {opportunity.other_furniture}
                  </Paragraph>
                </div>
              </>
            )}
          </Card>

          {/* 竞争与决策信息 */}
          <Card title="竞争与决策信息" style={{ marginBottom: 24 }}>
            <Descriptions column={1}>
              <Descriptions.Item label="竞争对手">
                <Paragraph>{opportunity.competitors || '暂无记录'}</Paragraph>
              </Descriptions.Item>
              <Descriptions.Item label="我司优势">
                <Paragraph>{opportunity.our_advantage || '暂无记录'}</Paragraph>
              </Descriptions.Item>
              <Descriptions.Item label="客户顾虑">
                <Paragraph>{opportunity.customer_concern || '暂无记录'}</Paragraph>
              </Descriptions.Item>
              <Descriptions.Item label="决策人">
                {opportunity.decision_maker || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="决策流程">
                <Paragraph>{opportunity.decision_process || '暂无记录'}</Paragraph>
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 跟进记录 */}
          <Card
            title="跟进记录"
            extra={
              <Button
                type="primary"
                size="small"
                icon={<PlusOutlined />}
                onClick={() => setFollowUpModalVisible(true)}
              >
                添加跟进
              </Button>
            }
          >
            {opportunity.follow_up_records && opportunity.follow_up_records.length > 0 ? (
              <Timeline mode="left">
                {opportunity.follow_up_records.map((record, index) => (
                  <Timeline.Item
                    key={record.id || index}
                    label={dayjs(record.date).format('YYYY-MM-DD HH:mm')}
                    dot={<ClockCircleOutlined style={{ fontSize: '16px' }} />}
                  >
                    <Card size="small" style={{ marginBottom: 8 }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Space>
                          <Tag color="blue">{record.type}</Tag>
                          <Text strong>{record.created_by || '系统'}</Text>
                        </Space>
                        <Paragraph style={{ margin: 0 }}>{record.content}</Paragraph>
                        {record.result && (
                          <div>
                            <Text type="secondary">结果：</Text>
                            <Text>{record.result}</Text>
                          </div>
                        )}
                        {record.next_action && (
                          <div>
                            <Text type="secondary">下一步：</Text>
                            <Text type="warning">{record.next_action}</Text>
                          </div>
                        )}
                      </Space>
                    </Card>
                  </Timeline.Item>
                ))}
              </Timeline>
            ) : (
              <Empty description="暂无跟进记录" />
            )}
          </Card>
        </Col>

        {/* 右侧：关键信息 */}
        <Col span={8}>
          {/* 关键联系人 */}
          <Card title="关键联系人" style={{ marginBottom: 24 }}>
            {opportunity.key_contacts && opportunity.key_contacts.length > 0 ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                {opportunity.key_contacts.map((contact, index) => (
                  <Card key={index} size="small" style={{ width: '100%' }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Space>
                        <Avatar icon={<UserOutlined />} />
                        <Text strong>{contact.name}</Text>
                        {contact.position && <Tag>{contact.position}</Tag>}
                      </Space>
                      {contact.phone && (
                        <div>
                          <PhoneOutlined style={{ marginRight: 8 }} />
                          {contact.phone}
                        </div>
                      )}
                      {contact.email && (
                        <div>
                          <MailOutlined style={{ marginRight: 8 }} />
                          {contact.email}
                        </div>
                      )}
                      {contact.role && (
                        <div>
                          <TeamOutlined style={{ marginRight: 8 }} />
                          {contact.role}
                        </div>
                      )}
                    </Space>
                  </Card>
                ))}
              </Space>
            ) : (
              <Empty description="暂无关键联系人" />
            )}
          </Card>

          {/* 时间节点 */}
          <Card title="时间节点" style={{ marginBottom: 24 }}>
            <Timeline>
              <Timeline.Item>
                <Text strong>预计成交时间</Text>
                <div>
                  {opportunity.expected_close_date ? (
                    <Text type="success">
                      {dayjs(opportunity.expected_close_date).format('YYYY-MM-DD')}
                    </Text>
                  ) : (
                    <Text type="secondary">未设置</Text>
                  )}
                </div>
              </Timeline.Item>
              <Timeline.Item>
                <Text strong>下次跟进时间</Text>
                <div>
                  {opportunity.next_follow_up_date ? (
                    <Text
                      type={
                        dayjs(opportunity.next_follow_up_date).isBefore(dayjs(), 'day')
                          ? 'danger'
                          : dayjs(opportunity.next_follow_up_date).diff(dayjs(), 'day') <= 3
                          ? 'warning'
                          : 'success'
                      }
                    >
                      {dayjs(opportunity.next_follow_up_date).format('YYYY-MM-DD')}
                    </Text>
                  ) : (
                    <Text type="secondary">未设置</Text>
                  )}
                </div>
              </Timeline.Item>
              <Timeline.Item>
                <Text strong>创建时间</Text>
                <div>{dayjs(opportunity.created_at).format('YYYY-MM-DD HH:mm')}</div>
              </Timeline.Item>
              <Timeline.Item>
                <Text strong>最后更新</Text>
                <div>{dayjs(opportunity.updated_at).format('YYYY-MM-DD HH:mm')}</div>
              </Timeline.Item>
            </Timeline>
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
        footer={null}
        destroyOnClose
      >
        <Form form={followUpForm} layout="vertical" onFinish={handleAddFollowUp}>
          <Form.Item
            name="type"
            label="跟进类型"
            rules={[{ required: true, message: '请选择跟进类型' }]}
            initialValue="电话"
          >
            <Select placeholder="选择跟进类型">
              <Option value="电话">电话</Option>
              <Option value="拜访">拜访</Option>
              <Option value="邮件">邮件</Option>
              <Option value="微信">微信</Option>
              <Option value="其他">其他</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="content"
            label="跟进内容"
            rules={[{ required: true, message: '请输入跟进内容' }]}
          >
            <TextArea rows={4} placeholder="详细记录跟进情况..." />
          </Form.Item>
          <Form.Item name="result" label="跟进结果">
            <TextArea rows={2} placeholder="记录跟进结果..." />
          </Form.Item>
          <Form.Item name="next_action" label="下一步行动">
            <Input placeholder="下一步计划做什么..." />
          </Form.Item>
          <Form.Item name="next_follow_up_date" label="下次跟进时间">
            <DatePicker style={{ width: '100%' }} placeholder="选择日期" />
          </Form.Item>
          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button
                onClick={() => {
                  setFollowUpModalVisible(false);
                  followUpForm.resetFields();
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default OpportunityDetail;
