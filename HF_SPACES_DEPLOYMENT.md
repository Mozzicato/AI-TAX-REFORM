# 🚀 Deployment to Hugging Face Spaces

This guide walks you through deploying NTRIA to Hugging Face Spaces with Gradio.

## Prerequisites

- Hugging Face account (create at https://huggingface.co)
- Git installed locally
- Git credentials configured

## Step 1: Create a Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in:
   - **Owner**: Your username
   - **Space name**: `TAXBOT` (or your preferred name)
   - **License**: `MIT`
   - **SDK**: `Gradio`
   - **Gradio template**: Leave empty (we'll use custom)
   - **Visibility**: Public (or Private if preferred)
4. Click **"Create Space"**

## Step 2: Generate Hugging Face Access Token

1. Go to https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Select:
   - **Name**: Git credential (or any name)
   - **Type**: `write`
4. Copy the token and save it securely

## Step 3: Clone the Space Repository

```bash
# Clone your new Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/TAXBOT
cd TAXBOT

# If you get a password prompt, use your HF token as the password
```

## Step 4: Add Files from AI-TAX-REFORM

Copy the following files to your Space repository:

```bash
# From AI-TAX-REFORM to your Space repo
cp /path/to/AI-TAX-REFORM/app.py .
cp /path/to/AI-TAX-REFORM/requirements.txt .
cp /path/to/AI-TAX-REFORM/README.md .
cp /path/to/AI-TAX-REFORM/packages.txt .
```

## Step 5: Configure Backend Connection

Edit your `.env` file (create if it doesn't exist):

```bash
# .env (in Space root)
BACKEND_API_URL=https://your-backend-api.com
```

**For local testing**: Leave as `http://localhost:8000` (default)

## Step 6: Commit and Push

```bash
git add .
git commit -m "Add NTRIA Gradio interface and dependencies"
git push
```

Use your HF token as the password when prompted.

## Step 7: Monitor Deployment

1. After pushing, go to your Space page: `https://huggingface.co/spaces/YOUR_USERNAME/TAXBOT`
2. Check the **"Logs"** tab to see build progress
3. Your Space should be live within 1-2 minutes

## Configuration Options

### Change App Appearance

Edit the `README.md` metadata at the top:

```yaml
---
title: NTRIA - Nigeria Tax Reform Intelligence Assistant
emoji: 🇳🇬
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 4.26.0
app_file: app.py
pinned: true
license: mit
---
```

**Color options**: `blue`, `green`, `red`, `yellow`, `pink`, `purple`, etc.

### Environment Variables

Add these to your Space settings (Space Settings → Variables and Secrets):

| Variable | Value | Type |
|----------|-------|------|
| `BACKEND_API_URL` | Your API endpoint | Secret |
| `API_TIMEOUT` | `30` (seconds) | Variable |

## Connecting to Backend

### Option 1: Local Backend (Development)

If your backend runs locally, you can use `localhost` for testing:

```python
BACKEND_API_URL = "http://localhost:8000"
```

### Option 2: Remote Backend (Production)

Deploy your FastAPI backend separately:

- **Railway**: https://railway.app
- **Render**: https://render.com
- **Heroku**: https://heroku.com
- **AWS**: https://aws.amazon.com

Update `BACKEND_API_URL` in Space environment variables.

### Option 3: Edge Case - No Backend

If backend is unavailable, the app will show a connection warning but remain usable with mock responses.

## Troubleshooting

### "Cannot reach backend API"

1. Check `BACKEND_API_URL` is correct in environment variables
2. Verify backend service is running and accessible
3. Check firewall/CORS settings
4. Review logs in Space settings

### Build Fails

1. Check `requirements.txt` has no conflicting versions
2. Look at Space logs for specific error
3. Ensure `app_file: app.py` points to correct file

### Slow Response

1. Increase `API_TIMEOUT` in environment variables
2. Check backend service performance
3. Monitor Space resources in settings

## Advanced: Custom Styling

You can add custom CSS to `app.py`:

```python
# In the Blocks context
gr.Markdown("""
<style>
  .gradio-container {
    max-width: 900px !important;
  }
</style>
""")
```

## Next Steps

1. ✅ Deploy to Hugging Face Spaces
2. 📊 Monitor usage analytics
3. 🔄 Update docs as features change
4. 🚀 Scale backend infrastructure if needed

## Resources

- [Gradio Documentation](https://www.gradio.app/docs)
- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Model Card Guide](https://huggingface.co/docs/hub/model-cards)

---

**Questions?** Check the [GitHub Issues](https://github.com/Mozzicato/AI-TAX-REFORM/issues) or create a new one.
