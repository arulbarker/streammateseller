#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT AI Integration - OpenAI API
"""

import requests
import json
import logging
from typing import Optional, Dict, Any
from modules_client.config_manager import config_manager

logger = logging.getLogger('StreamMate')

class ChatGPTAI:
    """ChatGPT AI API client"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config_manager.get_api_key("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            logger.warning("OpenAI API key not found")
    
    def generate_reply(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """Generate AI reply using ChatGPT (synchronous version for PyQt compatibility)"""
        if not self.api_key:
            logger.error("OpenAI API key not available")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "Kamu adalah AI assistant yang membantu streamer untuk berinteraksi dengan penonton. Balas dengan natural, friendly, dan relevan."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result["choices"][0]["message"]["content"]
                logger.debug(f"ChatGPT reply generated: {len(reply)} chars")
                return reply
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating ChatGPT reply: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection (synchronous version for PyQt compatibility)"""
        try:
            if not self.api_key:
                return False
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"ChatGPT connection test failed: {e}")
            return False

# Global instance
chatgpt_ai = ChatGPTAI()

def generate_reply(prompt: str, max_tokens: int = 500) -> Optional[str]:
    """Generate AI reply using ChatGPT"""
    return chatgpt_ai.generate_reply(prompt, max_tokens)