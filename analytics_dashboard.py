#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import os
import json


class AnalyticsDashboard:
    """Analytics dashboard for appointment data."""
    
    def __init__(self):
        self.sheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Setup credentials
        google_creds = os.getenv('GOOGLE_CREDENTIALS')
        if google_creds:
            creds_dict = json.loads(google_creds)
            self.creds = Credentials.from_service_account_info(creds_dict, scopes=self.scope)
        else:
            creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
            self.creds = Credentials.from_service_account_file(creds_file, scopes=self.scope)
        
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_key(self.sheet_id)
        self.worksheet = self.sheet.worksheet('Appointments')
    
    def get_appointment_data(self):
        """Fetch appointment data from Google Sheets."""
        try:
            data = self.worksheet.get_all_records()
            df = pd.DataFrame(data)
            if not df.empty:
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                df['Preferred Date'] = pd.to_datetime(df['Preferred Date'])
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def generate_daily_stats(self):
        """Generate daily appointment statistics."""
        df = self.get_appointment_data()
        if df.empty:
            return {"message": "No appointment data available"}
        
        # Daily appointments count
        daily_stats = df.groupby(df['Timestamp'].dt.date).size()
        
        # Popular doctors
        doctor_stats = df['Doctor Name'].value_counts()
        
        # Popular specializations
        specialty_stats = df['Specialization'].value_counts()
        
        # Popular times
        time_stats = df['Preferred Time'].value_counts()
        
        return {
            "total_appointments": len(df),
            "daily_appointments": daily_stats.to_dict(),
            "popular_doctors": doctor_stats.to_dict(),
            "popular_specialties": specialty_stats.to_dict(),
            "popular_times": time_stats.to_dict(),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def create_visualizations(self):
        """Create visualization charts for appointment data."""
        df = self.get_appointment_data()
        if df.empty:
            print("No data available for visualization")
            return
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('📊 Doctor Appointment Analytics Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Appointments by Doctor
        doctor_counts = df['Doctor Name'].value_counts()
        axes[0, 0].bar(doctor_counts.index, doctor_counts.values, color='skyblue')
        axes[0, 0].set_title('👨‍⚕️ Appointments by Doctor')
        axes[0, 0].set_xlabel('Doctor')
        axes[0, 0].set_ylabel('Number of Appointments')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Appointments by Specialization
        specialty_counts = df['Specialization'].value_counts()
        axes[0, 1].pie(specialty_counts.values, labels=specialty_counts.index, autopct='%1.1f%%', colors=['lightcoral', 'lightgreen', 'lightskyblue', 'gold'])
        axes[0, 1].set_title('🏥 Appointments by Specialization')
        
        # 3. Popular Time Slots
        time_counts = df['Preferred Time'].value_counts()
        axes[1, 0].bar(time_counts.index, time_counts.values, color='lightgreen')
        axes[1, 0].set_title('🕐 Popular Time Slots')
        axes[1, 0].set_xlabel('Time')
        axes[1, 0].set_ylabel('Number of Appointments')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Age Group Distribution
        age_counts = df['Age'].value_counts()
        axes[1, 1].bar(age_counts.index, age_counts.values, color='orange')
        axes[1, 1].set_title('👥 Age Group Distribution')
        axes[1, 1].set_xlabel('Age Group')
        axes[1, 1].set_ylabel('Number of Patients')
        
        plt.tight_layout()
        plt.savefig('analytics_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("📈 Analytics dashboard saved as 'analytics_dashboard.png'")
    
    def generate_weekly_report(self):
        """Generate a weekly appointment report."""
        df = self.get_appointment_data()
        if df.empty:
            return "No appointment data available"
        
        # Filter data for the last week
        one_week_ago = datetime.now() - timedelta(days=7)
        weekly_data = df[df['Timestamp'] >= one_week_ago]
        
        if weekly_data.empty:
            return "No appointments in the last week"
        
        report = f"""
📊 WEEKLY APPOINTMENTS REPORT
============================
📅 Report Period: {one_week_ago.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}

📈 Summary:
• Total appointments: {len(weekly_data)}
• Most popular doctor: {weekly_data['Doctor Name'].mode().iloc[0] if not weekly_data['Doctor Name'].mode().empty else 'N/A'}
• Most popular time: {weekly_data['Preferred Time'].mode().iloc[0] if not weekly_data['Preferred Time'].mode().empty else 'N/A'}
• Most common complaint: {weekly_data['Chief Complaint'].mode().iloc[0] if not weekly_data['Chief Complaint'].mode().empty else 'N/A'}

👨‍⚕️ Doctor Performance:
{weekly_data['Doctor Name'].value_counts().to_string()}

🏥 Specialization Demand:
{weekly_data['Specialization'].value_counts().to_string()}

📊 Daily Breakdown:
{weekly_data['Timestamp'].dt.date.value_counts().sort_index().to_string()}
        """
        
        return report


if __name__ == "__main__":
    # Example Usage:
    analytics = AnalyticsDashboard()
    
    # Generate daily statistics
    stats = analytics.generate_daily_stats()
    print("📊 Daily Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Generate weekly report
    print("\n" + analytics.generate_weekly_report())
    
    # Create visualizations
    analytics.create_visualizations()
