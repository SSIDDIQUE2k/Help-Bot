# 🚀 Multi-Platform Deployment Guide

Deploy your HelpBot to any of these popular platforms. Each has its own advantages!

## 🎯 Quick Comparison

| Platform | Free Tier | Ease | Best For |
|----------|-----------|------|----------|
| **Render** | ✅ Yes | ⭐⭐⭐⭐⭐ | Beginners, Python apps |
| **Railway** | ✅ Yes | ⭐⭐⭐⭐ | Modern deployment |
| **Heroku** | ❌ No | ⭐⭐⭐⭐ | Classic choice |
| **Fly.io** | ✅ Yes | ⭐⭐⭐ | Global deployment |
| **Vercel** | ✅ Yes | ⭐⭐ | Serverless (limited) |
| **DigitalOcean** | ❌ No | ⭐⭐⭐ | Full control |

---

## 🟢 Render (Recommended)

**Best for beginners and Python apps**

### Quick Deploy
1. Fork this repository
2. Go to [Render](https://render.com)
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Render auto-detects the `render.yaml` config
6. Deploy! 🎉

### Manual Setup
1. **Service Type**: Web Service
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
4. **Environment**: Python 3.11

---

## 🚂 Railway

**Modern deployment platform**

### Quick Deploy
1. Fork this repository
2. Go to [Railway](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select your repo
5. Railway uses the `railway.toml` config
6. Generate domain in Settings → Networking

---

## 🟣 Heroku

**Classic platform (paid plans only)**

### Deploy Steps
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login: `heroku login`
3. Create app: `heroku create your-helpbot-name`
4. Deploy: `git push heroku main`
5. Open: `heroku open`

**Files used**: `Procfile`, `runtime.txt`, `requirements.txt`

---

## 🪰 Fly.io

**Global edge deployment**

### Deploy Steps
1. Install [Fly CLI](https://fly.io/docs/getting-started/installing-flyctl/)
2. Login: `fly auth login`
3. Launch: `fly launch` (uses `fly.toml`)
4. Deploy: `fly deploy`
5. Open: `fly open`

---

## ⚡ Vercel

**Serverless deployment (limited for FastAPI)**

### Deploy Steps
1. Install [Vercel CLI](https://vercel.com/cli): `npm i -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel` (uses `vercel.json`)
4. Follow prompts

**Note**: Limited functionality due to serverless constraints

---

## 🌊 DigitalOcean App Platform

**Full-featured cloud platform**

### Deploy Steps
1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect GitHub repo
4. Choose "Autodeploy" (uses `Dockerfile`)
5. Configure:
   - **Type**: Web Service
   - **Port**: 8000
   - **Health Check**: `/health`

---

## 🐳 Docker Deployment

**For any Docker-compatible platform**

### Local Testing
```bash
# Build image
docker build -t helpbot .

# Run container
docker run -p 8000:8000 helpbot

# Access at http://localhost:8000
```

### Deploy to Cloud
- **Google Cloud Run**: `gcloud run deploy`
- **AWS ECS**: Use the Dockerfile
- **Azure Container Instances**: Deploy from Docker Hub

---

## 🔧 Environment Variables

For any platform, you can optionally add:

```env
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@domain.com
CONFLUENCE_API_TOKEN=your-api-token
CONFLUENCE_SPACE_KEY=your-space-key
ENVIRONMENT=production
```

**Note**: App works perfectly in demo mode without these!

---

## 🎯 Platform-Specific Tips

### Render
- ✅ Automatic HTTPS
- ✅ Free tier available
- ✅ Great for Python apps
- ✅ Auto-deploys from GitHub

### Railway
- ✅ Modern interface
- ✅ Great developer experience
- ✅ Automatic domain generation
- ⚠️ Must manually generate domain

### Heroku
- ✅ Mature platform
- ✅ Extensive add-ons
- ❌ No free tier anymore
- ✅ Great documentation

### Fly.io
- ✅ Global edge deployment
- ✅ Great performance
- ✅ Docker-based
- ⚠️ Steeper learning curve

---

## 🚀 Recommended Deployment Order

1. **Start with Render** - Easiest and most reliable
2. **Try Railway** - Modern and developer-friendly
3. **Consider Fly.io** - If you need global deployment
4. **Use Docker** - For maximum flexibility

---

## 🆘 Troubleshooting

### Common Issues
- **Port errors**: Ensure using `$PORT` environment variable
- **Build failures**: Check Python version (3.11 required)
- **Import errors**: Verify all files are committed to Git
- **Health check fails**: Ensure `/health` endpoint works

### Getting Help
- Check platform-specific logs
- Verify environment variables
- Test locally first: `python backend/app.py`
- Open GitHub issue if needed

---

## 🎉 Success!

Once deployed, your HelpBot will be available with:
- ✅ **Semantic search** with demo data
- ✅ **Modern responsive UI**
- ✅ **Widget embedding** capability
- ✅ **Health monitoring**
- ✅ **Optional Confluence integration**

**Happy deploying!** 🚀

## 🔧 Fixing Confluence Integration in Vercel

If your Vercel deployment is showing generic/demo responses instead of your actual Confluence data, you need to configure environment variables.

### Step 1: Get Your Confluence Credentials

1. **Confluence URL**: Your Atlassian URL (e.g., `https://your-company.atlassian.net`)
2. **Username**: Your Confluence email address
3. **API Token**: Generate at [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
4. **Space Key**: Found in your Confluence space URL (`/spaces/YOUR_SPACE_KEY/overview`)

### Step 2: Configure Vercel Environment Variables

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your HelpBot project
3. Go to **Settings** → **Environment Variables**
4. Add these variables:

```
CONFLUENCE_URL=https://your-company.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your-confluence-api-token
CONFLUENCE_SPACE_KEY=YOUR_SPACE_KEY
```

### Step 3: Redeploy

After adding environment variables:
1. Go to **Deployments** tab
2. Click **Redeploy** on your latest deployment
3. Or push a new commit to trigger automatic redeployment

### Step 4: Test Connection

Visit your deployed app and check:
- `/test-connection` endpoint should show Confluence connection status
- Search queries should return actual Confluence content instead of demo data

---

## Platform-Specific Deployment Instructions

### 1. Render Deployment

**Recommended for beginners** - Free tier with automatic builds

1. Fork this repository
2. Connect to [Render](https://render.com)
3. Create new Web Service
4. Connect your GitHub repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
6. Add environment variables in Render dashboard
7. Deploy!

**Render Configuration** (`render.yaml`):
```yaml
services:
  - type: web
    name: helpbot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: CONFLUENCE_URL
        value: https://your-company.atlassian.net
      - key: CONFLUENCE_USERNAME  
        value: your-email@company.com
      - key: CONFLUENCE_API_TOKEN
        sync: false
      - key: CONFLUENCE_SPACE_KEY
        value: YOUR_SPACE_KEY
```

### 2. Railway Deployment

**Modern platform** - Great developer experience

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`

**Railway Configuration** (`railway.toml`):
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn backend.app:app --host 0.0.0.0 --port $PORT"

[[services]]
name = "helpbot"
```

### 3. Vercel Deployment

**Serverless platform** - Great for global distribution

1. Install Vercel CLI: `npm install -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel --prod`

**Vercel Configuration** (`vercel.json`):
```json
{
  "builds": [
    {
      "src": "backend/app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/app.py"
    }
  ],
  "functions": {
    "backend/app.py": {
      "maxDuration": 30
    }
  }
}
```

### 4. Fly.io Deployment

**Global edge deployment** - Deploy close to your users

1. Install flyctl: [Installation Guide](https://fly.io/docs/getting-started/installing-flyctl/)
2. Login: `fly auth login`
3. Launch: `fly launch`
4. Deploy: `fly deploy`

**Fly Configuration** (`fly.toml`):
```toml
app = "helpbot-ai"
primary_region = "dfw"

[build]

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

### 5. Docker Deployment

**Container-based** - Deploy anywhere that supports Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
COPY config.env.example .env

EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run**:
```bash
docker build -t helpbot .
docker run -p 8000:8000 --env-file .env helpbot
```

### 6. Heroku Deployment

**Classic platform** - Requires paid plan

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-helpbot-app`
4. Deploy: `git push heroku main`

**Heroku Configuration**:
- `Procfile`: `web: uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
- `runtime.txt`: `python-3.11.0`

### 7. Platform.sh Deployment

**Enterprise platform** - Advanced features

**Platform.sh Configuration** (`.platform.app.yaml`):
```yaml
name: helpbot
type: python:3.11

web:
  commands:
    start: uvicorn backend.app:app --host 0.0.0.0 --port $PORT

disk: 1024

mounts:
  'logs':
    source: local
    source_path: logs
```

---

## Environment Variables Reference

### Required for Confluence Integration
```bash
CONFLUENCE_URL=https://your-company.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your-confluence-api-token
CONFLUENCE_SPACE_KEY=YOUR_SPACE_KEY
```

### Optional for AI Enhancement
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Server Configuration
```bash
PORT=8000
DEBUG=false
ENVIRONMENT=production
```

---

## Troubleshooting

### Common Issues

1. **"Demo mode" responses**: Environment variables not configured
2. **Connection timeout**: Check Confluence URL and credentials
3. **404 Space not found**: Verify CONFLUENCE_SPACE_KEY
4. **401 Unauthorized**: Check API token and username
5. **Build failures**: Ensure requirements.txt is present

### Debug Steps

1. Check `/health` endpoint for system status
2. Check `/test-connection` for Confluence connectivity
3. Review deployment logs for error messages
4. Verify environment variables are set correctly

### Getting Help

- Check the [GitHub Issues](https://github.com/SSIDDIQUE2k/Help-Bot/issues)
- Review deployment platform documentation
- Test locally first with `.env` file

---

## Security Notes

- Never commit API tokens to version control
- Use environment variables for all sensitive data
- Enable HTTPS in production
- Restrict CORS origins in production deployments
- Regularly rotate API tokens

---

## Performance Optimization

- Enable caching for Confluence responses
- Use CDN for static assets
- Configure appropriate timeout values
- Monitor memory usage and adjust instance size
- Consider using Redis for session storage

---

*For more detailed instructions, check the platform-specific documentation or create an issue in the repository.* 