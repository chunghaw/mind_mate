import json
import os
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
risk_table = dynamodb.Table(os.environ.get('RISK_ASSESSMENTS_TABLE', 'MindMate-RiskAssessments'))

def decimal_to_float(obj):
    """Convert DynamoDB Decimal to float"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET"
        },
        "body": json.dumps(body, default=str)
    }

def lambda_handler(event, context):
    """Get user's latest risk score"""
    try:
        # Get userId from query params
        user_id = event.get('queryStringParameters', {}).get('userId', 'demo-user') if event.get('queryStringParameters') else 'demo-user'
        
        # Query latest risk assessment
        response = risk_table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False,  # Most recent first
            Limit=1
        )
        
        if response.get('Items'):
            assessment = response['Items'][0]
            
            return _resp(200, {
                'ok': True,
                'riskScore': decimal_to_float(assessment.get('riskScore', 0)),
                'riskLevel': assessment.get('riskLevel', 'unknown'),
                'lastAssessment': assessment.get('timestamp'),
                'interventionTriggered': assessment.get('interventionsTriggered', []) != []
            })
        
        # No assessment found - return default
        return _resp(200, {
            'ok': True,
            'riskLevel': 'unknown',
            'message': 'No risk assessment available yet'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return _resp(500, {'error': str(e)})
