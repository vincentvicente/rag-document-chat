import os
from typing import Optional
import PyPDF2
from PyPDF2 import PdfReader
import docx

# 解析文件内容
def parse_file(file_path: str, extension: str) -> str:
    try:
        extension = extension.lower()
        if extension == '.pdf':
            return parse_pdf(file_path)
        elif extension == '.docx':
            return parse_docx(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {extension}")
    except Exception as e:
        print(f"解析文件时出错: {str(e)}")
        raise Exception(f"解析文件失败: {str(e)}")

# 解析PDF文件 - 改进版，借鉴AI Buddy项目的方法
def parse_pdf(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            pages = []
            
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        pages.append(page_text)
                except Exception as e:
                    print(f"解析PDF第{page_num+1}页时出错: {str(e)}")
            
            # 将页面用三个换行符连接，便于后续处理时识别页面边界
            return '\n\n\n'.join(pages)
    except Exception as e:
        print(f"解析PDF文件时出错: {str(e)}")
        raise e

# 解析DOCX文件 - 改进版
def parse_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        paragraphs = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)
        
        # 将段落用双换行符连接，便于后续处理
        return '\n\n'.join(paragraphs)
    except Exception as e:
        print(f"解析DOCX文件时出错: {str(e)}")
        raise e

