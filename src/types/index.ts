// CRM系统类型定义

// 基础类型
export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at: string;
}

// 分页响应
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// 分页参数
export interface PaginationParams {
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// 搜索参数
export interface SearchParams extends PaginationParams {
  search?: string;
  [key: string]: any;
}

// API响应
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  code?: number;
}

// 客户类型
export interface Customer extends BaseEntity {
  name: string;
  company?: string;
  phone?: string;
  email?: string;
  address?: string;
  industry?: string;
  customer_type: '潜在客户' | '现有客户' | 'VIP客户';
  source: '展会' | '推荐' | '网站' | '电话' | '其他';
  status: '活跃' | '休眠' | '流失';
  notes?: string;
}

// 销售机会类型 - 酒店家具项目专用
export interface Opportunity extends BaseEntity {
  customer_id: number;
  name: string; // 项目名称，如"XX酒店家具采购项目"
  description?: string;

  // 酒店项目基本信息
  hotel_name: string; // 酒店名称
  project_address: string; // 项目地址（省市区+详细地址）
  project_type: '新建酒店' | '酒店翻新' | '连锁扩张' | '其他';
  star_rating?: '经济型' | '三星' | '四星' | '五星' | '奢华';

  // 项目时间规划
  planned_opening_date?: string; // 计划开业时间
  expected_close_date?: string; // 预计成交时间

  // 采购规模
  room_count: number; // 客房数（购买套装数量）
  product_quantity?: { // 具体产品数量
    beds?: number; // 床
    nightstands?: number; // 床头柜
    wardrobes?: number; // 衣柜
    desks?: number; // 书桌
    chairs?: number; // 椅子
    sofas?: number; // 沙发
    coffee_tables?: number; // 茶几
    tv_cabinets?: number; // 电视柜
    other?: number; // 其他
  };

  // 预算信息
  renovation_budget?: number; // 装修翻新预算（万元）
  furniture_budget?: number; // 家具采购预算（万元）
  expected_value: number; // 预计订单金额（万元）

  // 销售跟进
  stage: '初步接触' | '需求调研' | '方案设计' | '报价谈判' | '合同签订' | '成交' | '丢失';
  probability: number; // 成交概率 0-100
  status: '进行中' | '已成交' | '已丢失' | '暂停';
  priority: '高' | '中' | '低';

  // 负责人和关联
  assigned_to?: string; // 负责销售
  assigned_to_name?: string; // 负责人姓名
  customer?: Customer; // 关联客户

  // 竞争对手信息
  competitors?: string; // 竞争对手
  our_advantage?: string; // 我司优势

  // 跟进记录
  last_contact_date?: string; // 最后联系时间
  next_follow_up_date?: string; // 下次跟进时间
  notes?: string; // 备注
}

// 订单类型
export interface Order extends BaseEntity {
  opportunity_id?: number;
  customer_id: number;
  order_number: string;
  order_date: string;
  total_amount: number;
  currency: string;
  status: '待处理' | '生产中' | '已发货' | '已完成' | '已取消';
  payment_status: '未支付' | '部分支付' | '已支付';
  shipping_address?: string;
  notes?: string;
  customer?: Customer;
  opportunity?: Opportunity;
  items?: OrderItem[];
}

// 订单明细类型
export interface OrderItem extends BaseEntity {
  order_id: number;
  product_code?: string;
  product_name?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  specifications?: string;
}

// 联系记录类型
export interface Contact extends BaseEntity {
  customer_id: number;
  contact_type: '电话' | '邮件' | '拜访' | '展会' | '微信' | '其他';
  subject?: string;
  content?: string;
  contact_date: string;
  follow_up_date?: string;
  assigned_to?: string;
  status: '待处理' | '进行中' | '已完成' | '已取消';
  customer?: Customer;
}

// 产品类型
export interface Product extends BaseEntity {
  item_id?: string;
  category?: string;
  product_code: string;
  description?: string;
  material?: string;
  moq: number; // 最小起订量
  unit_price: number;
  specifications?: string;
  images?: string; // JSON数组
  status: '可用' | '停用' | '缺货';
}

