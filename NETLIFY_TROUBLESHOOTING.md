# Netlify Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. **Parsing Error in Configuration**

**Problem**: Build fails with parsing error in netlify.toml
**Solutions**:

**Option A: Use Simple Configuration**
Rename `netlify.toml` to `netlify.toml.backup` and rename `netlify_simple.toml` to `netlify.toml`:
```bash
mv netlify.toml netlify.toml.backup
mv netlify_simple.toml netlify.toml
```

**Option B: Manual Build Settings**
In Netlify Dashboard, configure manually:
- **Build command**: `./build.sh`
- **Publish directory**: `backend/static`
- **Functions directory**: `netlify/functions`

**Option C: No Config File**
Delete netlify.toml and configure everything in the dashboard:
1. Build command: `pip install -r requirements.txt`
2. Publish directory: `backend/static`
3. Functions directory: `netlify/functions`

### 2. **Function Import Errors**

**Problem**: Cannot import backend modules
**Solutions**:

1. **Check Python Path**: The function should automatically handle paths
2. **Verify File Structure**:
   ```
   project/
   ├── netlify/functions/app.py
   ├── backend/app.py
   └── requirements.txt
   ```

### 3. **Build Command Fails**

**Problem**: Build process fails during pip install
**Solutions**:

1. **Use Alternative Build Commands**:
   ```bash
   # Option 1: Basic
   pip install -r requirements.txt
   
   # Option 2: With upgrade
   pip install --upgrade -r requirements.txt
   
   # Option 3: Force reinstall
   pip install --force-reinstall -r requirements.txt
   ```

2. **Check Python Version**: Ensure using Python 3.9
3. **Reduce Dependencies**: Use minimal requirements in `netlify/functions/requirements.txt`

### 4. **Environment Variables Not Working**

**Solutions**:
1. **Set in Netlify Dashboard**: Site Settings → Environment variables
2. **Redeploy**: After adding variables, trigger new deployment
3. **Case Sensitivity**: Variable names are case-sensitive

### 5. **Function Timeout**

**Problem**: Functions timing out (10-second limit)
**Solutions**:
1. **Optimize Code**: Reduce AI model response time
2. **Add Caching**: Cache Confluence responses
3. **Upgrade Plan**: Pro plan has longer timeouts

## Step-by-Step Debugging

### Method 1: Minimal Configuration
1. Delete `netlify.toml`
2. In Netlify Dashboard:
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `backend/static`
   - Functions directory: `netlify/functions`
3. Deploy

### Method 2: Simple TOML
1. Use `netlify_simple.toml` as `netlify.toml`
2. Deploy

### Method 3: Build Script
1. Use current `netlify.toml` with `./build.sh`
2. Check build logs for specific errors

## Environment Variables for Netlify

```bash
# Required for production
CONFLUENCE_BASE_URL=https://shaz.atlassian.net/wiki/
CONFLUENCE_USERNAME=siddiqueshazib4@gmail.com
CONFLUENCE_API_TOKEN=your_confluence_token
CONFLUENCE_SPACE_KEY=~plqtest1
HUGGINGFACE_API_TOKEN=your_hf_token

# Optional
PYTHON_VERSION=3.9
ENVIRONMENT=production
```

## Testing Locally

Test the function locally:
```bash
# Install netlify CLI
npm install -g netlify-cli

# Login to netlify
netlify login

# Test function locally
netlify dev
```

## If All Else Fails

**Alternative Platforms**:
1. **Railway**: `railway up` (simpler deployment)
2. **Render**: Git-based deployment
3. **Heroku**: Traditional PaaS
4. **DigitalOcean App Platform**: Container-based

**Contact Support**:
- Netlify Community Forum
- Check Netlify status page
- Review build logs carefully

## Success Indicators

When deployment works:
- ✅ Build completes without errors
- ✅ Function deploys successfully  
- ✅ Site loads at `https://[site-name].netlify.app`
- ✅ API endpoints respond (test `/health`)
- ✅ Environment variables accessible 