import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { documentApi } from '../lib/api';
import { Trash2 } from "lucide-react";
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "./ui/alert-dialog";

interface Document {
  id: number;
  originalName: string;
  uploadDate: string;
  previewText: string;
}

interface DocumentListProps {
  onDocumentDeleted?: () => void;
}

export function DocumentList({ onDocumentDeleted }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 获取所有文档
  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const docs = await documentApi.getAllDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      setError('获取文档列表失败');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  // 删除文档
  const handleDeleteDocument = async (id: number) => {
    try {
      await documentApi.deleteDocument(id.toString());
      setDocuments(documents.filter(doc => doc.id !== id));
      
      if (onDocumentDeleted) {
        onDocumentDeleted();
      }
    } catch (error) {
      console.error('Failed to delete document:', error);
      setError('删除文档失败');
    }
  };

  // 格式化日期
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>文档列表</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-4">加载中...</div>
        ) : error ? (
          <div className="text-center text-red-500 py-4">{error}</div>
        ) : documents.length === 0 ? (
          <div className="text-center text-gray-500 py-4">暂无文档</div>
        ) : (
          <div className="space-y-4">
            {documents.map((doc) => (
              <div 
                key={doc.id} 
                className="p-4 border rounded-lg flex justify-between items-center"
              >
                <div>
                  <h3 className="font-medium">{doc.originalName}</h3>
                  <p className="text-sm text-gray-500">
                    上传时间: {formatDate(doc.uploadDate)}
                  </p>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                    {doc.previewText}
                  </p>
                </div>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>确认删除</AlertDialogTitle>
                      <AlertDialogDescription>
                        您确定要删除文档 "{doc.originalName}" 吗？此操作无法撤销。
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>取消</AlertDialogCancel>
                      <AlertDialogAction 
                        onClick={() => handleDeleteDocument(doc.id)}
                      >
                        删除
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}


