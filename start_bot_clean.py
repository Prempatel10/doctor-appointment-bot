#!/usr/bin/env python3
"""
Clean Bot Startup Script
Ensures only one instance runs and handles conflicts gracefully
"""

import os
import sys
import subprocess
import time
import signal
from doctor_appointment_bot import main

def kill_existing_instances():
    """Kill any existing bot instances."""
    try:
        # Kill any existing Python processes running the bot
        subprocess.run(['pkill', '-f', 'doctor_appointment_bot.py'], 
                       capture_output=True, check=False)
        print("🧹 Cleaned up any existing bot instances")
        time.sleep(2)  # Wait for cleanup
    except Exception as e:
        print(f"⚠️ Cleanup note: {e}")

def start_bot():
    """Start the bot with proper error handling."""
    print("🚀 Starting Doctor Appointment Bot...")
    print("=" * 50)
    
    # Kill existing instances first
    kill_existing_instances()
    
    try:
        # Start the bot
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Bot error: {e}")
        print("🔄 Try running again in a few seconds...")
        sys.exit(1)

if __name__ == '__main__':
    start_bot()
