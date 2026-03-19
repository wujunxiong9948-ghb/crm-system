import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Statistic,
  Button,
  Space,
  Tag,
  Badge,
  Tooltip,
  Empty,
  Spin,
  message,
  Dropdown,
  Menu,
  Modal,
} from 'antd';
import {
  PlusOutlined,
  ReloadOutlined,
  EyeOutlined,
  EditOutlined,
  ArrowRightOutlined,
  ArrowLeftOutlined,
  FilterOutlined,
  DollarOutlined,
  CalendarOutlined,
  MoreOutlined,
} from '@ant-design/icons';
import { apiService } from '@/services/api';
import { usePermission, PERMISSION_CODES } from '@/utils/permission';
import OpportunityForm from './OpportunityForm';
import type { Opportunity } from '../../types/opportunity';
import dayjs from 'dayjs';

// 阶段配置
const STAGE_CONFIG: Record<string, { color: string; name: string; probability: number }> = {
  '初步接触': { color: '#bfbfbf', name: '初步接触', probability: 10 },
  '需求分析': { color: '#1890ff', name: '需求分析', probability: 25 },
  '方案报价': { color: '#faad14', name: '方案报价', probability: 50 },
  '谈判': { color: '#fa541c', name: '谈判', probability: 75 },
  '成交': { color: '#52c41a', name: '成交', probability: 100 },
  '丢失': { color: '#ff4d4f', name: '丢失', probability: 0 },
};

// 优先级颜色
const PRIORITY_COLORS: Record<string, string> = {
  '高': 'red',
  '中': 'orange',
  '低': 'green',
};

interface PipelineStats {
  total_count: number;
  total_value: number;
  weighted_value: number;
  by_stage: Record<string, { count: number; value: number }>;
}

