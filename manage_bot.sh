#!/bin/bash
# Doctor Appointment Bot Management Script

BOT_SERVICE="doctor-appointment-bot.service"

show_status() {
    echo "🏥 Doctor Appointment Bot Status"
    echo "================================"
    sudo systemctl status $BOT_SERVICE --no-pager -l
}

start_bot() {
    echo "🚀 Starting Doctor Appointment Bot..."
    sudo systemctl start $BOT_SERVICE
    echo "✅ Bot started!"
}

stop_bot() {
    echo "🛑 Stopping Doctor Appointment Bot..."
    sudo systemctl stop $BOT_SERVICE
    echo "✅ Bot stopped!"
}

restart_bot() {
    echo "🔄 Restarting Doctor Appointment Bot..."
    sudo systemctl restart $BOT_SERVICE
    echo "✅ Bot restarted!"
}

show_logs() {
    echo "📋 Doctor Appointment Bot Logs"
    echo "==============================="
    sudo journalctl -u $BOT_SERVICE -f --no-pager
}

enable_autostart() {
    echo "⚡ Enabling autostart..."
    sudo systemctl enable $BOT_SERVICE
    echo "✅ Bot will start automatically on boot!"
}

disable_autostart() {
    echo "❌ Disabling autostart..."
    sudo systemctl disable $BOT_SERVICE
    echo "✅ Bot autostart disabled!"
}

show_help() {
    echo "🏥 Doctor Appointment Bot Management"
    echo "===================================="
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status    - Show bot status"
    echo "  start     - Start the bot"
    echo "  stop      - Stop the bot"
    echo "  restart   - Restart the bot"
    echo "  logs      - Show bot logs (live)"
    echo "  enable    - Enable autostart on boot"
    echo "  disable   - Disable autostart"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 restart"
    echo "  $0 logs"
}

case "$1" in
    status)
        show_status
        ;;
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    logs)
        show_logs
        ;;
    enable)
        enable_autostart
        ;;
    disable)
        disable_autostart
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
