#!/usr/bin/env python3
"""
Email Configuration Setup Script
Helps set up email credentials for the bot
"""

import os
import getpass
from secure_loader import get_secure_config

def setup_email_credentials():
    """Interactive setup for email credentials."""
    print("🔧 Email Configuration Setup")
    print("=" * 40)
    
    print("\n📧 For Gmail, you need:")
    print("1. Your Gmail address")
    print("2. An App Password (not your regular password)")
    print("   - Go to: https://myaccount.google.com/apppasswords")
    print("   - Generate an App Password for 'Mail'")
    print("   - Use that 16-character password here")
    
    print("\n📧 For other email providers:")
    print("- Outlook/Hotmail: Use your regular credentials") 
    print("- Yahoo: You may need an App Password")
    
    email_user = input("\n📧 Enter your email address: ").strip()
    
    if not email_user:
        print("❌ Email address is required!")
        return False
    
    email_password = getpass.getpass("🔑 Enter your email password (App Password for Gmail): ").strip()
    
    if not email_password:
        print("❌ Email password is required!")
        return False
    
    # Test the email configuration
    print("\n🧪 Testing email configuration...")
    
    # Set temporary environment variables for testing
    os.environ['EMAIL_USER'] = email_user
    os.environ['EMAIL_PASSWORD'] = email_password
    
    # Import after setting env vars
    from email_notifications import send_email_notification
    
    # Test email
    test_subject = "Doctor Bot - Email Configuration Test"
    test_body = f"""
Hello!

This is a test email from your Doctor Appointment Bot.

If you received this email, your email configuration is working correctly!

Configuration Details:
- Email Address: {email_user}
- SMTP Settings: Automatically detected
- Time: {os.popen('date').read().strip()}

Your bot is ready to send appointment confirmations!

Best regards,
Doctor Appointment Bot
"""
    
    try:
        success = send_email_notification(email_user, test_subject, test_body)
        
        if success:
            print("✅ Email test successful!")
            print(f"✅ Test email sent to: {email_user}")
            
            # Save to secure configuration
            try:
                secure_config = get_secure_config()
                config = secure_config.get_config()
                config['EMAIL_USER'] = email_user
                config['EMAIL_PASSWORD'] = email_password
                secure_config.save_config(config)
                print("✅ Email credentials saved to secure configuration")
                return True
            except Exception as e:
                print(f"⚠️ Could not save to secure config: {e}")
                print("💡 You can manually set these environment variables:")
                print(f"   EMAIL_USER={email_user}")
                print(f"   EMAIL_PASSWORD=[your_password]")
                return True
                
        else:
            print("❌ Email test failed!")
            print("💡 Common issues:")
            print("  - For Gmail: Make sure you're using an App Password")
            print("  - Check your email address and password")
            print("  - Ensure 2-Factor Authentication is enabled (for Gmail)")
            return False
            
    except Exception as e:
        print(f"❌ Email test error: {e}")
        return False

def main():
    """Main setup function."""
    print("🏥 Doctor Appointment Bot - Email Setup")
    print("=" * 50)
    
    # Check current configuration
    current_email = os.getenv('EMAIL_USER')
    if current_email:
        print(f"📧 Current email: {current_email}")
        update = input("Do you want to update the email configuration? (y/n): ").lower()
        if update != 'y':
            print("👍 Keeping current configuration")
            return
    
    success = setup_email_credentials()
    
    if success:
        print("\n🎉 Email configuration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Your bot can now send appointment confirmation emails")
        print("2. Test by booking an appointment through your bot")
        print("3. Check the Google Sheets for 'Email Sent: Yes' status")
        
        print("\n🚀 Start your bot with:")
        print("   python3 doctor_appointment_bot.py")
    else:
        print("\n❌ Email configuration failed")
        print("📞 Need help? Check the setup instructions in the README")

if __name__ == "__main__":
    main()
