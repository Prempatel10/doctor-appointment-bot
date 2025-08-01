#!/usr/bin/env python3
"""
Clean Doctor Appointment Bot - Reliable Polling Version
No webhooks, no conflicts, simple and effective
"""

import logging
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(
    MAIN_MENU, DOCTOR_SELECTION, PATIENT_NAME, PATIENT_AGE, 
    PATIENT_GENDER, PATIENT_PHONE, PATIENT_EMAIL, CHIEF_COMPLAINT,
    PREFERRED_DATE, PREFERRED_TIME, ADDITIONAL_NOTES, CONFIRM_BOOKING
) = range(12)

# Available doctors data
DOCTORS = {
    "1": {
        "name": "Dr. Sarah Smith",
        "specialization": "General Medicine",
        "fees": "$50",
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "available_times": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
    },
    "2": {
        "name": "Dr. Mark Johnson", 
        "specialization": "Cardiology",
        "fees": "$80",
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "available_times": ["10:00", "11:00", "14:00", "15:00"]
    },
    "3": {
        "name": "Dr. Emily Davis",
        "specialization": "Dermatology", 
        "fees": "$70",
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "available_times": ["09:00", "11:00", "15:00", "16:00"]
    },
    "4": {
        "name": "Dr. Robert Wilson",
        "specialization": "Orthopedics",
        "fees": "$90", 
        "available_days": ["Tuesday", "Thursday", "Friday"],
        "available_times": ["10:00", "11:00", "14:00", "15:00"]
    }
}


