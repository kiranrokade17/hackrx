import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class LLMService:
    """Service for generating answers using Google Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-1.5-flash"  # Updated to current model
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model"""
        try:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info("Gemini model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise Exception(f"Failed to initialize Gemini model: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_answer(self, question: str, relevant_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate answer using Gemini based on question and relevant document chunks
        """
        try:
            # Prepare context from relevant chunks
            context = self._prepare_context(relevant_chunks)
            
            # Create prompt
            prompt = self._create_prompt(question, context)
            
            # Generate response
            logger.info(f"Generating answer for question: {question[:100]}...")
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                return "Unable to generate answer for this question."
            
            answer = response.text.strip()
            logger.info(f"Generated answer with {len(answer)} characters")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"Error generating answer: {str(e)}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_batch_answers(self, questions: List[str], relevant_chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Generate answers for multiple questions in a SINGLE API call
        This reduces API usage from N calls to 1 call for N questions
        """
        try:
            if not questions:
                return []
            
            # Prepare context from relevant chunks
            context = self._prepare_context(relevant_chunks)
            
            # Create batch prompt with all questions
            batch_prompt = self._create_batch_prompt(questions, context)
            
            # Single API call for all questions
            logger.info(f"Generating batch answers for {len(questions)} questions in ONE API call...")
            response = self.model.generate_content(batch_prompt)
            
            if not response or not response.text:
                return ["Unable to generate answer for this question." for _ in questions]
            
            # Parse the batch response into individual answers
            answers = self._parse_batch_response(response.text, len(questions))
            
            logger.info(f"Generated {len(answers)} answers using 1 API call (instead of {len(questions)} calls)")
            return answers
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            # Fallback to individual processing with delays
            return await self._fallback_individual_processing(questions, relevant_chunks)
    
    def _create_batch_prompt(self, questions: List[str], context: str) -> str:
        """
        Create a prompt to process multiple questions in one API call
        """
        questions_text = ""
        for i, question in enumerate(questions, 1):
            questions_text += f"{i}. {question}\n"
        
        batch_prompt = f"""You are an expert document analyst. Answer ALL the questions below based on the provided context.

INSTRUCTIONS:
1. Answer each question based STRICTLY on the provided context
2. Format your response as numbered answers: 1. [answer] 2. [answer] etc.
3. Keep answers concise but complete
4. If information is not available, state "Information not available in the document"
5. Maintain professional language appropriate for the domain

CONTEXT:
{context}

QUESTIONS:
{questions_text}

ANSWERS (respond with numbered format):"""

        return batch_prompt
    
    def _parse_batch_response(self, response_text: str, expected_count: int) -> List[str]:
        """
        Parse numbered responses from batch output into individual answers
        """
        import re
        
        answers = []
        
        # Split response into lines and look for numbered answers
        lines = response_text.strip().split('\n')
        current_answer = ""
        current_number = 0
        
        for line in lines:
            line = line.strip()
            
            # Check if line starts with a number (1., 2., 3., etc.)
            number_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if number_match:
                # Save previous answer if exists
                if current_answer:
                    answers.append(current_answer.strip())
                
                # Start new answer
                current_number = int(number_match.group(1))
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
            answers.append("Information not available in the document.")
        
        return answers[:expected_count]
    
    async def _fallback_individual_processing(self, questions: List[str], relevant_chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Fallback to individual processing with rate limiting if batch fails
        """
        import asyncio
        
        logger.warning("Batch processing failed, falling back to individual processing with delays")
        answers = []
        
        for i, question in enumerate(questions):
            try:
                # Add delay between requests to avoid rate limits
                if i > 0:
                    await asyncio.sleep(3)  # 3 second delay
                
                answer = await self.generate_answer(question, relevant_chunks)
                answers.append(answer)
                
            except Exception as e:
                logger.error(f"Error processing question {i+1}: {str(e)}")
                answers.append(f"Error processing question: {str(e)}")
        
        return answers
    
    def _prepare_context(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        """
        Prepare context from relevant document chunks
        """
        if not relevant_chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(relevant_chunks[:5]):  # Limit to top 5 chunks
            content = chunk.get("content", "")
            similarity = chunk.get("similarity_score", 0)
            
            context_parts.append(f"Context {i+1} (relevance: {similarity:.3f}):\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """
        Create a well-structured prompt for the LLM
        """
        prompt = f"""You are an expert document analyst specializing in insurance, legal, HR, and compliance domains. Your task is to answer questions based on the provided document context.

INSTRUCTIONS:
1. Analyze the context carefully and provide accurate, detailed answers
2. Base your response strictly on the information provided in the context
3. If the context doesn't contain enough information, state this clearly
4. Provide specific details, numbers, timeframes, and conditions when available
5. Use clear, professional language appropriate for the domain
6. If there are multiple relevant points, organize them logically

CONTEXT:
{context}

QUESTION: {question}

ANSWER: Please provide a comprehensive answer based on the context above."""

        return prompt
    
    async def summarize_document(self, document_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of the document
        """
        try:
            # Take first few chunks for summary
            summary_chunks = document_chunks[:3]
            context = self._prepare_context(summary_chunks)
            
            prompt = f"""Please provide a concise summary of this document, highlighting key points, policies, and important information:

{context}

Summary:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip() if response and response.text else "Unable to generate summary."
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def health_check(self) -> str:
        """Health check for LLM service"""
        try:
            if self.model is None:
                return "unhealthy - model not initialized"
            
            # Test with a simple prompt
            test_response = self.model.generate_content("Hello")
            return "healthy" if test_response else "unhealthy"
            
        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            return "unhealthy"
