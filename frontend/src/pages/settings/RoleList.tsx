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
  Tree,
  message,
  Popconfirm,
  Row,
  Col,
  Checkbox,
  Select,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  SafetyOutlined,
} from '@ant-design/icons';
import { roleApi } from '../../services/api';

interface Role {
  id: number;
  name: string;
  code: string;
  description: string;
  status: string;
  is_system: boolean;
  permissions: { id: number; name: string; code: string; module: string }[];
}

interface Permission {
  id: number;
  name: string;
  code: string;
  module: string;
}

const RoleList: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [permissionModalVisible, setPermissionModalVisible] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [form] = Form.useForm();
  const [searchKeyword, setSearchKeyword] = useState('');
  const [permissions, setPermissions] = useState<Record<string, Permission[]>>({});
  const [selectedPermissions, setSelectedPermissions] = useState<number[]>([]);
  const [currentRoleId, setCurrentRoleId] = useState<number | null>(null);

  const fetchRoles = async () => {
    setLoading(true);
    try {
      const response = await roleApi.getRoles({ keyword: searchKeyword });
      setRoles(response.items || []);
    } catch (error) {
      message.error('获取角色列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchPermissions = async () => {
    try {
      const response = await roleApi.getPermissions();
      setPermissions(response || {});
    } catch (error) {
      message.error('获取权限列表失败');
    }
  };

  useEffect(() => {
    fetchRoles();
    fetchPermissions();
  }, []);

  const handleSearch = () => {
    fetchRoles();
  };

  const handleAdd = () => {
    setEditingRole(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Role) => {
    setEditingRole(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleSave = async (values: any) => {
    try {
      if (editingRole) {
        await roleApi.updateRole(editingRole.id, values);
        message.success('角色更新成功');
      } else {
        await roleApi.createRole(values);
        message.success('角色创建成功');
      }
      setModalVisible(false);
      fetchRoles();
    } catch (error: any) {
      message.error(error.response?.data?.error || '操作失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await roleApi.deleteRole(id);
      message.success('角色删除成功');
      fetchRoles();
    } catch (error: any) {
      message.error(error.response?.data?.error || '删除失败');
    }
  };

  const handleSetPermissions = (record: Role) => {
    setCurrentRoleId(record.id);
    setSelectedPermissions(record.permissions?.map(p => p.id) || []);
    setPermissionModalVisible(true);
  };

  const handleSavePermissions = async () => {
    if (!currentRoleId) return;
    try {
      await roleApi.updateRole(currentRoleId, { permission_ids: selectedPermissions });
      message.success('权限设置成功');
      setPermissionModalVisible(false);
      fetchRoles();
    } catch (error: any) {
      message.error(error.response?.data?.error || '设置失败');
    }
  };

  const columns = [
    {
      title: '角色名称',
      dataIndex: 'name',
      render: (text: string, record: Role) => (
        <Space>
          <SafetyOutlined />
          <span>{text}</span>
          {record.is_system && <Tag color="red">系统</Tag>}
        </Space>
      ),
    },
    {
      title: '角色代码',
      dataIndex: 'code',
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true,
    },
    {
      title: '权限数量',
      key: 'permission_count',
      render: (record: Role) => record.permissions?.length || 0,
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
      title: '操作',
      key: 'action',
      render: (record: Role) => (
        <Space size="small">
          <Button type="text" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button type="text" onClick={() => handleSetPermissions(record)}>
            权限设置
          </Button>
          {!record.is_system && (
            <Popconfirm title="确定要删除该角色吗？" onConfirm={() => handleDelete(record.id)}>
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="角色权限管理"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增角色
        </Button>
      }
    >
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Input.Search
            placeholder="搜索角色名称、代码"
            value={searchKeyword}
            onChange={e => setSearchKeyword(e.target.value)}
            onSearch={handleSearch}
            enterButton={<SearchOutlined />}
          />
        </Col>
      </Row>

      <Table columns={columns} dataSource={roles} rowKey="id" loading={loading} />

      {/* 角色编辑弹窗 */}
      <Modal
        title={editingRole ? '编辑角色' : '新增角色'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item
            name="name"
            label="角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          >
            <Input placeholder="请输入角色名称" />
          </Form.Item>

          <Form.Item
            name="code"
            label="角色代码"
            rules={[{ required: true, message: '请输入角色代码' }]}
          >
            <Input disabled={!!editingRole} placeholder="请输入角色代码，如：sales_manager" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} placeholder="请输入角色描述" />
          </Form.Item>

          <Form.Item name="status" label="状态" initialValue="active">
            <Select>
              <Select.Option value="active">启用</Select.Option>
              <Select.Option value="inactive">禁用</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 权限设置弹窗 */}
      <Modal
        title="权限设置"
        open={permissionModalVisible}
        onOk={handleSavePermissions}
        onCancel={() => setPermissionModalVisible(false)}
        width={700}
      >
        <div style={{ maxHeight: 400, overflow: 'auto' }}>
          {Object.entries(permissions).map(([module, perms]) => (
            <Card key={module} size="small" title={module} style={{ marginBottom: 16 }}>
              <Checkbox.Group
                value={selectedPermissions}
                onChange={values => setSelectedPermissions(values as number[])}
              >
                <Row gutter={[16, 8]}>
                  {perms.map(perm => (
                    <Col span={8} key={perm.id}>
                      <Checkbox value={perm.id}>{perm.name}</Checkbox>
                    </Col>
                  ))}
                </Row>
              </Checkbox.Group>
            </Card>
          ))}
        </div>
      </Modal>
    </Card>
  );
};

export default RoleList;
