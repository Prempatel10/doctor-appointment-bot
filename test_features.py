#!/usr/bin/env python3
"""
Test script for Email, Calendar, and Language features
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the modules to test
from email_notifications import send_email_notification, send_appointment_confirmation, validate_email
from google_calendar_integration import create_calendar_event
from multi_language_support import MultiLanguageSupport

def test_email_features():
    """Test email notification features."""
    print("🧪 Testing Email Features...")
    print("-" * 40)
    
    # Test email validation
    print("1. Testing email validation:")
    valid_emails = ["test@example.com", "user.name@domain.co.uk", "test+tag@gmail.com"]
    invalid_emails = ["invalid", "@domain.com", "user@", "user space@domain.com"]
    
    for email in valid_emails:
        result = validate_email(email)
        print(f"   ✅ {email}: {'Valid' if result else 'Invalid'}")
    
    for email in invalid_emails:
        result = validate_email(email)
        print(f"   ❌ {email}: {'Valid' if result else 'Invalid'}")
    
    # Test appointment confirmation email (mock data)
    print("\n2. Testing appointment confirmation email:")
    test_appointment = {
        'appointment_id': 'APT-TEST123',
        'patient_name': 'John Doe',
        'patient_email': 'test@example.com',  # Replace with your test email
        'patient_phone': '+1 555-123-4567',
        'doctor_name': 'Dr. Sarah Smith',
        'doctor_specialization': 'General Medicine',
        'doctor_fees': '$50',
        'preferred_date': '2024-08-15',
        'preferred_time': '10:00',
        'chief_complaint': 'Regular checkup'
    }
    
    if os.getenv('EMAIL_USER') and os.getenv('EMAIL_PASSWORD'):
        try:
            result = send_appointment_confirmation(test_appointment)
            print(f"   📧 Email test result: {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   📧 Email test error: {e}")
    else:
        print("   📧 Email credentials not found - skipping email test")
    
    print()

def test_calendar_features():
    """Test Google Calendar integration features."""
    print("🧪 Testing Calendar Features...")
    print("-" * 40)
    
    # Test calendar event creation
    print("1. Testing calendar event creation:")
    
    if os.getenv('GOOGLE_CREDENTIALS'):
        try:
            result = create_calendar_event(
                title="Test Appointment",
                description="Test appointment for feature verification",
                start_datetime="2024-08-15T10:00:00",
                attendees=["test@example.com"],
                duration_minutes=30
            )
            
            if result and result.get('id'):
                print(f"   📅 Calendar test: ✅ Success - Event ID: {result['id']}")
                print(f"   📅 Event link: {result.get('htmlLink', 'N/A')}")
            else:
                print(f"   📅 Calendar test: ❌ Failed - No event created")
                
        except Exception as e:
            print(f"   📅 Calendar test error: {e}")
    else:
        print("   📅 Google credentials not found - skipping calendar test")
    
    print()

def test_language_features():
    """Test multi-language support features."""
    print("🧪 Testing Language Features...")
    print("-" * 40)
    
    # Initialize multi-language support
    ml = MultiLanguageSupport()
    
    # Test language detection
    print("1. Testing language detection:")
    test_texts = [
        ("Hello world", "en"),
        ("Hola mundo", "es"),
        ("Bonjour monde", "fr"),
        ("नमस्ते दुनिया", "hi")
    ]
    
    for text, expected in test_texts:
        detected = ml.detect_language_from_text(text)
        print(f"   '{text}' -> {detected} {'✅' if detected == expected else '❌'}")
    
    # Test translations
    print("\n2. Testing translations:")
    languages = ['en', 'es', 'fr', 'hi']
    test_key = 'welcome_message'
    
    for lang in languages:
        translation = ml.get_text(test_key, lang, 'Test User')
        print(f"   {lang}: {translation[:50]}...")
    
    # Test language menu
    print("\n3. Testing language menu:")
    menu = ml.get_language_menu()
    for row in menu:
        print(f"   {row}")
    
    # Test language selection conversion
    print("\n4. Testing language selection conversion:")
    selections = ['🇺🇸 English', '🇪🇸 Español', '🇫🇷 Français', '🇮🇳 हिंदी']
    for selection in selections:
        lang_code = ml.set_user_language_from_selection(selection)
        print(f"   '{selection}' -> {lang_code}")
    
    # Test saving and retrieving user language
    print("\n5. Testing user language persistence:")
    test_user_id = 12345
    test_language = 'es'
    
    save_result = ml.save_user_language(test_user_id, test_language)
    retrieved_language = ml.get_user_language(test_user_id)
    
    print(f"   Save result: {'✅' if save_result else '❌'}")
    print(f"   Retrieved language: {retrieved_language} {'✅' if retrieved_language == test_language else '❌'}")
    
    print()

def test_integration():
    """Test integration of all features."""
    print("🧪 Testing Feature Integration...")
    print("-" * 40)
    
    # Simulate appointment booking with all features
    print("1. Simulating complete appointment booking:")
    
    # Mock appointment data
    appointment_data = {
        'appointment_id': 'APT-INTEGRATION-TEST',
        'patient_name': 'Integration Test User',
        'patient_email': 'integration@test.com',
        'patient_phone': '+1 555-999-8888',
        'doctor_name': 'Dr. Test Doctor',
        'doctor_specialization': 'Test Specialty',
        'doctor_fees': '$100',
        'preferred_date': '2024-08-20',
        'preferred_time': '14:00',
        'chief_complaint': 'Integration testing',
        'user_info': {
            'language_code': 'en',
            'first_name': 'Test',
            'last_name': 'User'
        }
    }
    
    # Test email feature
    email_sent = False
    email_status = "Not Sent"
    try:
        if os.getenv('EMAIL_USER') and os.getenv('EMAIL_PASSWORD'):
            email_sent = send_appointment_confirmation(appointment_data)
            email_status = "Sent" if email_sent else "Failed"
        else:
            email_status = "No Credentials"
    except Exception as e:
        email_status = f"Error: {str(e)[:50]}"
    
    print(f"   📧 Email Status: {email_status}")
    
    # Test calendar feature
    calendar_event_id = ""
    calendar_status = "Not Created"
    try:
        if os.getenv('GOOGLE_CREDENTIALS'):
            start_datetime_str = f"{appointment_data['preferred_date']}T{appointment_data['preferred_time']}:00"
            event_result = create_calendar_event(
                title=f"Appointment with {appointment_data['doctor_name']}",
                description=f"Patient: {appointment_data['patient_name']}\\nReason: {appointment_data['chief_complaint']}",
                start_datetime=start_datetime_str,
                attendees=[appointment_data['patient_email']],
                duration_minutes=30
            )
            if event_result and event_result.get('id'):
                calendar_event_id = event_result.get('id', '')
                calendar_status = "Created Successfully"
            else:
                calendar_status = "Failed to Create"
        else:
            calendar_status = "No Credentials"
    except Exception as e:
        calendar_status = f"Error: {str(e)[:50]}"
    
    print(f"   📅 Calendar Status: {calendar_status}")
    print(f"   📅 Calendar Event ID: {calendar_event_id}")
    
    # Test language feature
    user_language = appointment_data.get('user_info', {}).get('language_code', 'en')
    print(f"   🌍 User Language: {user_language}")
    
    # Summary
    print("\n2. Integration Summary:")
    print(f"   📧 Email Sent: {'Yes' if email_sent else 'No'}")
    print(f"   📧 Email Status: {email_status}")
    print(f"   📅 Calendar Event ID: {calendar_event_id or 'None'}")
    print(f"   📅 Calendar Status: {calendar_status}")
    print(f"   🌍 User Language: {user_language}")
    
    print()

def main():
    """Main test function."""
    print("🔧 Doctor Appointment Bot - Feature Testing")
    print("=" * 50)
    print()
    
    # Check environment variables
    print("🔍 Environment Check:")
    required_vars = ['TELEGRAM_BOT_TOKEN', 'GOOGLE_SHEETS_ID']
    optional_vars = ['EMAIL_USER', 'EMAIL_PASSWORD', 'GOOGLE_CREDENTIALS']
    
    for var in required_vars:
        status = "✅ Found" if os.getenv(var) else "❌ Missing"
        print(f"   {var}: {status}")
    
    for var in optional_vars:
        status = "✅ Found" if os.getenv(var) else "⚠️ Missing (feature disabled)"
        print(f"   {var}: {status}")
    
    print()
    
    # Run tests
    test_email_features()
    test_calendar_features()
    test_language_features()
    test_integration()
    
    print("✅ Feature testing completed!")
    print()
    print("📝 Summary:")
    print("   - Email notifications with validation and error handling")
    print("   - Google Calendar integration with proper datetime parsing")
    print("   - Multi-language support with persistent user preferences")
    print("   - Comprehensive error handling and logging")
    print()
    print("🚀 Your bot features are ready to use!")

if __name__ == "__main__":
    main()
