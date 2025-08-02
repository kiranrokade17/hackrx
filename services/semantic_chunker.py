import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class SemanticChunker:
    """
    Intelligent semantic chunking for RAG
    Creates meaningful chunks based on document structure and content
    """
    
    def __init__(self, chunk_size: int = 1500, overlap: int = 200, max_chunk_size: int = 20000):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.max_chunk_size = max_chunk_size  # Much smaller than Google API limit (36000 bytes)
    
    def chunk_document(self, text: str, document_type: str = "resume") -> List[Dict[str, Any]]:
        """
        Create semantic chunks based on document type and structure
        """
        try:
            # Force chunking for very large documents
            if len(text) > self.max_chunk_size:
                logger.info(f"Large document ({len(text)} chars) - forcing chunking")
                return self._force_chunk_large_document(text)
            
            if document_type.lower() == "resume":
                chunks = self._chunk_resume(text)
            else:
                chunks = self._chunk_generic_document(text)
            
            # Validate all chunks are within size limits
            validated_chunks = []
            for chunk in chunks:
                if len(chunk["content"]) > self.max_chunk_size:
                    # Split oversized chunks
                    sub_chunks = self._split_oversized_chunk(chunk)
                    validated_chunks.extend(sub_chunks)
                else:
                    validated_chunks.append(chunk)
            
            return validated_chunks
                
        except Exception as e:
            logger.error(f"Error in semantic chunking: {str(e)}")
            return self._fallback_chunking(text)
    
    def _chunk_resume(self, text: str) -> List[Dict[str, Any]]:
        """
        Smart resume chunking - preserves semantic sections
        """
        chunks = []
        
        # Common resume section patterns
        section_patterns = [
            r'(?i)(contact|personal)\s*(information|details)',
            r'(?i)(skills|technical\s*skills|competencies)',
            r'(?i)(work\s*experience|experience|employment)',
            r'(?i)(education|academic|qualifications)',
            r'(?i)(projects?|project\s*work)',
            r'(?i)(certifications?|awards?|achievements?)',
            r'(?i)(objective|summary|profile)'
        ]
        
        # Try to identify sections
        sections = self._identify_sections(text, section_patterns)
        
        if sections:
            # Create chunks based on identified sections
            for i, (section_name, section_text, start_pos) in enumerate(sections):
                chunk = {
                    "chunk_id": f"section_{i}",
                    "content": f"{section_name}\n{section_text}".strip(),
                    "metadata": {
                        "section_type": section_name.lower(),
                        "chunk_index": i,
                        "char_count": len(section_text),
                        "start_position": start_pos
                    }
                }
                chunks.append(chunk)
                logger.info(f"Created resume section chunk: {section_name} ({len(section_text)} chars)")
        else:
            # Fallback to paragraph-based chunking
            chunks = self._chunk_by_paragraphs(text)
        
        # Ensure we have the header/name info in first chunk
        header_chunk = self._extract_header_info(text)
        if header_chunk and chunks:
            chunks[0]["content"] = header_chunk + "\n\n" + chunks[0]["content"]
        
        return chunks
    
    def _identify_sections(self, text: str, patterns: List[str]) -> List[tuple]:
        """
        Identify document sections using patterns
        """
        sections = []
        text_lines = text.split('\n')
        current_section = None
        current_content = []
        
        for i, line in enumerate(text_lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check if this line matches a section header
            section_match = None
            for pattern in patterns:
                if re.search(pattern, line_stripped):
                    section_match = line_stripped
                    break
            
            if section_match:
                # Save previous section
                if current_section:
                    section_text = '\n'.join(current_content).strip()
                    if section_text:
                        sections.append((current_section, section_text, i - len(current_content)))
                
                # Start new section
                current_section = section_match
                current_content = []
            else:
                # Add to current section
                if current_section:
                    current_content.append(line_stripped)
        
        # Add final section
        if current_section and current_content:
            section_text = '\n'.join(current_content).strip()
            if section_text:
                sections.append((current_section, section_text, len(text_lines) - len(current_content)))
        
        return sections
    
    def _extract_header_info(self, text: str) -> str:
        """
        Extract name and contact info from document header
        """
        lines = text.split('\n')[:10]  # Look at first 10 lines
        header_content = []
        
        for line in lines:
            line = line.strip()
            if line and (
                # Likely to be name/contact info
                '@' in line or  # Email
                'linkedin' in line.lower() or  # LinkedIn
                'github' in line.lower() or   # GitHub  
                re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', line) or  # Name pattern
                re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line)  # Phone pattern
            ):
                header_content.append(line)
        
        return '\n'.join(header_content)
    
    def _chunk_by_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk by paragraphs with overlap
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                # Save current chunk
                chunk = {
                    "chunk_id": f"para_{chunk_index}",
                    "content": current_chunk.strip(),
                    "metadata": {
                        "chunk_index": chunk_index,
                        "char_count": len(current_chunk),
                        "chunk_type": "paragraph"
                    }
                }
                chunks.append(chunk)
                
                # Start new chunk with overlap
                words = current_chunk.split()
                overlap_words = words[-self.overlap//10:] if len(words) > self.overlap//10 else []
                current_chunk = ' '.join(overlap_words) + '\n\n' + para
                chunk_index += 1
            else:
                current_chunk += '\n\n' + para if current_chunk else para
        
        # Add final chunk
        if current_chunk.strip():
            chunk = {
                "chunk_id": f"para_{chunk_index}",
                "content": current_chunk.strip(),
                "metadata": {
                    "chunk_index": chunk_index,
                    "char_count": len(current_chunk),
                    "chunk_type": "paragraph"
                }
            }
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_generic_document(self, text: str) -> List[Dict[str, Any]]:
        """
        Generic document chunking strategy
        """
        return self._chunk_by_paragraphs(text)
    
    def _fallback_chunking(self, text: str) -> List[Dict[str, Any]]:
        """
        Simple fallback chunking if semantic chunking fails
        """
        chunks = []
        chunk_index = 0
        
        # Use smaller chunk size for fallback to ensure API compliance
        safe_chunk_size = min(self.chunk_size, 15000)  # Very conservative limit
        
        for i in range(0, len(text), safe_chunk_size - self.overlap):
            chunk_text = text[i:i + safe_chunk_size]
            
            # Ensure chunk is well under API limit (check byte size too)
            if len(chunk_text) > 15000 or len(chunk_text.encode('utf-8')) > 15000:
                chunk_text = chunk_text[:10000]  # Very safe limit
            
            chunk = {
                "chunk_id": f"fallback_{chunk_index}",
                "content": chunk_text,
                "metadata": {
                    "chunk_index": chunk_index,
                    "char_count": len(chunk_text),
                    "chunk_type": "fallback"
                }
            }
            chunks.append(chunk)
            chunk_index += 1
        
        logger.info(f"Fallback chunking created {len(chunks)} chunks")
        return chunks

    def _force_chunk_large_document(self, text: str) -> List[Dict[str, Any]]:
        """
        Force chunking for very large documents to ensure API compliance
        """
        chunks = []
        chunk_index = 0
        
        # Split into smaller manageable chunks
        safe_size = 10000  # Very conservative for large docs
        for i in range(0, len(text), safe_size - self.overlap):
            chunk_text = text[i:i + safe_size]
            
            # Ensure chunk is well under API limit
            if len(chunk_text.encode('utf-8')) > 15000:
                chunk_text = chunk_text[:8000]  # Extra safe limit
            
            chunk = {
                "chunk_id": f"large_doc_{chunk_index}",
                "content": chunk_text,
                "metadata": {
                    "chunk_index": chunk_index,
                    "char_count": len(chunk_text),
                    "chunk_type": "large_document"
                }
            }
            chunks.append(chunk)
            chunk_index += 1
            
            logger.info(f"Created large document chunk {chunk_index}: {len(chunk_text)} chars")
        
        return chunks

    def _split_oversized_chunk(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split a chunk that exceeds the maximum size limit
        """
        chunks = []
        content = chunk["content"]
        base_id = chunk["chunk_id"]
        
        # Split by sentences first, then by characters if needed
        sentences = re.split(r'[.!?]+', content)
        current_chunk = ""
        sub_chunk_index = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.max_chunk_size and current_chunk:
                # Save current sub-chunk
                sub_chunk = {
                    "chunk_id": f"{base_id}_part_{sub_chunk_index}",
                    "content": current_chunk.strip(),
                    "metadata": {
                        "chunk_index": sub_chunk_index,
                        "char_count": len(current_chunk),
                        "chunk_type": "split_chunk",
                        "parent_chunk": base_id
                    }
                }
                chunks.append(sub_chunk)
                current_chunk = sentence
                sub_chunk_index += 1
            else:
                current_chunk += sentence
        
        # Add final sub-chunk
        if current_chunk.strip():
            sub_chunk = {
                "chunk_id": f"{base_id}_part_{sub_chunk_index}",
                "content": current_chunk.strip(),
                "metadata": {
                    "chunk_index": sub_chunk_index,
                    "char_count": len(current_chunk),
                    "chunk_type": "split_chunk",
                    "parent_chunk": base_id
                }
            }
            chunks.append(sub_chunk)
        
        return chunks
