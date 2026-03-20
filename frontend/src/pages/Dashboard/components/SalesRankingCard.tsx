import React from 'react';
import { Card, Avatar, Typography, Spin, Empty } from 'antd';
import { TrophyOutlined, UserOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi, SalesRankingItem } from '@/services/dashboardApi';
import './RankingCard.less';

const { Title, Text } = Typography;

interface SalesRankingCardProps {
  period?: string;
  limit?: number;
}

export const SalesRankingCard: React.FC<SalesRankingCardProps> = ({ 
  period = 'month', 
  limit = 5 
}) => {
  const { data, isLoading } = useQuery({
    queryKey: ['salesRanking', period, limit],
    queryFn: () => dashboardApi.getSalesRanking(period, limit),
    staleTime: 5 * 60 * 1000, // 5分钟缓存
  });

  const rankings = data?.rankings || [];

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1: return '#FFD700'; // 金色
      case 2: return '#C0C0C0'; // 银色
      case 3: return '#CD7F32'; // 铜色
      default: return '#8c8c8c';
    }
  };

  const getRankIcon = (rank: number) => {
    if (rank <= 3) {
      return <TrophyOutlined style={{ color: getRankColor(rank), fontSize: 20 }} />;
    }
    return <Text strong style={{ color: getRankColor(rank), fontSize: 16 }}>{rank}</Text>;
  };

  return (
    <Card 
      title={<span><TrophyOutlined /> 销售业绩排行榜</span>} 
      className="ranking-card"
      loading={isLoading}
    >
      {rankings.length === 0 ? (
        <Empty description="暂无数据" />
      ) : (
        <div className="ranking-list">
          {rankings.map((item: SalesRankingItem) => (
            <div key={item.user_id} className="ranking-item">
              <div className="rank-icon">{getRankIcon(item.rank)}</div>
              <Avatar 
                src={item.avatar} 
                icon={<UserOutlined />} 
                size={40}
                className="user-avatar"
              />
              <div className="user-info">
                <div className="user-name">{item.user_name}</div>
                <div className="user-dept">{item.department || '未分配部门'}</div>
              </div>
              <div className="sales-info">
                <div className="sales-amount">
                  ¥{item.order_amount.toLocaleString()}
                </div>
                <div className="sales-count">{item.order_count}单</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
