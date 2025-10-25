# LLM Configuration Quick Reference

## 🚀 Quick Setup (30 seconds)

1. **Install dependencies**
   ```bash
   pip install openai anthropic
   ```

2. **Get API key**
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

3. **Configure in app**
   - Open app → Go to **Settings** page
   - Click "➕ Add New LLM Configuration"
   - Select provider & model
   - Paste API key
   - Click "💾 Save Configuration"

4. **Start using**
   - Go to Strategy Builder
   - See "🤖 LLM Active" status
   - Parse strategies with AI!

## 📊 Model Comparison

| Provider | Model | Speed | Accuracy | Cost | Recommended For |
|----------|-------|-------|----------|------|-----------------|
| Anthropic | Claude 3.5 Sonnet | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | $$ | **Best overall choice** |
| OpenAI | GPT-4 | ⚡⚡ | ⭐⭐⭐⭐⭐ | $$$ | Complex strategies |
| Anthropic | Claude 3 Haiku | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | $ | Budget/simple strategies |
| OpenAI | GPT-3.5 Turbo | ⚡⚡⚡⚡ | ⭐⭐⭐ | $ | Budget/simple strategies |

## 🔑 API Key Formats

- **OpenAI**: `sk-proj-...` or `sk-...` (48-51 chars)
- **Anthropic**: `sk-ant-...` (~108 chars)

## ⚙️ Common Tasks

### Switch Provider
1. Settings → Find desired config
2. Click "✅ Activate"
3. Return to Strategy Builder

### Test Connection
1. Settings → "Test LLM Connection"
2. Click "🧪 Test Connection"
3. View results

### Delete Config
1. Settings → Expand config
2. Click "🗑️ Delete"
3. Confirm

## 💰 Cost Per Strategy Parse

- **Claude 3.5 Sonnet**: ~$0.01
- **Claude 3 Haiku**: ~$0.001
- **GPT-4**: ~$0.03
- **GPT-3.5**: ~$0.002

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Test failed: Authentication error" | Check API key validity |
| "Import could not be resolved" | Run `pip install openai anthropic` |
| "No LLM configured" warning | Add config in Settings |
| Rate limit error | Wait or upgrade API tier |

## 📱 UI Navigation

```
App Home
└── 5_Settings (⚙️ Settings)
    ├── Add New LLM Configuration
    ├── Active Configuration
    ├── All Saved Configurations
    └── Test LLM Connection

Strategy Builder (📝 Define Strategy)
├── LLM Status Indicator
├── Strategy Description Input
└── Parse Strategy Button
```

## 🌐 Language Support

All UI elements available in:
- 🇺🇸 English
- 🇨🇳 Chinese (中文)

## 📚 Documentation Files

- `LLM_CONFIGURATION_GUIDE.md` - Comprehensive guide
- `LLM_MULTI_PROVIDER_SUMMARY.md` - Technical details
- `LLM_QUICK_REFERENCE.md` - This file

## ⭐ Recommended Configuration

**For most users:**
- Provider: **Anthropic**
- Model: **claude-3-5-sonnet-20241022**
- Reason: Best balance of speed, accuracy, and cost

**Alternative for OpenAI users:**
- Provider: **OpenAI**
- Model: **gpt-4-turbo-preview**
- Reason: Slightly better for very complex strategies

## 🔒 Security Tips

✅ DO:
- Set usage limits on API keys
- Monitor usage on provider dashboards
- Delete unused configurations
- Keep database file secure

❌ DON'T:
- Share your API keys
- Commit keys to version control
- Share your `metrade.db` file
- Use production keys for testing

## 🆘 Getting Help

1. Check error message in app
2. Review `LLM_CONFIGURATION_GUIDE.md`
3. Test connection in Settings
4. Verify API key on provider dashboard
5. Check provider status pages

---

**Quick Start**: Settings → Add Config → Select Model → Paste Key → Save → Use! 🎉
