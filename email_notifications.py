#!/usr/bin/env python3

import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
import re

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def validate_email(email):
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_email_notification(to_email, subject, body, html_body=None):
    """Send an email notification with optional HTML content and improved error handling."""
    try:
        # Validate email address
        if not validate_email(to_email):
            logger.error(f"Invalid email address: {to_email}")
            return False
        
        EMAIL_ADDRESS = os.getenv('EMAIL_USER')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
        
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            logger.error("Email credentials not found in environment variables!")
            return False
        
        # Validate sender email
        if not validate_email(EMAIL_ADDRESS):
            logger.error(f"Invalid sender email address: {EMAIL_ADDRESS}")
            return False

        msg = EmailMessage()
        msg.set_content(body)
        
        # Add HTML content if provided
        if html_body:
            msg.add_alternative(html_body, subtype='html')
        
        msg['Subject'] = subject
        msg['From'] = f"Doctor Appointment System <{EMAIL_ADDRESS}>"
        msg['To'] = to_email
        msg['Reply-To'] = EMAIL_ADDRESS
        
        # Determine SMTP settings based on email provider
        smtp_settings = get_smtp_settings(EMAIL_ADDRESS)
        
        # Try different SMTP approaches
        try:
            # First try SMTP_SSL
            with smtplib.SMTP_SSL(smtp_settings['host'], smtp_settings['port']) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
        except Exception as ssl_error:
            logger.warning(f"SMTP_SSL failed: {ssl_error}, trying SMTP with STARTTLS")
            # Fallback to SMTP with STARTTLS
            with smtplib.SMTP(smtp_settings['host'], smtp_settings['starttls_port']) as smtp:
                smtp.starttls()
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"Recipients refused: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def get_smtp_settings(email_address):
    """Get SMTP settings based on email provider."""
    domain = email_address.split('@')[1].lower()
    
    if 'gmail' in domain:
        return {'host': 'smtp.gmail.com', 'port': 465, 'starttls_port': 587}
    elif 'outlook' in domain or 'hotmail' in domain or 'live' in domain:
        return {'host': 'smtp-mail.outlook.com', 'port': 465, 'starttls_port': 587}
    elif 'yahoo' in domain:
        return {'host': 'smtp.mail.yahoo.com', 'port': 465, 'starttls_port': 587}
    else:
        # Default to Gmail settings
        return {'host': 'smtp.gmail.com', 'port': 465, 'starttls_port': 587}


