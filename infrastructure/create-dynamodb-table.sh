#!/bin/bash
# Create the main DynamoDB table for Mind Mate
# Usage: ./create-dynamodb-table.sh [TABLE_NAME]

set -e

TABLE_NAME=${1:-EmoCompanion}

echo "🗄️  Creating DynamoDB table: $TABLE_NAME"

# Check if table already exists
if aws dynamodb describe-table --table-name "$TABLE_NAME" 2>/dev/null; then
    echo "✅ Table $TABLE_NAME already exists"
    exit 0
fi

# Create the table
aws dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --tags \
        Key=Application,Value=MindMate \
        Key=Environment,Value=Production

echo "⏳ Waiting for table to be active..."
aws dynamodb wait table-exists --table-name "$TABLE_NAME"

echo "✅ Table $TABLE_NAME created successfully!"
echo ""
echo "Table structure:"
echo "- Primary Key: PK (Partition Key), SK (Sort Key)"
echo "- GSI: UserIndex (userId, timestamp)"
echo "- Billing: Pay per request"
echo ""
echo "Usage patterns:"
echo "- User profiles: PK=USER#userId, SK=PROFILE"
echo "- Chat messages: PK=USER#userId, SK=CHAT#timestamp"
echo "- Mood logs: PK=USER#userId, SK=MOOD#timestamp"
echo "- Daily recaps: PK=USER#userId, SK=RECAP#date"
echo ""
echo "Note: GSI can be added later if needed for additional query patterns"