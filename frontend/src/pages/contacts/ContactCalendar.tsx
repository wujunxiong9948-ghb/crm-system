import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Calendar,
  Badge,
  Modal,
  List,
  Tag,
  Button,
  Space,
  Tooltip,
  Empty,
  Select,
  Row,
  Col,
  Statistic,
  Avatar,
} from 'antd';
import {
  PlusOutlined,
  ReloadOutlined,
  PhoneOutlined,
  MailOutlined,
  UserOutlined,
  MessageOutlined,
  CalendarOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { apiService } from '@/services/api';
import { usePermission, PERMISSION_CODES } from '@/utils/permission';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';

// 联系类型配置
const CONTACT_TYPES = [
  { value: '电话', icon: <PhoneOutlined />, color: 'blue' },
  { value: '邮件', icon: <MailOutlined />, color: 'green' },
  { value: '拜访', icon: <UserOutlined />, color: 'orange' },
  { value: '微信', icon: <MessageOutlined />, color: 'cyan' },
  { value: '展会', icon: <CalendarOutlined />, color: 'purple' },
  { value: '其他', icon: <MessageOutlined />, color: 'default' },
];

// 状态颜色配置
const STATUS_COLORS: Record<string, string> = {
  '待处理': 'warning',
  '进行中': 'processing',
  '已完成': 'success',
  '已取消': 'default',
};

interface Contact {
  id: number;
  customer_id: number;
  customer_name: string;
  contact_type: string;
  subject: string;
  content: string;
  contact_date: string;
  follow_up_date: string;
  status: string;
}

const ContactCalendar: React.FC = () => {
  const navigate = useNavigate();
  const { hasPermissionCode } = usePermission();
  
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Dayjs | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedDateContacts, setSelectedDateContacts] = useState<Contact[]>([]);
  const [currentMonth, setCurrentMonth] = useState(dayjs());

  // 获取联系记录
  const fetchContacts = async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/contacts', {
        params: { per_page: 1000 },
      });
      if (response.success) {
        const contactsData = response.data?.contacts || response.data || [];
        setContacts(Array.isArray(contactsData) ? contactsData : []);
      }
    } catch (error) {
      console.error('获取联系记录失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContacts();
  }, []);

  // 获取某天的联系记录
  const getContactsByDate = (date: Dayjs) => {
    return contacts.filter(contact => {
      const contactDate = dayjs(contact.contact_date);
      return contactDate.isSame(date, 'day');
    });
  };

  // 日历单元格渲染
  const dateCellRender = (value: Dayjs) => {
    const dayContacts = getContactsByDate(value);
    
    if (dayContacts.length === 0) return null;

    return (
      <ul className="events" style={{ listStyle: 'none', margin: 0, padding: 0 }}>
        {dayContacts.slice(0, 3).map((contact, index) => {
          const typeConfig = CONTACT_TYPES.find(t => t.value === contact.contact_type) || CONTACT_TYPES[5];
          return (
            <li key={index} style={{ marginBottom: 2 }}>
              <Tooltip title={`${contact.customer_name}: ${contact.subject}`}>
                <Badge
                  color={typeConfig.color}
                  text={
                    <span 
                      style={{ 
                        fontSize: 11, 
                        cursor: 'pointer',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        display: 'inline-block',
                        maxWidth: 100,
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/customers/${contact.customer_id}`);
                      }}
                    >
                      {contact.subject}
                    </span>
                  }
                />
              </Tooltip>
            </li>
          );
        })}
        {dayContacts.length > 3 && (
          <li style={{ fontSize: 11, color: '#999' }}>
            +{dayContacts.length - 3} 更多...
          </li>
        )}
      </ul>
    );
  };

  // 选择日期
  const onSelect = (value: Dayjs) => {
    setSelectedDate(value);
    const dayContacts = getContactsByDate(value);
    setSelectedDateContacts(dayContacts);
    if (dayContacts.length > 0) {
      setModalVisible(true);
    }
  };

  // 面板变化
  const onPanelChange = (value: Dayjs) => {
    setCurrentMonth(value);
  };

  // 获取联系类型配置
  const getContactTypeConfig = (type: string) => {
    return CONTACT_TYPES.find(t => t.value === type) || CONTACT_TYPES[5];
  };

  // 计算本月统计
  const monthStats = React.useMemo(() => {
    const monthContacts = contacts.filter(c => 
      dayjs(c.contact_date).isSame(currentMonth, 'month')
    );
    
    return {
      total: monthContacts.length,
      completed: monthContacts.filter(c => c.status === '已完成').length,
      pending: monthContacts.filter(c => c.status === '待处理').length,
      byType: CONTACT_TYPES.map(t => ({
        ...t,
        count: monthContacts.filter(c => c.contact_type === t.value).length,
      })),
    };
  }, [contacts, currentMonth]);

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title={`${currentMonth.format('MM')}月联系总数`}
              value={monthStats.total}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成"
              value={monthStats.completed}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待处理"
              value={monthStats.pending}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ textAlign: 'center', padding: '8px 0' }}>
              {hasPermissionCode(PERMISSION_CODES.CUSTOMER_CREATE) && (
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />} 
                  size="large"
                  onClick={() => navigate('/contacts')}
                >
                  新增联系记录
                </Button>
              )}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 联系类型分布 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          {monthStats.byType.map(type => (
            <Col key={type.value} span={4}>
              <div style={{ textAlign: 'center' }}>
                <Tag color={type.color} icon={type.icon} style={{ fontSize: 14, padding: '4px 12px' }}>
                  {type.value}: {type.count}
                </Tag>
              </div>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 日历 */}
      <Card
        title={
          <Space>
            <span>联系日历 - {currentMonth.format('YYYY年MM月')}</span>
            <Button icon={<ReloadOutlined />} onClick={fetchContacts}>
              刷新
            </Button>
          </Space>
        }
      >
        <Calendar
          dateCellRender={dateCellRender}
          onSelect={onSelect}
          onPanelChange={onPanelChange}
          mode="month"
        />
      </Card>

      {/* 日期详情弹窗 */}
      <Modal
        title={selectedDate ? `${selectedDate.format('YYYY年MM月DD日')} 的联系记录` : '联系记录'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setModalVisible(false)}>关闭</Button>,
        ]}
        width={700}
      >
        {selectedDateContacts.length > 0 ? (
          <List
            itemLayout="horizontal"
            dataSource={selectedDateContacts}
            renderItem={(item) => {
              const typeConfig = getContactTypeConfig(item.contact_type);
              return (
                <List.Item
                  actions={[
                    <Button 
                      type="link" 
                      icon={<EyeOutlined />}
                      onClick={() => navigate(`/customers/${item.customer_id}`)}
                    >
                      查看客户
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar 
                        style={{ backgroundColor: typeConfig.color }}
                        icon={typeConfig.icon}
                      />
                    }
                    title={
                      <Space>
                        <span>{item.subject}</span>
                        <Tag color={typeConfig.color}>{item.contact_type}</Tag>
                        <Tag color={STATUS_COLORS[item.status]}>{item.status}</Tag>
                      </Space>
                    }
                    description={
                      <div>
                        <div>
                          <strong>客户:</strong> {item.customer_name}
                        </div>
                        <div>
                          <strong>时间:</strong> {dayjs(item.contact_date).format('HH:mm')}
                        </div>
                        <div style={{ marginTop: 8, color: '#666' }}>
                          {item.content}
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              );
            }}
          />
        ) : (
          <Empty description="该日暂无联系记录" />
        )}
      </Modal>
    </div>
  );
};

export default ContactCalendar;