// 活动提醒类型
export interface Activity extends BaseEntity {
  type: '提醒' | '通知' | '任务';
  title: string;
  description?: string;
  related_id?: number;
  related_type?: 'customer' | 'opportunity' | 'order';
  due_date?: string;
  priority: '高' | '中' | '低';
  assigned_to?: string;
  status: '待处理' | '进行中' | '已完成' | '已取消';
}

// 用户类型
export interface User extends BaseEntity {
  username: string;
  password_hash: string;
  full_name?: string;
  email?: string;
  role: 'admin' | 'manager' | 'sales' | 'user';
  status: 'active' | 'inactive';
  last_login?: string;
}

// 系统设置类型
export interface SystemSetting extends BaseEntity {
  setting_key: string;
  setting_value?: string;
  description?: string;
}

// 通知日志类型
export interface NotificationLog extends BaseEntity {
  notification_type: 'qq' | 'email' | 'sms' | 'system';
  title?: string;
  content?: string;
  recipient?: string;
  status: 'pending' | 'sent' | 'failed' | 'read';
  error_message?: string;
  sent_at?: string;
}

// 仪表盘统计类型
export interface DashboardStats {
  total_customers: number;
  total_opportunities: number;
  total_orders: number;
  total_revenue: number;
  active_opportunities: number;
  pending_orders: number;
  recent_activities: Activity[];
  sales_trend: {
    date: string;
    amount: number;
  }[];
  customer_distribution: {
    type: string;
    count: number;
  }[];
}

// 销售报表类型
export interface SalesReport {
  period: 'daily' | 'weekly' | 'monthly' | 'yearly';
  start_date: string;
  end_date: string;
  total_sales: number;
  total_orders: number;
  average_order_value: number;
  top_products: {
    product_code: string;
    product_name: string;
    quantity: number;
    revenue: number;
  }[];
  sales_by_date: {
    date: string;
    sales: number;
    orders: number;
  }[];
}

// 客户分析类型
export interface CustomerAnalysis {
  total_customers: number;
  new_customers_this_month: number;
  customer_growth_rate: number;
  customer_distribution: {
    type: string;
    count: number;
    percentage: number;
  }[];
  top_customers: {
    customer_id: number;
    customer_name: string;
    total_orders: number;
    total_spent: number;
    last_order_date: string;
  }[];
  customer_lifetime_value: {
    customer_id: number;
    customer_name: string;
    lifetime_value: number;
    first_order_date: string;
    last_order_date: string;
  }[];
}

// 表单验证类型
export interface ValidationRules {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  email?: boolean;
  phone?: boolean;
  custom?: (value: any) => boolean | string;
}

// 表单字段类型
export interface FormField {
  name: string;
  label: string;
  type:
    | 'text'
    | 'number'
    | 'email'
    | 'phone'
    | 'date'
    | 'select'
    | 'textarea'
    | 'checkbox'
    | 'radio';
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  options?: { label: string; value: any }[];
  validation?: ValidationRules;
  defaultValue?: any;
}

// 菜单项类型
export interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  path?: string;
  children?: MenuItem[];
  permission?: string[];
}

// 表格列类型
export interface TableColumn<T> {
  key: string;
  title: string;
  dataIndex?: keyof T;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  filterable?: boolean;
  fixed?: 'left' | 'right';
  ellipsis?: boolean;
}

// 过滤器类型
export interface FilterOption {
  label: string;
  value: any;
}

export interface FilterConfig {
  key: string;
  label: string;
  type: 'text' | 'select' | 'date' | 'number' | 'checkbox' | 'radio';
  options?: FilterOption[];
  placeholder?: string;
  defaultValue?: any;
}

// 图表数据类型
export interface ChartData {
  name: string;
  value: number;
  [key: string]: any;
}

// 通知类型
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// 文件上传类型
export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  uploaded_at: string;
}

// 导入/导出配置
export interface ImportExportConfig {
  fields: {
    key: string;
    label: string;
    required: boolean;
    type: 'string' | 'number' | 'date' | 'boolean';
  }[];
  template_url?: string;
  max_rows?: number;
  allowed_formats?: string[];
}

// 系统配置类型
export interface SystemConfig {
  company_name: string;
  currency: string;
  timezone: string;
  date_format: string;
  items_per_page: number;
  notification_enabled: boolean;
  backup_enabled: boolean;
  [key: string]: any;
}
