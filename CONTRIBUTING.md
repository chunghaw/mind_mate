# Contributing to Mind Mate

Thanks for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites
- AWS account
- AWS CLI configured
- Python 3.12+
- Git

### Local Development

1. **Clone the repo**
```bash
git clone <your-repo-url>
cd aws_ai_agent_hackathon
```

2. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

3. **Set up environment variables**
```bash
export TABLE_NAME=EmoCompanion
export BUCKET=mindmate-uploads-YOUR_ACCOUNT_ID
export SENDER_EMAIL=your@email.com
export RECIPIENT_EMAIL=user@email.com
```

4. **Test Lambda functions locally**
```python
# Test logMood
python backend/lambdas/logMood/lambda_function.py
```

## Project Structure

See `PROJECT_STRUCTURE.md` for detailed layout.

## Making Changes

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed

### 3. Test Your Changes
```bash
# Test Lambda function
aws lambda invoke \
  --function-name YOUR_FUNCTION \
  --payload '{"test":"data"}' \
  response.json

# Test API endpoint
curl -X POST "$API_URL/mood" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","mood":7}'
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add new feature"
```

Use conventional commits:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `refactor:` code refactoring
- `test:` adding tests

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

## Code Style

### Python
- Follow PEP 8
- Use type hints where possible
- Keep functions small and focused
- Add docstrings for complex functions

```python
def lambda_handler(event: dict, context: Any) -> dict:
    """
    Handle mood logging request.
    
    Args:
        event: API Gateway event with mood data
        context: Lambda context object
        
    Returns:
        API Gateway response with status and body
    """
    pass
```

### JavaScript
- Use ES6+ features
- Use `const` by default
- Add JSDoc comments for functions

```javascript
/**
 * Send mood data to API
 * @param {number} mood - Mood value (1-10)
 * @returns {Promise<Object>} API response
 */
async function sendMood(mood) {
    // ...
}
```

## Testing

### Unit Tests (Future)
```bash
pytest backend/tests/
```

### Integration Tests
```bash
./test/test-api.sh YOUR_API_URL
```

### Manual Testing Checklist
- [ ] Mood logging works
- [ ] Selfie analysis returns emotions
- [ ] Avatar generation completes
- [ ] Daily recap email received
- [ ] Risk scan detects low moods
- [ ] DynamoDB entries created
- [ ] S3 objects uploaded
- [ ] CloudWatch logs show no errors

## Documentation

Update these files when making changes:
- `README.md` - Main setup guide
- `docs/API_REFERENCE.md` - API changes
- `docs/SETUP_GUIDE.md` - Setup steps
- `PROJECT_STRUCTURE.md` - New files/folders

## Common Tasks

### Adding a New Lambda Function

1. Create directory: `backend/lambdas/newFunction/`
2. Add `lambda_function.py`
3. Update `infrastructure/deploy-lambdas.sh`
4. Add API Gateway route
5. Update documentation

### Adding a New API Endpoint

1. Create Lambda function
2. Add route in API Gateway
3. Update `frontend/index.html`
4. Update `docs/API_REFERENCE.md`
5. Add test in `test/test-api.sh`

### Updating Bedrock Prompts

1. Edit prompt in Lambda function
2. Test with sample data
3. Document in `docs/BEDROCK_PROMPTS.md`
4. Deploy updated Lambda

## Deployment

### Deploy Lambda Changes
```bash
cd infrastructure
./deploy-lambdas.sh EmoCompanion mindmate-uploads-ACCOUNT_ID
```

### Deploy Frontend Changes
```bash
# Update Amplify app
aws amplify update-app --app-id YOUR_APP_ID
```

### Deploy Infrastructure Changes
```bash
aws cloudformation update-stack \
  --stack-name mindmate-stack \
  --template-body file://infrastructure/cloudformation-template.yaml
```

## Getting Help

- Check `docs/TROUBLESHOOTING.md`
- Review CloudWatch Logs
- Ask in GitHub Issues
- Check AWS documentation

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn
- Focus on the code, not the person

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
