#!/usr/bin/env python3
"""
Railway Security Configuration Script
Securely configure environment variables in Railway
"""

import os
import json
import subprocess
import getpass
from encrypt_secrets import SecureDataManager


def check_railway_cli():
    """Check if Railway CLI is installed and authenticated"""
    try:
        result = subprocess.run(['railway', 'whoami'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI authenticated as: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI not authenticated. Run 'railway login' first.")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not found. Please install it first.")
        return False


def set_railway_environment_variables():
    """Set environment variables in Railway securely"""
    if not check_railway_cli():
        return False
    
    print("🔐 Setting up secure environment variables in Railway...")
    
    # Get current Railway variables to avoid overwriting
    try:
        result = subprocess.run(['railway', 'variables'], capture_output=True, text=True)
        print("Current Railway environment variables:")
        print(result.stdout)
    except Exception as e:
        print(f"Warning: Could not fetch current variables: {e}")
    
    # Ask user for sensitive data
    telegram_token = getpass.getpass("Enter Telegram Bot Token: ")
    google_sheets_id = getpass.getpass("Enter Google Sheets ID: ")
    
    print("\n📝 For Google Credentials, you have two options:")
    print("1. Paste the JSON content directly")
    print("2. Load from a local credentials.json file")
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "2":
        try:
            with open('credentials.json', 'r') as f:
                google_credentials = f.read().strip()
            print("✅ Loaded Google credentials from credentials.json")
        except FileNotFoundError:
            print("❌ credentials.json not found. Please create it first.")
            return False
    else:
        print("Paste your Google service account JSON (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "":
                if lines and lines[-1] == "":
                    break
                lines.append("")
            else:
                lines.append(line)
        google_credentials = "\n".join(lines[:-1])
    
    # Validate JSON format
    try:
        json.loads(google_credentials)
        print("✅ Google credentials JSON is valid")
    except json.JSONDecodeError:
        print("❌ Invalid JSON format for Google credentials")
        return False
    
    # Set environment variables in Railway
    variables = {
        'TELEGRAM_BOT_TOKEN': telegram_token,
        'GOOGLE_SHEETS_ID': google_sheets_id,
        'GOOGLE_CREDENTIALS': google_credentials,
        'GOOGLE_CREDENTIALS_FILE': 'credentials.json'
    }
    
    print("\n🚀 Setting environment variables in Railway...")
    
    for key, value in variables.items():
        try:
            # Use railway CLI to set variables
            result = subprocess.run([
                'railway', 'variables', 'set', f"{key}={value}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Set {key}")
            else:
                print(f"❌ Failed to set {key}: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error setting {key}: {e}")
            return False
    
    print("\n✅ All environment variables set successfully in Railway!")
    print("\n🔒 Security recommendations:")
    print("1. Variables are now encrypted and stored securely in Railway")
    print("2. Remove any local credential files from your repository")
    print("3. Regularly rotate your tokens and credentials")
    print("4. Monitor Railway deployment logs for any issues")
    print("5. Use Railway's built-in secrets management")
    
    return True


def create_railway_security_checklist():
    """Create a security checklist for Railway deployment"""
    checklist = """
# Railway Security Checklist ✅

## Environment Variables Security
- [ ] All sensitive data stored as Railway environment variables
- [ ] No hardcoded credentials in source code
- [ ] TELEGRAM_BOT_TOKEN set securely
- [ ] GOOGLE_CREDENTIALS set as JSON string
- [ ] GOOGLE_SHEETS_ID configured
- [ ] Credentials rotated regularly

## Code Security
- [ ] .env files added to .gitignore
- [ ] credentials.json excluded from repository
- [ ] No API keys in commit history
- [ ] Encryption utilities implemented
- [ ] Secure configuration loader created

## Railway Platform Security
- [ ] Railway account secured with 2FA
- [ ] Team access properly configured
- [ ] Deployment logs monitored
- [ ] Environment separation (dev/prod)
- [ ] Regular security updates applied

## Monitoring & Maintenance
- [ ] Bot activity monitored
- [ ] Error logs reviewed regularly
- [ ] Credential expiration tracked
- [ ] Security patches applied
- [ ] Backup strategy implemented

## Emergency Procedures
- [ ] Credential revocation process documented
- [ ] Emergency contacts identified
- [ ] Incident response plan created
- [ ] Recovery procedures tested

---
Generated by Railway Security Configuration Script
"""
    
    with open('RAILWAY_SECURITY_CHECKLIST.md', 'w') as f:
        f.write(checklist)
    
    print("✅ Created security checklist: RAILWAY_SECURITY_CHECKLIST.md")


def main():
    """Main function"""
    print("🔐 Railway Security Configuration")
    print("=" * 50)
    
    print("\nOptions:")
    print("1. Configure Railway environment variables")
    print("2. Create security checklist")
    print("3. Both")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice in ['1', '3']:
        if set_railway_environment_variables():
            print("\n✅ Environment variables configured successfully!")
        else:
            print("\n❌ Failed to configure environment variables.")
            return
    
    if choice in ['2', '3']:
        create_railway_security_checklist()
    
    print("\n🎉 Railway security configuration complete!")
    print("\n📚 Next steps:")
    print("1. Test your bot deployment: railway logs")
    print("2. Verify environment variables: railway variables")
    print("3. Monitor deployment: railway open")
    print("4. Review security checklist")


if __name__ == "__main__":
    main()
