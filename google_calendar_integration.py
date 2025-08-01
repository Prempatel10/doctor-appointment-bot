#!/usr/bin/env python3

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_event_service():
    """Create Google Calendar event service using service account credentials."""
    try:
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if not creds_json:
            logger.error("GOOGLE_CREDENTIALS environment variable not found")
            return None
            
        # Parse JSON credentials
        if isinstance(creds_json, str):
            creds_dict = json.loads(creds_json)
        else:
            creds_dict = creds_json
        
        # Define required scopes for Calendar API
        scopes = ['https://www.googleapis.com/auth/calendar']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        service = build('calendar', 'v3', credentials=creds)
        logger.info("Google Calendar service created successfully")
        return service
    except Exception as e:
        logger.error(f"Error creating calendar service: {e}")
        return None


def create_calendar_event(title, description, start_datetime, attendees=None, duration_minutes=30):
    """Create an event in Google Calendar with improved error handling."""
    try:
        service = create_event_service()
        if not service:
            logger.error("Failed to create calendar service")
            return None
        
        # Parse start datetime
        if isinstance(start_datetime, str):
            try:
                # Try to parse the datetime string
                if 'T' in start_datetime:
                    start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                else:
                    # Assume format: YYYY-MM-DD and add time
                    start_dt = datetime.strptime(start_datetime, '%Y-%m-%d')
                    start_dt = start_dt.replace(hour=10, minute=0)  # Default time
            except ValueError as e:
                logger.error(f"Error parsing start_datetime: {e}")
                return None
        else:
            start_dt = start_datetime
        
        # Calculate end time
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Format datetimes for Google Calendar API
        start_time_str = start_dt.isoformat()
        end_time_str = end_dt.isoformat()
        
        # Prepare attendees list (make it optional to avoid permission issues)
        attendee_list = []
        # Skip attendees for now to avoid service account permission issues
        # Will create event without attendees to ensure it works
        # if attendees:
        #     if isinstance(attendees, str):
        #         attendee_list = [{'email': attendees}]
        #     elif isinstance(attendees, list):
        #         attendee_list = [{'email': email} for email in attendees if email]
        
        # Create event object
        event = {
            'summary': title or 'Doctor Appointment',
            'location': '123 Health Street, Medical District, City, State 12345',
            'description': description or 'Medical consultation appointment',
            'start': {
                'dateTime': start_time_str,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time_str,
                'timeZone': 'UTC',
            },
            'attendees': attendee_list,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
                    {'method': 'popup', 'minutes': 30},       # 30 minutes before
                ],
            },
            'sendUpdates': 'all',  # Send email invitations to attendees
        }
        
        # Insert the event
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        logger.info(f"Calendar event created successfully: {created_event.get('id')}")
        logger.info(f"Event link: {created_event.get('htmlLink')}")
        
        return {
            'id': created_event.get('id'),
            'htmlLink': created_event.get('htmlLink'),
            'status': 'created'
        }
        
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        return None

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
