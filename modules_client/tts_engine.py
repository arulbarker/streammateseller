#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamMate AI - Client-side TTS Engine
Wrapper for server-side TTS functionality
"""

import logging
from typing import Optional

# Import from server module
try:
    from modules_server.tts_engine import speak as server_speak, get_tts_engine
except ImportError:
    server_speak = None
    get_tts_engine = None

# Setup logging
logger = logging.getLogger('StreamMate')

def speak(text: str, language_code: str = "id-ID", voice_name: str = None, output_device=None, on_finished=None) -> bool:
    """Client-side speak function that delegates to server TTS"""
    if server_speak:
        return server_speak(text, language_code, voice_name, output_device, on_finished)
    else:
        logger.error("Server TTS engine not available")
        return False

def speak_text(text: str) -> bool:
    """Alias for speak function"""
    return speak(text)

# For compatibility with existing imports
if __name__ == "__main__":
    # Test the client TTS
    test_text = "Test dari client TTS engine."
    print(f"Testing client TTS with text: {test_text}")
    
    success = speak(test_text)
    print(f"Client TTS test {'successful' if success else 'failed'}")