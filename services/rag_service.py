import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio

logger = logging.getLogger(__name__)

class RAGService:
    """
    Proper RAG (Retrieval-Augmented Generation) Service
    Implements two-phase approach: Indexing and Generation
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.embedding_model = "text-embedding-004"
        self.generation_model = "gemini-1.5-flash"
        self.genai_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize Google AI models for embedding and generation"""
        try:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=self.api_key)
            self.genai_model = genai.GenerativeModel(self.generation_model)
            logger.info("RAG models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG models: {str(e)}")
            raise Exception(f"Failed to initialize RAG models: {str(e)}")
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Phase 1: Create embeddings for text chunks using Google's embedding model
        """
        try:
            embeddings = []
            
            # Process in batches to avoid rate limits
            batch_size = 10
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                
                # Use Google's embedding model
                batch_embeddings = []
                for text in batch:
                    result = genai.embed_content(
                        model=f"models/{self.embedding_model}",
                        content=text,
                        task_type="retrieval_document"
                    )
                    batch_embeddings.append(result['embedding'])
                
                embeddings.extend(batch_embeddings)
                
                # Small delay to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            logger.info(f"Created {len(embeddings)} embeddings using {self.embedding_model}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise Exception(f"Failed to create embeddings: {str(e)}")
    
    async def create_query_embedding(self, query: str) -> List[float]:
        """
        Phase 2: Create embedding for the user's question
        """
        try:
            result = genai.embed_content(
                model=f"models/{self.embedding_model}",
                content=query,
                task_type="retrieval_query"
            )
            
            logger.info(f"Created query embedding for: {query[:50]}...")
            return result['embedding']
            
        except Exception as e:
            logger.error(f"Error creating query embedding: {str(e)}")
            raise Exception(f"Failed to create query embedding: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_answer(self, question: str, relevant_context: str) -> str:
        """
        Phase 2: Generate answer using only the retrieved relevant context
        """
        try:
            # Create focused RAG prompt for clean, concise answers
            prompt = f"""You are an AI assistant that provides clean, direct answers based ONLY on the provided context.

INSTRUCTIONS:
1. Answer the question using ONLY information from the context
2. Provide a clean, direct answer without extra formatting or bold text
3. Keep the answer concise but complete
4. Do not use markdown formatting, bullet points, or special characters
5. If the context doesn't contain the answer, say "This information is not available in the provided document"
6. Write in clear, plain text sentences

CONTEXT:
{relevant_context}

QUESTION: {question}

ANSWER:"""

            logger.info(f"Generating RAG answer for: {question[:50]}...")
            
            response = self.genai_model.generate_content(prompt)
            
            if not response or not response.text:
                return "Unable to generate answer for this question."
            
            answer = response.text.strip()
            
            # Clean up any remaining formatting
            answer = answer.replace("**", "").replace("*", "")
            answer = answer.replace("###", "").replace("##", "").replace("#", "")
            answer = answer.replace("- ", "").replace("• ", "")
            
            logger.info(f"Generated clean RAG answer with {len(answer)} characters")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating RAG answer: {str(e)}")
            return f"Error generating answer: {str(e)}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_batch_answers(self, questions: List[str], relevant_context: str) -> List[str]:
        """
        Generate answers for multiple questions in a SINGLE API call
        This reduces API usage from N calls to 1 call for N questions
        """
        try:
            if not questions:
                return []
            
            # Create batch prompt with all questions
            questions_text = ""
            for i, question in enumerate(questions, 1):
                questions_text += f"{i}. {question}\n"
            
            batch_prompt = f"""You are an AI assistant that provides clean, direct answers based ONLY on the provided context.

INSTRUCTIONS:
1. Answer ALL questions using ONLY information from the context
2. Format your response as numbered answers: 1. [answer] 2. [answer] etc.
3. Provide clean, direct answers without extra formatting or bold text
4. Keep answers concise but complete
5. Do not use markdown formatting, bullet points, or special characters
6. If the context doesn't contain the answer, say "This information is not available in the provided document"
7. Write in clear, plain text sentences

CONTEXT:
{relevant_context}

QUESTIONS:
{questions_text}

ANSWERS (respond with numbered format):"""

            logger.info(f"Generating batch RAG answers for {len(questions)} questions in ONE API call...")
            
            response = self.genai_model.generate_content(batch_prompt)
            
            if not response or not response.text:
                return ["Unable to generate answer for this question." for _ in questions]
            
            # Parse the batch response into individual answers
            answers = self._parse_batch_response(response.text, len(questions))
            
            # Clean up formatting for all answers
            cleaned_answers = []
            for answer in answers:
                cleaned_answer = answer.replace("**", "").replace("*", "")
                cleaned_answer = cleaned_answer.replace("###", "").replace("##", "").replace("#", "")
                cleaned_answer = cleaned_answer.replace("- ", "").replace("• ", "")
                cleaned_answers.append(cleaned_answer)
            
            logger.info(f"Generated {len(cleaned_answers)} clean RAG answers using 1 API call (instead of {len(questions)} calls)")
            return cleaned_answers
            
        except Exception as e:
            logger.error(f"Error in batch RAG processing: {str(e)}")
            # Fallback to individual processing with delays
            return await self._fallback_individual_processing(questions, relevant_context)
    
    def _parse_batch_response(self, response_text: str, expected_count: int) -> List[str]:
        """
        Parse numbered responses from batch output into individual answers
        """
        import re
        
        answers = []
        
        # Split response into lines and look for numbered answers
        lines = response_text.strip().split('\n')
        current_answer = ""
        
        for line in lines:
            line = line.strip()
            
            # Check if line starts with a number (1., 2., 3., etc.)
            number_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if number_match:
                # Save previous answer if exists
                if current_answer:
                    answers.append(current_answer.strip())
                
                # Start new answer
                current_answer = number_match.group(2)
            else:
                # Continue current answer
                if current_answer and line:
                    current_answer += " " + line
        
        # Add the last answer
        if current_answer:
            answers.append(current_answer.strip())
        
        # Ensure we have the right number of answers
        while len(answers) < expected_count:
            answers.append("This information is not available in the provided document.")
        
        return answers[:expected_count]
    
    async def _fallback_individual_processing(self, questions: List[str], relevant_context: str) -> List[str]:
        """
        Fallback to individual processing with rate limiting if batch fails
        """
        logger.warning("Batch RAG processing failed, falling back to individual processing with delays")
        answers = []
        
        for i, question in enumerate(questions):
            try:
                # Add delay between requests to avoid rate limits
                if i > 0:
                    await asyncio.sleep(3)  # 3 second delay
                
                answer = await self.generate_answer(question, relevant_context)
                answers.append(answer)
                
            except Exception as e:
                logger.error(f"Error processing question {i+1}: {str(e)}")
                answers.append(f"Error processing question: {str(e)}")
        
        return answers
    
    def health_check(self) -> str:
        """Health check for RAG service"""
        try:
            if self.genai_model is None:
                return "unhealthy - models not initialized"
            
            # Test with a simple prompt
            test_response = self.genai_model.generate_content("Test")
            return "healthy" if test_response else "unhealthy"
            
        except Exception as e:
            logger.error(f"RAG health check failed: {str(e)}")
            return "unhealthy"
