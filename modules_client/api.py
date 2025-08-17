#!/usr/bin/env python3
"""
API Bridge untuk StreamMate AI Client
Menghubungkan aplikasi client dengan server VPS untuk AI processing
"""

import json
import requests
import logging
import os
from modules_client.config_manager import ConfigManager
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class APIClient:
    """API Client - SUPABASE ONLY MODE"""
    SUPABASE_ONLY = True
    VPS_DISABLED = True
    def __init__(self):
        self.cfg = ConfigManager()
        # SUPABASE ONLY MODE - No VPS dependencies
        self.base_url = "supabase_backend"
        print(f"[API] SUPABASE ONLY MODE: Using Supabase backend")
        
        self.timeout = 30
        
    def _get_server_url(self):
        """SUPABASE ONLY MODE: Use Supabase backend"""
        return "supabase_backend"
    
    def _make_request(self, endpoint, data, timeout=None):
        """Make request dengan error handling"""
        if timeout is None:
            timeout = self.timeout
            
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError:
            if self.base_url == "https://api.streammateai.com":
                # Production server down, fallback ke localhost
                logger.warning("Production server unavailable, trying localhost...")
                self.base_url = "supabase_backend"
                return self._make_request(endpoint, data, timeout)
            else:
                raise
    
    def generate_reply(self, prompt: str) -> str:
        """Generate AI reply melalui server"""
        try:
            response = self._make_request("ai_reply", {"text": prompt})
            return response.json().get("reply", "")
        except Exception as e:
            logger.error(f"AI API failed: {e}")
            # Fallback untuk developer mode saja
            if "localhost" in self.base_url:
                try:
                    from modules_server.deepseek_ai import generate_reply as local_gen
                    logger.info("Using local DeepSeek fallback")
                    return local_gen(prompt)
                except Exception as local_error:
                    logger.error(f"Local fallback failed: {local_error}")
            
            return "Maaf, sistem AI sedang dalam maintenance"

# Global instance
_api_client = APIClient()

# Export functions
def generate_reply(prompt: str) -> str:
    return _api_client.generate_reply(prompt)

def get_server_info():
    """Info server yang sedang digunakan (untuk debugging)"""
    return {
        "server_url": _api_client.base_url,
        "mode": "development" if "localhost" in _api_client.base_url else "production"
    }

class APIBridge:
    """Bridge untuk komunikasi dengan Supabase server"""
    
    def __init__(self):
        # Initialize server URLs first
        self.vps_server = "supabase_backend"
        self.local_server = "http://localhost:8888"
        self.active_server = self._get_active_server()
        
        # Import Supabase client
        try:
            from modules_client.supabase_client import get_supabase_client
            self.supabase_client = get_supabase_client()
            self.use_supabase = True
            print("[API] Using Supabase backend")
        except ImportError:
            # Fallback to VPS server if Supabase not available
            self.use_supabase = False
            print("[API] Using VPS backend (fallback)")
        
    def _get_active_server(self):
        """Test koneksi server dan return yang aktif"""
        # Test VPS server dulu
        try:
            response = requests.get(f"{self.vps_server}/api/health", timeout=3)
            if response.status_code == 200:
                print(f"[API] VPS server active: {self.vps_server}")
                return self.vps_server
        except Exception:
            pass
        
        # Test local server
        try:
            response = requests.get(f"{self.local_server}/api/health", timeout=10)
            if response.status_code == 200:
                print(f"[API] Local server active: {self.local_server}")
                return self.local_server
        except Exception:
            pass
        
        # Default ke VPS jika keduanya gagal
        print(f"[API] No server responded, defaulting to VPS: {self.vps_server}")
        return self.vps_server

# Global API bridge instance
api_bridge = APIBridge()

