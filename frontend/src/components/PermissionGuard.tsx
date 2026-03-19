import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Modal, Result, Button } from 'antd';
import { createPermissionChecker } from '../utils/permission';
import { apiService } from '../services/api';

interface PermissionGuardProps {
  children: React.ReactNode;
  requiredRole?: string[];
}

// 权限守卫组件
export const PermissionGuard: React.FC<PermissionGuardProps> = ({ 
  children, 
  requiredRole 
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [userRole, setUserRole] = useState<string>('');

  useEffect(() => {
    const checkPermission = () => {
      // 获取当前用户信息
      const userInfo = apiService.getCurrentUser();
      if (!userInfo) {
        setHasPermission(false);
        return;
      }

      const role = userInfo.role || 'user';
      setUserRole(role);

      // 如果指定了需要的角色，检查是否匹配
      if (requiredRole && requiredRole.length > 0) {
        if (!requiredRole.includes(role)) {
          setHasPermission(false);
          return;
        }
      }

      // 使用权限检查器检查路径权限
      const checker = createPermissionChecker(role);
      const allowed = checker.hasPermission(location.pathname);
      setHasPermission(allowed);
    };

    checkPermission();
  }, [location.pathname, requiredRole]);

  if (hasPermission === null) {
    // 加载中
    return null;
  }

  if (!hasPermission) {
    const checker = createPermissionChecker(userRole);
    
    return (
      <Result
        status="403"
        title="403"
        subTitle={
          <div>
            <p>抱歉，您没有权限访问此页面</p>
            <p style={{ color: '#999', fontSize: '14px' }}>
              当前角色：{checker.getRoleDisplayName()}
            </p>
          </div>
        }
        extra={
          <Button type="primary" onClick={() => navigate('/dashboard')}>
            返回首页
          </Button>
        }
      />
    );
  }

  return <>{children}</>;
};

// 权限检查 Hook
export const useRoutePermission = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const checkPermission = (path?: string): boolean => {
    const userInfo = apiService.getCurrentUser();
    if (!userInfo) return false;

    const checker = createPermissionChecker(userInfo.role);
    const targetPath = path || location.pathname;
    const hasPerm = checker.hasPermission(targetPath);

    if (!hasPerm) {
      Modal.error({
        title: '无权限',
        content: `您的角色 [${checker.getRoleDisplayName()}] 没有权限执行此操作`,
        okText: '确定',
      });
    }

    return hasPerm;
  };

  const navigateIfAllowed = (path: string) => {
    if (checkPermission(path)) {
      navigate(path);
      return true;
    }
    return false;
  };

  return { checkPermission, navigateIfAllowed };
};

export default PermissionGuard;
