#!/bin/bash

# Script to integrate ML wellness widget into existing frontend
# This creates a new version of the frontend with ML integration

set -e

echo "🔧 Integrating ML Wellness Widget into Frontend..."

SOURCE_FILE="frontend/mind-mate-v3.html"
OUTPUT_FILE="frontend/mind-mate-ml.html"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "❌ Error: $SOURCE_FILE not found"
    exit 1
fi

echo "📄 Creating $OUTPUT_FILE..."

# Copy the source file
cp "$SOURCE_FILE" "$OUTPUT_FILE"

# Add CSS link before </head>
sed -i '' '/<\/head>/i\
    <link rel="stylesheet" href="ml-wellness-widget.css">\
' "$OUTPUT_FILE"

# Add script before </body>
sed -i '' '/<\/body>/i\
    <script src="ml-wellness-widget.js"></script>\
' "$OUTPUT_FILE"

# Add widget container after header (after the first </div> following class="header")
sed -i '' '/<div class="header">/,/<\/div>/{
    /<\/div>/a\
\
        <!-- ML Wellness Widget -->\
        <div id="ml-wellness-widget"></div>
}' "$OUTPUT_FILE"

# Add initialization in window.onload
sed -i '' '/window.onload = () => {/a\
            initMLWidget(API, USER_ID);
' "$OUTPUT_FILE"

echo "✅ ML widget integrated successfully!"
echo ""
echo "Output file: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "1. Review $OUTPUT_FILE"
echo "2. Deploy to your hosting service"
echo "3. Test the ML wellness widget"