def generate_reply(prompt: str, timeout: int = 30) -> str:
    """
    Generate AI reply using Supabase with VPS fallback
    
    Args:
        prompt: User prompt for AI
        timeout: Request timeout in seconds
        
    Returns:
        AI generated reply string, or fallback response if failed
    """
    print(f"[API] generate_reply called with prompt length: {len(prompt)}")
    
    # Method 1: Try DeepSeek API directly (preferred for basic mode)
    try:
        print(f"[API] Trying DeepSeek AI endpoint...")
        from modules_client.deepseek_ai import generate_reply as deepseek_generate
        reply = deepseek_generate(prompt)
        if reply and len(reply.strip()) > 0:
            print(f"[API] DeepSeek AI success: {len(reply)} chars")
            return reply
        else:
            print(f"[API] DeepSeek AI returned empty reply")
    except Exception as e:
        print(f"[API] DeepSeek AI error: {e}")
    
    # Method 2: Try Supabase API (fallback)
    if api_bridge.use_supabase:
        try:
            print(f"[API] Trying Supabase AI endpoint...")
            reply = api_bridge.supabase_client.generate_ai_reply(prompt, timeout)
            if reply and len(reply.strip()) > 0:
                print(f"[API] Supabase AI success: {len(reply)} chars")
                return reply
            else:
                print(f"[API] Supabase AI returned empty reply")
        except Exception as e:
            print(f"[API] Supabase AI error: {e}")
    
    # Method 3: Try VPS API endpoint (fallback) - SKIP INVALID URLs
    if api_bridge.active_server and api_bridge.active_server.startswith(("http://", "https://")):
        try:
            print(f"[API] Trying VPS API endpoint...")
            
            response = requests.post(
                f"{api_bridge.active_server}/api/ai/generate",
                json={"prompt": prompt},
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle FastAPI response format
                if result.get("status") == "success" and "data" in result:
                    reply = result["data"].get("reply", "").strip()
                    if reply:
                        print(f"[API] VPS API success: {len(reply)} chars")
                        return reply
                
                # Handle old format (fallback)
                elif "reply" in result:
                    reply = result.get("reply", "").strip()
                    if reply:
                        print(f"[API] VPS API success (old format): {len(reply)} chars")
                        return reply
                
                print(f"[API] VPS API returned empty reply")
                
            else:
                print(f"[API] VPS API error: {response.status_code}")
                if response.status_code == 404:
                    print(f"[API] Endpoint /api/ai/generate not found on server")
                try:
                    error_detail = response.json()
                    print(f"[API] Error detail: {error_detail}")
                except:
                    print(f"[API] Error response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"[API] VPS API request failed: {e}")
        except Exception as e:
            print(f"[API] VPS API unexpected error: {e}")
    else:
        print(f"[API] Skipping VPS API (invalid URL: {api_bridge.active_server})")
    
    # Method 1.5: Try existing /api/ai/reply endpoint as fallback
    if api_bridge.active_server and api_bridge.active_server.startswith(("http://", "https://")):
        try:
            print(f"[API] Trying existing /api/ai/reply endpoint...")
            
            response = requests.post(
                f"{api_bridge.active_server}/api/ai/reply",
                json={"text": prompt},  # Different format for existing endpoint
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle various response formats
                reply = ""
                if "data" in result and isinstance(result["data"], dict):
                    reply = result["data"].get("reply", "").strip()
                elif "reply" in result:
                    reply = result.get("reply", "").strip()
                elif "data" in result and isinstance(result["data"], str):
                    reply = result["data"].strip()
                
                if reply:
                    print(f"[API] Existing endpoint success: {len(reply)} chars")
                    return reply
                else:
                    print(f"[API] Existing endpoint returned empty reply")
                    
            else:
                print(f"[API] Existing endpoint error: {response.status_code}")
                
        except Exception as e:
            print(f"[API] Existing endpoint error: {e}")
    else:
        print(f"[API] Skipping existing endpoint (invalid URL: {api_bridge.active_server})")
    
    # Method 2: Try direct DeepSeek API if local API key available
    try:
        print(f"[API] Trying direct DeepSeek API...")
        
        # Check if we have local API key from config or env
        from modules_client.config_manager import ConfigManager
        cfg = ConfigManager()
        deepseek_key = cfg.get("api_keys", {}).get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key and len(deepseek_key) > 10:
            print(f"[API] Using local DeepSeek API key...")
            
            headers = {
                "Authorization": f"Bearer {deepseek_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.8,
                "top_p": 0.95,
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result["choices"][0]["message"]["content"].strip()
                if reply:
                    # Clean reply for safe encoding
                    try:
                        reply_clean = reply.encode('utf-8', errors='replace').decode('utf-8')
                        print(f"[API] Direct DeepSeek success: {len(reply_clean)} chars")
                        return reply_clean
                    except Exception as enc_error:
                        print(f"[API] Encoding fix failed: {enc_error}")
                        return reply
            else:
                print(f"[API] Direct DeepSeek error: {response.status_code}")
                
        else:
            print(f"[API] No local DeepSeek API key found")
            
    except Exception as e:
        print(f"[API] Direct DeepSeek API error: {e}")
    
    # Method 3: Fallback response
    print(f"[API] All methods failed, using fallback response")
    return _get_fallback_response(prompt)

def _get_fallback_response(prompt: str) -> str:
    """Generate enhanced fallback response when AI API fails"""
    prompt_lower = prompt.lower()
    
    # Extract author name from prompt if possible
    author = "teman"
    if "penonton" in prompt and "bertanya" in prompt:
        # Try to extract author name from typical prompt format
        import re
        author_match = re.search(r'Penonton (\w+) bertanya', prompt)
        if author_match:
            author = author_match.group(1)
    
    # Enhanced rule-based responses for gaming context
    if any(word in prompt_lower for word in ["halo", "hai", "hello", "hi"]):
        responses = [
            f"Hai {author}! Lagi push rank nih, gimana kabarmu?",
            f"Halo {author}! Welcome to stream, lagi main MOBA nih",
            f"Hai {author}! Thanks udah join stream, enjoy ya!"
        ]
        import random
        return random.choice(responses)
    
    elif any(word in prompt_lower for word in ["kabar", "apa kabar", "gimana"]):
        responses = [
            f"Baik {author}! Lagi semangat push rank, kamu gimana?",
            f"Alhamdulillah baik {author}, lagi fokus main nih",
            f"Baik dong {author}, lagi grinding rank soalnya hehe"
        ]
        import random
        return random.choice(responses)
    
    elif any(word in prompt_lower for word in ["build", "item", "gear", "equipment"]):
        responses = [
            f"{author} untuk build sekarang meta damage penetration dulu bro",
            f"Build {author}? War axe, hunter strike, malefic roar meta banget",
            f"{author} coba build damage dulu, nanti tank item terakhir"
        ]
        import random
        return random.choice(responses)
    
    elif any(word in prompt_lower for word in ["rank", "ranking", "tier", "main"]):
        responses = [
            f"{author} lagi push rank nih, target mythic season ini",
            f"Rank {author}? Lagi di legend, target mythic nih",
            f"{author} main rank yuk, butuh duo partner nih"
        ]
        import random
        return random.choice(responses)
    
    elif any(word in prompt_lower for word in ["hero", "champion", "character"]):
        responses = [
            f"{author} hero favorit gue Layla, damage nya gila sih",
            f"Hero {author}? Coba main marksman, enak buat carry",
            f"{author} hero meta sekarang assassin sama marksman"
        ]
        import random
        return random.choice(responses)
    
    elif any(word in prompt_lower for word in ["makan", "udah makan", "lunch", "dinner"]):
        responses = [
            f"Udah makan {author}, sekarang lagi fokus main nih",
            f"{author} udah makan dong, kamu jangan lupa makan ya",
            f"Alhamdulillah udah makan {author}, energy full buat main"
        ]
        import random
        return random.choice(responses)
    
    elif any(word in prompt_lower for word in ["col", "bang"]):
        responses = [
            f"Iya {author}! Ada yang bisa gue bantu?",
            f"Hai {author}! Gimana ada pertanyaan?",
            f"Yes {author}! Mau tanya apa nih?"
        ]
        import random
        return random.choice(responses)
    
    else:
        # General responses
        responses = [
            f"Hai {author}! Thanks udah nonton stream",
            f"{author} ada yang mau ditanyain tentang game?",
            f"Halo {author}! Enjoy streamnya ya, jangan lupa follow",
            f"{author} gimana pendapat kamu tentang gameplay tadi?",
            f"Thanks {author}! Semoga terhibur sama streamnya"
        ]
        import random
        return random.choice(responses)

def test_api_connection():
    """Test API connection and return status"""
    results = {
        "vps_server": False,
        "local_server": False,
        "deepseek_direct": False,
        "active_server": None
    }
    
    # Test VPS server
    try:
        response = requests.get(f"{api_bridge.vps_server}/api/health", timeout=3)
        results["vps_server"] = response.status_code == 200
    except:
        pass
    
    # Test local server  
    try:
        response = requests.get(f"{api_bridge.local_server}/api/health", timeout=10)
        results["local_server"] = response.status_code == 200
    except:
        pass
    
    # Test direct DeepSeek
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key and len(deepseek_key) > 10:
        try:
            headers = {"Authorization": f"Bearer {deepseek_key}"}
            response = requests.get("https://api.deepseek.com/v1/models", headers=headers, timeout=5)
            results["deepseek_direct"] = response.status_code == 200
        except:
            pass
    
    results["active_server"] = api_bridge.active_server
    return results

if __name__ == "__main__":
    # Test script
    print("Testing API connections...")
    status = test_api_connection()
    
    print("\n=== API Connection Status ===")
    print(f"VPS Server (69.62.79.238): {'✅' if status['vps_server'] else '❌'}")
    print(f"Local Server (localhost:8888): {'✅' if status['local_server'] else '❌'}")
    print(f"Direct DeepSeek API: {'✅' if status['deepseek_direct'] else '❌'}")
    print(f"Active Server: {status['active_server']}")
    
    # Test generate_reply
    print("\n=== Testing AI Generation ===")
    test_prompt = "Penonton TestUser bertanya: halo bang apa kabar?"
    result = generate_reply(test_prompt)
    print(f"Test Result: {result}")
