// 权限码定义 - 与后端数据库保持一致
export const PERMISSION_CODES = {
  // 客户权限
  CUSTOMER_VIEW: 'customer:view',
  CUSTOMER_CREATE: 'customer:create',
  CUSTOMER_UPDATE: 'customer:update',
  CUSTOMER_DELETE: 'customer:delete',
  CUSTOMER_EXPORT: 'customer:export',
  CUSTOMER_IMPORT: 'customer:import',
  // 机会权限
  OPPORTUNITY_VIEW: 'opportunity:view',
  OPPORTUNITY_CREATE: 'opportunity:create',
  OPPORTUNITY_UPDATE: 'opportunity:update',
  OPPORTUNITY_DELETE: 'opportunity:delete',
  OPPORTUNITY_TRANSFER: 'opportunity:transfer',
  OPPORTUNITY_EXPORT: 'opportunity:export',
  // 订单权限
  ORDER_VIEW: 'order:view',
  ORDER_CREATE: 'order:create',
  ORDER_UPDATE: 'order:update',
  ORDER_DELETE: 'order:delete',
  ORDER_APPROVE: 'order:approve',
  ORDER_EXPORT: 'order:export',
  // 产品权限
  PRODUCT_VIEW: 'product:view',
  PRODUCT_CREATE: 'product:create',
  PRODUCT_UPDATE: 'product:update',
  PRODUCT_DELETE: 'product:delete',
  // 报表权限
  REPORT_VIEW: 'report:view',
  REPORT_EXPORT: 'report:export',
  // 系统权限
  USER_MANAGE: 'user:manage',
  ROLE_MANAGE: 'role:manage',
  SETTINGS_MANAGE: 'settings:manage',
  LOG_VIEW: 'log:view',
} as const;

// 各角色的权限码列表 - 与数据库保持一致
export const ROLE_PERMISSIONS: Record<string, string[]> = {
  admin: ['*'], // 管理员拥有所有权限
  manager: [
    // 客户权限
    'customer:view', 'customer:create', 'customer:update', 'customer:export',
    // 机会权限
    'opportunity:view', 'opportunity:create', 'opportunity:update', 'opportunity:delete', 'opportunity:transfer', 'opportunity:export',
    // 订单权限
    'order:view', 'order:create', 'order:update', 'order:export',
    // 产品权限
    'product:view',
    // 报表权限
    'report:view', 'report:export',
    // 系统权限
    'log:view',
  ],
  sales: [
    // 客户权限 - 无 delete, import
    'customer:view', 'customer:create', 'customer:update', 'customer:export',
    // 机会权限 - 无 delete, transfer
    'opportunity:view', 'opportunity:create', 'opportunity:update', 'opportunity:export',
    // 订单权限 - 无 update, delete, approve
    'order:view', 'order:create', 'order:export',
    // 产品权限 - 只有 view
    'product:view',
    // 报表权限 - 只有 view
    'report:view',
  ],
  user: [
    // 最小权限
    'customer:view',
    'opportunity:view',
    'product:view',
  ],
};

// 权限配置 - 定义各角色可访问的菜单
export const PERMISSION_CONFIG = {
  // 管理员 - 拥有所有权限
  admin: {
    allowedMenus: ['*'], // * 表示所有菜单
    allowedPaths: ['*'],
  },
  // 经理 - 可以查看大部分功能，但不能管理系统设置
  manager: {
    allowedMenus: [
      '/dashboard',
      '/customers',
      '/opportunities',
      '/opportunities/new',
      '/opportunities/pipeline',
      '/orders',
      '/orders/new',
      '/products',
      '/contacts',
      '/contacts/calendar',
      '/reports',
      '/reports/sales',
      '/reports/customers',
      '/reports/products',
      '/settings/profile',
      '/settings/notifications',
    ],
    allowedPaths: [
      '/dashboard',
      '/customers',
      '/opportunities',
      '/orders',
      '/products',
      '/contacts',
      '/reports',
      '/settings/profile',
      '/settings/notifications',
    ],
  },
  // 销售 - 只能查看和操作自己的数据
  sales: {
    allowedMenus: [
      '/dashboard',
      '/customers',
      '/opportunities',
      '/opportunities/new',
      '/opportunities/pipeline',
      '/orders',
      '/orders/new',
      '/products',
      '/contacts',
      '/contacts/calendar',
      '/reports',
      '/settings/profile',
      '/settings/notifications',
    ],
    allowedPaths: [
      '/dashboard',
      '/customers',
      '/opportunities',
      '/orders',
      '/products',
      '/contacts',
      '/reports',
      '/settings/profile',
      '/settings/notifications',
    ],
  },
  // 普通用户 - 最小权限
  user: {
    allowedMenus: [
      '/dashboard',
      '/customers',
      '/opportunities',
      '/products',
      '/contacts',
      '/settings/profile',
      '/settings/notifications',
    ],
    allowedPaths: [
      '/dashboard',
      '/customers',
      '/opportunities',
      '/products',
      '/contacts',
      '/settings/profile',
      '/settings/notifications',
    ],
  },
};

