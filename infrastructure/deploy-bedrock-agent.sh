#!/bin/bash

# Deploy Bedrock Agent for Mind Mate
# Time: ~10-15 minutes

set -e

echo "🤖 Deploying Bedrock Agent for Mind Mate..."

# Configuration
AGENT_NAME="MindMateAgent"
FOUNDATION_MODEL="anthropic.claude-3-5-sonnet-20240620-v1:0"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION"
echo "Model: $FOUNDATION_MODEL"

# Step 1: Create IAM role for Bedrock Agent
echo ""
echo "📋 Step 1: Creating IAM role for Bedrock Agent..."

ROLE_NAME="MindMateBedrockAgentRole"

# Check if role exists
if aws iam get-role --role-name $ROLE_NAME 2>/dev/null; then
    echo "✅ Role $ROLE_NAME already exists"
else
    # Create trust policy
    cat > /tmp/agent-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    # Create role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file:///tmp/agent-trust-policy.json \
        --description "Role for Mind Mate Bedrock Agent"

    # Attach policy for Bedrock model invocation
    cat > /tmp/agent-permissions.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:$REGION::foundation-model/$FOUNDATION_MODEL"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:$REGION:$ACCOUNT_ID:function:mindmate-*"
    }
  ]
}
EOF

    aws iam put-role-policy \
        --role-name $ROLE_NAME \
        --policy-name BedrockAgentPermissions \
        --policy-document file:///tmp/agent-permissions.json

    echo "✅ Created role: $ROLE_NAME"
    echo "⏳ Waiting 10 seconds for IAM propagation..."
    sleep 10
fi

ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"
echo "Role ARN: $ROLE_ARN"

# Step 2: Create Bedrock Agent
echo ""
echo "🤖 Step 2: Creating Bedrock Agent..."

AGENT_INSTRUCTION="You are a compassionate AI mental health companion named 'Your Gentle Guardian'. 

Your role is to:
- Provide empathetic, non-judgmental support for mental wellness
- Listen actively and ask thoughtful follow-up questions
- Detect signs of crisis and provide appropriate resources
- Encourage healthy coping strategies
- NEVER provide medical diagnosis or treatment advice
- Always prioritize user safety and wellbeing

Communication style:
- Warm, caring, and authentic
- Use natural conversation (no stage directions like *smiles*)
- Keep responses concise (2-3 sentences typically)
- Adapt to user's personality and communication preferences
- Be direct when safety is at risk

When you detect crisis keywords or high risk:
- Express concern directly
- Provide crisis resources (988, Crisis Text Line)
- Encourage professional help
- Stay supportive and non-judgmental"

# Create agent
AGENT_RESPONSE=$(aws bedrock-agent create-agent \
    --agent-name "$AGENT_NAME" \
    --foundation-model "$FOUNDATION_MODEL" \
    --instruction "$AGENT_INSTRUCTION" \
    --agent-resource-role-arn "$ROLE_ARN" \
    --region $REGION \
    --output json)

AGENT_ID=$(echo $AGENT_RESPONSE | jq -r '.agent.agentId')
echo "✅ Created agent: $AGENT_ID"

# Step 3: Create Action Group (connects to Lambda functions)
echo ""
echo "⚡ Step 3: Creating Action Group for mental health tools..."

# Create API schema for action group
cat > /tmp/agent-api-schema.json <<EOF
{
  "openapi": "3.0.0",
  "info": {
    "title": "Mind Mate Mental Health API",
    "version": "1.0.0",
    "description": "API for mental health support functions"
  },
  "paths": {
    "/mood/log": {
      "post": {
        "summary": "Log user mood",
        "description": "Records the user's current mood score and notes",
        "operationId": "logMood",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "userId": {"type": "string"},
                  "mood": {"type": "integer", "minimum": 1, "maximum": 10},
                  "notes": {"type": "string"}
                },
                "required": ["userId", "mood"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Mood logged successfully"
          }
        }
      }
    },
    "/risk/calculate": {
      "post": {
        "summary": "Calculate mental health risk score",
        "description": "Analyzes user patterns to calculate current risk level",
        "operationId": "calculateRisk",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "userId": {"type": "string"}
                },
                "required": ["userId"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Risk assessment complete",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "riskScore": {"type": "number"},
                    "riskLevel": {"type": "string"},
                    "riskFactors": {"type": "array", "items": {"type": "string"}}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
EOF

# Upload schema to S3
S3_BUCKET="mindmate-ml-models-$ACCOUNT_ID"
aws s3 cp /tmp/agent-api-schema.json s3://$S3_BUCKET/agent/api-schema.json

# Create action group
aws bedrock-agent create-agent-action-group \
    --agent-id $AGENT_ID \
    --agent-version DRAFT \
    --action-group-name "MentalHealthActions" \
    --action-group-executor lambda="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:mindmate-chat" \
    --api-schema s3="{s3BucketName=$S3_BUCKET,s3ObjectKey=agent/api-schema.json}" \
    --region $REGION

echo "✅ Created action group"

# Step 4: Prepare Agent
echo ""
echo "🔧 Step 4: Preparing agent (this takes 2-3 minutes)..."

aws bedrock-agent prepare-agent \
    --agent-id $AGENT_ID \
    --region $REGION

echo "⏳ Waiting for agent preparation..."
sleep 30

# Check status
STATUS=$(aws bedrock-agent get-agent --agent-id $AGENT_ID --region $REGION --query 'agent.agentStatus' --output text)
echo "Agent status: $STATUS"

# Step 5: Create Agent Alias
echo ""
echo "🏷️  Step 5: Creating agent alias..."

ALIAS_RESPONSE=$(aws bedrock-agent create-agent-alias \
    --agent-id $AGENT_ID \
    --agent-alias-name "production" \
    --region $REGION \
    --output json)

ALIAS_ID=$(echo $ALIAS_RESPONSE | jq -r '.agentAlias.agentAliasId')
echo "✅ Created alias: $ALIAS_ID"

# Step 6: Grant Lambda permissions
echo ""
echo "🔐 Step 6: Granting Lambda invoke permissions to agent..."

aws lambda add-permission \
    --function-name mindmate-chat \
    --statement-id AllowBedrockAgent \
    --action lambda:InvokeFunction \
    --principal bedrock.amazonaws.com \
    --source-arn "arn:aws:bedrock:$REGION:$ACCOUNT_ID:agent/$AGENT_ID" \
    --region $REGION 2>/dev/null || echo "Permission already exists"

# Save configuration
echo ""
echo "💾 Saving configuration..."

cat > bedrock-agent-config.json <<EOF
{
  "agentId": "$AGENT_ID",
  "agentAliasId": "$ALIAS_ID",
  "agentName": "$AGENT_NAME",
  "foundationModel": "$FOUNDATION_MODEL",
  "region": "$REGION",
  "roleArn": "$ROLE_ARN"
}
EOF

echo "✅ Configuration saved to: bedrock-agent-config.json"

# Summary
echo ""
echo "========================================="
echo "✅ Bedrock Agent Deployment Complete!"
echo "========================================="
echo ""
echo "Agent ID: $AGENT_ID"
echo "Alias ID: $ALIAS_ID"
echo "Model: $FOUNDATION_MODEL"
echo "Region: $REGION"
echo ""
echo "Next steps:"
echo "1. Test the agent with: aws bedrock-agent-runtime invoke-agent"
echo "2. Update your frontend to use the agent"
echo "3. Monitor usage in CloudWatch"
echo ""
echo "Cost estimate: ~\$3-5 per 1M tokens (input)"
echo ""
