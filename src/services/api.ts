import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse } from '@/types';

// API配置 - 生产环境直接访问后端
const API_BASE_URL = 'http://localhost:5000/api/v1';
const API_TIMEOUT = 30000; // 30秒

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 添加时间戳防止缓存
    if (config.method?.toLowerCase() === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      };
    }

    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // 处理成功的响应
    if (response.data && response.data.success === false) {
      return Promise.reject(response.data);
    }
    return response;
  },
  error => {
    // 处理错误响应
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response;

      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_info');
          window.location.href = '/login';
          break;

        case 403:
          // 禁止访问
          console.error('权限不足:', data.message);
          break;

        case 404:
          // 资源未找到
          console.error('资源未找到:', data.message);
          break;

        case 500:
          // 服务器内部错误
          console.error('服务器错误:', data.message);
          break;

        default:
          console.error(`请求错误 ${status}:`, data.message);
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('网络错误，请检查网络连接');
    } else {
      // 请求配置错误
      console.error('请求配置错误:', error.message);
    }

    return Promise.reject(error);
  }
);

// API服务类
class ApiService {
  // 通用GET请求
  async get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.get<ApiResponse<T>>(url, config);
    return response.data as T;
  }

  // 通用POST请求
  async post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.post<ApiResponse<T>>(url, data, config);
    return response.data as T;
  }

  // 通用PUT请求
  async put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.put<ApiResponse<T>>(url, data, config);
    return response.data as T;
  }

  // 通用PATCH请求
  async patch<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.patch<ApiResponse<T>>(url, data, config);
    return response.data as T;
  }

  // 通用DELETE请求
  async delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.delete<ApiResponse<T>>(url, config);
    return response.data as T;
  }

  // 文件上传
  async uploadFile<T = unknown>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<ApiResponse<T>>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: progressEvent => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data as T;
  }

  // 下载文件
  async downloadFile(url: string, filename?: string): Promise<void> {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    });

    const blob = new Blob([response as BlobPart]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }

  // 设置认证token
  setAuthToken(token: string): void {
    localStorage.setItem('access_token', token);
    apiClient.defaults.headers.common.Authorization = `Bearer ${token}`;
  }

  // 清除认证token
  clearAuthToken(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    delete apiClient.defaults.headers.common.Authorization;
  }

  // 检查是否已认证
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  // 获取当前用户信息
  getCurrentUser(): Record<string, unknown> | null {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? (JSON.parse(userInfo) as Record<string, unknown>) : null;
  }

  // 设置当前用户信息
  setCurrentUser(userInfo: Record<string, unknown>): void {
    localStorage.setItem('user_info', JSON.stringify(userInfo));
  }
}

// 导出单例实例
export const apiService = new ApiService();

// 导出具体的API端点
export const apiEndpoints = {
  // 认证相关
  auth: {
    login: '/auth/login',
    logout: '/auth/logout',
    refresh: '/auth/refresh',
    profile: '/auth/profile',
  },

  // 客户管理
  customers: {
    list: '/customers',
    detail: (id: number) => `/customers/${id}`,
    create: '/customers',
    update: (id: number) => `/customers/${id}`,
    delete: (id: number) => `/customers/${id}`,
    search: '/customers/search',
    stats: '/customers/stats',
    import: '/customers/import',
    export: '/customers/export',
  },

  // 销售机会
  opportunities: {
    list: '/opportunities',
    detail: (id: number) => `/opportunities/${id}`,
    create: '/opportunities',
    update: (id: number) => `/opportunities/${id}`,
    delete: (id: number) => `/opportunities/${id}`,
    pipeline: '/opportunities/pipeline',
    forecast: '/opportunities/forecast',
    stats: '/opportunities/stats',
  },

  // 订单管理
  orders: {
    list: '/orders',
    detail: (id: number) => `/orders/${id}`,
    create: '/orders',
    update: (id: number) => `/orders/${id}`,
    delete: (id: number) => `/orders/${id}`,
    summary: '/orders/summary',
    stats: '/orders/stats',
    export: '/orders/export',
  },

  // 产品管理
  products: {
    list: '/products',
    detail: (code: string) => `/products/${code}`,
    create: '/products',
    update: (code: string) => `/products/${code}`,
    delete: (code: string) => `/products/${code}`,
    import: '/products/import',
    categories: '/products/categories',
    search: '/products/search',
    stats: '/products/stats',
  },

  // 联系记录
  contacts: {
    list: '/contacts',
    detail: (id: number) => `/contacts/${id}`,
    create: '/contacts',
    update: (id: number) => `/contacts/${id}`,
    delete: (id: number) => `/contacts/${id}`,
    recent: '/contacts/recent',
    upcoming: '/contacts/upcoming',
    stats: '/contacts/stats',
  },

  // 活动提醒
  activities: {
    list: '/activities',
    detail: (id: number) => `/activities/${id}`,
    create: '/activities',
    update: (id: number) => `/activities/${id}`,
    delete: (id: number) => `/activities/${id}`,
    upcoming: '/activities/upcoming',
    stats: '/activities/stats',
  },

  // 报表分析
  reports: {
    sales: '/reports/sales',
    customers: '/reports/customers',
    performance: '/reports/performance',
    export: '/reports/export',
  },

  // 系统管理
  system: {
    health: '/system/health',
    backup: '/system/backup',
    restore: '/system/restore',
    settings: '/system/settings',
    users: '/system/users',
    logs: '/system/logs',
  },

  // 仪表盘
  dashboard: {
    stats: '/dashboard/stats',
    overview: '/dashboard/overview',
    alerts: '/dashboard/alerts',
  },
};

export default apiService;
