"""Gemini AI LLM client"""
import logging
import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from config.settings import LOG_LEVEL

logger = logging.getLogger(__name__)


class GeminiLLMClient:
    """Client for interacting with Gemini AI"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize Gemini LLM client
        
        Args:
            api_key: Google AI API key (defaults to GEMINI_API_KEY env var)
            model_name: Model name (default: gemini-2.0-flash-exp)
        """
        from config.settings import GEMINI_API_KEY, GEMINI_MODEL
        
        self.api_key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name or GEMINI_MODEL or "gemini-2.0-flash-exp"
        self.model = genai.GenerativeModel(self.model_name)
        
        logger.info(f"Initialized Gemini LLM client with model: {self.model_name}")
    
    def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Generate response from Gemini
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        try:
            generation_config = {
                "temperature": temperature,
            }
            
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating response from Gemini: {e}")
            raise
    
    def generate_structured_response(self, prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Generate structured response (JSON-like)
        
        Args:
            prompt: Input prompt with JSON format instructions
            temperature: Lower temperature for more deterministic output
            
        Returns:
            Parsed response as dictionary
        """
        try:
            # Add JSON format instruction
            json_prompt = f"{prompt}\n\nRespond in valid JSON format only."
            
            response_text = self.generate_response(json_prompt, temperature=temperature)
            
            # Try to extract JSON from response
            import json
            import re
            
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Try parsing entire response as JSON
                return json.loads(response_text)
                
        except Exception as e:
            logger.error(f"Error generating structured response: {e}")
            logger.debug(f"Response text: {response_text}")
            raise