def send_appointment_confirmation(appointment_data):
    """Send appointment confirmation email to patient."""
    patient_email = appointment_data.get('patient_email')
    patient_name = appointment_data.get('patient_name')
    doctor_name = appointment_data.get('doctor_name')
    doctor_specialization = appointment_data.get('doctor_specialization')
    doctor_fees = appointment_data.get('doctor_fees')
    preferred_date = appointment_data.get('preferred_date')
    preferred_time = appointment_data.get('preferred_time')
    appointment_id = appointment_data.get('appointment_id')
    chief_complaint = appointment_data.get('chief_complaint')
    patient_phone = appointment_data.get('patient_phone')
    
    if not patient_email:
        print("❌ No patient email provided for confirmation")
        return False
    
    subject = f"Appointment Confirmation - {appointment_id}"
    
    # Plain text body
    body = f"""
Dear {patient_name},

Your appointment has been successfully confirmed!

Appointment Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Appointment ID: {appointment_id}
Doctor: {doctor_name}
Specialization: {doctor_specialization}
Date: {preferred_date}
Time: {preferred_time}
Consultation Fee: {doctor_fees}
Reason for Visit: {chief_complaint}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Important Instructions:
• Please arrive 15 minutes before your scheduled time
• Bring a valid photo ID and insurance card
• Payment of {doctor_fees} is due at the time of service
• If you need to reschedule or cancel, please call us at +1 (555) 123-4567

Clinic Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Address: 123 Health Street, Medical District, City, State 12345
Phone: +1 (555) 123-4567
Email: info@clinic.com
Website: www.clinic.com

Office Hours:
Monday - Friday: 9:00 AM - 6:00 PM
Saturday: 10:00 AM - 4:00 PM
Sunday: Closed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for choosing our medical services. We look forward to seeing you!

Best regards,
Doctor Appointment System
Healthcare Clinic

This is an automated message. Please do not reply to this email.
For any inquiries, please contact us at info@clinic.com or +1 (555) 123-4567.
"""
    
    # HTML body for better formatting
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Appointment Confirmation</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
        .appointment-details {{ background-color: white; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
        .info-section {{ margin: 15px 0; }}
        .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; border-radius: 0 0 5px 5px; font-size: 12px; }}
        .highlight {{ color: #4CAF50; font-weight: bold; }}
        .important {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 Appointment Confirmed!</h1>
        <p>Your healthcare appointment has been successfully scheduled</p>
    </div>
    
    <div class="content">
        <p>Dear <strong>{patient_name}</strong>,</p>
        
        <p>We're pleased to confirm your appointment with our medical team. Please find your appointment details below:</p>
        
        <div class="appointment-details">
            <h3>📋 Appointment Information</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 5px 0;"><strong>Appointment ID:</strong></td><td style="padding: 5px 0;"><span class="highlight">{appointment_id}</span></td></tr>
                <tr><td style="padding: 5px 0;"><strong>Doctor:</strong></td><td style="padding: 5px 0;">{doctor_name}</td></tr>
                <tr><td style="padding: 5px 0;"><strong>Specialization:</strong></td><td style="padding: 5px 0;">{doctor_specialization}</td></tr>
                <tr><td style="padding: 5px 0;"><strong>Date:</strong></td><td style="padding: 5px 0;"><span class="highlight">{preferred_date}</span></td></tr>
                <tr><td style="padding: 5px 0;"><strong>Time:</strong></td><td style="padding: 5px 0;"><span class="highlight">{preferred_time}</span></td></tr>
                <tr><td style="padding: 5px 0;"><strong>Consultation Fee:</strong></td><td style="padding: 5px 0;">{doctor_fees}</td></tr>
                <tr><td style="padding: 5px 0;"><strong>Reason for Visit:</strong></td><td style="padding: 5px 0;">{chief_complaint}</td></tr>
            </table>
        </div>
        
        <div class="important">
            <h3>⚠️ Important Instructions</h3>
            <ul>
                <li>Please arrive <strong>15 minutes before</strong> your scheduled time</li>
                <li>Bring a valid <strong>photo ID</strong> and <strong>insurance card</strong></li>
                <li>Payment of <strong>{doctor_fees}</strong> is due at the time of service</li>
                <li>For rescheduling or cancellations, call us at <strong>+1 (555) 123-4567</strong></li>
            </ul>
        </div>
        
        <div class="info-section">
            <h3>🏥 Clinic Information</h3>
            <p><strong>Address:</strong> 123 Health Street, Medical District<br>
            City, State 12345</p>
            <p><strong>Phone:</strong> +1 (555) 123-4567<br>
            <strong>Email:</strong> info@clinic.com<br>
            <strong>Website:</strong> www.clinic.com</p>
            
            <p><strong>Office Hours:</strong><br>
            Monday - Friday: 9:00 AM - 6:00 PM<br>
            Saturday: 10:00 AM - 4:00 PM<br>
            Sunday: Closed</p>
        </div>
        
        <p>Thank you for choosing our medical services. We look forward to providing you with excellent healthcare!</p>
    </div>
    
    <div class="footer">
        <p><strong>Doctor Appointment System</strong><br>
        Healthcare Clinic</p>
        <p>This is an automated message. For inquiries, contact us at info@clinic.com</p>
    </div>
</body>
</html>
"""
    
    return send_email_notification(patient_email, subject, body, html_body)


def send_appointment_reminder(appointment_data, reminder_type="24h"):
    """Send appointment reminder email."""
    patient_email = appointment_data.get('patient_email')
    patient_name = appointment_data.get('patient_name')
    doctor_name = appointment_data.get('doctor_name')
    preferred_date = appointment_data.get('preferred_date')
    preferred_time = appointment_data.get('preferred_time')
    appointment_id = appointment_data.get('appointment_id')
    
    if not patient_email:
        return False
    
    if reminder_type == "24h":
        subject = f"Reminder: Your appointment tomorrow - {appointment_id}"
        timing_text = "tomorrow"
    else:
        subject = f"Reminder: Your appointment today - {appointment_id}"
        timing_text = "today"
    
    body = f"""
Dear {patient_name},

This is a friendly reminder about your upcoming appointment {timing_text}.

Appointment Details:
• Appointment ID: {appointment_id}
• Doctor: {doctor_name}
• Date: {preferred_date}
• Time: {preferred_time}

Please remember to:
• Arrive 15 minutes early
• Bring your ID and insurance card
• Contact us if you need to reschedule: +1 (555) 123-4567

Thank you!

Best regards,
Doctor Appointment System
"""
    
    return send_email_notification(patient_email, subject, body)


if __name__ == "__main__":
    # Example Usage:
    test_appointment = {
        'appointment_id': 'APT-TEST123',
        'patient_name': 'John Doe',
        'patient_email': 'john.doe@example.com',
        'patient_phone': '+1 555-123-4567',
        'doctor_name': 'Dr. Sarah Smith',
        'doctor_specialization': 'General Medicine',
        'doctor_fees': '$50',
        'preferred_date': '2024-08-15',
        'preferred_time': '10:00',
        'chief_complaint': 'Regular checkup'
    }
    
    print("Testing appointment confirmation email...")
    success = send_appointment_confirmation(test_appointment)
    if success:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Failed to send test email.")
