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