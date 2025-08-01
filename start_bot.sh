#!/bin/bash

echo "🏥 Starting Enhanced Doctor Appointment Bot"
echo "==========================================="

# Cleanup existing processes
echo "🧹 Stopping existing processes..."
pkill -f enhanced_doctor_bot.py >/dev/null 2>&1
pkill -f ngrok >/dev/null 2>&1
sleep 3

# Delete any existing webhook
echo "🗑️ Clearing old webhook..."
source venv/bin/activate
python3 set_webhook.py delete >/dev/null 2>&1

# Start Flask app
echo "🚀 Starting Flask application..."
source venv/bin/activate
python3 enhanced_doctor_bot.py &
FLASK_PID=$!
echo "Flask PID: $FLASK_PID"

# Wait for Flask to initialize
echo "⏳ Waiting for Flask to start..."
sleep 5

# Check Flask status
if curl -s http://localhost:5000 | grep -q "Enhanced Doctor Appointment Bot"; then
    echo "✅ Flask app is running"
else
    echo "❌ Flask app failed to start"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

# Start ngrok
echo "🌐 Starting ngrok tunnel..."
ngrok http 5000 &
NGROK_PID=$!
echo "Ngrok PID: $NGROK_PID"

# Wait for ngrok
echo "⏳ Waiting for ngrok tunnel..."
sleep 10

# Get public URL
echo "🔍 Getting ngrok public URL..."
PUBLIC_URL=""
for i in {1..5}; do
    PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for tunnel in data.get('tunnels', []):
        if tunnel.get('proto') == 'https':
            print(tunnel['public_url'])
            break
except:
    pass
")
    if [ -n "$PUBLIC_URL" ]; then
        break
    fi
    echo "Attempt $i/5: Waiting for ngrok..."
    sleep 2
done

if [ -z "$PUBLIC_URL" ]; then
    echo "❌ Failed to get ngrok URL"
    kill $FLASK_PID $NGROK_PID 2>/dev/null
    exit 1
fi

echo "✅ Ngrok URL: $PUBLIC_URL"

# Set webhook
echo "📡 Setting webhook..."
WEBHOOK_URL="$PUBLIC_URL/webhook"
echo "Webhook URL: $WEBHOOK_URL"

if python3 set_webhook.py set "$WEBHOOK_URL"; then
    echo "✅ Webhook set successfully!"
else
    echo "❌ Failed to set webhook"
    kill $FLASK_PID $NGROK_PID 2>/dev/null
    exit 1
fi

# Show status
echo ""
echo "🎉 Bot is now running!"
echo "======================"
echo "📱 Local: http://localhost:5000"
echo "🌐 Public: $PUBLIC_URL"
echo "🎯 Webhook: $WEBHOOK_URL"
echo "📊 Monitor: http://localhost:4040"
echo ""
echo "✨ Your bot is ready to receive messages!"
echo "💬 Test it by sending /start to your bot on Telegram"
echo ""
echo "Press Ctrl+C to stop..."

# Handle cleanup on exit
cleanup() {
    echo -e "\n🛑 Shutting down..."
    kill $FLASK_PID $NGROK_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

trap cleanup INT TERM

# Keep running
while true; do
    # Check if processes are still running
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "❌ Flask app stopped unexpectedly"
        break
    fi
    if ! kill -0 $NGROK_PID 2>/dev/null; then
        echo "❌ Ngrok stopped unexpectedly"
        break
    fi
    sleep 5
done

cleanup
