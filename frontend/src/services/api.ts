import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse } from '@/types';

// API配置 - 开发环境使用代理，生产环境使用完整URL
const isDevelopment = process.env.NODE_ENV === 'development';
const API_BASE_URL = isDevelopment ? '/api/v1' : 'http://localhost:5000/api/v1';
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
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.get<ApiResponse<T>>(url, config);
    return response.data as T;
  }

  // 通用POST请求
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.post<ApiResponse<T>>(url, data, config);
    return response.data as T;
  }

  // 通用PUT请求
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.put<ApiResponse<T>>(url, data, config);
    return response.data as T;
  }

  // 通用PATCH请求
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.patch<ApiResponse<T>>(url, data, config);
    return response.data as T;
  }

  // 通用DELETE请求
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.delete<ApiResponse<T>>(url, config);
    return response.data as T;
  }

  // 文件上传
  async uploadFile<T = any>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void,
    fieldName: string = 'file'
  ): Promise<T> {
    const formData = new FormData();
    formData.append(fieldName, file);

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

    const blob = new Blob([response as any]);
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
  getCurrentUser(): any {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  }

  // 设置当前用户信息
  setCurrentUser(userInfo: any): void {
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
    dashboard: '/reports/dashboard',
    sales: '/reports/sales',
    customers: '/reports/customers',
    products: '/reports/products',
    performance: '/reports/performance',
    export: '/reports/export',
  },

  // 系统设置
  settings: {
    // 用户管理
    users: '/settings/users',
    userDetail: (id: number) => `/settings/users/${id}`,
    resetPassword: (id: number) => `/settings/users/${id}/reset-password`,
    toggleUserStatus: (id: number) => `/settings/users/${id}/toggle-status`,

    // 角色权限
    roles: '/settings/roles',
    allRoles: '/settings/roles/all',
    roleDetail: (id: number) => `/settings/roles/${id}`,
    permissions: '/settings/permissions',
    permissionModules: '/settings/permissions/modules',

    // 公司信息
    company: '/settings/company',
    companyLogo: '/settings/company/logo',

    // 业务字典
    dictionaries: '/settings/dictionaries',
    dictionaryTypes: '/settings/dictionaries/types',
    dictionariesByType: '/settings/dictionaries/by-type',
    dictionaryDetail: (id: number) => `/settings/dictionaries/${id}`,
    batchDictionaries: '/settings/dictionaries/batch',

    // 操作日志
    logs: '/settings/logs',
    logDetail: (id: number) => `/settings/logs/${id}`,
    logActions: '/settings/logs/actions',
    logModules: '/settings/logs/modules',
    clearLogs: '/settings/logs/clear',
    exportLogs: '/settings/logs/export',

    // 个人设置
    profile: '/settings/profile',
    changePassword: '/settings/profile/password',
    uploadAvatar: '/settings/profile/avatar',

    // 通知设置
    notificationSettings: '/settings/notification-settings',
    testNotification: '/settings/notification-settings/test',
  },

  // 仪表盘
  dashboard: {
    stats: '/dashboard/stats',
    overview: '/dashboard/overview',
    alerts: '/dashboard/alerts',
  },
};

// 用户管理API
export const userApi = {
  getUsers: (params?: any) => apiService.get(apiEndpoints.settings.users, { params }),
  getUser: (id: number) => apiService.get(apiEndpoints.settings.userDetail(id)),
  createUser: (data: any) => apiService.post(apiEndpoints.settings.users, data),
  updateUser: (id: number, data: any) => apiService.put(apiEndpoints.settings.userDetail(id), data),
  deleteUser: (id: number) => apiService.delete(apiEndpoints.settings.userDetail(id)),
  resetPassword: (id: number, data?: any) => apiService.post(apiEndpoints.settings.resetPassword(id), data || {}),
  toggleUserStatus: (id: number) => apiService.post(apiEndpoints.settings.toggleUserStatus(id)),
  getAllRoles: () => apiService.get(apiEndpoints.settings.allRoles),
};

// 角色权限API
export const roleApi = {
  getRoles: (params?: any) => apiService.get(apiEndpoints.settings.roles, { params }),
  getRole: (id: number) => apiService.get(apiEndpoints.settings.roleDetail(id)),
  createRole: (data: any) => apiService.post(apiEndpoints.settings.roles, data),
  updateRole: (id: number, data: any) => apiService.put(apiEndpoints.settings.roleDetail(id), data),
  deleteRole: (id: number) => apiService.delete(apiEndpoints.settings.roleDetail(id)),
  getPermissions: () => apiService.get(apiEndpoints.settings.permissions),
  getPermissionModules: () => apiService.get(apiEndpoints.settings.permissionModules),
};

// 公司信息API
export const companyApi = {
  getCompanyInfo: () => apiService.get(apiEndpoints.settings.company),
  updateCompanyInfo: (data: any) => apiService.put(apiEndpoints.settings.company, data),
};

// 业务字典API
export const dictionaryApi = {
  getDictionaries: (params?: any) => apiService.get(apiEndpoints.settings.dictionaries, { params }),
  getDictionaryTypes: () => apiService.get(apiEndpoints.settings.dictionaryTypes),
  getDictionariesByType: () => apiService.get(apiEndpoints.settings.dictionariesByType),
  createDictionary: (data: any) => apiService.post(apiEndpoints.settings.dictionaries, data),
  updateDictionary: (id: number, data: any) => apiService.put(apiEndpoints.settings.dictionaryDetail(id), data),
  deleteDictionary: (id: number) => apiService.delete(apiEndpoints.settings.dictionaryDetail(id)),
  batchCreateDictionaries: (data: any) => apiService.post(apiEndpoints.settings.batchDictionaries, data),
};

// 操作日志API
export const logApi = {
  getLogs: (params?: any) => apiService.get(apiEndpoints.settings.logs, { params }),
  getLog: (id: number) => apiService.get(apiEndpoints.settings.logDetail(id)),
  getLogActions: () => apiService.get(apiEndpoints.settings.logActions),
  getLogModules: () => apiService.get(apiEndpoints.settings.logModules),
  clearLogs: (data: any) => apiService.post(apiEndpoints.settings.clearLogs, data),
  exportLogs: (params?: any) => {
    const queryString = params ? '?' + new URLSearchParams(params).toString() : '';
    window.open(`${API_BASE_URL}${apiEndpoints.settings.exportLogs}${queryString}`, '_blank');
  },
};

// 个人设置API
export const profileApi = {
  getProfile: () => apiService.get(apiEndpoints.settings.profile),
  updateProfile: (data: any) => apiService.put(apiEndpoints.settings.profile, data),
  changePassword: (data: any) => apiService.put(apiEndpoints.settings.changePassword, data),
};

// 通知设置API
export const notificationApi = {
  getSettings: () => apiService.get(apiEndpoints.settings.notificationSettings),
  updateSettings: (data: any) => apiService.put(apiEndpoints.settings.notificationSettings, data),
  testNotification: (channel: string) => apiService.post(apiEndpoints.settings.testNotification, { channel }),
};

export default apiService;
