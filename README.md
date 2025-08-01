# 🏥 Doctor Appointment Telegram Bot

A Telegram bot that allows patients to request doctor appointments through a conversational interface. All appointment details are automatically stored in Google Sheets for clinic management.

## ✨ Features

- **Interactive Appointment Booking**: Step-by-step conversation flow
- **Google Sheets Integration**: Automatic data storage
- **Patient Information Collection**:
  - Full name
  - Age
  - Phone number
  - Email address
  - Chief complaint/health concern
  - Preferred appointment date and time
  - Additional notes
- **User-Friendly Interface**: Custom keyboards and clear instructions
- **Error Handling**: Graceful error handling with user feedback
- **Data Validation**: Input validation for age and other fields

## 🛠️ Prerequisites

- Python 3.7 or higher
- A Telegram account
- Google account with access to Google Sheets
- Google Cloud Platform account (for API access)

## 📦 Installation

1. **Clone or download this project**:
   ```bash
   git clone <repository-url>
   cd doctor-appointment-bot
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment (Linux/Mac)
   source venv/bin/activate
   
   # Or use the provided activation script
   source activate_venv.sh
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the setup script**:
   ```bash
   python setup.py
   ```
   
   This will guide you through:
   - Installing required packages
   - Creating environment configuration
   - Setting up Google Sheets integration
   - Configuring Telegram bot credentials

## 🔧 Manual Setup

If you prefer to set up manually:

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Save the bot token (you'll need it later)

### 2. Set up Google Sheets

1. Create a new Google Sheet
2. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
   ```

### 3. Configure Google Cloud Platform

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Google Sheets API
   - Google Drive API
4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Provide name and description
   - Download the JSON credentials file
5. Rename the credentials file to `credentials.json`
6. Place it in the project directory

### 4. Share Google Sheet

1. Open your Google Sheet
2. Click "Share" button
3. Add the service account email (found in `credentials.json`)
4. Give it "Editor" permissions

### 5. Create Environment File

Create a `.env` file with your configuration:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Google Sheets Configuration
GOOGLE_SHEETS_ID=your_google_sheets_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## 🚀 Usage

### Starting the Bot

```bash
python doctor_bot.py
```

### Using the Bot

1. Find your bot on Telegram using the username you created
2. Send `/start` to begin booking an appointment
3. Follow the prompts to provide your information:
   - Full name
   - Age
   - Phone number
   - Email address
   - Health concern description
   - Preferred appointment date
   - Preferred time (with quick options)
   - Additional notes
4. Review and confirm your appointment request

### Available Commands

- `/start` - Begin booking an appointment
- `/help` - Show help information
- `/cancel` - Cancel current booking process

## 📊 Google Sheets Structure

The bot automatically creates an "Appointments" worksheet with these columns:

| Column | Field | Description |
|--------|-------|-------------|
| A | Timestamp | When the appointment was requested |
| B | Patient Name | Full name of the patient |
| C | Age | Patient's age |
| D | Phone | Contact phone number |
| E | Email | Email address |
| F | Chief Complaint | Main health concern |
| G | Preferred Date | Requested appointment date |
| H | Preferred Time | Requested appointment time |
| I | Additional Notes | Any special requests or notes |
| J | Telegram User ID | Unique Telegram user identifier |

## 🔒 Security Considerations

- **Environment Variables**: Sensitive data is stored in `.env` file
- **Service Account**: Uses Google Service Account for secure API access
- **No Data Storage**: Bot doesn't store personal data locally
- **Input Validation**: Basic validation for user inputs

## 🛡️ Error Handling

The bot includes comprehensive error handling:

- **Invalid Age**: Prompts for valid age input (1-120)
- **Google Sheets Errors**: Graceful handling of API failures
- **Network Issues**: Retry mechanisms for temporary failures
- **User Cancellation**: Clean process cancellation with `/cancel`

## 📁 Project Structure

```
doctor-appointment-bot/
├── doctor_bot.py          # Main bot application
├── setup.py              # Setup script
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your environment variables (create this)
├── credentials.json     # Google service account credentials (add this)
└── README.md           # This file
```

## 🔧 Customization

### Modifying Time Options

Edit the `time_keyboard` in `get_preferred_date()` function:

```python
time_keyboard = [
    ['9:00 AM', '10:00 AM', '11:00 AM'],
    ['2:00 PM', '3:00 PM', '4:00 PM'],
    ['5:00 PM', '6:00 PM', 'Other time']
]
```

### Adding Fields

To add new fields:

1. Add a new conversation state
2. Create handler function
3. Update the conversation handler states
4. Modify Google Sheets headers and data row

### Changing Messages

All user-facing messages can be customized in the respective handler functions.

## 🐛 Troubleshooting

### Common Issues

1. **"TELEGRAM_BOT_TOKEN not found"**
   - Check your `.env` file exists and contains the correct token

2. **Google Sheets permission errors**
   - Ensure the service account email has editor access to your sheet
   - Verify the credentials.json file is in the correct location

3. **Bot not responding**
   - Check if the bot is running
   - Verify the bot token is correct
   - Ensure your bot privacy settings allow messages

4. **Import errors**
   - Run `pip install -r requirements.txt` to install dependencies

### Debug Mode

Add this line to enable detailed logging:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the error logs
3. Open an issue on GitHub
4. Contact the development team

## 🎯 Future Enhancements

- [ ] Appointment confirmation system
- [ ] SMS notifications
- [ ] Multiple doctor support
- [ ] Appointment rescheduling
- [ ] Calendar integration
- [ ] Patient history tracking
- [ ] Multi-language support
- [ ] Appointment reminders

---

**Made with ❤️ for healthcare accessibility**
