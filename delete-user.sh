#!/bin/bash
# delete-user.sh - Delete a specific user from all DynamoDB tables

set -e

USER_ID="b4f824b8-f051-708c-c5e6-e343f08103f5"

echo "=========================================="
echo "Deleting User: $USER_ID"
echo "=========================================="
echo ""

# Confirm deletion
echo "This will permanently delete all data for user: $USER_ID"
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

echo ""
echo "Deleting user data..."

# Delete from main EmoCompanion table
echo "Checking EmoCompanion table..."
ITEMS=$(aws dynamodb query \
  --table-name EmoCompanion \
  --key-condition-expression "PK = :pk" \
  --expression-attribute-values "{\":pk\":{\"S\":\"USER#$USER_ID\"}}" \
  --projection-expression "PK,SK" \
  --output json 2>/dev/null || echo '{"Items":[]}')

ITEM_COUNT=$(echo "$ITEMS" | jq '.Items | length')
echo "Found $ITEM_COUNT items in EmoCompanion table"

if [ "$ITEM_COUNT" -gt 0 ]; then
  echo "Deleting items from EmoCompanion..."
  echo "$ITEMS" | jq -c '.Items[]' | while read ITEM; do
    PK=$(echo "$ITEM" | jq -r '.PK.S')
    SK=$(echo "$ITEM" | jq -r '.SK.S')
    
    aws dynamodb delete-item \
      --table-name EmoCompanion \
      --key "{\"PK\":{\"S\":\"$PK\"},\"SK\":{\"S\":\"$SK\"}}" \
      > /dev/null 2>&1
  done
  echo "  ✓ Deleted $ITEM_COUNT items from EmoCompanion"
fi

# Delete from MoodFeatures table (if exists)
echo "Checking MoodFeatures table..."
aws dynamodb delete-item \
  --table-name MoodFeatures \
  --key "{\"userId\":{\"S\":\"$USER_ID\"}}" \
  > /dev/null 2>&1 && echo "  ✓ Deleted from MoodFeatures" || echo "  - No data in MoodFeatures"

# Delete from MindMate-RiskAssessments table
echo "Checking MindMate-RiskAssessments table..."
RISK_ITEMS=$(aws dynamodb query \
  --table-name MindMate-RiskAssessments \
  --key-condition-expression "userId = :uid" \
  --expression-attribute-values "{\":uid\":{\"S\":\"$USER_ID\"}}" \
  --projection-expression "userId,assessmentId" \
  --output json 2>/dev/null || echo '{"Items":[]}')

RISK_COUNT=$(echo "$RISK_ITEMS" | jq '.Items | length')
echo "Found $RISK_COUNT items in MindMate-RiskAssessments table"

if [ "$RISK_COUNT" -gt 0 ]; then
  echo "Deleting items from MindMate-RiskAssessments..."
  # Use batch delete for better performance
  echo "$RISK_ITEMS" | jq -c '.Items[]' | head -25 | while read ITEM; do
    USER_ID_VAL=$(echo "$ITEM" | jq -r '.userId.S')
    ASSESSMENT_ID=$(echo "$ITEM" | jq -r '.assessmentId.S')
    
    echo "Deleting assessment: $ASSESSMENT_ID"
    aws dynamodb delete-item \
      --table-name MindMate-RiskAssessments \
      --key "{\"userId\":{\"S\":\"$USER_ID_VAL\"},\"assessmentId\":{\"S\":\"$ASSESSMENT_ID\"}}" \
      > /dev/null 2>&1 || echo "Failed to delete $ASSESSMENT_ID"
  done
  echo "  ✓ Deleted items from MindMate-RiskAssessments"
fi

# Delete from MindMate-Interventions table
echo "Checking MindMate-Interventions table..."
INTERVENTION_ITEMS=$(aws dynamodb query \
  --table-name MindMate-Interventions \
  --key-condition-expression "userId = :uid" \
  --expression-attribute-values "{\":uid\":{\"S\":\"$USER_ID\"}}" \
  --projection-expression "userId,interventionId" \
  --output json 2>/dev/null || echo '{"Items":[]}')

INTERVENTION_COUNT=$(echo "$INTERVENTION_ITEMS" | jq '.Items | length')
echo "Found $INTERVENTION_COUNT items in MindMate-Interventions table"

if [ "$INTERVENTION_COUNT" -gt 0 ]; then
  echo "Deleting items from MindMate-Interventions..."
  echo "$INTERVENTION_ITEMS" | jq -c '.Items[]' | while read ITEM; do
    USER_ID_VAL=$(echo "$ITEM" | jq -r '.userId.S')
    INTERVENTION_ID=$(echo "$ITEM" | jq -r '.interventionId.S')
    
    aws dynamodb delete-item \
      --table-name MindMate-Interventions \
      --key "{\"userId\":{\"S\":\"$USER_ID_VAL\"},\"interventionId\":{\"S\":\"$INTERVENTION_ID\"}}" \
      > /dev/null 2>&1
  done
  echo "  ✓ Deleted $INTERVENTION_COUNT items from MindMate-Interventions"
fi

# Check Cognito User Pool
echo "Checking Cognito User Pool..."
COGNITO_USER=$(aws cognito-idp admin-get-user \
  --user-pool-id us-east-1_0xN9Gguz1 \
  --username "$USER_ID" \
  --output json 2>/dev/null || echo '{}')

if [ "$(echo "$COGNITO_USER" | jq -r '.Username // empty')" != "" ]; then
  echo "Found user in Cognito, deleting..."
  aws cognito-idp admin-delete-user \
    --user-pool-id us-east-1_0xN9Gguz1 \
    --username "$USER_ID" \
    > /dev/null 2>&1
  echo "  ✓ Deleted from Cognito User Pool"
else
  echo "  - No user found in Cognito User Pool"
fi

echo ""
echo "=========================================="
echo "✓ User Deletion Complete"
echo "=========================================="
echo "User $USER_ID has been deleted from all systems"