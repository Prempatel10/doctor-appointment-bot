#!/bin/bash
# Doctor Appointment Bot - Virtual Environment Activation Script

echo "🏥 Doctor Appointment Bot - Virtual Environment"
echo "==============================================="

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "📍 Python location: $(which python)"
echo "🐍 Python version: $(python --version)"
echo ""
echo "📋 Available commands:"
echo "  python doctor_bot.py     - Run the bot"
echo "  python setup.py          - Run setup wizard"
echo "  python test_sheets.py    - Test Google Sheets connection"
echo "  deactivate               - Exit virtual environment"
echo ""
echo "💡 Remember: You need to activate this environment each time you work on the project!"
echo "   Run: source activate_venv.sh"
echo ""

# Keep the shell active
exec "$SHELL"
