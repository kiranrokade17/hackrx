import aiofiles
import requests
import tempfile
import os
import logging
from typing import List, Dict, Any
import PyPDF2
from docx import Document
from io import BytesIO
import re

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing documents from URLs"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc']
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200  # overlap between chunks
    
    async def process_document(self, document_url: str) -> str:
        """
        Download and extract text from document URL or local file path
        """
        try:
            logger.info(f"Processing document from URL: {document_url}")
            
            # Check if it's a local file URL or path
            if document_url.startswith('file:///') or (os.path.exists(document_url) and not document_url.startswith('http')):
                # Handle file:/// URLs
                if document_url.startswith('file:///'):
                    # Convert file:/// URL to local path
                    file_path = document_url.replace('file:///', '')
                    # Handle Windows drive letters (e.g., file:///C:/path -> C:/path)
                    if len(file_path) > 1 and file_path[1] == ':':
                        file_path = file_path
                    else:
                        file_path = '/' + file_path
                else:
                    # Direct file path
                    file_path = document_url
                
                logger.info(f"Processing local file: {file_path}")
                
                # Read local file
                with open(file_path, 'rb') as file:
                    content = file.read()
                
                # Determine file type from extension
                if file_path.lower().endswith('.pdf'):
                    text = self._extract_text_from_pdf(content)
                elif file_path.lower().endswith(('.docx', '.doc')):
                    text = self._extract_text_from_docx(content)
                else:
                    # Try to read as text file
                    text = content.decode('utf-8', errors='ignore')
                    
            else:
                # Download document from URL
                response = requests.get(document_url, timeout=30)
                response.raise_for_status()
                
                # Determine file type from URL or content-type
                content_type = response.headers.get('content-type', '').lower()
                
                if 'pdf' in content_type or document_url.lower().endswith('.pdf'):
                    text = self._extract_text_from_pdf(response.content)
                elif 'word' in content_type or document_url.lower().endswith(('.docx', '.doc')):
                    text = self._extract_text_from_docx(response.content)
                else:
                    # Try to extract as text
                    text = response.text
            
            logger.info(f"Extracted {len(text)} characters from document")
            return text
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise Exception(f"Failed to process document: {str(e)}")
    
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX content"""
        try:
            docx_file = BytesIO(content)
            doc = Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    
    async def chunk_document(self, text: str) -> List[Dict[str, Any]]:
        """
        Split document into chunks for embedding
        """
        try:
            # Clean the text
            text = self._clean_text(text)
            
            chunks = []
            words = text.split()
            
            current_chunk = ""
            chunk_id = 0
            
            for word in words:
                if len(current_chunk) + len(word) + 1 <= self.chunk_size:
                    current_chunk += " " + word if current_chunk else word
                else:
                    if current_chunk:
                        chunks.append({
                            "chunk_id": f"chunk_{chunk_id}",
                            "content": current_chunk.strip(),
                            "metadata": {
                                "chunk_index": chunk_id,
                                "char_count": len(current_chunk)
                            }
                        })
                        chunk_id += 1
                    
                    # Start new chunk with overlap
                    overlap_words = current_chunk.split()[-self.chunk_overlap//10:] if current_chunk else []
                    current_chunk = " ".join(overlap_words + [word])
            
            # Add the last chunk
            if current_chunk:
                chunks.append({
                    "chunk_id": f"chunk_{chunk_id}",
                    "content": current_chunk.strip(),
                    "metadata": {
                        "chunk_index": chunk_id,
                        "char_count": len(current_chunk)
                    }
                })
            
            logger.info(f"Created {len(chunks)} chunks from document")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking document: {str(e)}")
            raise Exception(f"Failed to chunk document: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        
        return text.strip()
    
    def health_check(self) -> str:
        """Health check for document processor"""
        return "healthy"
