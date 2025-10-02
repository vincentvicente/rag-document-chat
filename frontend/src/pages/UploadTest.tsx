import React, { useState } from 'react';
import { documentApi } from '../lib/api';

export default function UploadTest() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError(null);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('请选择文件');
      return;
    }

    setIsUploading(true);
    setError(null);
    setResult(null);

    try {
      const response = await documentApi.uploadDocument(file);
      setResult(response);
      console.log('上传成功:', response);
    } catch (err) {
      console.error('上传失败:', err);
      setError(`上传失败: ${err instanceof Error ? err.message : '未知错误'}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">文件上传测试</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">选择文件 (PDF/DOCX)</label>
          <input
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={handleFileChange}
            className="border border-gray-300 p-2 w-full rounded"
          />
        </div>
        
        <button
          onClick={handleUpload}
          disabled={isUploading || !file}
          className={`px-4 py-2 rounded ${
            isUploading || !file
              ? 'bg-gray-300 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          {isUploading ? '上传中...' : '上传文件'}
        </button>
        
        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
        
        {result && (
          <div className="mt-4">
            <h2 className="text-xl font-semibold mb-2">上传成功</h2>
            <pre className="bg-gray-100 p-3 rounded overflow-auto max-h-60">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}


