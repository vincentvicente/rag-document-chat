import os
from typing import Optional
import PyPDF2
from PyPDF2 import PdfReader
import docx

# Parse file content
def parse_file(file_path: str, extension: str) -> str:
    try:
        extension = extension.lower()
        if extension == '.pdf':
            return parse_pdf(file_path)
        elif extension == '.docx':
            return parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    except Exception as e:
        print(f"Error parsing file: {str(e)}")
        raise Exception(f"Failed to parse file: {str(e)}")

# Parse PDF file - Improved version, inspired by AI Buddy project
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
                    print(f"Error parsing PDF page {page_num+1}: {str(e)}")
            
            # Join pages with triple newlines to help identify page boundaries in subsequent processing
            return '\n\n\n'.join(pages)
    except Exception as e:
        print(f"Error parsing PDF file: {str(e)}")
        raise e

# Parse DOCX file - Improved version
def parse_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        paragraphs = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)
        
        # Join paragraphs with double newlines for subsequent processing
        return '\n\n'.join(paragraphs)
    except Exception as e:
        print(f"Error parsing DOCX file: {str(e)}")
        raise e