// 菜单显示模式：'hide' - 完全隐藏, 'disabled' - 显示但禁用
export type MenuDisplayMode = 'hide' | 'disabled';

// 权限检查工具类
export class PermissionChecker {
  private _userRole: string;
  private _permissions: string[];

  constructor(userRole: string = 'user', permissions?: string[]) {
    this._userRole = userRole || 'user';
    this._permissions = permissions || ROLE_PERMISSIONS[this._userRole] || ROLE_PERMISSIONS.user;
  }

  // 获取用户角色
  get userRole(): string {
    return this._userRole;
  }

  // 获取用户权限列表
  get permissions(): string[] {
    return this._permissions;
  }

  // 检查是否有特定权限码
  hasPermissionCode(permissionCode: string): boolean {
    // 管理员拥有所有权限
    if (this._permissions.includes('*')) return true;
    return this._permissions.includes(permissionCode);
  }

  // 检查是否有权限访问指定路径
  hasPermission(path: string): boolean {
    const config = PERMISSION_CONFIG[this._userRole as keyof typeof PERMISSION_CONFIG];
    if (!config) return false;

    // 管理员拥有所有权限
    if (config.allowedPaths.includes('*')) return true;

    // 检查路径是否匹配
    return config.allowedPaths.some(allowedPath => {
      // 精确匹配
      if (allowedPath === path) return true;
      // 前缀匹配（用于父菜单）
      if (path.startsWith(allowedPath + '/')) return true;
      return false;
    });
  }

  // 检查菜单项是否应该显示
  shouldShowMenu(menuKey: string): boolean {
    const config = PERMISSION_CONFIG[this._userRole as keyof typeof PERMISSION_CONFIG];
    if (!config) return false;

    // 管理员显示所有菜单
    if (config.allowedMenus.includes('*')) return true;

    return config.allowedMenus.includes(menuKey);
  }

  // 获取过滤后的菜单项
  filterMenuItems(menuItems: any[]): any[] {
    return menuItems
      .map(item => {
        // 检查当前菜单项
        if (!this.shouldShowMenu(item.key)) {
          return null;
        }

        // 如果有子菜单，递归过滤
        if (item.children && item.children.length > 0) {
          const filteredChildren = this.filterMenuItems(item.children);
          if (filteredChildren.length === 0) {
            // 如果所有子菜单都被隐藏，且父菜单本身也不是独立页面，则隐藏父菜单
            // 但保留一些重要的父菜单（如系统设置）
            if (item.key === '/settings') {
              return { ...item, children: [] };
            }
            return null;
          }
          return { ...item, children: filteredChildren };
        }

        return item;
      })
      .filter(Boolean) as any[];
  }

  // 检查是否显示无权限提示（用于无法隐藏的独立功能）
  shouldShowNoPermission(path: string): boolean {
    return !this.hasPermission(path);
  }

  // 获取用户角色显示名称
  getRoleDisplayName(): string {
    const roleNames: Record<string, string> = {
      admin: '管理员',
      manager: '经理',
      sales: '销售',
      user: '普通用户',
    };
    return roleNames[this._userRole] || '未知角色';
  }
}

// 创建权限检查器实例的工厂函数
export const createPermissionChecker = (userRole?: string, permissions?: string[]): PermissionChecker => {
  // 如果没有提供角色，尝试从 localStorage 获取
  if (!userRole) {
    try {
      const userInfo = localStorage.getItem('user_info');
      if (userInfo) {
        const parsed = JSON.parse(userInfo);
        userRole = parsed.role;
        permissions = parsed.permissions;
      }
    } catch {
      // 解析失败，使用默认角色
    }
  }
  return new PermissionChecker(userRole, permissions);
};

// 权限相关的工具钩子（用于 React 组件）
export const usePermission = (userRole?: string, permissions?: string[]) => {
  const checker = createPermissionChecker(userRole, permissions);
  
  return {
    hasPermission: (path: string) => checker.hasPermission(path),
    hasPermissionCode: (code: string) => checker.hasPermissionCode(code),
    shouldShowMenu: (menuKey: string) => checker.shouldShowMenu(menuKey),
    filterMenuItems: (items: any[]) => checker.filterMenuItems(items),
    shouldShowNoPermission: (path: string) => checker.shouldShowNoPermission(path),
    getRoleDisplayName: () => checker.getRoleDisplayName(),
    role: checker.userRole,
    permissions: checker.permissions,
  };
};

export default PermissionChecker;
