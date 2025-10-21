#!/bin/bash
# cleanup_test_data.sh - Remove all test data from DynamoDB

set -e

echo "=========================================="
echo "Cleaning Up Test Data"
echo "=========================================="
echo ""

# Test user patterns to clean up
PATTERNS=(
  "test-"
  "demo-"
  "e2e-test-"
  "ml-test-"
  "feature-test-"
  "behavioral-test-"
)

echo "Scanning for test users..."
echo ""

# Get all user IDs from DynamoDB
ALL_USERS=$(aws dynamodb scan \
  --table-name EmoCompanion \
  --filter-expression "attribute_exists(userId)" \
  --projection-expression "userId" \
  --output json | jq -r '.Items[].userId.S' | sort -u)

# Filter test users
TEST_USERS=()
for USER in $ALL_USERS; do
  for PATTERN in "${PATTERNS[@]}"; do
    if [[ $USER == $PATTERN* ]]; then
      TEST_USERS+=("$USER")
      break
    fi
  done
done

if [ ${#TEST_USERS[@]} -eq 0 ]; then
  echo "No test users found."
  exit 0
fi

echo "Found ${#TEST_USERS[@]} test users:"
for USER in "${TEST_USERS[@]}"; do
  echo "  - $USER"
done
echo ""

read -p "Delete all test users? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

echo ""
echo "Deleting test data..."

# Delete each test user's data
for USER in "${TEST_USERS[@]}"; do
  echo "Deleting $USER..."
  
  # Query all items for this user
  ITEMS=$(aws dynamodb query \
    --table-name EmoCompanion \
    --key-condition-expression "PK = :pk" \
    --expression-attribute-values "{\":pk\":{\"S\":\"USER#$USER\"}}" \
    --projection-expression "PK,SK" \
    --output json)
  
  # Delete each item
  echo "$ITEMS" | jq -c '.Items[]' | while read ITEM; do
    PK=$(echo "$ITEM" | jq -r '.PK.S')
    SK=$(echo "$ITEM" | jq -r '.SK.S')
    
    aws dynamodb delete-item \
      --table-name EmoCompanion \
      --key "{\"PK\":{\"S\":\"$PK\"},\"SK\":{\"S\":\"$SK\"}}" \
      > /dev/null 2>&1
  done
  
  # Also delete from MoodFeatures table
  aws dynamodb delete-item \
    --table-name MoodFeatures \
    --key "{\"userId\":{\"S\":\"$USER\"}}" \
    > /dev/null 2>&1 || true
  
  echo "  ✓ Deleted"
done

echo ""
echo "=========================================="
echo "✓ Cleanup Complete"
echo "=========================================="
echo "Deleted ${#TEST_USERS[@]} test users"
