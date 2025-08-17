#!/usr/bin/env python3
"""
Test script untuk debug masalah force close saat trigger
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_deepseek_api():
    """Test DeepSeek API secara langsung"""
    print("\n=== Testing DeepSeek API ===")
    try:
        from modules_client.deepseek_ai import generate_reply as deepseek_generate
        
        test_prompt = "Penonton TestUser bertanya: halo bang apa kabar?"
        print(f"Testing with prompt: {test_prompt}")
        
        result = deepseek_generate(test_prompt)
        print(f"DeepSeek Result: {result}")
        return result is not None
        
    except Exception as e:
        print(f"DeepSeek Error: {e}")
        traceback.print_exc()
        return False

def test_chatgpt_api():
    """Test ChatGPT API secara langsung"""
    print("\n=== Testing ChatGPT API ===")
    try:
        from modules_client.chatgpt_ai import generate_reply as chatgpt_generate
        
        test_prompt = "Penonton TestUser bertanya: halo bang apa kabar?"
        print(f"Testing with prompt: {test_prompt}")
        
        result = chatgpt_generate(test_prompt)
        print(f"ChatGPT Result: {result}")
        return result is not None
        
    except Exception as e:
        print(f"ChatGPT Error: {e}")
        traceback.print_exc()
        return False

def test_api_bridge():
    """Test API bridge generate_reply function"""
    print("\n=== Testing API Bridge ===")
    try:
        from modules_client.api import generate_reply
        
        test_prompt = "Penonton TestUser bertanya: halo bang apa kabar?"
        print(f"Testing with prompt: {test_prompt}")
        
        result = generate_reply(test_prompt)
        print(f"API Bridge Result: {result}")
        return result is not None
        
    except Exception as e:
        print(f"API Bridge Error: {e}")
        traceback.print_exc()
        return False

def test_reply_thread_simulation():
    """Simulasi ReplyThread tanpa PyQt"""
    print("\n=== Testing ReplyThread Simulation ===")
    try:
        from modules_client.api import generate_reply
        
        # Simulate ReplyThread parameters
        author = "TestUser"
        message = "halo bang apa kabar?"
        
        # Build prompt like ReplyThread does
        prompt = (
            f"Kamu adalah AI Co-Host yang sedang live streaming YouTube Live. "
            f"Penonton {author} bertanya: '{message}'. "
            f"Sapa {author} dengan ramah. "
            f"Awali dengan nama {author}. "
            f"Jawab dalam Bahasa Indonesia maksimal 2 kalimat pendek. "
            f"Gaya santai tanpa emoji berlebihan. "
        )
        
        print(f"Full prompt: {prompt}")
        
        reply = generate_reply(prompt)
        print(f"Reply Thread Simulation Result: {reply}")
        
        if not reply:
            print("No reply received, using fallback")
            reply = f"Hai {author} sorry koneksi bermasalah"
        
        print(f"Final reply: {reply}")
        return True
        
    except Exception as e:
        print(f"Reply Thread Simulation Error: {e}")
        traceback.print_exc()
        return False

def test_config_loading():
    """Test loading konfigurasi"""
    print("\n=== Testing Config Loading ===")
    try:
        from modules_client.config_manager import ConfigManager
        
        cfg = ConfigManager()
        ai_provider = cfg.get("ai_provider", "deepseek")
        api_keys = cfg.get("api_keys", {})
        
        print(f"AI Provider: {ai_provider}")
        print(f"Available API Keys: {list(api_keys.keys())}")
        
        deepseek_key = api_keys.get("DEEPSEEK_API_KEY")
        openai_key = api_keys.get("OPENAI_API_KEY")
        
        print(f"DeepSeek Key: {'✅ Available' if deepseek_key else '❌ Missing'}")
        print(f"OpenAI Key: {'✅ Available' if openai_key else '❌ Missing'}")
        
        return True
        
    except Exception as e:
        print(f"Config Loading Error: {e}")
        traceback.print_exc()
        return False

def main():
    print("🔍 StreamMate AI Trigger Debug Test")
    print("=" * 50)
    
    # Test 1: Config loading
    config_ok = test_config_loading()
    
    # Test 2: API Bridge
    api_bridge_ok = test_api_bridge()
    
    # Test 3: DeepSeek API
    deepseek_ok = test_deepseek_api()
    
    # Test 4: ChatGPT API
    chatgpt_ok = test_chatgpt_api()
    
    # Test 5: ReplyThread simulation
    reply_thread_ok = test_reply_thread_simulation()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Config Loading: {'✅' if config_ok else '❌'}")
    print(f"API Bridge: {'✅' if api_bridge_ok else '❌'}")
    print(f"DeepSeek API: {'✅' if deepseek_ok else '❌'}")
    print(f"ChatGPT API: {'✅' if chatgpt_ok else '❌'}")
    print(f"ReplyThread Simulation: {'✅' if reply_thread_ok else '❌'}")
    
    if all([config_ok, api_bridge_ok, reply_thread_ok]):
        print("\n🎉 All core tests passed! The issue might be in PyQt event loop interaction.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()