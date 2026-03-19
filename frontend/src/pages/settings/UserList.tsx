import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Tag,
  Space,
  Modal,
  Form,
  Select,
  message,
  Popconfirm,
  Avatar,
  Switch,
  Row,
  Col,
  Result,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  LockOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { userApi } from '../../services/api';
import { createPermissionChecker } from '../../utils/permission';

const { Option } = Select;

interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  phone: string;
  role: string;
  status: string;
  department: string;
  position: string;
  avatar: string;
  last_login: string;
  created_at: string;
  roles: { id: number; name: string; code: string }[];
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();
  const [searchKeyword, setSearchKeyword] = useState('');
  const [roles, setRoles] = useState<{ id: number; name: string }[]>([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  // 检查权限
  const permissionChecker = createPermissionChecker();
  const hasPermission = permissionChecker.hasPermission('/settings/users');

  // 如果没有权限，显示无权限提示
  if (!hasPermission) {
    return (
      <Result
        status="403"
        title="403"
        subTitle={
          <div>
            <p>抱歉，您没有权限访问用户管理页面</p>
            <p style={{ color: '#999', fontSize: '14px' }}>
              当前角色：{permissionChecker.getRoleDisplayName()}
            </p>
          </div>
        }
        extra={
          <Button type="primary" onClick={() => window.location.href = '/dashboard'}>
            返回首页
          </Button>
        }
      />
    );
  }

  const fetchUsers = async (params = {}) => {
    setLoading(true);
    try {
      const response = await userApi.getUsers({
        page: pagination.current,
        per_page: pagination.pageSize,
        keyword: searchKeyword,
        ...params,
      });
      setUsers(response.items || []);
      setPagination({
        ...pagination,
        total: response.total || 0,
      });
    } catch (error) {
      message.error('获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await userApi.getAllRoles();
      setRoles(response || []);
    } catch (error) {
      console.error('获取角色列表失败', error);
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchRoles();
  }, []);

  const handleSearch = () => {
    setPagination({ ...pagination, current: 1 });
    fetchUsers({ page: 1 });
  };

  const handleTableChange = (newPagination: any) => {
    setPagination(newPagination);
    fetchUsers({
      page: newPagination.current,
      per_page: newPagination.pageSize,
    });
  };

  const handleAdd = () => {
    setEditingUser(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: User) => {
    setEditingUser(record);
    form.setFieldsValue({
      ...record,
      role_ids: record.roles?.map(r => r.id) || [],
    });
    setModalVisible(true);
  };

  const handleSave = async (values: any) => {
    try {
      if (editingUser) {
        await userApi.updateUser(editingUser.id, values);
        message.success('用户更新成功');
      } else {
        await userApi.createUser(values);
        message.success('用户创建成功');
      }
      setModalVisible(false);
      fetchUsers();
    } catch (error: any) {
      message.error(error.response?.data?.error || '操作失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await userApi.deleteUser(id);
      message.success('用户删除成功');
      fetchUsers();
    } catch (error: any) {
      message.error(error.response?.data?.error || '删除失败');
    }
  };

  const handleToggleStatus = async (record: User) => {
    try {
      await userApi.toggleUserStatus(record.id);
      message.success(`用户已${record.status === 'active' ? '禁用' : '启用'}`);
      fetchUsers();
    } catch (error: any) {
      message.error(error.response?.data?.error || '操作失败');
    }
  };

  const handleResetPassword = async (record: User) => {
    Modal.confirm({
      title: '重置密码',
      content: (
        <div>
          <p>确定要重置用户 {record.full_name} 的密码吗？</p>
          <p>重置后的默认密码为：123456</p>
        </div>
      ),
      onOk: async () => {
        try {
          await userApi.resetPassword(record.id);
          message.success('密码重置成功');
        } catch (error: any) {
          message.error(error.response?.data?.error || '重置失败');
        }
      },
    });
  };

  const getRoleColor = (role: string) => {
    const colors: Record<string, string> = {
      admin: 'red',
      manager: 'orange',
      sales: 'blue',
      user: 'default',
    };
    return colors[role] || 'default';
  };

  const getRoleText = (role: string) => {
    const texts: Record<string, string> = {
      admin: '管理员',
      manager: '经理',
      sales: '销售',
      user: '普通用户',
    };
    return texts[role] || role;
  };

  const columns = [
    {
      title: '用户',
      key: 'user',
      render: (record: User) => (
        <Space>
          <Avatar
            src={record.avatar}
            icon={<UserOutlined />}
            style={{ backgroundColor: record.avatar ? undefined : '#1890ff' }}
          />
          <div>
            <div style={{ fontWeight: 500 }}>{record.full_name}</div>
            <div style={{ fontSize: 12, color: '#999' }}>@{record.username}</div>
          </div>
        </Space>
      ),
    },
    {
      title: '联系方式',
      key: 'contact',
      render: (record: User) => (
        <div>
          <div>{record.email || '-'}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.phone || '-'}</div>
        </div>
      ),
    },
    {
      title: '部门/职位',
      key: 'dept',
      render: (record: User) => (
        <div>
          <div>{record.department || '-'}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.position || '-'}</div>
        </div>
      ),
    },
    {
      title: '角色',
      dataIndex: 'role',
      render: (role: string) => <Tag color={getRoleColor(role)}>{getRoleText(role)}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'success' : 'default'}>
          {status === 'active' ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '最后登录',
      dataIndex: 'last_login',
      render: (date: string) => (date ? new Date(date).toLocaleString() : '-'),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (record: User) => (
        <Space size="small">
          <Button type="text" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button type="text" icon={<LockOutlined />} onClick={() => handleResetPassword(record)}>
            重置密码
          </Button>
          <Popconfirm
            title={`确定要${record.status === 'active' ? '禁用' : '启用'}该用户吗？`}
            onConfirm={() => handleToggleStatus(record)}
          >
            <Switch checked={record.status === 'active'} size="small" />
          </Popconfirm>
          <Popconfirm title="确定要删除该用户吗？" onConfirm={() => handleDelete(record.id)}>
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="用户管理"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增用户
        </Button>
      }
    >
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Input.Search
            placeholder="搜索用户名、姓名、邮箱、手机号"
            value={searchKeyword}
            onChange={e => setSearchKeyword(e.target.value)}
            onSearch={handleSearch}
            enterButton={<SearchOutlined />}
          />
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        pagination={pagination}
        onChange={handleTableChange}
      />

      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="username"
                label="用户名"
                rules={[{ required: !editingUser, message: '请输入用户名' }]}
              >
                <Input disabled={!!editingUser} placeholder="4-20位字母数字下划线" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="full_name"
                label="姓名"
                rules={[{ required: true, message: '请输入姓名' }]}
              >
                <Input placeholder="请输入姓名" />
              </Form.Item>
            </Col>
          </Row>

          {!editingUser && (
            <Form.Item
              name="password"
              label="密码"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password placeholder="至少6位" />
            </Form.Item>
          )}

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="email" label="邮箱">
                <Input placeholder="请输入邮箱" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="phone" label="手机号">
                <Input placeholder="请输入手机号" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="department" label="部门">
                <Input placeholder="请输入部门" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="position" label="职位">
                <Input placeholder="请输入职位" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="role" label="角色" rules={[{ required: true, message: '请选择角色' }]}>
            <Select placeholder="请选择角色">
              <Option value="admin">管理员</Option>
              <Option value="manager">经理</Option>
              <Option value="sales">销售</Option>
              <Option value="user">普通用户</Option>
            </Select>
          </Form.Item>

          <Form.Item name="role_ids" label="分配角色">
            <Select mode="multiple" placeholder="请选择角色">
              {roles.map(role => (
                <Option key={role.id} value={role.id}>
                  {role.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="status" label="状态" initialValue="active">
            <Select>
              <Option value="active">启用</Option>
              <Option value="inactive">禁用</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default UserList;
