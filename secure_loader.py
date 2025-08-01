#!/usr/bin/env python3
"""
Secure Configuration Loader
Loads and decrypts sensitive configuration data for the doctor appointment bot
"""

import os
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureConfigLoader:
    """Loads encrypted configuration securely"""
    
    def __init__(self, master_password="SecureDoctor2025!@#"):
        self.master_password = master_password
        self.config = {}
        self.load_config()
    
    def _generate_key_from_password(self, password):
        """Generate encryption key from master password"""
        password_bytes = password.encode()
        salt = b'salt_doctor_appointment_bot_2025'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def decrypt_file(self, encrypted_file_path):
        """Decrypt an encrypted file"""
        try:
            key = self._generate_key_from_password(self.master_password)
            cipher = Fernet(key)
            
            with open(encrypted_file_path, 'r') as f:
                encrypted_b64 = f.read()
            
            encrypted_data = base64.urlsafe_b64decode(encrypted_b64.encode())
            decrypted_data = cipher.decrypt(encrypted_data)
            
            return decrypted_data.decode()
        except Exception as e:
            print(f"❌ Failed to decrypt {encrypted_file_path}: {e}")
            return None
    
    def load_config(self):
        """Load configuration from various sources in priority order"""
        
        # 1. Try to load from Railway/Production environment variables
        if self._load_from_env_vars():
            print("✅ Loaded configuration from environment variables")
            return
        
        # 2. Try to load from encrypted files
        if self._load_from_encrypted_files():
            print("✅ Loaded configuration from encrypted files")
            return
        
        # 3. Try to load from backup location (development only)
        if self._load_from_backup():
            print("⚠️  Loaded configuration from backup files (development mode)")
            return
        
        raise ValueError("❌ Could not load configuration from any source")
    
    def _load_from_env_vars(self):
        """Load from environment variables (Railway deployment)"""
        try:
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
            google_creds = os.getenv('GOOGLE_CREDENTIALS')
            sheets_id = os.getenv('GOOGLE_SHEETS_ID')
            email_user = os.getenv('EMAIL_USER')
            email_password = os.getenv('EMAIL_PASSWORD')
            
            if telegram_token and sheets_id:
                self.config = {
                    'TELEGRAM_BOT_TOKEN': telegram_token,
                    'GOOGLE_CREDENTIALS': google_creds,
                    'GOOGLE_SHEETS_ID': sheets_id,
                    'EMAIL_USER': email_user or '',
                    'EMAIL_PASSWORD': email_password or '',
                    'GOOGLE_CREDENTIALS_FILE': os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
                }
                return True
        except Exception:
            pass
        return False
    
    def _load_from_encrypted_files(self):
        """Load from encrypted configuration files"""
        try:
            if not (os.path.exists('.env.encrypted') and os.path.exists('credentials.json.encrypted')):
                return False
            
            # Decrypt .env file
            env_content = self.decrypt_file('.env.encrypted')
            if not env_content:
                return False
            
            # Parse .env content
            env_vars = {}
            for line in env_content.strip().split('\n'):
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
            
            # Decrypt credentials.json
            creds_content = self.decrypt_file('credentials.json.encrypted')
            if not creds_content:
                return False
            
            self.config = {
                'TELEGRAM_BOT_TOKEN': env_vars.get('TELEGRAM_BOT_TOKEN', ''),
                'GOOGLE_CREDENTIALS': creds_content,
                'GOOGLE_SHEETS_ID': env_vars.get('GOOGLE_SHEETS_ID', ''),
                'EMAIL_USER': env_vars.get('EMAIL_USER', ''),
                'EMAIL_PASSWORD': env_vars.get('EMAIL_PASSWORD', ''),
                'GOOGLE_CREDENTIALS_FILE': 'credentials.json'
            }
            return True
        except Exception as e:
            print(f"❌ Failed to load encrypted config: {e}")
            return False
    
    def _load_from_backup(self):
        """Load from backup files (development only)"""
        try:
            env_path = '.sensitive_backup/.env'
            creds_path = '.sensitive_backup/credentials.json'
            
            if not (os.path.exists(env_path) and os.path.exists(creds_path)):
                return False
            
            # Read .env file
            with open(env_path, 'r') as f:
                env_content = f.read()
            
            # Parse .env content
            env_vars = {}
            for line in env_content.strip().split('\n'):
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
            
            # Read credentials file
            with open(creds_path, 'r') as f:
                creds_content = f.read()
            
            self.config = {
                'TELEGRAM_BOT_TOKEN': env_vars.get('TELEGRAM_BOT_TOKEN', ''),
                'GOOGLE_CREDENTIALS': creds_content,
                'GOOGLE_SHEETS_ID': env_vars.get('GOOGLE_SHEETS_ID', ''),
                'EMAIL_USER': env_vars.get('EMAIL_USER', ''),
                'EMAIL_PASSWORD': env_vars.get('EMAIL_PASSWORD', ''),
                'GOOGLE_CREDENTIALS_FILE': 'credentials.json'
            }
            return True
        except Exception:
            return False
    
    def get_config(self):
        """Get the loaded configuration"""
        return self.config
    
    def get(self, key, default=None):
        """Get a specific configuration value"""
        return self.config.get(key, default)

# Global instance
_secure_config = None

def get_secure_config():
    """Get the global secure configuration instance"""
    global _secure_config
    if _secure_config is None:
        _secure_config = SecureConfigLoader()
    return _secure_config

if __name__ == "__main__":
    # Test the loader
    try:
        config = SecureConfigLoader()
        print("🔐 Configuration loaded successfully!")
        print(f"📋 Available keys: {list(config.get_config().keys())}")
        
        # Test individual values (masked for security)
        telegram_token = config.get('TELEGRAM_BOT_TOKEN', '')
        if telegram_token:
            print(f"📱 Telegram token: {telegram_token[:10]}...{telegram_token[-10:]}")
        
        sheets_id = config.get('GOOGLE_SHEETS_ID', '')
        if sheets_id:
            print(f"📊 Google Sheets ID: {sheets_id[:10]}...{sheets_id[-10:]}")
            
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
