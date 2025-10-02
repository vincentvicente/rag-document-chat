import React, { useState } from 'react';
import { DocumentUpload } from '../components/DocumentUpload';
import { DocumentChat } from '../components/DocumentChat';
import { DocumentList } from '../components/DocumentList';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";

export default function Rag() {
  const [refreshChat, setRefreshChat] = useState(0);
  const [refreshDocList, setRefreshDocList] = useState(0);

  const handleUploadSuccess = () => {
    // 上传成功后刷新聊天组件和文档列表
    setRefreshChat(prev => prev + 1);
    setRefreshDocList(prev => prev + 1);
  };

  const handleDocumentDeleted = () => {
    // 文档删除后刷新聊天组件
    setRefreshChat(prev => prev + 1);
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">RAG 文档问答系统</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1">
          <div className="space-y-6">
            <DocumentUpload onUploadSuccess={handleUploadSuccess} />
            
            <Tabs defaultValue="documents" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="documents">文档列表</TabsTrigger>
                <TabsTrigger value="history">查询历史</TabsTrigger>
              </TabsList>
              <TabsContent value="documents">
                <DocumentList 
                  key={refreshDocList} 
                  onDocumentDeleted={handleDocumentDeleted} 
                />
              </TabsContent>
              <TabsContent value="history">
                <div className="p-4 text-center text-gray-500 border rounded-lg">
                  查询历史功能即将推出
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
        
        <div className="md:col-span-2">
          <DocumentChat key={refreshChat} />
        </div>
      </div>
    </div>
  );
}