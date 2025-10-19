#!/bin/bash

# Test script for Hackathon Demo UI
echo "🚀 Opening Mind Mate Hackathon Demo UI..."
echo ""
echo "📍 File: frontend/mind-mate-hackathon.html"
echo ""

# Get the absolute path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
HTML_FILE="$SCRIPT_DIR/frontend/mind-mate-hackathon.html"

# Check if file exists
if [ ! -f "$HTML_FILE" ]; then
    echo "❌ Error: HTML file not found at $HTML_FILE"
    exit 1
fi

echo "✅ File found!"
echo ""
echo "Opening in default browser..."

# Open in default browser (works on macOS)
open "$HTML_FILE"

echo ""
echo "✨ The UI should now be open in your browser!"
echo ""
echo "📋 What you should see:"
echo "  ✅ Green gradient hero section at top (sticky)"
echo "  ✅ Wellness Score: 0.0 (will animate when JS is added)"
echo "  ✅ 49 Features Analyzed"
echo "  ✅ 94% ML Confidence"
echo "  ✅ Risk Level: LOW"
echo "  ✅ Chat section with companion avatar"
echo "  ✅ Input field and send button"
echo "  ✅ Quick action buttons at bottom"
echo ""
echo "🔧 Current Status:"
echo "  ✅ HTML structure complete"
echo "  ✅ CSS styling complete"
echo "  ⏳ JavaScript functionality (next tasks)"
echo ""
echo "💡 Next: Run tasks 3-14 to add interactive functionality"
