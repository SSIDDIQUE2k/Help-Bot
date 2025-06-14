# HelpBot - AI Error Assistant

An intelligent error assistant that integrates with Confluence to provide instant solutions to technical issues. Now enhanced with **Ollama** for natural language processing and conversational AI responses.

## 🚀 Features

### Core Features
- **Confluence Integration**: Automatically searches your Confluence knowledge base
- **Intelligent Error Parsing**: Extracts structured error information from documentation
- **Web Interface**: Clean, modern UI for easy interaction
- **Real-time Connection Testing**: Verify Confluence connectivity

### 🤖 AI Enhancement (New!)
- **Natural Language Processing**: Powered by Ollama for intelligent error analysis
- **Conversational Responses**: Get friendly, human-like explanations
- **Error Categorization**: Automatic classification (connection, configuration, authentication, etc.)
- **Severity Assessment**: Understand the impact level (low, medium, high)
- **Smart Suggestions**: Related queries you might be interested in
- **Enhanced Explanations**: Clear, step-by-step resolution instructions

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Confluence account with API access
- (Optional) Ollama for AI enhancement

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SSIDDIQUE2k/Help-Bot.git
   cd Help-Bot
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   Create a `.env` file in the root directory:
   ```env
   CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
   CONFLUENCE_USERNAME=your-email@domain.com
   CONFLUENCE_API_TOKEN=your-api-token
   CONFLUENCE_SPACE_KEY=YOUR_SPACE_KEY
   ```

4. **Set up Ollama (Optional but Recommended)**:
   ```bash
   python setup_ollama.py
   ```
   This will guide you through installing Ollama and downloading the AI model.

5. **Start the application**:
   ```bash
   cd backend
   python app.py
   ```

6. **Access the web interface**:
   Open http://localhost:8000 in your browser

## 🤖 Ollama Integration

### Automatic Setup
Run the setup script for guided installation:
```bash
python setup_ollama.py
```

### Manual Setup
1. **Install Ollama**:
   - macOS: `brew install ollama`
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - Windows: Download from https://ollama.ai/download

2. **Start Ollama service**:
   ```bash
   ollama serve
   ```

3. **Pull a model**:
   ```bash
   ollama pull llama3.2
   ```

### Supported Models
- `llama3.2` (recommended) - Fast and efficient
- `llama3.1` - More capable but slower
- `codellama` - Specialized for code-related errors

## 📊 API Endpoints

- `GET /` - Web interface
- `POST /query` - Submit error queries
- `GET /test-connection` - Test Confluence connection
- `GET /health` - Health check with feature status
- `GET /ollama-status` - Check AI enhancement status

## 🎯 Usage Examples

### Basic Error Query
```
"Getting connection timeout error when connecting to database"
```

### Specific Error Log
```
"Error Log 3999: AS2 connection failed"
```

### Natural Language Query
```
"Why is my API returning 500 errors?"
```

## 🔧 Configuration

### Environment Variables
- `CONFLUENCE_URL` - Your Confluence base URL
- `CONFLUENCE_USERNAME` - Your Confluence username/email
- `CONFLUENCE_API_TOKEN` - Your Confluence API token
- `CONFLUENCE_SPACE_KEY` - The space to search in

### Ollama Configuration
The Ollama service runs on `http://localhost:11434` by default. You can customize this in the `OllamaService` class.

## 🏗️ Architecture

```
HelpBot/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── helpbot/
│   │   ├── confluence_client.py    # Confluence API integration
│   │   ├── html_extractor.py       # Error parsing logic
│   │   └── ollama_service.py       # AI enhancement service
│   ├── templates/
│   │   └── index.html         # Web interface
│   └── requirements.txt       # Python dependencies
├── setup_ollama.py           # Ollama setup script
├── .env                      # Environment configuration
└── README.md
```

## 🚦 Status Indicators

The web interface shows real-time status for:
- **Confluence Connection**: Green (connected) / Red (disconnected)
- **AI Enhancement**: "AI Enhanced" / "Basic Mode"
- **Error Severity**: Low / Medium / High
- **Error Category**: Connection / Configuration / Authentication / Data / General

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both basic and AI-enhanced modes
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**Ollama not working?**
- Ensure Ollama service is running: `ollama serve`
- Check if model is downloaded: `ollama list`
- Verify connection: `curl http://localhost:11434/api/version`

**Confluence connection failed?**
- Verify your API token is correct
- Check if your Confluence URL includes `/wiki`
- Ensure your user has access to the specified space

**No error entries found?**
- Check if your Confluence page has the expected format
- Verify the space key is correct
- Try the universal parser fallback

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Custom model fine-tuning
- [ ] Integration with other knowledge bases
- [ ] Advanced error analytics
- [ ] Team collaboration features
