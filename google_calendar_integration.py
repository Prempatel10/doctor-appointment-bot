#!/usr/bin/env python3

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os


def create_event_service():
    """Create Google Calendar event service using service account credentials."""
    creds = None
    creds_dict = os.getenv('GOOGLE_CREDENTIALS')
    creds = Credentials.from_service_account_info(creds_dict)
    service = build('calendar', 'v3', credentials=creds)
    return service


def create_calendar_event(summary, location, description, start_time, end_time, attendees_emails):
    """Create an event in Google Calendar."""
    service = create_event_service()
    event = {
      'summary': summary,
      'location': location,
      'description': description,
      'start': {
        'dateTime': start_time,
        'timeZone': 'UTC',
      },
      'end': {
        'dateTime': end_time,
        'timeZone': 'UTC',
      },
      'attendees': [{'email': email} for email in attendees_emails],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')
    return event

if __name__ == "__main__":
    # Example Usage:
    create_calendar_event(
        summary="Doctor Appointment",
        location="123 Health Street, Medical District",
        description="Consultation",
        start_time="2025-08-02T10:00:00-07:00",
        end_time="2025-08-02T10:30:00-07:00",
        attendees_emails=["patient@example.com"]
    )
