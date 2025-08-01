#!/usr/bin/env python3
"""
Setup script for Doctor Appointment Telegram Bot
Helps configure Google Sheets and Telegram Bot credentials
"""

import os
import json
from pathlib import Path

def create_env_file():
    """Create .env file with user input"""
    print("🔧 Setting up environment variables...")
    
    # Get Telegram Bot Token
    bot_token = input("\n📱 Enter your Telegram Bot Token (from @BotFather): ").strip()
    
    # Get Google Sheets ID
    print("\n📊 Google Sheets Setup:")
    print("1. Create a new Google Sheet")
    print("2. Copy the Sheet ID from the URL")
    print("   Example: https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit")
    sheets_id = input("Enter your Google Sheets ID: ").strip()
    
    # Create .env file
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={bot_token}

# Google Sheets Configuration
GOOGLE_SHEETS_ID={sheets_id}
GOOGLE_CREDENTIALS_FILE=credentials.json
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")

def setup_google_credentials():
    """Guide user through Google Credentials setup"""
    print("\n🔐 Google Service Account Setup:")
    print("1. Go to the Google Cloud Console (https://console.cloud.google.com/)")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Google Sheets API and Google Drive API")
    print("4. Create a Service Account:")
    print("   - Go to IAM & Admin > Service Accounts")
    print("   - Click 'Create Service Account'")
    print("   - Give it a name and description")
    print("   - Click 'Create and Continue'")
    print("   - Skip role assignment (click 'Continue')")
    print("   - Click 'Done'")
    print("5. Create credentials:")
    print("   - Click on the created service account")
    print("   - Go to 'Keys' tab")
    print("   - Click 'Add Key' > 'Create new key'")
    print("   - Select 'JSON' format")
    print("   - Download the JSON file")
    print("6. Rename the downloaded file to 'credentials.json'")
    print("7. Place it in this project directory")
    print("8. Share your Google Sheet with the service account email")
    print("   (found in the credentials.json file)")
    
    input("\nPress Enter when you've completed these steps...")
    
    # Check if credentials file exists
    if os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
            service_email = creds.get('client_email', 'Not found')
            print(f"✅ credentials.json found!")
            print(f"📧 Service Account Email: {service_email}")
            print("🔄 Make sure to share your Google Sheet with this email address!")
        except json.JSONDecodeError:
            print("❌ credentials.json file is not valid JSON")
    else:
        print("❌ credentials.json not found in the current directory")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    os.system("pip install -r requirements.txt")
    print("✅ Dependencies installed!")

def create_sample_sheet_structure():
    """Show the expected Google Sheets structure"""
    print("\n📋 Expected Google Sheets Structure:")
    print("The bot will automatically create a worksheet named 'Appointments' with these columns:")
    
    headers = [
        "Timestamp", "Patient Name", "Age", "Phone", "Email",
        "Chief Complaint", "Preferred Date", "Preferred Time",
        "Additional Notes", "Telegram User ID"
    ]
    
    for i, header in enumerate(headers, 1):
        print(f"  Column {chr(64+i)}: {header}")

def main():
    print("🏥 Doctor Appointment Telegram Bot Setup")
    print("=" * 50)
    
    # Check if already configured
    if os.path.exists('.env') and os.path.exists('credentials.json'):
        overwrite = input("\n⚠️  Configuration files already exist. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    try:
        # Step 1: Install dependencies
        install_dependencies()
        
        # Step 2: Create environment file
        create_env_file()
        
        # Step 3: Setup Google credentials
        setup_google_credentials()
        
        # Step 4: Show sheet structure
        create_sample_sheet_structure()
        
        print("\n🎉 Setup completed!")
        print("\n🚀 To run the bot:")
        print("   python doctor_bot.py")
        print("\n📝 To test the bot:")
        print("   1. Start the bot")
        print("   2. Find your bot on Telegram")
        print("   3. Send /start command")
        print("   4. Follow the appointment booking process")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")

if __name__ == '__main__':
    main()
