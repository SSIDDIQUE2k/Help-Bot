# 🚀 Railway Deployment Guide

This guide will help you deploy HelpBot to Railway in just a few minutes.

## 🎯 Quick Deploy

### Option 1: One-Click Deploy (Recommended)

1. Click the deploy button in the README
2. Connect your GitHub account to Railway
3. Configure environment variables (optional)
4. Deploy!

### Option 2: Manual Deploy

1. **Fork the Repository**
   - Go to https://github.com/SSIDDIQUE2k/Help-Bot
   - Click "Fork" to create your own copy

2. **Create Railway Project**
   - Visit [Railway](https://railway.app)
   - Sign up/login with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your forked repository

3. **Configure Environment Variables** (Optional)
   
   In Railway dashboard, go to Variables tab and add:
   
   ```
   CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
   CONFLUENCE_USERNAME=your-email@domain.com
   CONFLUENCE_API_TOKEN=your-api-token
   CONFLUENCE_SPACE_KEY=your-space-key
   ```
   
   **Note**: If you don't configure these, the app runs in demo mode with sample data.

4. **Deploy**
   - Railway will automatically detect the Python app
   - Build process starts automatically
   - Your app will be live in 2-3 minutes

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `CONFLUENCE_URL` | No | Your Confluence base URL | `https://company.atlassian.net/wiki` |
| `CONFLUENCE_USERNAME` | No | Your Confluence email | `user@company.com` |
| `CONFLUENCE_API_TOKEN` | No | Confluence API token | `ATATT3xFfGF0...` |
| `CONFLUENCE_SPACE_KEY` | No | Space key to search | `HELP` |
| `PORT` | Auto | Railway sets this automatically | `8000` |
| `ENVIRONMENT` | No | Set to `development` for debug mode | `production` |

### Getting Confluence API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name like "HelpBot"
4. Copy the token (save it securely!)

## 🚦 Deployment Status

After deployment, check these endpoints:

- **Main App**: `https://your-app.railway.app/`
- **Health Check**: `https://your-app.railway.app/health`
- **Widget Demo**: `https://your-app.railway.app/widget`

## 🔍 Troubleshooting

### Build Fails

**Issue**: Build process fails
**Solution**: 
- Check the build logs in Railway dashboard
- Ensure all files are committed to your repository
- Verify requirements.txt is present

### App Won't Start

**Issue**: App starts but returns 500 errors
**Solution**:
- Check the deployment logs
- Verify environment variables are set correctly
- Test the `/health` endpoint

### Confluence Connection Issues

**Issue**: Confluence integration not working
**Solution**:
- Verify your API token is correct
- Check if your Confluence URL includes `/wiki`
- Ensure your user has access to the specified space
- Test with `/test-connection` endpoint

### Widget Not Loading

**Issue**: Widget doesn't appear on external sites
**Solution**:
- Check CORS settings (already configured for `*`)
- Verify the widget URL is correct
- Check browser console for errors

## 📊 Monitoring

### Health Checks

Railway automatically monitors your app using the `/health` endpoint. This endpoint returns:
```json
{
  "status": "healthy",
  "service": "helpbot",
  "mode": "confluence|demo",
  "confluence_configured": true|false,
  "ollama_available": false,
  "features": {
    "confluence_integration": true|false,
    "demo_data": true|false,
    "natural_language_processing": false,
    "error_enhancement": false,
    "conversational_responses": false,
    "widget_sidebar_toggle": true
  }
}
```

### Logs

Access logs in Railway dashboard:
- Go to your project
- Click on the service
- Navigate to "Logs" tab

## 🔄 Updates

To update your deployed app:

1. Make changes to your forked repository
2. Commit and push to GitHub
3. Railway automatically redeploys

## 💡 Tips

1. **Demo Mode**: The app works great without Confluence - perfect for testing
2. **Widget Integration**: Use the widget on any website by including the script
3. **Custom Domain**: Railway allows custom domains in paid plans
4. **Scaling**: Railway automatically scales based on traffic
5. **Environment**: Set `ENVIRONMENT=development` for detailed error messages

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review Railway deployment logs
3. Test the `/health` endpoint
4. Open an issue on GitHub

## 🎉 Success!

Once deployed, your HelpBot will be available at:
`https://your-app-name.railway.app`

The widget can be embedded anywhere using:
```html
<script>
  window.HELPBOT_API_URL = 'https://your-app-name.railway.app';
</script>
<script src="https://your-app-name.railway.app/widget.js"></script>
```

Happy deploying! 🚀 