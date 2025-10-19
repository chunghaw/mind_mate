#!/bin/bash

# Add demo mood data for hackathon user
# This creates realistic mood entries for the past 7 days

USER_ID="hackathon-demo-user"
TABLE_NAME="EmoCompanion"

echo "📊 Adding demo mood data for $USER_ID..."

# Generate mood entries for the past 7 days
for i in {0..6}; do
    # Calculate date (going backwards from today)
    DATE=$(date -u -v-${i}d +"%Y-%m-%dT%H:%M:%S.000Z" 2>/dev/null || date -u -d "$i days ago" +"%Y-%m-%dT%H:%M:%S.000Z")
    
    # Generate mood value (trending upward from 6.5 to 8.5)
    MOOD=$(echo "6.5 + $i * 0.3" | bc)
    
    echo "Adding mood entry for $DATE: $MOOD"
    
    aws dynamodb put-item \
        --table-name $TABLE_NAME \
        --item "{
            \"PK\": {\"S\": \"USER#$USER_ID\"},
            \"SK\": {\"S\": \"MOOD#$DATE\"},
            \"type\": {\"S\": \"MOOD\"},
            \"userId\": {\"S\": \"$USER_ID\"},
            \"mood\": {\"N\": \"$MOOD\"},
            \"tags\": {\"L\": [{\"S\": \"calm\"}, {\"S\": \"focused\"}]},
            \"notes\": {\"S\": \"Feeling good today\"},
            \"ts\": {\"S\": \"$DATE\"}
        }" \
        --region us-east-1 2>&1 | grep -v "^$"
done

echo ""
echo "✅ Demo mood data added successfully!"
echo ""
echo "🧪 Test the risk calculation:"
echo "curl -X POST https://a5ttrfkhcr76hqo546gp3slfli0bkhlw.lambda-url.us-east-1.on.aws/calculate-risk \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"userId\":\"$USER_ID\"}'"
