/**
 * 销售机会类型定义 - 酒店家具项目专用
 * 包含完整的28个字段
 */

// 销售阶段
export type OpportunityStage = '初步接触' | '需求分析' | '方案报价' | '谈判' | '成交' | '丢失';

// 项目状态
export type OpportunityStatus = '进行中' | '已成交' | '已丢失';

// 优先级
export type Priority = '高' | '中' | '低';

// 项目类型
export type ProjectType = '新建酒店' | '酒店翻新' | '连锁扩张';

// 酒店星级
export type HotelStar = '经济型' | '三星' | '四星' | '五星' | '超五星';

// 跟进记录
export interface FollowUpRecord {
  id: number;
  date: string;
  type: string;
  content: string;
  result?: string;
  next_action?: string;
  created_by?: string;
}

// 关键联系人
export interface KeyContact {
  name: string;
  position?: string;
  phone?: string;
  email?: string;
  role?: string;
}

// 客户简要信息
export interface CustomerBrief {
  id: number;
  name: string;
  company?: string;
  phone?: string;
  email?: string;
}

// 销售机会完整接口（28个字段）
export interface Opportunity {
  id: number;
  created_at: string;
  updated_at: string;

  // 基本信息
  customer_id: number;
  name: string;
  description?: string;

  // 酒店项目信息
  hotel_name?: string;
  project_type: ProjectType;
  hotel_star?: HotelStar;
  room_count?: number;

  // 地址信息
  province?: string;
  city?: string;
  district?: string;
  address?: string;

  // 时间节点
  planned_opening_date?: string;
  expected_close_date?: string;
  next_follow_up_date?: string;

  // 预算信息（万元）
  renovation_budget: number;
  furniture_budget: number;
  expected_value: number;

  // 产品数量
  bed_count: number;
  nightstand_count: number;
  wardrobe_count: number;
  desk_count: number;
  chair_count: number;
  sofa_count: number;
  coffee_table_count: number;
  tv_cabinet_count: number;
  other_furniture?: string;

  // 销售信息
  stage: OpportunityStage;
  probability: number;
  priority: Priority;
  assigned_to?: string;
  status: OpportunityStatus;

  // 竞争信息
  competitors?: string;
  our_advantage?: string;
  customer_concern?: string;

  // 决策信息
  decision_maker?: string;
  decision_process?: string;
  key_contacts: KeyContact[];

  // 跟进记录
  follow_up_records: FollowUpRecord[];

  // 关联数据
  customer?: CustomerBrief;
  
  // 后端返回的平级客户字段（用于列表展示）
  customer_name?: string;
  customer_company?: string;
}

// 创建销售机会请求
export interface CreateOpportunityRequest {
  customer_id: number;
  name: string;
  description?: string;

  hotel_name?: string;
  project_type?: ProjectType;
  hotel_star?: HotelStar;
  room_count?: number;

  province?: string;
  city?: string;
  district?: string;
  address?: string;

  planned_opening_date?: string;
  expected_close_date?: string;
  next_follow_up_date?: string;

  renovation_budget?: number;
  furniture_budget?: number;
  expected_value?: number;

  bed_count?: number;
  nightstand_count?: number;
  wardrobe_count?: number;
  desk_count?: number;
  chair_count?: number;
  sofa_count?: number;
  coffee_table_count?: number;
  tv_cabinet_count?: number;
  other_furniture?: string;

  stage?: OpportunityStage;
  probability?: number;
  priority?: Priority;
  assigned_to?: string;
  status?: OpportunityStatus;

  competitors?: string;
  our_advantage?: string;
  customer_concern?: string;

  decision_maker?: string;
  decision_process?: string;
  key_contacts?: KeyContact[];
}

// 更新销售机会请求
export interface UpdateOpportunityRequest extends Partial<CreateOpportunityRequest> {}

// 跟进记录请求
export interface AddFollowUpRequest {
  type: string;
  content: string;
  result?: string;
  next_action?: string;
  next_follow_up_date?: string;
}

// 销售机会列表查询参数
export interface OpportunityQueryParams {
  page?: number;
  page_size?: number;
  keyword?: string;
  stage?: string;
  status?: string;
  priority?: string;
  assigned_to?: string;
  project_type?: string;
  hotel_star?: string;
  min_amount?: number;
  max_amount?: number;
}

// 分页响应
export interface PaginationData {
  current: number;
  pageSize: number;
  total: number;
  pages: number;
}

// 统计信息
export interface OpportunityStats {
  total_count: number;
  active_count: number;
  won_count: number;
  lost_count: number;
  total_value: number;
}

// 销售机会列表响应
export interface OpportunityListResponse {
  data: Opportunity[];
  pagination: PaginationData;
  stats: OpportunityStats;
}

// 阶段分布统计
export interface StageDistribution {
  stage: string;
  count: number;
  value: number;
}

// 项目类型分布
export interface ProjectTypeDistribution {
  type: string;
  count: number;
}

// 概览统计
export interface OverviewStats {
  total: number;
  active: number;
  won: number;
  lost: number;
  new_this_month: number;
  due_soon: number;
}

// 完整统计响应
export interface OpportunityStatsResponse {
  overview: OverviewStats;
  stage_distribution: StageDistribution[];
  project_type_distribution: ProjectTypeDistribution[];
  total_pipeline_value: number;
}

// 筛选选项
export interface FilterOptions {
  stages: string[];
  statuses: string[];
  priorities: string[];
  project_types: string[];
  hotel_stars: string[];
  follow_up_types: string[];
  assignees: string[];
}

// 阶段配置（用于进度条展示）
export const STAGE_CONFIG: Record<OpportunityStage, { color: string; probability: number }> = {
  '初步接触': { color: '#1890ff', probability: 10 },
  '需求分析': { color: '#52c41a', probability: 25 },
  '方案报价': { color: '#faad14', probability: 50 },
  '谈判': { color: '#fa8c16', probability: 75 },
  '成交': { color: '#52c41a', probability: 100 },
  '丢失': { color: '#ff4d4f', probability: 0 },
};

// 优先级配置
export const PRIORITY_CONFIG: Record<Priority, { color: string; label: string }> = {
  '高': { color: 'red', label: '高优先级' },
  '中': { color: 'orange', label: '中优先级' },
  '低': { color: 'blue', label: '低优先级' },
};

// 状态配置
export const STATUS_CONFIG: Record<OpportunityStatus, { color: string; label: string }> = {
  '进行中': { color: 'processing', label: '进行中' },
  '已成交': { color: 'success', label: '已成交' },
  '已丢失': { color: 'default', label: '已丢失' },
};

// 项目类型配置
export const PROJECT_TYPE_CONFIG: Record<ProjectType, { color: string; label: string }> = {
  '新建酒店': { color: 'blue', label: '新建酒店' },
  '酒店翻新': { color: 'orange', label: '酒店翻新' },
  '连锁扩张': { color: 'purple', label: '连锁扩张' },
};

// 酒店星级配置
export const HOTEL_STAR_CONFIG: Record<HotelStar, { color: string; icon: string }> = {
  '经济型': { color: '#8c8c8c', icon: '★' },
  '三星': { color: '#1890ff', icon: '★★★' },
  '四星': { color: '#722ed1', icon: '★★★★' },
  '五星': { color: '#faad14', icon: '★★★★★' },
  '超五星': { color: '#f5222d', icon: '★★★★★+' },
};
