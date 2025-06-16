# HelpBot Netlify Deployment Guide 🚀

## Quick Deployment Steps

### 1. Connect to Netlify
1. Go to [Netlify](https://app.netlify.com/)
2. Click "Add new site" → "Import an existing project"
3. Connect your GitHub account
4. Select your `Help-Bot` repository

### 2. Configure Build Settings
Netlify should auto-detect the settings from `netlify.toml`, but verify:

**Build Settings:**
- **Base directory**: `.` (root)
- **Build command**: `pip install -r requirements.txt && echo 'Build completed'`
- **Publish directory**: `backend/static`
- **Functions directory**: `netlify/functions`

### 3. Environment Variables
Add these in Netlify Dashboard → Site Settings → Environment Variables:

```bash
# Confluence Configuration
CONFLUENCE_BASE_URL=https://shaz.atlassian.net/wiki/
CONFLUENCE_USERNAME=siddiqueshazib4@gmail.com
CONFLUENCE_API_TOKEN=your_confluence_api_token
CONFLUENCE_SPACE_KEY=~plqtest1

# AI Provider Configuration
HUGGINGFACE_API_TOKEN=hf_your_huggingface_token_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Application Settings
ENVIRONMENT=production
PYTHON_VERSION=3.9
```

### 4. Deploy
1. Click "Deploy site"
2. Wait for build to complete
3. Your HelpBot will be available at `https://[random-name].netlify.app`

## Features Enabled ✅

- **Dual AI Providers**: Ollama (primary) + Hugging Face (backup)
- **Real-time Confluence Search**: No caching issues
- **Automatic Fallbacks**: Multiple error handling layers
- **Production-Ready**: Optimized for Netlify serverless functions

## Architecture on Netlify

```
Internet → Netlify CDN → Serverless Function (FastAPI) → Confluence/AI APIs
```

**Benefits:**
- ✅ **No Password Protection** (unlike Vercel preview deployments)
- ✅ **Generous Free Tier**: 100GB bandwidth, 125,000 function invocations
- ✅ **Easy Environment Management**: Simple dashboard
- ✅ **Automatic HTTPS**: SSL certificates included
- ✅ **Global CDN**: Fast worldwide access

## Troubleshooting

### Build Fails
1. Check Python version in `runtime.txt` matches `netlify.toml`
2. Verify all dependencies in `requirements.txt` are compatible
3. Check build logs for specific error messages

### Function Timeout
- Netlify functions have 10-second timeout by default
- Upgrade to Pro for longer timeouts if needed
- Optimize AI model calls for faster responses

### Environment Variables Not Working
1. Verify variables are set in Netlify dashboard
2. Check variable names match exactly (case-sensitive)
3. Redeploy after adding new variables

## Custom Domain (Optional)

1. Go to Site Settings → Domain management
2. Add custom domain: `helpbot.yourdomain.com`
3. Configure DNS records as instructed
4. SSL certificate auto-generated

## Monitoring

- **Build Logs**: Netlify Dashboard → Deploys
- **Function Logs**: Dashboard → Functions → View logs
- **Analytics**: Dashboard → Analytics (Pro plan)

---

**Next Steps After Deployment:**
1. Test all endpoints work correctly
2. Verify Confluence integration
3. Test Hugging Face fallback
4. Set up custom domain (optional)
5. Configure monitoring/alerts (optional) 