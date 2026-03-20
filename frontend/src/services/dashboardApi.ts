/**
 * Dashboard API 服务
 * 仪表盘数据接口
 */
import { apiService } from './api';

export interface SalesRankingItem {
  rank: number;
  user_id: number;
  user_name: string;
  avatar?: string;
  department?: string;
  order_count: number;
  order_amount: number;
}

export interface SalesRankingResponse {
  period: string;
  start_date: string;
  rankings: SalesRankingItem[];
}

export interface FollowupRankingItem {
  rank: number;
  user_id: number;
  user_name: string;
  avatar?: string;
  department?: string;
  contact_count: number;
  customer_count: number;
  conversion_rate: number;
}

export interface FollowupRankingResponse {
  period: string;
  start_date: string;
  rankings: FollowupRankingItem[];
}

export interface TargetCompletionResponse {
  target_type: string;
  target_year: number;
  target_month: number;
  target_amount: number;
  current_amount: number;
  completion_rate: number;
  remaining_amount: number;
  remaining_days: number;
  trend: {
    date: string;
    amount: number;
  }[];
}

export interface TodoItem {
  id: number;
  type: 'reminder' | 'customer' | 'order';
  title: string;
  content?: string;
  customer_name?: string;
  customer_company?: string;
  order_number?: string;
  total_amount?: number;
  due_time?: string;
  priority: 'high' | 'normal' | 'low';
}

export interface TodoCategory {
  count: number;
  items: TodoItem[];
}

export interface TodosResponse {
  total_count: number;
  categories: {
    reminders: TodoCategory;
    pending_contacts: TodoCategory;
    pending_orders: TodoCategory;
  };
}

export const dashboardApi = {
  /**
   * 获取销售业绩排行榜
   */
  getSalesRanking: async (period: string = 'month', limit: number = 5) => {
    const response = await apiService.get('/dashboard/sales-ranking', {
      params: { period, limit }
    });
    return response.data as SalesRankingResponse;
  },

  /**
   * 获取客户跟进排行榜
   */
  getFollowupRanking: async (period: string = 'month', limit: number = 5) => {
    const response = await apiService.get('/dashboard/followup-ranking', {
      params: { period, limit }
    });
    return response.data as FollowupRankingResponse;
  },

  /**
   * 获取目标完成度
   */
  getTargetCompletion: async () => {
    const response = await apiService.get('/dashboard/target-completion');
    return response.data as TargetCompletionResponse;
  },

  /**
   * 获取待办聚合
   */
  getTodos: async () => {
    const response = await apiService.get('/dashboard/todos');
    return response.data as TodosResponse;
  },
};
