#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk menguji API DeepSeek, OpenAI, dan TTS
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Tambahkan path modules_client ke sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules_client'))

try:
    from deepseek_ai import DeepSeekAI
    from chatgpt_ai import ChatGPTAI
except ImportError as e:
    print(f"Error importing AI modules: {e}")
    sys.exit(1)

def load_config():
    """Load konfigurasi dari settings.json"""
    config_path = Path(__file__).parent / 'config' / 'settings.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

async def test_deepseek_api(config):
    """Test API DeepSeek"""
    print("\n=== Testing DeepSeek API ===")
    try:
        api_key = config['api_keys']['DEEPSEEK_API_KEY']
        if not api_key or api_key == 'your_deepseek_api_key_here':
            print("❌ DeepSeek API key tidak ditemukan atau masih placeholder")
            return False
            
        deepseek = DeepSeekAI()
        
        # Test koneksi
        print("Testing connection...")
        test_result = deepseek.test_connection()
        if test_result:
            print("✅ DeepSeek API connection: SUCCESS")
        else:
            print("❌ DeepSeek API connection: FAILED")
            return False
            
        # Test generate reply
        print("Testing generate reply...")
        response = deepseek.generate_reply("Halo, apa kabar?")
        if response and response.strip():
            print(f"✅ DeepSeek Response: {response[:100]}...")
            return True
        else:
            print("❌ DeepSeek returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek API Error: {e}")
        return False

async def test_openai_api(config):
    """Test API OpenAI"""
    print("\n=== Testing OpenAI API ===")
    try:
        api_key = config['api_keys']['OPENAI_API_KEY']
        if not api_key or api_key == 'your_openai_api_key_here':
            print("❌ OpenAI API key tidak ditemukan atau masih placeholder")
            return False
            
        openai_ai = ChatGPTAI(api_key)
        
        # Test koneksi
        print("Testing connection...")
        test_result = await openai_ai.test_connection()
        if test_result:
            print("✅ OpenAI API connection: SUCCESS")
        else:
            print("❌ OpenAI API connection: FAILED")
            return False
            
        # Test generate reply
        print("Testing generate reply...")
        response = await openai_ai.generate_reply("Halo, apa kabar?")
        if response and response.strip():
            print(f"✅ OpenAI Response: {response[:100]}...")
            return True
        else:
            print("❌ OpenAI returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return False

def test_tts_config(config):
    """Test konfigurasi TTS"""
    print("\n=== Testing TTS Configuration ===")
    try:
        # Cek apakah ada konfigurasi TTS
        tts_voice = config.get('cohost_voice_model', '')
        if tts_voice:
            print(f"✅ TTS Voice Model: {tts_voice}")
        else:
            print("❌ TTS Voice Model tidak ditemukan")
            return False
            
        # Cek Google TTS credentials jika ada
        gcloud_creds_path = Path(__file__).parent / 'config' / 'gcloud_tts_credentials.json'
        if gcloud_creds_path.exists():
            print("✅ Google TTS credentials file found")
            try:
                with open(gcloud_creds_path, 'r') as f:
                    creds = json.load(f)
                    # Check for OAuth credentials format
                    if creds.get('installed') and creds['installed'].get('client_id'):
                        print("✅ Google TTS credentials valid format (OAuth)")
                    # Check for service account format
                    elif creds.get('type') == 'service_account':
                        print("✅ Google TTS credentials valid format (Service Account)")
                    else:
                        print("❌ Google TTS credentials invalid format")
                        return False
            except Exception as e:
                print(f"❌ Error reading Google TTS credentials: {e}")
                return False
        else:
            print("⚠️  Google TTS credentials file not found (using default TTS)")
            
        return True
        
    except Exception as e:
        print(f"❌ TTS Configuration Error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting API Tests...")
    
    # Load config
    config = load_config()
    if not config:
        print("❌ Failed to load configuration")
        return
        
    print(f"✅ Configuration loaded successfully")
    print(f"Current AI Provider: {config.get('ai_provider', 'not set')}")
    
    # Test results
    results = {
        'deepseek': False,
        'openai': False,
        'tts': False
    }
    
    # Test APIs
    results['deepseek'] = await test_deepseek_api(config)
    results['openai'] = await test_openai_api(config)
    results['tts'] = test_tts_config(config)
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service.upper()}: {'PASS' if status else 'FAIL'}")
    
    all_passed = all(results.values())
    print(f"\n🎯 Overall Status: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Semua API dan konfigurasi berfungsi dengan baik!")
    else:
        print("\n⚠️  Beberapa API atau konfigurasi perlu diperbaiki.")

if __name__ == "__main__":
    asyncio.run(main())