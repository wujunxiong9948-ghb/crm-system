import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Tag,
  Space,
  DatePicker,
  Select,
  message,
  Row,
  Col,
  Modal,
  Descriptions,
} from 'antd';
import {
  SearchOutlined,
  FileTextOutlined,
  DownloadOutlined,
  ClearOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { logApi } from '../../services/api';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface LogItem {
  id: number;
  user_id: number;
  username: string;
  action: string;
  module: string;
  description: string;
  ip_address: string;
  user_agent: string;
  request_data: string;
  response_data: string;
  status: string;
  error_message: string;
  created_at: string;
}

const actionMap: Record<string, { text: string; color: string }> = {
  create: { text: '创建', color: 'green' },
  update: { text: '更新', color: 'blue' },
  delete: { text: '删除', color: 'red' },
  login: { text: '登录', color: 'cyan' },
  logout: { text: '登出', color: 'default' },
  view: { text: '查看', color: 'default' },
  export: { text: '导出', color: 'purple' },
  import: { text: '导入', color: 'orange' },
};

const moduleMap: Record<string, string> = {
  customer: '客户管理',
  opportunity: '机会管理',
  order: '订单管理',
  product: '产品管理',
  user: '用户管理',
  role: '角色管理',
  system: '系统设置',
  auth: '认证授权',
};

const OperationLog: React.FC = () => {
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [selectedAction, setSelectedAction] = useState('');
  const [selectedModule, setSelectedModule] = useState('');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedLog, setSelectedLog] = useState<LogItem | null>(null);
  const [actions, setActions] = useState<string[]>([]);
  const [modules, setModules] = useState<string[]>([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  const fetchLogs = async (params = {}) => {
    setLoading(true);
    try {
      const queryParams: any = {
        page: pagination.current,
        per_page: pagination.pageSize,
        keyword: searchKeyword,
        ...params,
      };

      if (selectedAction) queryParams.action = selectedAction;
      if (selectedModule) queryParams.module = selectedModule;
      if (dateRange && dateRange[0] && dateRange[1]) {
        queryParams.start_date = dateRange[0].format('YYYY-MM-DD');
        queryParams.end_date = dateRange[1].format('YYYY-MM-DD');
      }

      const response = await logApi.getLogs(queryParams);
      setLogs(response.items || []);
      setPagination({
        ...pagination,
        total: response.total || 0,
      });
    } catch (error) {
      message.error('获取操作日志失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchFilters = async () => {
    try {
      const [actionsRes, modulesRes] = await Promise.all([
        logApi.getLogActions(),
        logApi.getLogModules(),
      ]);
      setActions(actionsRes || []);
      setModules(modulesRes || []);
    } catch (error) {
      console.error('获取筛选条件失败', error);
    }
  };

  useEffect(() => {
    fetchLogs();
    fetchFilters();
  }, []);

  const handleSearch = () => {
    setPagination({ ...pagination, current: 1 });
    fetchLogs({ page: 1 });
  };

  const handleTableChange = (newPagination: any) => {
    setPagination(newPagination);
    fetchLogs({
      page: newPagination.current,
      per_page: newPagination.pageSize,
    });
  };

  const handleClearLogs = () => {
    Modal.confirm({
      title: '清理日志',
      content: '确定要清理90天前的操作日志吗？此操作不可恢复。',
      onOk: async () => {
        try {
          await logApi.clearLogs({ days: 90 });
          message.success('日志清理成功');
          fetchLogs();
        } catch (error: any) {
          message.error(error.response?.data?.error || '清理失败');
        }
      },
    });
  };

  const handleExport = () => {
    const params: any = {};
    if (dateRange && dateRange[0] && dateRange[1]) {
      params.start_date = dateRange[0].format('YYYY-MM-DD');
      params.end_date = dateRange[1].format('YYYY-MM-DD');
    }
    logApi.exportLogs(params);
  };

  const handleViewDetail = (record: LogItem) => {
    setSelectedLog(record);
    setDetailModalVisible(true);
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 80,
    },
    {
      title: '用户',
      dataIndex: 'username',
      width: 120,
    },
    {
      title: '操作',
      dataIndex: 'action',
      width: 100,
      render: (action: string) => {
        const config = actionMap[action] || { text: action, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '模块',
      dataIndex: 'module',
      width: 120,
      render: (module: string) => moduleMap[module] || module,
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true,
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      width: 130,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 80,
      render: (status: string) => (
        <Tag color={status === 'success' ? 'success' : 'error'}>
          {status === 'success' ? '成功' : '失败'}
        </Tag>
      ),
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (record: LogItem) => (
        <Button type="text" icon={<EyeOutlined />} onClick={() => handleViewDetail(record)}>
          详情
        </Button>
      ),
    },
  ];

  return (
    <Card
      title={
        <span>
          <FileTextOutlined /> 操作日志
        </span>
      }
      extra={
        <Space>
          <Button icon={<ClearOutlined />} onClick={handleClearLogs}>
            清理日志
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            导出
          </Button>
        </Space>
      }
    >
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Input.Search
            placeholder="搜索描述、IP地址"
            value={searchKeyword}
            onChange={e => setSearchKeyword(e.target.value)}
            onSearch={handleSearch}
            enterButton={<SearchOutlined />}
          />
        </Col>
        <Col span={4}>
          <Select
            placeholder="操作类型"
            allowClear
            style={{ width: '100%' }}
            value={selectedAction}
            onChange={setSelectedAction}
          >
            {actions.map(action => (
              <Option key={action} value={action}>
                {actionMap[action]?.text || action}
              </Option>
            ))}
          </Select>
        </Col>
        <Col span={4}>
          <Select
            placeholder="模块"
            allowClear
            style={{ width: '100%' }}
            value={selectedModule}
            onChange={setSelectedModule}
          >
            {modules.map(module => (
              <Option key={module} value={module}>
                {moduleMap[module] || module}
              </Option>
            ))}
          </Select>
        </Col>
        <Col span={6}>
          <RangePicker style={{ width: '100%' }} value={dateRange} onChange={setDateRange} />
        </Col>
        <Col span={4}>
          <Button type="primary" onClick={handleSearch}>
            查询
          </Button>
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={logs}
        rowKey="id"
        loading={loading}
        pagination={pagination}
        onChange={handleTableChange}
        scroll={{ x: 1200 }}
      />

      <Modal
        title="日志详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={700}
      >
        {selectedLog && (
          <Descriptions bordered column={2}>
            <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
            <Descriptions.Item label="用户">{selectedLog.username}</Descriptions.Item>
            <Descriptions.Item label="操作">
              <Tag color={actionMap[selectedLog.action]?.color || 'default'}>
                {actionMap[selectedLog.action]?.text || selectedLog.action}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="模块">
              {moduleMap[selectedLog.module] || selectedLog.module}
            </Descriptions.Item>
            <Descriptions.Item label="IP地址">{selectedLog.ip_address}</Descriptions.Item>
            <Descriptions.Item label="时间">
              {dayjs(selectedLog.created_at).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={selectedLog.status === 'success' ? 'success' : 'error'}>
                {selectedLog.status === 'success' ? '成功' : '失败'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="描述" span={2}>
              {selectedLog.description}
            </Descriptions.Item>
            {selectedLog.error_message && (
              <Descriptions.Item label="错误信息" span={2}>
                <div style={{ color: 'red' }}>{selectedLog.error_message}</div>
              </Descriptions.Item>
            )}
            <Descriptions.Item label="请求数据" span={2}>
              <pre style={{ maxHeight: 200, overflow: 'auto', background: '#f5f5f5', padding: 8 }}>
                {selectedLog.request_data || '-'}
              </pre>
            </Descriptions.Item>
            <Descriptions.Item label="响应数据" span={2}>
              <pre style={{ maxHeight: 200, overflow: 'auto', background: '#f5f5f5', padding: 8 }}>
                {selectedLog.response_data || '-'}
              </pre>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </Card>
  );
};

export default OperationLog;
