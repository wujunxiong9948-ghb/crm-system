import React, { useState, useRef } from 'react';
import { Button, Space, Upload, message, Modal } from 'antd';
import { DownloadOutlined, UploadOutlined, FileExcelOutlined } from '@ant-design/icons';
import { apiService } from '@/services/api';

interface ExportImportButtonsProps {
  module: 'customers' | 'opportunities' | 'orders' | 'products';
  searchParams?: Record<string, any>;
  onImportSuccess?: () => void;
}

const ExportImportButtons: React.FC<ExportImportButtonsProps> = ({
  module,
  searchParams = {},
  onImportSuccess
}) => {
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [importLoading, setImportLoading] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);
  const fileInputRef = useRef<any>(null);

  // 导出数据
  const handleExport = async () => {
    try {
      // 构建查询参数
      const params = new URLSearchParams();
      if (searchParams.keyword) {
        params.append('search', searchParams.keyword);
      }

      // 下载文件
      const response = await apiService.get(`/export/${module}?${params.toString()}`, {
        responseType: 'blob'
      });

      // 创建下载链接
      const blob = new Blob([response], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${module}_${new Date().getTime()}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.success('导出成功');
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败');
    }
  };

  // 下载模板
  const handleDownloadTemplate = async () => {
    try {
      const response = await apiService.get(`/export/${module}/template`, {
        responseType: 'blob'
      });

      const blob = new Blob([response], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${module}_template.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.success('模板下载成功');
    } catch (error) {
      console.error('下载模板失败:', error);
      message.error('下载模板失败');
    }
  };

  // 导入数据
  const handleImport = async (file: File) => {
    setImportLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiService.post(`/export/${module}/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setImportResult(response.data);
      message.success('导入完成');
      
      if (onImportSuccess) {
        onImportSuccess();
      }
    } catch (error: any) {
      console.error('导入失败:', error);
      message.error(error.message || '导入失败');
    } finally {
      setImportLoading(false);
    }
    return false; // 阻止默认上传
  };

  // 模块名称映射
  const moduleNames: Record<string, string> = {
    customers: '客户',
    opportunities: '销售机会',
    orders: '订单',
    products: '产品'
  };

  return (
    <>
      <Space>
        <Button
          icon={<DownloadOutlined />}
          onClick={handleExport}
        >
          导出Excel
        </Button>
        <Button
          icon={<UploadOutlined />}
          onClick={() => setImportModalVisible(true)}
        >
          批量导入
        </Button>
      </Space>

      {/* 导入弹窗 */}
      <Modal
        title={`导入${moduleNames[module]}`}
        open={importModalVisible}
        onCancel={() => {
          setImportModalVisible(false);
          setImportResult(null);
        }}
        footer={null}
      >
        <div style={{ padding: '20px 0' }}>
          <p>
            1. 先下载导入模板，按模板格式填写数据
            <Button type="link" onClick={handleDownloadTemplate}>
              下载模板
            </Button>
          </p>
          
          <p>2. 上传填写好的Excel文件</p>
          
          <Upload.Dragger
            name="file"
            accept=".xlsx,.xls"
            beforeUpload={handleImport}
            showUploadList={false}
            disabled={importLoading}
          >
            <p className="ant-upload-drag-icon">
              <FileExcelOutlined style={{ fontSize: 48, color: '#52c41a' }} />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
            <p className="ant-upload-hint">支持 .xlsx, .xls 格式</p>
          </Upload.Dragger>

          {/* 导入结果 */}
          {importResult && (
            <div style={{ marginTop: 20, padding: 16, background: '#f6ffed', borderRadius: 4 }}>
              <p><strong>导入结果：</strong></p>
              <p>成功：{importResult.success_count} 条</p>
              <p>失败：{importResult.error_count} 条</p>
              <p>总计：{importResult.total} 条</p>
              
              {importResult.errors && importResult.errors.length > 0 && (
                <div style={{ marginTop: 10 }}>
                  <p><strong>错误信息：</strong></p>
                  <ul style={{ color: '#ff4d4f', fontSize: 12 }}>
                    {importResult.errors.map((error: string, idx: number) => (
                      <li key={idx}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </Modal>
    </>
  );
};

export default ExportImportButtons;
