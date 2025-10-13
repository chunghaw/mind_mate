# Mind Mate - Project Structure

```
aws_ai_agent_hackathon/
├── agent.md                          # Original project requirements
├── README.md                         # Step-by-step deployment guide
├── PROJECT_STRUCTURE.md              # This file
│
├── backend/
│   └── lambdas/
│       ├── logMood/
│       │   └── lambda_function.py    # Store mood entries
│       ├── analyzeSelfie/
│       │   └── lambda_function.py    # Detect emotions from photos
│       ├── analyzeScene/
│       │   └── lambda_function.py    # Detect surroundings/context
│       ├── generateAvatar/
│       │   └── lambda_function.py    # Create AI pet avatar (Titan)
│       ├── dailyRecap/
│       │   └── lambda_function.py    # Send daily email summary
│       └── riskScan/
│           └── lambda_function.py    # Detect mental health risks
│
├── frontend/
│   └── index.html                    # Single-page web app (deploy to Amplify)
│
├── infrastructure/
│   ├── cloudformation-template.yaml  # IaC for DynamoDB, S3, IAM, API Gateway
│   └── deploy-lambdas.sh            # Script to deploy all Lambda functions
│
├── test/
│   └── test-api.sh                  # curl-based API testing script
│
└── docs/
    └── SETUP_GUIDE.md               # Quick setup instructions
```
