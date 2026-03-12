import React from 'react';
import { Spin, Space } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

interface LoadingSpinnerProps {
  fullScreen?: boolean;
  size?: 'small' | 'default' | 'large';
  tip?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  fullScreen = false,
  size = 'large',
  tip = '加载中...',
}) => {
  const spinner = (
    <Spin indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} size={size} tip={tip} />
  );

  if (fullScreen) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          backgroundColor: '#f5f5f5',
        }}
      >
        <Space direction="vertical" align="center" size="large">
          {spinner}
        </Space>
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '40px 20px',
      }}
    >
      <Space direction="vertical" align="center" size="large">
        {spinner}
      </Space>
    </div>
  );
};

export default LoadingSpinner;
