import React from 'react';
import { Button, Result, Space } from 'antd';
import { HomeOutlined, ReloadOutlined } from '@ant-design/icons';

interface ErrorFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetErrorBoundary }) => {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5',
        padding: '20px',
      }}
    >
      <Result
        status="error"
        title="应用发生错误"
        subTitle={
          <div style={{ textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>
            <p>我们很抱歉，应用遇到了一个错误。错误信息如下：</p>
            <pre
              style={{
                backgroundColor: '#f0f0f0',
                padding: '15px',
                borderRadius: '4px',
                overflow: 'auto',
                fontSize: '12px',
                margin: '10px 0',
              }}
            >
              {error.message}
            </pre>
            <p>如果问题持续存在，请联系技术支持。</p>
          </div>
        }
        extra={
          <Space>
            <Button
              type="primary"
              icon={<HomeOutlined />}
              onClick={() => (window.location.href = '/')}
            >
              返回首页
            </Button>
            <Button icon={<ReloadOutlined />} onClick={resetErrorBoundary}>
              重试
            </Button>
            <Button
              type="dashed"
              onClick={() => {
                if (window.location.href.includes('localhost')) {
                  window.location.reload();
                }
              }}
            >
              刷新页面
            </Button>
          </Space>
        }
      />
    </div>
  );
};

export default ErrorFallback;
