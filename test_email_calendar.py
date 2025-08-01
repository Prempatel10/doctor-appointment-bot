#!/usr/bin/env python3
"""
Test Email and Calendar Integration
"""

import os
from datetime import datetime
from email_notifications import send_appointment_confirmation
from google_calendar_integration import create_calendar_event

def test_email_integration():
    """Test email functionality."""
    print("📧 Testing Email Integration...")
    
    if not os.getenv('EMAIL_USER') or not os.getenv('EMAIL_PASSWORD'):
        print("❌ Email credentials not found")
        print("💡 Run: python3 setup_email.py")
        return False
    
    test_appointment = {
        'appointment_id': 'APT-EMAIL-TEST',
        'patient_name': 'Test Patient',
        'patient_email': os.getenv('EMAIL_USER'),  # Send to yourself
        'doctor_name': 'Dr. Test Doctor',
        'doctor_specialization': 'Test Specialty',
        'doctor_fees': '$50',
        'preferred_date': '2025-08-05',
        'preferred_time': '10:00',
        'chief_complaint': 'Email integration test'
    }
    
    try:
        result = send_appointment_confirmation(test_appointment)
        if result:
            print("✅ Email test successful!")
            print(f"✅ Test email sent to: {os.getenv('EMAIL_USER')}")
            return True
        else:
            print("❌ Email test failed")
            return False
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

def test_calendar_integration():
    """Test calendar functionality."""
    print("\n📅 Testing Calendar Integration...")
    
    if not os.getenv('GOOGLE_CREDENTIALS'):
        print("❌ Google credentials not found")
        return False
    
    try:
        result = create_calendar_event(
            title='Test Appointment - Integration Check',
            description='Testing calendar integration for Doctor Bot',
            start_datetime='2025-08-05T14:00:00',
            duration_minutes=30
        )
        
        if result and result.get('id'):
            print("✅ Calendar test successful!")
            print(f"✅ Event ID: {result['id']}")
            print(f"✅ Event link: {result.get('htmlLink', 'N/A')}")
            return True
        else:
            print("❌ Calendar test failed - no event created")
            return False
            
    except Exception as e:
        print(f"❌ Calendar error: {e}")
        print("💡 Make sure Google Calendar API is enabled")
        return False

def main():
    """Run all tests."""
    print("🧪 Doctor Appointment Bot - Integration Testing")
    print("=" * 50)
    
    email_ok = test_email_integration()
    calendar_ok = test_calendar_integration()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    print(f"📧 Email Integration: {'✅ WORKING' if email_ok else '❌ NEEDS SETUP'}")
    print(f"📅 Calendar Integration: {'✅ WORKING' if calendar_ok else '❌ NEEDS SETUP'}")
    
    if email_ok and calendar_ok:
        print("\n🎉 ALL INTEGRATIONS WORKING!")
        print("Your next appointment will show:")
        print("  • Email Sent: Yes")
        print("  • Email Status: Sent")
        print("  • Calendar Event ID: [actual ID]") 
        print("  • Calendar Status: Created Successfully")
        
    else:
        print("\n🔧 SETUP NEEDED:")
        if not email_ok:
            print("  📧 Email: Run 'python3 setup_email.py'")
        if not calendar_ok:
            print("  📅 Calendar: Enable Google Calendar API")
            print("      Link: https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=471132420021")
    
    print("\n🚀 Start your bot: python3 doctor_appointment_bot.py")

if __name__ == "__main__":
    main()
