import React from 'react';
import { Card, Progress, Statistic, Row, Col, Typography, Spin } from 'antd';
import { TargetOutlined, CalendarOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/services/dashboardApi';
import dayjs from 'dayjs';
import './TargetProgressCard.less';

const { Title, Text } = Typography;

export const TargetProgressCard: React.FC = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['targetCompletion'],
    queryFn: () => dashboardApi.getTargetCompletion(),
    staleTime: 1 * 60 * 1000, // 1分钟缓存
  });

  if (isLoading) {
    return <Card loading={true} />;
  }

  if (!data) {
    return <Card title="月度目标完成度"><Text>暂无数据</Text></Card>;
  }

  const {
    target_amount,
    current_amount,
    completion_rate,
    remaining_amount,
    remaining_days
  } = data;

  // 判断完成状态
  const getStatusColor = () => {
    if (completion_rate >= 100) return '#52c41a'; // 绿色 - 已完成
    if (completion_rate >= 80) return '#1890ff';  // 蓝色 - 良好
    if (completion_rate >= 50) return '#faad14';  // 黄色 - 警告
    return '#ff4d4f'; // 红色 - 危险
  };

  return (
    <Card 
      title={<span><TargetOutlined /> 月度目标完成度</span>}
      className="target-progress-card"
    >
      <div className="target-header">
        <Text className="target-period">
          {data.target_year}年{data.target_month}月
        </Text>
      </div>

      <div className="progress-section">
        <Progress 
          type="circle" 
          percent={Math.min(completion_rate, 100)}
          strokeColor={getStatusColor()}
          width={120}
          format={(percent) => (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold' }}>{percent}%</div>
              <div style={{ fontSize: 12, color: '#8c8c8c' }}>完成度</div>
            </div>
          )}
        />
      </div>

      <Row gutter={16} className="target-stats">
        <Col span={12}>
          <Statistic 
            title="目标金额" 
            value={target_amount} 
            precision={2}
            prefix="¥"
            formatter={(value) => `¥${Number(value).toLocaleString()}`}
          />
        </Col>
        <Col span={12}>
          <Statistic 
            title="已完成" 
            value={current_amount} 
            precision={2}
            valueStyle={{ color: getStatusColor() }}
            formatter={(value) => `¥${Number(value).toLocaleString()}`}
          />
        </Col>
      </Row>

      <div className="target-footer">
        <div className="remaining-info">
          <Text type="secondary">
            还差 <Text strong>¥{remaining_amount.toLocaleString()}</Text>
          </Text>
        </div>
        <div className="days-info">
          <CalendarOutlined />
          <Text type="secondary"> 剩余 {remaining_days} 天</Text>
        </div>
      </div>
    </Card>
  );
};
