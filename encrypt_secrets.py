#!/usr/bin/env python3
"""
Secure Encryption Utility for Sensitive Data
Encrypts sensitive data like API keys, tokens, and credentials
"""

import base64
import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass


class SecureDataManager:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self, master_password: str = None):
        if master_password is None:
            master_password = getpass.getpass("Enter master password for encryption: ")
        
        # Generate a key from the master password
        self.key = self._generate_key_from_password(master_password)
        self.cipher = Fernet(self.key)
    
    def _generate_key_from_password(self, password: str) -> bytes:
        """Generate encryption key from master password"""
        password_bytes = password.encode()
        salt = b'salt_doctor_appointment_bot_2025'  # Fixed salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def encrypt_dict(self, data_dict: dict) -> dict:
        """Encrypt all values in a dictionary"""
        encrypted_dict = {}
        for key, value in data_dict.items():
            if isinstance(value, str):
                encrypted_dict[key] = self.encrypt_data(value)
            else:
                encrypted_dict[key] = value
        return encrypted_dict
    
    def decrypt_dict(self, encrypted_dict: dict) -> dict:
        """Decrypt all values in a dictionary"""
        decrypted_dict = {}
        for key, value in encrypted_dict.items():
            if isinstance(value, str) and key in ['TELEGRAM_BOT_TOKEN', 'GOOGLE_CREDENTIALS', 'GOOGLE_SHEETS_ID']:
                try:
                    decrypted_dict[key] = self.decrypt_data(value)
                except:
                    decrypted_dict[key] = value  # If decryption fails, keep original
            else:
                decrypted_dict[key] = value
        return decrypted_dict


def create_encrypted_env_file():
    """Create encrypted environment file"""
    print("🔐 Creating encrypted environment configuration...")
    
    # Get sensitive data from user
    telegram_token = getpass.getpass("Enter Telegram Bot Token: ")
    google_sheets_id = getpass.getpass("Enter Google Sheets ID: ")
    google_credentials = getpass.getpass("Enter Google Credentials JSON (as string): ")
    
    # Initialize encryption manager
    manager = SecureDataManager()
    
    # Sensitive data to encrypt
    sensitive_data = {
        'TELEGRAM_BOT_TOKEN': telegram_token,
        'GOOGLE_SHEETS_ID': google_sheets_id,
        'GOOGLE_CREDENTIALS': google_credentials,
        'GOOGLE_CREDENTIALS_FILE': 'credentials.json'  # This can remain unencrypted
    }
    
    # Encrypt the data
    encrypted_data = manager.encrypt_dict(sensitive_data)
    
    # Save to encrypted config file
    with open('.env.encrypted', 'w') as f:
        json.dump(encrypted_data, f, indent=2)
    
    print("✅ Encrypted configuration saved to .env.encrypted")
    print("⚠️  Make sure to add .env.encrypted to your .gitignore if it contains sensitive data")
    
    return encrypted_data


def create_secure_loader():
    """Create a secure configuration loader for the bot"""
    loader_code = '''#!/usr/bin/env python3
"""
Secure Configuration Loader
Loads and decrypts sensitive configuration data
"""

import os
import json
import getpass
from encrypt_secrets import SecureDataManager


class SecureConfigLoader:
    """Loads encrypted configuration securely"""
    
    def __init__(self):
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from various sources"""
        # Try to load from Railway environment variables first
        if self._load_from_railway():
            print("✅ Loaded configuration from Railway environment")
            return
        
        # Try to load from encrypted file
        if self._load_from_encrypted_file():
            print("✅ Loaded configuration from encrypted file")
            return
        
        # Fallback to regular environment variables
        if self._load_from_env():
            print("✅ Loaded configuration from environment variables")
            return
        
        raise ValueError("❌ Could not load configuration from any source")
    
    def _load_from_railway(self) -> bool:
        """Load from Railway environment variables"""
        try:
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
            google_creds = os.getenv('GOOGLE_CREDENTIALS')
            sheets_id = os.getenv('GOOGLE_SHEETS_ID')
            
            if telegram_token and google_creds and sheets_id:
                self.config = {
                    'TELEGRAM_BOT_TOKEN': telegram_token,
                    'GOOGLE_CREDENTIALS': google_creds,
                    'GOOGLE_SHEETS_ID': sheets_id,
                    'GOOGLE_CREDENTIALS_FILE': os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
                }
                return True
        except Exception:
            pass
        return False
    
    def _load_from_encrypted_file(self) -> bool:
        """Load from encrypted configuration file"""
        try:
            if not os.path.exists('.env.encrypted'):
                return False
            
            with open('.env.encrypted', 'r') as f:
                encrypted_config = json.load(f)
            
            # Get master password
            master_password = getpass.getpass("Enter master password to decrypt configuration: ")
            manager = SecureDataManager(master_password)
            
            # Decrypt configuration
            self.config = manager.decrypt_dict(encrypted_config)
            return True
        except Exception as e:
            print(f"❌ Failed to load encrypted config: {e}")
            return False
    
    def _load_from_env(self) -> bool:
        """Load from regular environment variables"""
        try:
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
            google_creds = os.getenv('GOOGLE_CREDENTIALS')
            sheets_id = os.getenv('GOOGLE_SHEETS_ID')
            
            if telegram_token and sheets_id:
                self.config = {
                    'TELEGRAM_BOT_TOKEN': telegram_token,
                    'GOOGLE_CREDENTIALS': google_creds,
                    'GOOGLE_SHEETS_ID': sheets_id,
                    'GOOGLE_CREDENTIALS_FILE': os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
                }
                return True
        except Exception:
            pass
        return False
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def get_all(self) -> dict:
        """Get all configuration"""
        return self.config.copy()
'''
    
    with open('secure_config.py', 'w') as f:
        f.write(loader_code)
    
    print("✅ Created secure configuration loader: secure_config.py")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create-config":
        create_encrypted_env_file()
        create_secure_loader()
    else:
        print("Usage:")
        print("  python encrypt_secrets.py --create-config  # Create encrypted configuration")
        print("\nSecurity Features:")
        print("  • PBKDF2 key derivation with 100,000 iterations")
        print("  • Fernet symmetric encryption (AES 128)")
        print("  • Base64 encoding for safe storage")
        print("  • Master password protection")
        print("  • Support for Railway environment variables")
