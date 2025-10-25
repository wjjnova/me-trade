# LLM Configuration Guide

## Overview
The Me Trade Strategy Builder now supports multiple LLM providers for AI-powered strategy parsing. You can configure and switch between OpenAI (GPT) and Anthropic (Claude) models through a user-friendly settings interface.

## Features

### Supported Providers
1. **OpenAI (GPT Models)**
   - GPT-4
   - GPT-4 Turbo Preview
   - GPT-3.5 Turbo
   - GPT-3.5 Turbo 16K

2. **Anthropic (Claude Models)**
   - Claude 3.5 Sonnet (Recommended)
   - Claude 3 Opus
   - Claude 3 Sonnet
   - Claude 3 Haiku

### Key Capabilities
- ✅ Configure multiple LLM providers
- ✅ Store multiple API keys securely
- ✅ Switch between configurations
- ✅ Test LLM connections before use
- ✅ Delete configurations
- ✅ View masked API keys for security
- ✅ Automatic fallback to rule-based parsing

## Setup Guide

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs both `openai` and `anthropic` packages.

### Step 2: Get API Keys

#### For OpenAI (GPT)
1. Visit https://platform.openai.com/api-keys
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy your API key (starts with `sk-`)

#### For Anthropic (Claude)
1. Visit https://console.anthropic.com/
2. Create an account or sign in
3. Go to API Keys section
4. Generate a new API key
5. Copy your API key (starts with `sk-ant-`)

### Step 3: Configure in App

1. Launch the Me Trade app:
   ```bash
   streamlit run app.py
   ```

2. Navigate to **Settings** page (last item in sidebar)

3. Click **"➕ Add New LLM Configuration"**

4. Fill in the form:
   - **Provider**: Choose OpenAI or Anthropic
   - **Model**: Select from available models
   - **API Key**: Paste your API key

5. Click **"💾 Save Configuration"**

Your LLM is now active and ready to use!

## Using LLM in Strategy Builder

### Automatic Integration
Once configured, the LLM is automatically used in the Strategy Builder:

1. Go to **Strategy Builder** → **Define Strategy** tab
2. You'll see a status message: 🤖 **LLM Active: OpenAI (gpt-4)** or similar
3. Enter your strategy description in natural language
4. Click **"Parse Strategy"**
5. The LLM generates all three formats automatically

### Without LLM
If no LLM is configured, you'll see:
> ⚠️ No LLM configured. Using rule-based parsing.

The app will still work using simple pattern matching, but results may be less accurate.

## Managing Configurations

### View All Configurations
In the Settings page, scroll to **"All Saved Configurations"** to see:
- ✅ Active configurations (marked with checkmark)
- 🤖 Provider and model details
- Masked API keys (e.g., `sk-xxx...1234`)
- Creation dates

### Switch Active Configuration
1. Find the configuration you want to activate
2. Expand its panel
3. Click **"✅ Activate"**
4. Only one configuration can be active at a time

### Delete a Configuration
1. Expand the configuration panel
2. Click **"🗑️ Delete"**
3. Confirm deletion
4. The configuration and API key are permanently removed

## Testing Your Configuration

### Built-in Connection Test
1. In Settings page, scroll to **"Test LLM Connection"**
2. Enter a sample strategy description (pre-filled for you)
3. Click **"🧪 Test Connection"**
4. Wait for results (usually 3-10 seconds)
5. View parsed results:
   - Human Readable description
   - JSON strategy definition
   - Backtrader code snippet

### Test Results
- ✓ **Success**: Your LLM is configured correctly
- ❌ **Error**: Check API key, network connection, or API status

## Model Recommendations

### For Best Results
- **OpenAI GPT-4**: Most accurate, slower, higher cost
- **Claude 3.5 Sonnet**: Best balance of speed/accuracy/cost (Recommended)
- **GPT-3.5 Turbo**: Fastest, lower cost, less accurate

### For Budget-Conscious Users
- **Claude 3 Haiku**: Very fast, very cheap, good for simple strategies
- **GPT-3.5 Turbo**: Similar performance to Haiku

### For Complex Strategies
- **GPT-4 Turbo**: Handles complex multi-condition strategies
- **Claude 3 Opus**: Best at understanding nuanced instructions

## Security & Privacy

### API Key Storage
- API keys are stored in local SQLite database
- Keys are **not** transmitted except to respective LLM providers
- Keys are masked in UI (shows first 8 and last 4 characters)
- Database file: `data/metrade.db`

