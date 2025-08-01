#!/bin/bash

echo "🏥 Enhanced Doctor Appointment Bot - Manual Test"
echo "==============================================="

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f enhanced_doctor_bot.py >/dev/null 2>&1
pkill -f ngrok >/dev/null 2>&1
sleep 2

# Start Flask app in background
echo "🚀 Starting Flask app..."
source venv/bin/activate
python3 enhanced_doctor_bot.py > flask.log 2>&1 &
FLASK_PID=$!
echo "Flask app started with PID: $FLASK_PID"

# Wait for Flask to start
echo "⏳ Waiting for Flask to initialize..."
sleep 5

# Check if Flask is running
if curl -s http://localhost:5000 >/dev/null; then
    echo "✅ Flask app is running on port 5000"
else
    echo "❌ Flask app failed to start"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

# Start ngrok
echo "🌐 Starting ngrok tunnel..."
ngrok http 5000 > ngrok.log 2>&1 &
NGROK_PID=$!
echo "Ngrok started with PID: $NGROK_PID"

# Wait for ngrok to establish tunnel
echo "⏳ Waiting for ngrok to establish tunnel..."
sleep 8

# Get public URL
echo "🔍 Getting public URL..."
PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    for tunnel in tunnels:
        if tunnel.get('proto') == 'https':
            print(tunnel['public_url'])
            sys.exit(0)
    if tunnels:
        url = tunnels[0]['public_url']
        if url.startswith('http://'):
            url = url.replace('http://', 'https://', 1)
        print(url)
except:
    pass
" 2>/dev/null)

if [ -n "$PUBLIC_URL" ]; then
    echo "✅ Ngrok tunnel established: $PUBLIC_URL"
    echo "🎯 Webhook URL: $PUBLIC_URL/webhook"
    
    # Set webhook
    echo "📡 Setting Telegram webhook..."
    if python3 set_webhook.py set "$PUBLIC_URL/webhook"; then
        echo "✅ Webhook configured successfully!"
    else
        echo "⚠️  Webhook setup failed, but continuing..."
    fi
    
    echo ""
    echo "🎉 Bot is ready for testing!"
    echo "================================"
    echo "📱 Flask App: http://localhost:5000"
    echo "🌐 Public URL: $PUBLIC_URL"
    echo "🎯 Webhook: $PUBLIC_URL/webhook"
    echo "📊 Ngrok Dashboard: http://localhost:4040"
    echo ""
    echo "🤖 Test your bot by messaging @YourBotName on Telegram"
    echo ""
    echo "Press Ctrl+C to stop all services..."
    
    # Wait for user interrupt
    trap 'echo -e "\n🛑 Stopping services..."; kill $FLASK_PID $NGROK_PID 2>/dev/null; exit 0' INT
    
    while true; do
        sleep 1
    done
    
else
    echo "❌ Failed to get ngrok URL"
    kill $FLASK_PID $NGROK_PID 2>/dev/null
    exit 1
fi
