# 📅 Google Calendar Integration Setup

## Current Status
Your Google Calendar integration is **configured but requires API activation**.

## 🔧 Quick Fix Steps

### 1. Enable Google Calendar API
1. Go to [Google Cloud Console](https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=471132420021)
2. Click **"Enable"** button
3. Wait 2-3 minutes for activation

### 2. Alternative: Create New Project
If the above link doesn't work:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Go to **APIs & Services** > **Library**
4. Search for **"Google Calendar API"**
5. Click on it and press **"Enable"**

### 3. Service Account Setup (If Needed)
If you need to create new credentials:

1. Go to **APIs & Services** > **Credentials**
2. Click **"Create Credentials"** > **"Service Account"**
3. Fill in the details and create
4. In the service account, click **"Keys"** > **"Add Key"** > **"JSON"**
5. Download the JSON file
6. Use the content of this file as your `GOOGLE_CREDENTIALS`

## 🧪 Test Calendar Integration

After enabling the API, test with:

```bash
cd /home/prem/Desktop/King/New/doctor-appointment-bot
source venv/bin/activate
python3 -c "
from google_calendar_integration import create_calendar_event
result = create_calendar_event(
    title='Test Appointment',
    description='Testing calendar integration',
    start_datetime='2025-08-05T10:00:00'
)
print('✅ Calendar test successful!' if result else '❌ Calendar test failed')
"
```

## 🎯 Expected Results

After setup, your appointments should show:
- **Calendar Event ID**: `abc123def456` (actual Google Calendar event ID)
- **Calendar Status**: `Created Successfully`

## 🔍 Troubleshooting

### Common Issues:

1. **"API not enabled"** 
   - Solution: Follow Step 1 above

2. **"Service accounts cannot invite attendees"**
   - This is fixed in the updated code (attendees removed)

3. **"Forbidden" errors**
   - Check service account permissions
   - Ensure Calendar API is enabled

4. **"Invalid credentials"**
   - Verify GOOGLE_CREDENTIALS in your secure config

## ✅ Verification

Once working, your Google Sheets will show:
- Column S: Calendar Event ID (e.g., `abc123def456`)
- Column T: Calendar Status (`Created Successfully`)

## 🚀 Quick Enable Command

Run this to enable the API for your project:

```bash
# If you have gcloud CLI installed
gcloud services enable calendar-json.googleapis.com --project=471132420021
```

Your calendar integration will work immediately after enabling the API! 🎉
