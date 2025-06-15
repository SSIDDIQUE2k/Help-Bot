# 🤖 HelpBot - AI Error Assistant

An intelligent error analysis system with semantic search capabilities, AI-enhanced responses, and a modern widget interface.

## ✨ Features

- **🔍 Advanced Semantic Search**: Finds relevant errors from natural language descriptions
- **🤖 AI-Enhanced Analysis**: Powered by Ollama for intelligent error categorization
- **📚 Confluence Integration**: Seamlessly connects to your knowledge base
- **🎯 Dual Interface**: Widget and sidebar modes for optimal user experience
- **⚡ Real-time Processing**: Instant error analysis with severity assessment
- **📱 Responsive Design**: Works perfectly on desktop and mobile

## 🚀 Deploy to Railway

### Quick Deploy
1. Fork this repository to your GitHub account
2. Go to [Railway](https://railway.app) and sign up/login
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your forked repository
5. Railway will automatically detect and deploy your Python app
6. Your app will be live in 2-3 minutes!

### Environment Variables (Optional)
Add these in Railway dashboard under Variables:
```
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@domain.com
CONFLUENCE_API_TOKEN=your-api-token
CONFLUENCE_SPACE_KEY=your-space-key
```

**Note**: App works perfectly in demo mode without these variables.

## 🛠️ Local Development

### Prerequisites

- Python 3.9+
- pip

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SSIDDIQUE2k/Help-Bot.git
   cd Help-Bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (optional):
   ```bash
   cp config.env.example .env
   # Edit .env with your Confluence credentials
   ```

4. **Run the application**:
   ```bash
   python backend/app.py
   ```

5. **Access the application**:
   - Main UI: http://localhost:8000
   - Widget Demo: http://localhost:8000/widget
   - Health Check: http://localhost:8000/health

## 🔧 Configuration

### Confluence Integration (Optional)

To connect to your Confluence space, set these environment variables:

```env
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@domain.com
CONFLUENCE_API_TOKEN=your-api-token
CONFLUENCE_SPACE_KEY=your-space-key
```

**Note**: If Confluence is not configured, the system runs in demo mode with sample data.

### Ollama AI Integration (Optional)

For local development with AI features:

1. Install [Ollama](https://ollama.ai)
2. Pull the model: `ollama pull llama3.2`
3. Start Ollama service: `ollama serve`

**Note**: AI features are optional and the system works without Ollama.

## 📖 API Documentation

### Endpoints

- `GET /` - Main application interface
- `GET /widget` - Widget demo page
- `GET /widget.js` - Embeddable widget JavaScript
- `POST /query` - Process error queries
- `GET /health` - Health check and system status
- `GET /test-connection` - Test Confluence connection

### Widget Integration

Embed HelpBot in any website:

```html
<script>
  window.HELPBOT_API_URL = 'https://your-railway-app.railway.app';
  window.HELPBOT_POSITION = 'bottom-right';
  window.HELPBOT_DEFAULT_MODE = 'widget';
</script>
<script src="https://your-railway-app.railway.app/widget.js"></script>
```

## 🏗️ Architecture

```
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── helpbot/
│   │   ├── confluence_client.py   # Confluence integration
│   │   ├── html_extractor.py      # Content parsing
│   │   └── ollama_service.py      # AI processing
│   ├── static/
│   │   └── helpbot-widget.js      # Widget JavaScript
│   └── templates/
│       ├── index.html             # Main UI
│       └── widget.html            # Widget template
├── requirements.txt           # Python dependencies
├── railway.toml              # Railway configuration
└── nixpacks.toml            # Build configuration
```

## 🔍 How It Works

1. **Query Processing**: User submits error description
2. **Semantic Analysis**: Advanced keyword extraction and error categorization
3. **Knowledge Search**: Multi-strategy search (exact match → keywords → fallback)
4. **Content Extraction**: Structured parsing of documentation
5. **AI Enhancement**: Optional AI analysis for categorization and responses
6. **Response Generation**: Formatted results with explanations and solutions

## 🎯 Use Cases

- **Technical Support**: Instant error resolution from knowledge base
- **Developer Tools**: Embedded help widget for applications
- **Documentation Search**: Semantic search through technical docs
- **Error Tracking**: Categorized error analysis and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/SSIDDIQUE2k/Help-Bot/issues)
- **Documentation**: Check the `/health` endpoint for system status
- **Demo**: Try the widget on the main page

## 🚀 Deployment Status

- ✅ Railway-ready with automatic builds
- ✅ Environment variable configuration
- ✅ Health checks and monitoring
- ✅ Scalable FastAPI backend
- ✅ Demo mode with sample data

---

**Built with ❤️ using FastAPI and Railway**