### Security Best Practices
- ✅ Use API keys with usage limits
- ✅ Monitor your API usage on provider dashboards
- ✅ Delete unused configurations
- ✅ Keep your database file secure
- ❌ Don't share your `metrade.db` file
- ❌ Don't commit API keys to version control

### Rotating API Keys
If you need to rotate your API key:
1. Generate new key on provider dashboard
2. Delete old configuration in Settings
3. Add new configuration with new key

## Troubleshooting

### "Test failed: Authentication error"
**Cause**: Invalid or expired API key
**Solution**: 
- Verify your API key on provider dashboard
- Generate a new key and update configuration

### "Test failed: Connection timeout"
**Cause**: Network issues or API downtime
**Solution**:
- Check your internet connection
- Visit provider status page (status.openai.com or status.anthropic.com)
- Try again in a few minutes

### "No LLM configured" warning in Strategy Builder
**Cause**: No active configuration
**Solution**:
- Go to Settings page
- Add a new configuration or activate existing one
- Return to Strategy Builder

### LLM returns invalid JSON
**Cause**: Model misunderstood instructions (rare)
**Solution**:
- Try a different model (GPT-4 or Claude 3.5 Sonnet)
- Simplify your strategy description
- Check fallback parsing worked (should auto-recover)

### "Import openai/anthropic could not be resolved"
**Cause**: Missing dependencies
**Solution**:
```bash
pip install openai anthropic
```

## Cost Considerations

### Pricing (Approximate, as of Oct 2025)

#### OpenAI
- **GPT-4**: ~$0.03 per 1K tokens input, ~$0.06 output
- **GPT-3.5 Turbo**: ~$0.0015 per 1K tokens input/output

#### Anthropic
- **Claude 3.5 Sonnet**: ~$0.003 per 1K tokens input, ~$0.015 output
- **Claude 3 Haiku**: ~$0.00025 per 1K tokens input, ~$0.00125 output

### Typical Strategy Parse
- Input: ~500 tokens (system prompt + user description)
- Output: ~800 tokens (three formats)
- **Total cost per parse**: $0.01 - $0.05 depending on model

### Cost Optimization Tips
1. Use cheaper models for simple strategies
2. Test with rule-based parsing first
3. Use LLM only when needed
4. Set usage limits on API keys

## API Rate Limits

### OpenAI
- Free tier: 3 requests/minute
- Paid tier 1: 60 requests/minute
- See: https://platform.openai.com/docs/guides/rate-limits

### Anthropic
- Default: 50 requests/minute
- Scale with usage tier
- See: https://docs.anthropic.com/claude/reference/rate-limits

### Handling Rate Limits
The app automatically falls back to rule-based parsing if rate limits are hit. No manual intervention needed.

## Advanced Configuration

### Environment Variables (Alternative)
For backward compatibility, you can still use environment variables:

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

This will work even without UI configuration, but UI settings take precedence.

### Database Schema
```sql
CREATE TABLE llm_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    api_key TEXT NOT NULL,
    is_active INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### Programmatic Access
```python
from src.db import get_db
from src.strategy import NLParser

# Load active config
db = get_db()
config = db.fetchone("SELECT * FROM llm_configs WHERE is_active = 1")

# Initialize parser
llm_config = {
    'provider': config['provider'],
    'model': config['model'],
    'api_key': config['api_key']
}
parser = NLParser(use_llm=True, llm_config=llm_config)

# Parse strategy
human, json_def, code = parser.parse_with_llm("Your strategy here")
```

## FAQ

### Q: Can I use multiple providers simultaneously?
A: No, only one configuration can be active at a time. You can switch between them.

### Q: What happens if my API key runs out of credits?
A: The app will show an error and automatically fall back to rule-based parsing.

### Q: Is my API key encrypted?
A: Currently stored in plain text in SQLite. For production use, consider encrypting the database or using secret management.

### Q: Can I use local LLM models?
A: Not currently supported, but could be added. Submit a feature request!

### Q: Does the app work without LLM configuration?
A: Yes! It uses rule-based parsing. LLM is optional but recommended for better accuracy.

### Q: Which provider is better?
A: Both are excellent. Claude 3.5 Sonnet offers best value. GPT-4 is slightly more accurate for complex strategies.

## Support

### Getting Help
- Check error messages in app
- Review logs in terminal
- Test connection in Settings page
- Try different model if issues persist

### Reporting Issues
Include in your report:
- Provider and model used
- Error message (mask your API key!)
- Sample strategy description (if possible)
- Steps to reproduce

---

**Last Updated**: October 25, 2025
**Version**: 2.1.0
**Feature**: Multi-LLM Support with UI Configuration
