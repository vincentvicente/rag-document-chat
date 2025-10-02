// API客户端配置
const API_BASE_URL = 'http://localhost:3000/api';

// 文档相关API
export const documentApi = {
  // 上传文档
  async uploadDocument(file: File) {
    const formData = new FormData();
    formData.append('document', file);

    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    return await response.json();
  },

  // 获取所有文档
  async getAllDocuments() {
    const response = await fetch(`${API_BASE_URL}/documents`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch documents: ${response.status}`);
    }

    return await response.json();
  },

  // 获取单个文档
  async getDocument(id: string) {
    const response = await fetch(`${API_BASE_URL}/documents/${id}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch document: ${response.status}`);
    }

    return await response.json();
  },

  // 删除文档
  async deleteDocument(id: string) {
    const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete document: ${response.status}`);
    }

    return await response.json();
  }
};

// 查询相关API
export const queryApi = {
  // 发送查询
  async sendQuery(documentId: string | null, query: string) {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        documentId,
        query,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Query failed: ${response.status}`);
    }

    return await response.json();
  },

  // 获取查询历史
  async getQueryHistory() {
    const response = await fetch(`${API_BASE_URL}/query/history`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch query history: ${response.status}`);
    }

    return await response.json();
  }
};