const OpportunityPipeline: React.FC = () => {
  const navigate = useNavigate();
  const { hasPermissionCode } = usePermission();
  
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<PipelineStats | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null | undefined>(null);

  // 获取销售机会列表
  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/opportunities', {
        params: { per_page: 1000 },
      });
      console.log('API Response:', response);
      
      // 适配后端返回格式: {data: [...], pagination: {...}}
      if (response && Array.isArray(response.data)) {
        console.log('使用直接data格式，数量:', response.data.length);
        setOpportunities(response.data);
      } else if (response && response.data && Array.isArray(response.data.items)) {
        console.log('使用items格式，数量:', response.data.items.length);
        setOpportunities(response.data.items);
      } else {
        console.log('未知格式，设置为空数组');
        setOpportunities([]);
      }
    } catch (error) {
      message.error('获取销售机会失败');
      console.error('获取销售机会失败:', error);
      setOpportunities([]);
    } finally {
      setLoading(false);
    }
  };

  // 获取统计数据
  const fetchStats = async () => {
    try {
      const response = await apiService.get('/opportunities/stats');
      console.log('Stats API response:', response);
      
      // 适配后端实际返回格式
      if (response) {
        // 从by_stage计算总预计金额和加权金额
        let totalValue = 0;
        let weightedValue = 0;
        let totalCount = 0;
        
        if (response.by_stage && Array.isArray(response.by_stage)) {
          response.by_stage.forEach((stage: any) => {
            totalValue += stage.value || 0;
            totalCount += stage.count || 0;
          });
        }
        
        // 加权金额需要额外计算（后端没返回probability）
        // 这里用总金额的50%作为估算
        weightedValue = totalValue * 0.5;
        
        setStats({
          total_count: totalCount,
          total_value: totalValue,
          weighted_value: weightedValue,
          by_stage: response.by_stage || []
        });
      }
    } catch (error) {
      console.error('获取统计数据失败:', error);
    }
  };

  useEffect(() => {
    fetchOpportunities();
    fetchStats();
  }, []);

  // 更新机会阶段
  const handleStageChange = async (opportunityId: number, newStage: string) => {
    try {
      const response = await apiService.put(`/opportunities/${opportunityId}/stage`, {
        stage: newStage,
        probability: STAGE_CONFIG[newStage]?.probability || 10,
      });
      if (response.success) {
        message.success('阶段更新成功');
        fetchOpportunities();
        fetchStats();
      }
    } catch (error) {
      message.error('阶段更新失败');
      console.error('阶段更新失败:', error);
    }
  };

  // 打开编辑弹窗
  const handleEdit = (opportunity: Opportunity) => {
    setSelectedOpportunity(opportunity);
    setModalVisible(true);
  };

  // 新建机会
  const handleNew = () => {
    setSelectedOpportunity(null);
    setModalVisible(true);
  };

  // 提交成功回调
  const handleSuccess = () => {
    setModalVisible(false);
    setSelectedOpportunity(null);
    message.success(selectedOpportunity ? '销售机会更新成功' : '销售机会创建成功');
    fetchOpportunities();
    fetchStats();
  };

  // 按阶段分组
  const groupedByStage = Object.keys(STAGE_CONFIG).reduce((acc, stage) => {
    acc[stage] = opportunities.filter(opp => opp.stage === stage);
    return acc;
  }, {} as Record<string, Opportunity[]>);

  // 渲染机会卡片
  const renderOpportunityCard = (opportunity: Opportunity) => {
    const stageMenu = (
      <Menu>
        {Object.keys(STAGE_CONFIG)
          .filter(stage => stage !== opportunity.stage && stage !== '丢失')
          .map(stage => (
            <Menu.Item key={stage} onClick={() => handleStageChange(opportunity.id, stage)}>
              移动到 {stage}
            </Menu.Item>
          ))}
      </Menu>
    );

    return (
      <Card
        key={opportunity.id}
        size="small"
        className="mb-2 cursor-pointer hover:shadow-md transition-shadow"
        onClick={() => navigate(`/opportunities/${opportunity.id}`)}
        title={
          <div className="flex justify-between items-center">
            <span className="font-medium truncate" style={{ maxWidth: 150 }}>
              {opportunity.name}
            </span>
            <Space>
              <Tag color={PRIORITY_COLORS[opportunity.priority]}>
                {opportunity.priority}
              </Tag>
              <Dropdown overlay={stageMenu} trigger={['click']}>
                <Button 
                  type="text" 
                  size="small" 
                  icon={<MoreOutlined />}
                  onClick={(e) => e.stopPropagation()}
                />
              </Dropdown>
            </Space>
          </div>
        }
      >
        <div className="text-sm">
          <div className="text-gray-600 mb-1">{opportunity.hotel_name || opportunity.name}</div>
          <div className="flex justify-between items-center">
            <span className="font-semibold text-blue-600">
              ¥{(opportunity.expected_value / 10000).toFixed(1)}万
            </span>
            <span className="text-gray-500 text-xs">
              {opportunity.probability}%
            </span>
          </div>
          {opportunity.expected_close_date && (
            <div className="text-gray-400 text-xs mt-1">
              预计成交: {dayjs(opportunity.expected_close_date).format('MM-DD')}
            </div>
          )}
        </div>
      </Card>
    );
  };

  if (loading) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      {/* 顶部统计 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总机会数"
              value={stats?.total_count || opportunities.length}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总预计金额"
              value={stats?.total_value || 0}
              precision={0}
              formatter={(value) => `¥${(Number(value) / 10000).toFixed(1)}万`}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="加权金额"
              value={stats?.weighted_value || 0}
              precision={0}
              formatter={(value) => `¥${(Number(value) / 10000).toFixed(1)}万`}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ textAlign: 'center', padding: '8px 0' }}>
              {hasPermissionCode(PERMISSION_CODES.OPPORTUNITY_CREATE) && (
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />} 
                  size="large"
                  onClick={handleNew}
                  style={{ width: '100%' }}
                >
                  新建销售机会
                </Button>
              )}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 管道视图 */}
      <Card 
        title={
          <Space>
            <span>销售管道</span>
            <Button icon={<ReloadOutlined />} onClick={() => { fetchOpportunities(); fetchStats(); }}>
              刷新
            </Button>
          </Space>
        }
      >
        <div style={{ overflowX: 'auto' }}>
          <Row gutter={12} style={{ minWidth: 1200 }}>
            {Object.entries(STAGE_CONFIG)
              .filter(([stage]) => stage !== '丢失')
              .map(([stage, config]) => {
                const stageOpps = groupedByStage[stage] || [];
                const stageValue = stageOpps.reduce((sum, opp) => sum + (opp.expected_value || 0), 0);
                
                return (
                  <Col key={stage} span={4}>
                    <div 
                      className="pipeline-column"
                      style={{ 
                        backgroundColor: '#f5f5f5', 
                        borderRadius: 8,
                        padding: 12,
                        minHeight: 400,
                      }}
                    >
                      {/* 列标题 */}
                      <div 
                        className="flex justify-between items-center mb-3"
                        style={{ borderBottom: `2px solid ${config.color}`, paddingBottom: 8 }}
                      >
                        <div>
                          <span style={{ fontWeight: 'bold', color: config.color }}>{config.name}</span>
                          <Badge 
                            count={stageOpps.length} 
                            style={{ marginLeft: 8, backgroundColor: config.color }}
                          />
                        </div>
                        <Tooltip title={`预计金额: ¥${stageValue.toLocaleString()}`}>
                          <span className="text-gray-500 text-sm">
                            ¥{(stageValue / 10000).toFixed(1)}万
                          </span>
                        </Tooltip>
                      </div>

                      {/* 机会列表 */}
                      <div className="space-y-2">
                        {stageOpps.length > 0 ? (
                          stageOpps.map(renderOpportunityCard)
                        ) : (
                          <Empty 
                            image={Empty.PRESENTED_IMAGE_SIMPLE} 
                            description="暂无机会"
                            style={{ marginTop: 40 }}
                          />
                        )}
                      </div>
                    </div>
                  </Col>
                );
              })}
          </Row>
        </div>
      </Card>

      {/* 已关闭机会 */}
      {groupedByStage['丢失']?.length > 0 && (
        <Card title="已关闭" style={{ marginTop: 24 }}>
          <Row gutter={16}>
            {groupedByStage['丢失'].map(opp => (
              <Col key={opp.id} span={6} style={{ marginBottom: 16 }}>
                {renderOpportunityCard(opp)}
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 新建/编辑弹窗 */}
      <Modal
        title={selectedOpportunity ? '编辑销售机会' : '新建销售机会'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setSelectedOpportunity(null);
        }}
        footer={null}
        width={900}
        destroyOnClose
      >
        <OpportunityForm
          opportunity={selectedOpportunity}
          onSuccess={handleSuccess}
          onCancel={() => {
            setModalVisible(false);
            setSelectedOpportunity(null);
          }}
        />
      </Modal>
    </div>
  );
};

export default OpportunityPipeline;