class GoogleSheetsStorage:
    """Manages appointment data storage in Google Sheets."""

    def __init__(self):
        self.sheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Try to get credentials from environment variable first (for Railway)
        google_creds = os.getenv('GOOGLE_CREDENTIALS')
        if google_creds:
            import json
            creds_dict = json.loads(google_creds)
            self.creds = Credentials.from_service_account_info(creds_dict, scopes=self.scope)
        else:
            # Fallback to file (for local development)
            creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
            self.creds = Credentials.from_service_account_file(creds_file, scopes=self.scope)
            
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_key(self.sheet_id)
        self.worksheet = self.get_or_create_worksheet('Appointments')

    def get_or_create_worksheet(self, title: str):
        try:
            return self.sheet.worksheet(title)
        except gspread.WorksheetNotFound:
            worksheet = self.sheet.add_worksheet(title=title, rows=1, cols=20)
            self.setup_headers(worksheet)
            return worksheet

    def setup_headers(self, worksheet):
        headers = [
            'Timestamp', 'Appointment ID', 'Status', 'Doctor ID', 'Doctor Name', 'Specialization', 'Consultation Fee',
            'Patient Name', 'Age', 'Gender', 'Number', 'Email-ID',
            'Chief Complaint', 'Preferred Date', 'Preferred Time', 'Additional Notes'
        ]
        worksheet.append_row(headers)
        # Format header row with bold text and background color
        worksheet.format('A1:P1', {
            'textFormat': {'bold': True, 'fontSize': 11},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        # Set column widths for better readability
        worksheet.batch_update([{
            'range': 'A:P',
            'majorDimension': 'COLUMNS',
            'values': [[]]
        }])

    def add_appointment(self, appointment_data: Dict[str, Any]) -> str:
        appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
        appointment_data['appointment_id'] = appointment_id
        appointment_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        appointment_data['status'] = 'Confirmed'

        # Extract Telegram User information
        user_info = appointment_data.get('user_info', {})
        
        # Data row mapping to Google Sheets columns:
        # Column mapping matches headers: Timestamp, Appointment ID, Status, Doctor ID, Doctor Name, Specialization, Consultation Fee,
        # Patient Name, Age, Gender, Number, Email-ID, Chief Complaint, Preferred Date, Preferred Time, Additional Notes,
        # Telegram User ID, Telegram Username, First Name, Last Name, Language Code, Is Bot, Is Premium
        row = [
            appointment_data['timestamp'],                    # Column A: Timestamp
            appointment_data['appointment_id'],               # Column B: Appointment ID
            appointment_data['status'],                       # Column C: Status
            appointment_data['doctor_id'],                    # Column D: Doctor ID
            appointment_data['doctor_name'],                  # Column E: Doctor Name
            appointment_data['doctor_specialization'],       # Column F: Specialization
            appointment_data['doctor_fees'],                  # Column G: Consultation Fee
            appointment_data['patient_name'],                 # Column H: Patient Name (User's full name)
            appointment_data['patient_age'],                  # Column I: Age (User's age group)
            appointment_data['patient_gender'],               # Column J: Gender (User's gender)
            appointment_data['patient_phone'],                # Column K: Number (User's phone number)
            appointment_data['patient_email'],                # Column L: Email-ID (User's email address)
            appointment_data['chief_complaint'],              # Column M: Chief Complaint
            appointment_data['preferred_date'],               # Column N: Preferred Date
            appointment_data['preferred_time'],               # Column O: Preferred Time
            appointment_data['additional_notes']             # Column P: Additional Notes
        ]
        
        try:
            self.worksheet.append_row(row)
            logger.info(f"Appointment {appointment_id} saved to Google Sheets with comprehensive user data.")
            return appointment_id
        except Exception as e:
            logger.error(f"Error saving to Google Sheets: {e}")
            return None

# Global storage instance - will be initialized in main()
appointment_storage = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and show main menu."""
    user = update.effective_user
    
    welcome_message = f"""
🏥 **Welcome to Doctor Appointment Bot, {user.first_name}!**

I'll help you book an appointment with our doctors.

Available Services:
• Book new appointment
• View available doctors
• Quick and easy scheduling

Click /book to start booking an appointment!
Or use the menu below:
"""
    
    keyboard = [
        ['📅 Book Appointment', '👨‍⚕️ View Doctors'],
        ['❓ Help', '📞 Contact']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
    return MAIN_MENU

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle main menu selections."""
    text = update.message.text
    
    if text == '📅 Book Appointment':
        return await book_appointment(update, context)
    elif text == '👨‍⚕️ View Doctors':
        return await view_doctors(update, context)
    elif text == '❓ Help':
        help_text = """
🆘 **Help & Instructions**

**How to book an appointment:**
1. Click '📅 Book Appointment'
2. Select your preferred doctor
3. Fill in your details
4. Choose date and time
5. Confirm your booking

**Available Commands:**
• /start - Start over
• /book - Book appointment
• /doctors - View doctors
• /help - Show this help

Need assistance? Contact us at support@clinic.com
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
        return MAIN_MENU
    elif text == '📞 Contact':
        contact_text = """
📞 **Contact Information**

**Clinic Address:**
123 Health Street, Medical District
City, State 12345

**Phone:** +1 (555) 123-4567
**Email:** info@clinic.com
**Website:** www.clinic.com

**Office Hours:**
Monday - Friday: 9:00 AM - 6:00 PM
Saturday: 10:00 AM - 4:00 PM
Sunday: Closed
"""
        await update.message.reply_text(contact_text, parse_mode='Markdown')
        return MAIN_MENU
    else:
        await update.message.reply_text(
            "Please use the menu buttons or type /book to start booking an appointment."
        )
        return MAIN_MENU

async def book_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the appointment booking process."""
    doctors_text = "👨‍⚕️ **Please select a doctor:**\n\n"
    
    keyboard = []
    for doc_id, doctor in DOCTORS.items():
        doctors_text += f"**{doc_id}.** {doctor['name']}\n"
        doctors_text += f"   📋 {doctor['specialization']}\n"
        doctors_text += f"   💰 Fees: {doctor['fees']}\n"
        doctors_text += f"   📅 Available: {', '.join(doctor['available_days'][:3])}{'...' if len(doctor['available_days']) > 3 else ''}\n\n"
        
        keyboard.append([f"{doc_id}. {doctor['name']} - {doctor['specialization']}"])
    
    keyboard.append(['🔙 Back to Main Menu'])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(doctors_text, reply_markup=reply_markup, parse_mode='Markdown')
    return DOCTOR_SELECTION

async def view_doctors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show detailed doctor information."""
    doctors_text = "👨‍⚕️ **Our Medical Team**\n\n"
    
    for doc_id, doctor in DOCTORS.items():
        doctors_text += f"**{doctor['name']}**\n"
        doctors_text += f"🏥 Specialization: {doctor['specialization']}\n"
        doctors_text += f"💰 Consultation Fee: {doctor['fees']}\n"
        doctors_text += f"📅 Available Days: {', '.join(doctor['available_days'])}\n"
        doctors_text += f"🕐 Available Times: {', '.join(doctor['available_times'])}\n\n"
    
    keyboard = [
        ['📅 Book Appointment'],
        ['🔙 Back to Main Menu']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(doctors_text, reply_markup=reply_markup, parse_mode='Markdown')
    return MAIN_MENU

async def doctor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle doctor selection."""
    text = update.message.text
    
    if text == '🔙 Back to Main Menu':
        return await start(update, context)
    
    # Extract doctor ID from the selection
    doctor_id = text.split('.')[0].strip()
    
    if doctor_id in DOCTORS:
        context.user_data['selected_doctor'] = doctor_id
        doctor = DOCTORS[doctor_id]
        
        confirmation_text = f"""
✅ **Doctor Selected:**
{doctor['name']} - {doctor['specialization']}
Consultation Fee: {doctor['fees']}

Now, let's get your details...

👤 **Please enter your full name:**
"""
        
        keyboard = [['🔙 Back to Doctor Selection']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(confirmation_text, reply_markup=reply_markup, parse_mode='Markdown')
        return PATIENT_NAME
    else:
        await update.message.reply_text("❌ Invalid selection. Please choose a doctor from the list.")
        return DOCTOR_SELECTION

async def patient_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle patient name input."""
    text = update.message.text
    
    if text == '🔙 Back to Doctor Selection':
        return await book_appointment(update, context)
    
    context.user_data['patient_name'] = text
    
    keyboard = [
        ['18-25', '26-35', '36-45', '46-60', '60+'],
        ['🔙 Back']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ Name recorded: **{text}**\n\n👤 **Please select your age group:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PATIENT_AGE

async def patient_age_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle patient age input."""
    text = update.message.text
    
    if text == '🔙 Back':
        await update.message.reply_text("👤 **Please enter your full name:**")
        return PATIENT_NAME
    
    context.user_data['patient_age'] = text
    
    keyboard = [
        ['👨 Male', '👩 Female', '🏳️‍⚧️ Other'],
        ['🔙 Back']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ Age group recorded: **{text}**\n\n⚧ **Please select your gender:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PATIENT_GENDER

async def patient_gender_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle patient gender input."""
    text = update.message.text
    
    if text == '🔙 Back':
        keyboard = [
            ['18-25', '26-35', '36-45', '46-60', '60+'],
            ['🔙 Back']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("👤 **Please select your age group:**", reply_markup=reply_markup, parse_mode='Markdown')
        return PATIENT_AGE
    
    context.user_data['patient_gender'] = text.replace('👨 ', '').replace('👩 ', '').replace('🏳️‍⚧️ ', '')
    
    keyboard = [['🔙 Back']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ Gender recorded: **{context.user_data['patient_gender']}**\n\n📞 **Please enter your phone number:**\n(Example: +1 555-123-4567)",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PATIENT_PHONE

async def patient_phone_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle patient phone input."""
    text = update.message.text
    
    if text == '🔙 Back':
        keyboard = [
            ['👨 Male', '👩 Female', '🏳️‍⚧️ Other'],
            ['🔙 Back']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("⚧ **Please select your gender:**", reply_markup=reply_markup, parse_mode='Markdown')
        return PATIENT_GENDER
    
    context.user_data['patient_phone'] = text
    
    keyboard = [['🔙 Back']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ Phone recorded: **{text}**\n\n📧 **Please enter your email address:**\n(Example: john@example.com)",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PATIENT_EMAIL

async def patient_email_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle patient email input."""
    text = update.message.text
    
    if text == '🔙 Back':
        keyboard = [['🔙 Back']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "📞 **Please enter your phone number:**\n(Example: +1 555-123-4567)",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return PATIENT_PHONE
    
    context.user_data['patient_email'] = text
    
    keyboard = [['🔙 Back']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ Email recorded: **{text}**\n\n🏥 **Please describe your chief complaint or reason for visit:**\n(Example: Regular checkup, chest pain, skin rash, etc.)",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return CHIEF_COMPLAINT

async def chief_complaint_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle chief complaint input."""
    text = update.message.text
    
    if text == '🔙 Back':
        keyboard = [['🔙 Back']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "📧 **Please enter your email address:**\n(Example: john@example.com)",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return PATIENT_EMAIL
    
    context.user_data['chief_complaint'] = text
    
    # Show available days for the selected doctor
    doctor_id = context.user_data['selected_doctor']
    doctor = DOCTORS[doctor_id] 
    available_days = doctor['available_days']
    
    keyboard = []
    # Generate next 7 days
    today = datetime.now()
    for i in range(7):
        date = today + timedelta(days=i)
        day_name = date.strftime('%A')
        if day_name in available_days:
            keyboard.append([f"{date.strftime('%Y-%m-%d')} ({day_name})"])
    
    keyboard.append(['🔙 Back'])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ Chief complaint recorded: **{text}**\n\n📅 **Please select your preferred date:**\n(Showing available days for {doctor['name']})",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PREFERRED_DATE

async def preferred_date_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle preferred date input."""
    text = update.message.text
    
    if text == '🔙 Back':
        keyboard = [['🔙 Back']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "🏥 **Please describe your chief complaint or reason for visit:**\n(Example: Regular checkup, chest pain, skin rash, etc.)",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return CHIEF_COMPLAINT
    
    # Extract date from selection
    selected_date = text.split(' ')[0]
    context.user_data['preferred_date'] = selected_date
    
    # Show available times for the selected doctor
    doctor_id = context.user_data['selected_doctor']
    doctor = DOCTORS[doctor_id]
    available_times = doctor['available_times']
    
    keyboard = []
    for time in available_times:
        keyboard.append([f"🕐 {time}"])
    
    keyboard.append(['🔙 Back'])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ Date selected: **{selected_date}**\n\n🕐 **Please select your preferred time:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PREFERRED_TIME

async def preferred_time_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle preferred time input."""
    text = update.message.text
    
    if text == '🔙 Back':
        # Regenerate date options
        doctor_id = context.user_data['selected_doctor']
        doctor = DOCTORS[doctor_id]
        available_days = doctor['available_days']
        
        keyboard = []
        today = datetime.now()
        for i in range(7):
            date = today + timedelta(days=i)
            day_name = date.strftime('%A')
            if day_name in available_days:
                keyboard.append([f"{date.strftime('%Y-%m-%d')} ({day_name})"])
        
        keyboard.append(['🔙 Back'])
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "📅 **Please select your preferred date:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return PREFERRED_DATE
    
    # Extract time from selection
    selected_time = text.replace('🕐 ', '')
    context.user_data['preferred_time'] = selected_time
    
    # Show booking confirmation
    doctor_id = context.user_data['selected_doctor']
    doctor = DOCTORS[doctor_id]
    
    confirmation_text = f"""
📋 **Appointment Summary**

👨‍⚕️ **Doctor:** {doctor['name']}
🏥 **Specialization:** {doctor['specialization']}
💰 **Consultation Fee:** {doctor['fees']}

👤 **Patient Details:**
• Name: {context.user_data['patient_name']}
• Age: {context.user_data['patient_age']}
• Gender: {context.user_data['patient_gender']}
• Phone: {context.user_data['patient_phone']}
• Email: {context.user_data['patient_email']}

🏥 **Appointment Details:**
• Chief Complaint: {context.user_data['chief_complaint']}
• Date: {context.user_data['preferred_date']}
• Time: {context.user_data['preferred_time']}

❓ **Additional Notes (Optional)**
Please enter any additional notes or type "None" to skip:
"""
    
    keyboard = [['None'], ['🔙 Back']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(confirmation_text, reply_markup=reply_markup, parse_mode='Markdown')
    return ADDITIONAL_NOTES

async def additional_notes_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle additional notes input."""
    text = update.message.text
    
    if text == '🔙 Back':
        doctor_id = context.user_data['selected_doctor']
        doctor = DOCTORS[doctor_id]
        available_times = doctor['available_times']
        
        keyboard = []
        for time in available_times:
            keyboard.append([f"🕐 {time}"])
        
        keyboard.append(['🔙 Back'])
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "🕐 **Please select your preferred time:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return PREFERRED_TIME
    
    context.user_data['additional_notes'] = text if text != 'None' else ''
    
    # Final confirmation
    doctor_id = context.user_data['selected_doctor']
    doctor = DOCTORS[doctor_id]
    
    final_confirmation = f"""
✅ **Final Appointment Confirmation**

👨‍⚕️ **Doctor:** {doctor['name']} ({doctor['specialization']})
👤 **Patient:** {context.user_data['patient_name']}
📅 **Date & Time:** {context.user_data['preferred_date']} at {context.user_data['preferred_time']}
💰 **Fee:** {doctor['fees']}
🏥 **Reason:** {context.user_data['chief_complaint']}
"""
    
    if context.user_data['additional_notes']:
        final_confirmation += f"📝 **Notes:** {context.user_data['additional_notes']}\n"
    
    final_confirmation += "\n**Please confirm your appointment:**"
    
    keyboard = [
        ['✅ Confirm Appointment'],
        ['🔙 Back', '❌ Cancel']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(final_confirmation, reply_markup=reply_markup, parse_mode='Markdown')
    return CONFIRM_BOOKING

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle final booking confirmation."""
    text = update.message.text
    
    if text == '🔙 Back':
        keyboard = [['None'], ['🔙 Back']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "❓ **Additional Notes (Optional)**\nPlease enter any additional notes or type 'None' to skip:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ADDITIONAL_NOTES
    
    elif text == '❌ Cancel':
        return await cancel_booking(update, context)
    
    elif text == '✅ Confirm Appointment':
        # Collect comprehensive user information
        user = update.effective_user
        user_info = {
            'first_name': user.first_name or 'N/A',
            'last_name': user.last_name or 'N/A',
            'language_code': user.language_code or 'N/A',
            'is_bot': user.is_bot,
            'is_premium': getattr(user, 'is_premium', False)
        }
        
        # Save the appointment with comprehensive data
        appointment_data = {
            'user_id': user.id,
            'username': user.username or 'N/A',
            'user_info': user_info,
            'doctor_id': context.user_data['selected_doctor'],
            'doctor_name': DOCTORS[context.user_data['selected_doctor']]['name'],
            'doctor_specialization': DOCTORS[context.user_data['selected_doctor']]['specialization'],
            'doctor_fees': DOCTORS[context.user_data['selected_doctor']]['fees'],
            'patient_name': context.user_data['patient_name'],
            'patient_age': context.user_data['patient_age'],
            'patient_gender': context.user_data['patient_gender'],
            'patient_phone': context.user_data['patient_phone'],
            'patient_email': context.user_data['patient_email'],
            'chief_complaint': context.user_data['chief_complaint'],
            'preferred_date': context.user_data['preferred_date'],
            'preferred_time': context.user_data['preferred_time'],
            'additional_notes': context.user_data.get('additional_notes', ''),
        }
        
        appointment_id = appointment_storage.add_appointment(appointment_data)
        
        success_message = f"""
🎉 **Appointment Confirmed Successfully!**

📋 **Appointment ID:** `{appointment_id}`

👨‍⚕️ **Doctor:** {appointment_data['doctor_name']}
👤 **Patient:** {appointment_data['patient_name']}
📅 **Date & Time:** {appointment_data['preferred_date']} at {appointment_data['preferred_time']}

📧 **Next Steps:**
1. You will receive a confirmation email shortly
2. Please arrive 15 minutes before your appointment
3. Bring a valid ID and insurance card
4. Save this appointment ID for your records

💰 **Payment:** {appointment_data['doctor_fees']} (payable at the clinic)

❓ **Need to modify or cancel?**
Please contact us at +1 (555) 123-4567

Thank you for choosing our clinic! 🏥
"""
        
        keyboard = [
            ['📅 Book Another Appointment'],
            ['🏠 Main Menu']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(success_message, reply_markup=reply_markup, parse_mode='Markdown')
        
        # Clear user data
        context.user_data.clear()
        
        return MAIN_MENU
    
    else:
        await update.message.reply_text("❌ Invalid option. Please use the buttons provided.")
        return CONFIRM_BOOKING

async def cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current booking process."""
    keyboard = [
        ['📅 Book Appointment', '👨‍⚕️ View Doctors'],
        ['❓ Help', '📞 Contact']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    
    await update.message.reply_text(
        "❌ **Appointment booking cancelled.**\n\nWhat would you like to do next?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Clear user data
    context.user_data.clear()
    
    return MAIN_MENU

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show help information."""
    help_text = """
🆘 **Help & Instructions**

**Available Commands:**
• /start - Start the bot
• /book - Book an appointment
• /doctors - View available doctors
• /help - Show this help message

**How to book an appointment:**
1. Use /book or click '📅 Book Appointment'
2. Select your preferred doctor
3. Fill in your personal details
4. Choose your preferred date and time
5. Review and confirm your booking

**Features:**
✅ Easy appointment booking
✅ Multiple specialist doctors
✅ Flexible scheduling
✅ Instant confirmation
✅ Appointment ID for tracking

**Support:**
📞 Phone: +1 (555) 123-4567
📧 Email: support@clinic.com

**Office Hours:**
Monday - Friday: 9:00 AM - 6:00 PM
Saturday: 10:00 AM - 4:00 PM
Sunday: Closed
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')
    return ConversationHandler.END

async def doctors_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show doctors list command."""
    return await view_doctors(update, context)

async def book_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Book appointment command."""
    return await book_appointment(update, context)

def main() -> None:
    """Run the bot."""
    # Get bot token
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("Please check your .env file.")
        return
    
    # Check Google Sheets credentials
    creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')
    
    if not creds_file or not sheet_id:
        print("❌ Error: Google Sheets configuration missing!")
        print("Please check GOOGLE_CREDENTIALS_FILE and GOOGLE_SHEETS_ID in your .env file.")
        return
    
    if not os.path.exists(creds_file):
        print(f"❌ Error: Credentials file '{creds_file}' not found!")
        print("Please make sure your credentials.json file is in the correct location.")
        return
    
    print("🏥 Starting Doctor Appointment Bot with Google Sheets Integration...")
    print("=" * 60)
    print("✅ Bot token loaded")
    print("✅ Google Sheets credentials found")
    
    # Initialize Google Sheets storage
    global appointment_storage
    try:
        appointment_storage = GoogleSheetsStorage()
        print("✅ Google Sheets connection established")
    except Exception as e:
        print(f"❌ Error initializing Google Sheets: {e}")
        print("Please check your credentials and sheet permissions.")
        return
    
    print("✅ Storage system initialized")
    print("🤖 Available doctors:")
    for doc_id, doctor in DOCTORS.items():
        print(f"   • {doctor['name']} - {doctor['specialization']} ({doctor['fees']})")
    print()
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('book', book_appointment),
            MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)
        ],
        states={
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)
            ],
            DOCTOR_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, doctor_selected)
            ],
            PATIENT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, patient_name_received)
            ],
            PATIENT_AGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, patient_age_received)
            ],
            PATIENT_GENDER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, patient_gender_received)
            ],
            PATIENT_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, patient_phone_received)
            ],
            PATIENT_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, patient_email_received)
            ],
            CHIEF_COMPLAINT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chief_complaint_received)
            ],
            PREFERRED_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, preferred_date_received)
            ],
            PREFERRED_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, preferred_time_received)
            ],
            ADDITIONAL_NOTES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, additional_notes_received)
            ],
            CONFIRM_BOOKING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_booking)
            ],
        },
        fallbacks=[
            CommandHandler('start', start),
            CommandHandler('help', help_command),
            CommandHandler('doctors', doctors_command),
            CommandHandler('book', book_command),
        ],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('doctors', doctors_command))
    
    print("🚀 Bot is starting with polling...")
    print("📱 Your bot is now ready to receive messages!")
    print("💬 Send /start to your bot on Telegram to begin")
    print()
    print("Press Ctrl+C to stop the bot.")
    print("=" * 50)
    
    # Run the bot
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # This helps avoid conflicts
        )
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")

if __name__ == '__main__':
    main()
