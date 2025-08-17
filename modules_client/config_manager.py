"""
Config Manager - Updated to use Supabase for configuration
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('StreamMate')

class ConfigManager:
    """Configuration manager with Supabase integration"""
    
    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = Path(config_file)
        self.supabase_config = None
        self._load_supabase_config()
        
    def _load_supabase_config(self):
        """Load Supabase configuration"""
        try:
            supabase_config_file = Path("config/supabase_config.json")
            if supabase_config_file.exists():
                with open(supabase_config_file, 'r', encoding='utf-8') as f:
                    self.supabase_config = json.load(f)
                logger.info("Supabase config loaded")
            else:
                logger.warning("Supabase config file not found")
        except Exception as e:
            logger.error(f"Error loading Supabase config: {e}")
    
    def get_api_key(self, key_name: str) -> Optional[str]:
        """Get API key from Supabase or fallback to local config"""
        try:
            # Try to get from Supabase first
            if self.supabase_config:
                from modules_client.supabase_config_client import config_client
                api_key = config_client.get_api_key(key_name)
                if api_key:
                    logger.debug(f"Got {key_name} from Supabase")
                    return api_key
        except Exception as e:
            logger.warning(f"Failed to get {key_name} from Supabase: {e}")
        
        # Fallback to local config
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Check in various possible locations
                if key_name in config:
                    return config[key_name]
                elif 'api_keys' in config and key_name in config['api_keys']:
                    return config['api_keys'][key_name]
                elif 'credentials' in config and key_name in config['credentials']:
                    return config['credentials'][key_name]
                    
        except Exception as e:
            logger.error(f"Error getting {key_name} from local config: {e}")
        
        return None
    
    def get_payment_config(self, provider: str, config_key: str) -> Optional[str]:
        """Get payment configuration from Supabase"""
        try:
            if self.supabase_config:
                from modules_client.supabase_config_client import config_client
                return config_client.get_payment_config(provider, config_key)
        except Exception as e:
            logger.warning(f"Failed to get payment config {provider}.{config_key}: {e}")
        return None
    
    def get_server_config(self, config_key: str) -> Optional[str]:
        """Get server configuration from Supabase"""
        try:
            if self.supabase_config:
                from modules_client.supabase_config_client import config_client
                return config_client.get_server_config(config_key)
        except Exception as e:
            logger.warning(f"Failed to get server config {config_key}: {e}")
        return None
    
    def get_google_credentials(self, credential_type: str) -> Optional[Dict[str, Any]]:
        """Get Google credentials from Supabase"""
        try:
            if self.supabase_config:
                from modules_client.supabase_config_client import config_client
                return config_client.get_google_credentials(credential_type)
        except Exception as e:
            logger.warning(f"Failed to get Google credentials {credential_type}: {e}")
        return None
    
    def load_settings(self) -> Dict[str, Any]:
        """Load all settings with Supabase integration"""
        settings = {}
        
        # Load local settings first
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except Exception as e:
                logger.error(f"Error loading local settings: {e}")
        
        # Override with Supabase configs
        try:
            if self.supabase_config:
                from modules_client.supabase_config_client import config_client
                
                # Get API keys
                api_keys = {}
                for key_name in ['DEEPSEEK_API_KEY', 'YOUTUBE_API_KEY', 'TRAKTEER_API_KEY', 'TR_API_KEY']:
                    api_key = config_client.get_api_key(key_name)
                    if api_key:
                        api_keys[key_name] = api_key
                
                if api_keys:
                    settings['api_keys'] = api_keys
                
                # Get payment config
                ipaymu_config = config_client.get_ipaymu_config()
                if ipaymu_config:
                    settings['ipaymu_config'] = ipaymu_config
                
                # Get server config
                environment = config_client.get_environment()
                if environment:
                    settings['environment'] = environment
                
                debug_mode = config_client.is_debug_mode()
                settings['debug_mode'] = debug_mode
                
                safety_mode = config_client.is_safety_mode()
                settings['safety_mode'] = safety_mode
                
        except Exception as e:
            logger.warning(f"Error loading Supabase settings: {e}")
        
        return settings
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        settings = self.load_settings()
        return settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value (local only for now)"""
        try:
            settings = self.load_settings()
            settings[key] = value
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Error setting config {key}: {e}")
            return False
    
    def save(self) -> bool:
        """Save current settings"""
        try:
            settings = self.load_settings()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

# Global instance
config_manager = ConfigManager()

