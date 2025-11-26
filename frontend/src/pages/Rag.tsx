import React, { useState } from 'react';
import { DocumentUpload } from '../components/DocumentUpload';
import { DocumentChat } from '../components/DocumentChat';
import { DocumentList } from '../components/DocumentList';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";

export default function Rag() {
  const [refreshChat, setRefreshChat] = useState(0);
  const [refreshDocList, setRefreshDocList] = useState(0);

  const handleUploadSuccess = () => {
    // Refresh chat component and document list after successful upload
    setRefreshChat(prev => prev + 1);
    setRefreshDocList(prev => prev + 1);
  };

  const handleDocumentDeleted = () => {
    // Refresh chat component after document deletion
    setRefreshChat(prev => prev + 1);
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">RAG Document Q&A System</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1">
          <div className="space-y-6">
            <DocumentUpload onUploadSuccess={handleUploadSuccess} />
            
            <Tabs defaultValue="documents" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="documents">Documents</TabsTrigger>
                <TabsTrigger value="history">Query History</TabsTrigger>
              </TabsList>
              <TabsContent value="documents">
                <DocumentList 
                  key={refreshDocList} 
                  onDocumentDeleted={handleDocumentDeleted} 
                />
              </TabsContent>
              <TabsContent value="history">
                <div className="p-4 text-center text-gray-500 border rounded-lg">
                  Query history feature coming soon
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